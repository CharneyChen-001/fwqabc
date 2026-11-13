# 上线前验收清单（P0–P2）

日期：2026-11-05。本清单只记录这次检查。站点没有合并，也没有部署。条款仍待站长审阅，不能当作合规认证。

## 检验方法

- `hugo --gc --minify` 生产构建，再核对 `public` 里的路径、sitemap、RSS 和邮箱链接。
- 对照 `data/links.yaml` 生成的 `static/_redirects` 与 `deploy/Caddyfile`，确认原有 `/go/` 目标没被改写。
- 抽查 `data/offers.json`：非美元标价不得写入 `monthly_usd`；小时价不得按周期月数折算。
- 本地 `hugo server` 打开中英文首页、联系、条款、比价筛选、两个工具，并做一次键盘切换和暗色切换。未访问真实商家结算页。

## 通过

- 中文旧入口仍在：`/`、`/deals/`、优惠文、`/free/`、`/cases/`、`/merchants/`（含 NameSilo）、`/routes/cn2-gia/`、`/routes/9929/`、`/routes/cmin2/`、`/about/`、`/disclosure/`。
- 新入口可打开：分类、知识库、`/servers/` 及香港/CN2 GIA/搬瓦工、搜索、两个工具、`/en/` 首页、英文关于/联系/条款/披露/比价/工具/知识库/线路说明。
- 草稿未输出：知识库三篇骨架、黑五骨架、`/guides/`、`/en/deals/`。
- 首页中英文都不含 `0001` 零日期。有日期的中文文章为 `2026年11月2日` 这类格式。
- `mailto:chuhaiABC@outlook.com` 出现在中英文联系、关于、条款。邮箱 TODO 已从这些页面去掉。
- 条款写明适用中华人民共和国法律中的中国大陆地区规定，不指定法院或仲裁地，运营主体仍写明未确认。内容范围说明不含色情、毒品、赌博、加密货币、涉政相关业务，并写明这不是全站审查结论。
- 中英文首页有 `hreflang` 与 `x-default`。`/sitemap.xml` 索引指向 `/zh-cn/sitemap.xml` 和 `/en/sitemap.xml`；中文子图再指向根上的 posts/servers/knowledge/pages。英文子图指向 `/en/sitemap-*.xml`。`/feed.xml` 与 `/index.xml` 都在，英文另有 `/en/feed.xml`。
- `/go/vultr` 仍到 `https://www.vultr.com/?ref=9932591`，搬瓦工 `/go/bandwagonhost` 仍带 `pid=88`。
- 3959 条报价里，小时价没有用 `period_divided`。两台 CloudCone 独服标价为 AUD，`monthly_usd` 现为 null，卡片写 `AUD 222.77` / `AUD 382.93`，不参与美元月价排序。
- Caddy 与 `static/_headers` 含 HSTS、nosniff、Referrer-Policy、`X-Frame-Options`、CSP。CSP 仍允许本站脚本和现有内联脚本。
- 工具：未选工作负载、非整数月访问量会提示；静态站 100001 次/月给出 1 vCPU / 2 GB。键盘在单选上按向下键可从 static 切到 cms。暗色下英文联系页背景为 `rgb(19, 23, 32)`。

## 未测试

- 没有把构建结果同步到线上，也没有用真实浏览器走完 Cloudflare 或 Caddy。
- 没有点开商家结算页核对当前价格，没有发测试邮件。
- 没有逐条打开约 4000 个套餐，也没有把每个筛选组合都点一遍。
- 没有启用 Umami，因此没有验证第三方统计域名下的 CSP。
- 没有做读屏全流程，只做了工具单选的键盘切换。

## 阻塞

没有必须先改代码才能继续审阅的阻塞项。下面两项要站长确认后才算能上线，不是代码故障：

- 服务条款仍标「待站长审阅」。运营主体、备案号、法院或仲裁地都没有填，也不应在未确认时填。
- 本清单不是法律意见，也不是全站合规认证。

## 已有内容与范围说明的关系

`content/deals/raksmart-2026-double11-black-friday.md` 的付款方式已按站长要求去掉比特币。结算页可用方式仍标待核实。

## 上线前仍要站长做的事

1. 通读 `/terms/` 与 `/en/terms/`。
2. 确认运营主体、备案信息是否要另页公布。
3. RakSmart 文中的比特币付款方式已删除，不必再确认是否保留。
4. 决定优惠长文和实测是否以后再做英文。
5. 在预发环境点一次 `/go/` 推广链接，确认联盟后台有点击。本仓库没有代替这一步。
