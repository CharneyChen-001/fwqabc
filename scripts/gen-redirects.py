#!/usr/bin/env python3
"""从 data/links.yaml 生成 deploy/Caddyfile 和 static/_redirects。无第三方依赖。"""
import pathlib, re
root = pathlib.Path(__file__).resolve().parent.parent
links = {}
for line in (root / "data/links.yaml").read_text(encoding="utf-8").splitlines():
    line = line.split(" #")[0].strip()
    if not line or line.startswith("#"):
        continue
    k, v = line.split(":", 1)
    k, v = k.strip(), v.strip().strip('"\'')
    if not re.fullmatch(r"[a-z0-9-]+", k):
        raise SystemExit(f"bad slug: {k}")
    links[k] = v

redir = "\n".join(f"\tredir /go/{k} {v} 302\n\tredir /go/{k}/ {v} 302" for k, v in sorted(links.items()))
caddy = f"""# 自动生成：python3 scripts/gen-redirects.py（勿手改 /go/ 部分）
fwqabc.com {{
\tredir https://www.fwqabc.com{{uri}} 0
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
