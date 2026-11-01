# VPS 实测标准清单

每篇评测都按本清单执行，保证数据真实、可复现。**不得编造或修改任何测试数据。**

## 0. 记录基本信息

- `test_date`：测试开始日期（北京时间，YYYY-MM-DD），写入文章 front matter
- `machine_source`：`自购` / `商家赞助` / `其他（说明）`，写入 front matter 并在正文“测试时间与机器来源”说明
- 套餐名称、价格、付款周期、续费价、机房、线路、下单日期

## 1. 订单截图

- 结算页（含价格、续费价、周期）
- 账单/付款成功页
- 控制台产品详情页（打码：IP 后两段、账户邮箱、订单号）

## 2. 系统与性能

```bash
# YABS：CPU（Geekbench）、磁盘 fio、iperf3 网络
curl -sL yabs.sh | bash
# 仅跑 Geekbench 6（跳过 fio 与 iperf）
curl -sL yabs.sh | bash -s -- -i -f -6
```

- 保存完整终端输出到 `static/images/<slug>/yabs.txt`，并截图
- 记录 Geekbench 结果链接（browser.geekbench.com）

## 3. 磁盘与网络测速

- 磁盘：YABS 的 fio 结果（4k/64k/512k/1m）；可补充 `dd if=/dev/zero of=test bs=1M count=1024 oflag=direct`
- 网络：YABS iperf3 结果；国内三网测速可使用 Speedtest CLI 选择国内电信/联通/移动测速服务器（记录服务器名称与时间）

## 4. 三网延迟与回程路由（ITDOG）

1. 打开 https://www.itdog.cn/ping/ ，输入服务器 IP，执行“单次/持续 Ping”，截图全国地图与各省延迟、丢包表。
2. 打开 https://www.itdog.cn/tcping/ 对 SSH/80 端口做 TCPing（应对禁 ICMP 的情况）。
3. 回程路由：https://www.itdog.cn/traceroute/ 选择电信、联通、移动各一个测试点做路由追踪，截图完整跳数，标注骨干（如 CN2 GIA 59.43.x.x、9929 218.105.x.x、CMIN2 223.120.x.x）。
4. 建议分别在**白天**与**晚高峰（20:00–23:00 北京时间）**各测一次，注明时间。

## 5. IP 归属 / ASN / 是否原生

- https://bgp.tools/ 查询 IP：记录 ASN、前缀、注册国家、上游
- 对照 IP 注册地与机房所在地，判断是否原生 IP（广播 IP 需说明）
- 截图保存

## 6. 稳定性监控

- 使用 Uptime Kuma 或 UptimeRobot 对 IP/端口做 **至少 7 天** 在线监控（1–5 分钟间隔）
- 记录在线率、宕机次数与时长，截图
- 期间如提交工单，记录响应时间与处理结果（售后评价依据）

## 7. 截图命名与存放

- 目录：`static/images/<slug>/`（`<slug>` 与文章文件名一致）
- 命名：`<序号>-<类型>[-<说明>].png`，全部小写连字符，例如：
  - `01-order-checkout.png`、`02-order-invoice.png`
  - `10-yabs.png`、`11-geekbench.png`
  - `20-itdog-ping.png`、`21-itdog-tcping.png`
  - `30-route-ct.png`、`31-route-cu.png`、`32-route-cm.png`
  - `40-bgptools.png`、`50-uptime-7d.png`
- 文章中引用：`![YABS 结果](/images/<slug>/10-yabs.png)`
- 上传前压缩图片（建议 WebP 或压缩 PNG，单张 < 300KB），并打码敏感信息

## 8. 发布前检查

- [ ] front matter：merchant、routes、datacenter、price、test_date、machine_source 已填写
- [ ] 所有数据均有截图或原始输出佐证
- [ ] 购买按钮使用 `{{< go "slug" "立即购买" >}}`，slug 存在于 data/links.yaml
- [ ] 文中无违规用途措辞
- [ ] `draft: false`
