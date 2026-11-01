# 服务器ABC（fwqabc.com）

国外VPS优惠与真实实测。Hugo + PaperMod 主题（git submodule）。

## 本地预览

```bash
git clone --recurse-submodules https://github.com/smiter1024/fwqabc.git
cd fwqabc
hugo server -D        # 含草稿预览：http://localhost:1313
hugo --gc --minify    # 生产构建，输出到 public/
```

需要 Hugo extended（最新版）。

## 目录结构

```
archetypes/      文章模板：review / deals / merchant / guide
content/
  deals/         优惠促销   /deals/
  review/        实测评测   /review/
  routes/        线路专题   /routes/（CN2 GIA、9929、CMIN2）
  guides/        按用途选   /guides/
  merchants/     商家目录   /merchants/
  tools/         工具       /tools/
  tutorials/     教程       /tutorials/
  disclosure.md about.md contact.md privacy.md
data/links.yaml  推广链接 slug -> 目标地址
data/picks.yaml  首页精选对比表
layouts/         主题覆盖：首页、文章页（推广提示）、go 短代码、robots.txt
scripts/gen-redirects.py  生成 deploy/Caddyfile 与 static/_redirects
deploy/          Caddyfile 与部署说明
deploy/github-workflow-deploy.yml（启用时移到 .github/workflows/deploy.yml）  手动触发的部署工作流
```

分类法：`merchants`（商家）、`routes`（线路）、`datacenters`（机房）、`tags`。
URL 使用小写连字符 slug；限时活动文章 slug 带年份（如 `2026-double11-vps-deals`）。

## 新增评测

```bash
hugo new content review/racknerd-2026-black-friday-review.md
```

按模板填写 front matter：`merchant`、`routes`、`datacenter`、`price`、`test_date`、`machine_source`（自购/赞助）。
所有测试数据必须来自真实测试，写完把 `draft: true` 改为 `false`。

新增优惠：`hugo new content deals/xxx-2026-....md`（自动使用 deals 模板）。

## 新增推广链接

1. 在 `data/links.yaml` 增加一行：`slug: https://商家推广地址`
2. 运行 `python3 scripts/gen-redirects.py` 更新 `deploy/Caddyfile` 和 `static/_redirects`
3. 文章中使用：`{{</* go "slug" "立即购买" */>}}`，渲染为指向 `/go/slug/` 的按钮（`rel="sponsored nofollow noopener"`，新窗口打开）

`/go/` 已在 robots.txt 中禁止抓取。使用未知 slug 时构建会报错。

## 内容规范

- 不编造测试数据与价格，未核实写 TODO；时间统一用北京时间。
- 每篇文章底部自动显示“本文含推广链接”并链接 /disclosure/。
- 合规：不得出现任何违规用途相关措辞（见内部规范）。

## 统计

在 `hugo.toml` 设置 `params.umami`（脚本地址）与 `params.umamiWebsiteId` 即启用 Umami，默认关闭。

## 未来合并说明

内容未来可能迁移到 `chuhaiabc.com/server/`，届时通过 301 整站跳转（`/deals/x/` → `chuhaiabc.com/server/deals/x/`）。**请保持现有 URL 结构稳定**，不要随意改 slug。
