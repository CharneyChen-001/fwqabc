#!/usr/bin/env python3
"""从 data/links.yaml 生成 deploy/Caddyfile、static/_redirects 和 static/_headers。无第三方依赖。"""
import pathlib, re
from urllib.parse import quote, urlsplit
root = pathlib.Path(__file__).resolve().parent.parent

def umami_origins():
    """hugo.toml 里配置了 Umami 时，把脚本源站放进 CSP，避免启用统计后被拦住。"""
    text = (root / "hugo.toml").read_text(encoding="utf-8")
    origins = []
    for match in re.finditer(r'(?m)^\s*umami(?:WebsiteId)?\s*=\s*"([^"]*)"', text):
        value = match.group(1).strip()
        if not value.startswith("http"):
            continue
        parts = urlsplit(value)
        if parts.scheme and parts.netloc:
            origins.append(f"{parts.scheme}://{parts.netloc}")
    # 去重并保持顺序
    unique = []
    for origin in origins:
        if origin not in unique:
            unique.append(origin)
    return unique
def parse(text):
    """极简 YAML 解析：顶层 slug + 两空格缩进的 key: value（无第三方依赖）。"""
    data, cur = {}, None
    for raw in text.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        line = re.sub(r"\s+#.*$", "", raw.rstrip())
        if not raw.startswith(" "):
            cur = line.rstrip(":").strip()
            if not re.fullmatch(r"[a-z0-9-]+", cur):
                raise SystemExit(f"bad slug: {cur}")
            data[cur] = {}
        else:
            k, v = line.strip().split(":", 1)
            data[cur][k.strip()] = v.strip().strip('"\'')
    return data

links = {}
for slug, c in parse((root / "data/links.yaml").read_text(encoding="utf-8")).items():
    landing, aff = c.get("landing", ""), c.get("aff", "")
    if not landing:
        raise SystemExit(f"{slug}: landing is required")
    if aff:
        tpl = c.get("aff_template") or landing
        target = tpl.format(aff=aff, landing=landing, landing_enc=quote(landing, safe=""))
    else:
        target = landing
    links[slug] = target

redir = "\n".join(f"\tredir /go/{k} {v} 302\n\tredir /go/{k}/ {v} 302" for k, v in sorted(links.items()))
# 站内脚本有内联代码（倒计时、主题切换、复制链接）。unsafe-inline 是为了不打断这些脚本。
# 筛选和搜索脚本在本站 /js/，不需要外部脚本域名。Umami 留空时不放第三方源。
extra = " ".join(umami_origins())
script_src = "script-src 'self' 'unsafe-inline'" + (f" {extra}" if extra else "")
connect_src = "connect-src 'self'" + (f" {extra}" if extra else "")
csp = (
    "default-src 'self'; "
    + script_src + "; "
    + "style-src 'self' 'unsafe-inline'; "
    + "img-src 'self' data: https:; "
    + "font-src 'self'; "
    + connect_src + "; "
    + "frame-ancestors 'none'; base-uri 'self'; form-action 'self'; object-src 'none'"
)
caddy = f"""# 自动生成：python3 scripts/gen-redirects.py（勿手改 /go/ 与安全头）
fwqabc.com {{
\troot * /var/www/fwqabc
\tencode zstd gzip
{redir}
\tredir /feed /feed.xml 301
\theader /go/* X-Robots-Tag "noindex, nofollow"
\theader {{
\t\tStrict-Transport-Security "max-age=31536000"
\t\tX-Content-Type-Options nosniff
\t\tReferrer-Policy strict-origin-when-cross-origin
\t\tX-Frame-Options DENY
\t\tPermissions-Policy "camera=(), microphone=(), geolocation=(), payment=()"
\t\tContent-Security-Policy "{csp}"
\t}}
\tfile_server
\thandle_errors {{
\t\trewrite * /404.html
\t\tfile_server
\t}}
}}

www.fwqabc.com {{
\tredir https://fwqabc.com{{uri}} 301
}}
"""
(root / "deploy").mkdir(exist_ok=True)
(root / "deploy/Caddyfile").write_text(caddy, encoding="utf-8")
lines = ["# 自动生成：python3 scripts/gen-redirects.py（Cloudflare Pages / Netlify 格式）"]
for k, v in sorted(links.items()):
    lines += [f"/go/{k} {v} 302", f"/go/{k}/ {v} 302"]
lines += ["# /feed.xml 由 Hugo 输出，和 /index.xml 都是 RSS。", "/feed /feed.xml 301"]
(root / "static/_redirects").write_text("\n".join(lines) + "\n", encoding="utf-8")
headers = f"""# 自动生成：python3 scripts/gen-redirects.py
/*
  Strict-Transport-Security: max-age=31536000
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
  X-Frame-Options: DENY
  Permissions-Policy: camera=(), microphone=(), geolocation=(), payment=()
  Content-Security-Policy: {csp}

/go/*
  X-Robots-Tag: noindex, nofollow
"""
(root / "static/_headers").write_text(headers, encoding="utf-8")
print(f"generated {len(links)} redirects")
