# 部署说明（香港/日本 VPS + Caddy + Cloudflare）

## 1. 服务器准备（Debian/Ubuntu）

```bash
sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https curl rsync
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list
sudo apt update && sudo apt install -y caddy
sudo mkdir -p /var/www/fwqabc && sudo chown $USER /var/www/fwqabc
```

## 2. Caddy 配置

`deploy/Caddyfile` 由 `python3 scripts/gen-redirects.py` 生成，包含 `/go/<slug>` 302 跳转。

```bash
sudo cp deploy/Caddyfile /etc/caddy/Caddyfile
sudo systemctl reload caddy
```

Caddy 会自动申请 Let's Encrypt 证书（HTTPS）。

## 3. Cloudflare

1. DNS 添加 `fwqabc.com` 与 `www` 的 A 记录指向服务器 IP。
2. 首次签证书时可先设为“仅 DNS”（灰云），证书签好后再切换为橙云。
3. SSL/TLS 模式设为 **Full (strict)**。
4. 可选：缓存规则对 `/go/*` 设为绕过缓存。

## 4. GitHub Actions 自动部署

`deploy/github-workflow-deploy.yml（启用时移到 .github/workflows/deploy.yml）` 默认只能手动运行（workflow_dispatch）。在仓库 Settings → Secrets 添加：

- `SSH_HOST`：服务器 IP/域名
- `SSH_USER`：部署用户（对 /var/www/fwqabc 有写权限）
- `SSH_KEY`：部署专用私钥（不要提交到仓库）

工作流会把 Caddyfile 上传到 `/tmp/fwqabc.Caddyfile`，需手动审阅后替换 `/etc/caddy/Caddyfile` 并 reload。

## 备选：Cloudflare Pages

构建命令 `hugo --gc --minify`，输出目录 `public`；`static/_redirects` 提供 `/go/` 跳转。
