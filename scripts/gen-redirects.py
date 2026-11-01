#!/usr/bin/env python3
"""从 data/links.yaml 生成 deploy/Caddyfile 和 static/_redirects。无第三方依赖。"""
import pathlib, re
root = pathlib.Path(__file__).resolve().parent.parent
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

from urllib.parse import quote
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
caddy = f"""# 自动生成：python3 scripts/gen-redirects.py（勿手改 /go/ 部分）
fwqabc.com {{
\troot * /var/www/fwqabc
\tencode zstd gzip
{redir}
\theader /go/* X-Robots-Tag "noindex, nofollow"
\theader {{
\t\tStrict-Transport-Security "max-age=31536000"
\t\tX-Content-Type-Options nosniff
\t\tReferrer-Policy strict-origin-when-cross-origin
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
(root / "static/_redirects").write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"generated {len(links)} redirects")
