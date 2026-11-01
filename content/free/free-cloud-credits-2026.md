---
title: "免费服务器与新用户赠金汇总 2026：甲骨文、谷歌云、AWS、Azure、Vultr"
date: 2026-11-01T13:40:00+08:00
lastmod: 2026-11-01T13:40:00+08:00
draft: true
description: "2026 免费云服务器与新用户赠金汇总：Oracle Always Free、Google Cloud e2-micro 与 $300 试用金、AWS 新版 Free Plan（最多 $200 赠金、6 个月）、Azure 免费账户 $200 与 12 个月 B1s，以及 Vultr VULTRMATCH，每条标注官方来源与核实日期。"
keywords: ["免费服务器", "免费云服务器 2026", "新用户赠金", "AWS Free Tier 2026", "谷歌云免费", "Azure 免费账户", "甲骨文免费"]
tags: ["免费服务器", "赠金"]
merchants: ["vultr"]
---

> 以下信息都来自各家**官方页面**，核实日期 2026-11-01（北京时间）。活动规则经常变，以官网为准。用途建议：建站练手、学习 Linux、跑小工具、搭测试环境。

## 一表看懂

来源均核实于 2026-11-01（北京时间）。

| 厂商 | 类型 | 免费内容（官方口径） | 期限 | 来源 |
|---|---|---|---|---|
| **甲骨文 Oracle Cloud** | 长期免费 + 试用金 | Always Free：A1 相当于 2 OCPU + 12 GB、2 台 AMD Micro、200 GB 块存储、每月 10 TB 出站；另有 US$300 试用金 | Always Free 长期；试用金 30 天 | [官方文档](https://docs.oracle.com/en-us/iaas/Content/FreeTier/freetier_topic-Always_Free_Resources.htm)、[FAQ](https://www.oracle.com/cloud/free/faq/) |
| **Google Cloud** | 长期免费额度 + 试用金 | 每月 1 台 e2-micro（仅 us-west1 / us-central1 / us-east1）、30 GB 标准持久化磁盘（standard persistent disk）、每月 1 GB 北美出站流量（不含到中国、澳大利亚）；新用户 $300 赠金 | 免费额度长期；赠金 90 天 | [官方文档](https://cloud.google.com/free/docs/free-cloud-features) |
| **AWS** | 新版 Free Plan（赠金制） | 新用户注册即得 $100，探索指定服务最多再得 $100，合计最多 $200；Free plan 账户 6 个月后或赠金用完自动关闭，不升级不扣费；另有 30+ 项服务长期免费额度 | 6 个月 | [aws.amazon.com/free](https://aws.amazon.com/free/) |
| **Microsoft Azure** | 免费账户 | $200 赠金（30 天）；新用户 12 个月内每月各 750 小时 B1s、B2pts v2（Arm）、B2ats v2（AMD）虚拟机；65+ 项服务长期免费额度 | 赠金 30 天；VM 12 个月 | [免费服务](https://azure.microsoft.com/en-us/pricing/free-services)、[账户](https://azure.microsoft.com/en-us/pricing/purchase-options/azure-account) |
| **Vultr** | 新用户充值返赠 | 码 VULTRMATCH：新账户首次充值 1:1 返赠，最高 $100 | 以官方页面为准 | [vultr.com/coupons](https://www.vultr.com/coupons/) |
| DigitalOcean | 新用户赠金 | 待核实 | — | 待核实 |

## 各家要点

### 甲骨文 Oracle Cloud：长期免费额度里规格较高的一家

它的长期免费额度里包含 2 OCPU / 12 GB 的 Arm 机型。代价也很明显：主区域创建后不能改、热门区域经常 out of capacity、闲置实例可能被回收、只用 Always Free 时没有工单支持。完整申请步骤和常见失败见 👉 [甲骨文 Oracle Cloud Always Free 申请指南](/free/oracle-cloud-always-free-guide-2026/)。

### Google Cloud：e2-micro 够跑小工具

- 免费的 e2-micro **只限三个美国区域**，按时长计算（每月一台机的时长），不是按台数。
- 出站流量免费额度只有**每月 1 GB（北美出发，不含到中国和澳大利亚）**，超出部分按量计费。建站时要留意流量，有访客从国内访问会很快超出。
- $300 赠金 90 天内有效，适合短期把各种服务都试一遍。

### AWS：2025 年起改为赠金制 Free Plan

官方页面现在的说法是：新账户注册即得 **$100**，完成指定服务探索**最多再得 $100**；**Free plan 账户在开户 6 个月后或赠金用完时自动关闭**（以先到者为准），不转为付费计划不会扣费。另有 30+ 项服务按月长期免费。过去常见的「12 个月 t2.micro/t3.micro 750 小时」说法，新账户请以当前官方页面为准（旧规则是否仍适用于老账户**待核实**）。

### Azure：$200 赠金 + 12 个月小规格 VM

- 免费账户提供 **$200 赠金（30 天内使用）**。
- 新用户 12 个月内每月可用 750 小时 B1s、B2pts v2（Arm）、B2ats v2（AMD）。
- 官方注明：想继续享受 12 个月免费服务，需要在 30 天内转为即用即付（Pay as you go）。

### Vultr：不送机器，送充值返赠

Vultr 没有长期免费机，新用户用码 **VULTRMATCH**，首次充值享受 1:1 返赠，**最高 $100**（以官方页面为准）。适合想要按小时计费、随开随删的测试场景。

{{< dealbox slug="vultr" merchant="Vultr 新用户" price="首充 1:1 返赠，最高 $100" validity="长期（以官方页面为准）" limits="需新账户 · 码 VULTRMATCH" >}}

## 使用免费额度的几条底线

- **一人一号，信息真实。** 各家条款基本都禁止多账户和虚假信息，违规可能导致封号、资源被删除。
- **不要用虚拟卡或他人的卡绕过验证。** 甲骨文官方明确不接受虚拟卡、一次性卡和预付卡。
- **设好预算提醒。** 赠金用完或超出免费额度后，部分平台会开始按量计费（AWS 新版 Free plan 不升级不扣费，其他平台规则以官网为准）。
- **重要数据自己备份。** 免费资源都没有 SLA 保障。

## 免费额度不够用？看低价付费 VPS

免费机适合练手。要跑正式站点，低价付费 VPS 有工单支持，也能按线路挑选：

{{< dealbox slug="racknerd" merchant="RackNerd" price="黑五价格待公布" validity="以官网活动页为准" limits="美国机房为主 · 普通线路" >}}

{{< dealbox slug="raksmart" merchant="RakSmart 双11秒杀" price="$1.99/月起" validity="11/11–11/17、11/25–11/30（北京时间）" limits="限量 · HDD · 不可叠加优惠券" >}}

{{< dealbox slug="bandwagonhost" merchant="搬瓦工 CN2 GIA-E" price="$89.99/季起" validity="常规方案，长期有效" limits="价格以结算页为准" >}}

更多：[双11 VPS 优惠汇总](/deals/2026-double11-vps-deals/)
