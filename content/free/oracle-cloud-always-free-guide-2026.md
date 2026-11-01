---
title: "甲骨文 Oracle Cloud Always Free 申请指南 2026：注册、选区、开 A1 实例与常见失败"
date: 2026-11-01T13:30:00+08:00
lastmod: 2026-11-01T13:30:00+08:00
draft: false
faq:
  - q: "甲骨文 Always Free 需要信用卡吗？"
    a: "需要。官方不接受带 PIN 的借记卡、虚拟卡、一次性卡和预付卡，建议用本人实体信用卡，信息与账单一致。"
  - q: "开机提示 Out of capacity 怎么办？"
    a: "这是主区域临时缺少 Always Free 机型，可以换可用域或隔段时间再试；急用就直接买低价 VPS。"
  - q: "免费实例会被回收吗？"
    a: "官方说明：连续 7 天内 CPU 第 95 百分位、网络、内存（仅 A1）使用率都低于 20% 的实例可能被回收。"
  - q: "升级为 Pay As You Go 后还免费吗？"
    a: "官方说明升级后 Always Free 资源仍然免费，只对超出部分计费，且升级后不能降级。建议先设预算提醒。"
description: "2026 甲骨文 Oracle Cloud 免费服务器申请指南：Always Free 资源（Ampere A1 2 OCPU/12GB、2 台 AMD Micro、200GB 块存储、每月 10TB 出站流量）、主区域不可更改、闲置回收规则、信用卡验证、out of capacity 应对，全部引用官方文档。"
keywords: ["甲骨文免费服务器", "Oracle Cloud Always Free", "甲骨文云申请", "Ampere A1", "免费VPS", "甲骨文注册"]
tags: ["免费服务器", "甲骨文", "Oracle Cloud"]
merchants: ["raksmart", "bandwagonhost", "racknerd", "vultr"]
---

> **说明：** 本文的注册和控制台步骤是**根据 Oracle 官方文档与公开页面整理**的，本文作者没有在本文中实际注册或开机测试。资源额度和规则核实于 2026-11-01（北京时间），以官方最新页面为准。标为「经验分享{{< tbc >}}」的内容来自论坛和第三方，未经官方确认。

## 先说结论：适合谁、不适合谁

**适合：**
- 想学 Linux、Docker、Nginx，或者搭测试环境、跑小工具的新手。
- 手上有一张**本人的实体信用卡**（或可当信用卡用的借记卡），能接受「可能开不出机、可能被回收」。

**不适合：**
- 要跑客户网站、外贸独立站等**正式业务**。官方明确说 Free Tier **不含 SLA**，只用 Always Free 资源的账户**不能提交 Oracle 工单**（[官方 FAQ](https://www.oracle.com/cloud/free/faq/)）。
- 没有可用的实体卡。官方**不接受带 PIN 的借记卡、虚拟卡、一次性卡和预付卡**（同上）。
- 需要稳定的国内访问线路。免费机的线路和延迟本站**待实测**。

{{< shot src="/img/free/free-server-decision.svg" alt="免费机还是低价付费机的选择决策图" cap="原创示意图：免费机还是低价付费机" w="960" h="420" >}}

## Always Free 到底送什么（官方口径）

以下内容来自官方文档《[Always Free Resources](https://docs.oracle.com/en-us/iaas/Content/FreeTier/freetier_topic-Always_Free_Resources.htm)》，核实日期 2026-11-01：

| 资源 | 官方额度 | 备注 |
|---|---|---|
| Ampere A1（Arm） | 每月前 1,500 OCPU 小时 + 9,000 GB 小时，官方注明对 Always Free 租户**相当于 2 OCPU + 12 GB 内存** | 可以开 1 台（2 OCPU），或 2 台各 1 OCPU |
| AMD Micro | 最多 2 台 VM.Standard.E2.1.Micro | 每台 1/8 OCPU、1 GB 内存、外网带宽最高 50 Mbps |
| 块存储 | 合计 200 GB（启动盘 + 数据盘）+ 5 个卷备份 | 启动盘最小约 47–50 GB，计入 200 GB |
| 对象存储 | 20 GB | 另含每月 50,000 次 API 请求 |
| 出站流量 | **每月 10 TB** | — |
| 负载均衡 | 1 个 10 Mbps 弹性负载均衡 + 1 个网络负载均衡 | — |
| 数据库 | 2 个 Autonomous AI Database，另有 MySQL HeatWave、NoSQL | 是否可用取决于主区域 |

> 官方原文：“first 1,500 OCPU hours and 9,000 GB hours per month… For Always Free tenancies, this is equivalent to 2 OCPUs and 12 GB of memory.”

{{< shot src="/img/free/oracle/oracle-always-free-docs.webp" alt="Oracle 官方 Always Free Resources 文档页面截图" w="960" h="600" >}}

还有几条要注意：
- **必须开在主区域。** Always Free 计算实例和块存储都只能建在租户的主区域（home region），建在别的区域按正常价格计费（同上）。
- **25 端口默认封禁。** 默认不允许通过 TCP 25 端口向外发邮件，需要提交限额申请（同上）。
- **另有 30 天试用金。** 注册后还有 **US$300 试用金，30 天有效**，用完或到期以先到者为准（[官方 FAQ](https://www.oracle.com/cloud/free/faq/)）。试用期用试用金开的付费资源，到期后会被回收；Always Free 资源不受影响。

## 准备清单

1. **一张本人的实体信用卡**，或能当信用卡用的借记卡。Oracle 会做临时「预授权」验证，官方说明这类冻结**通常 3–5 天内由银行解除，不会实际扣款**（[官方 FAQ](https://www.oracle.com/cloud/free/faq/)）。
2. **真实的姓名、地址、手机号和邮箱**。官方要求联系和账单信息**准确、有效**，**每人只允许一个免费账户**，禁止创建或尝试创建多个账户（同上）。
3. **想好主区域**（见下文），这个选择**创建后不能改**。
4. 一台能用 SSH 的电脑，提前生成 SSH 密钥。

{{< shot src="/img/free/oracle-signup-flow.svg" alt="甲骨文 Oracle Cloud 注册流程示意图" cap="原创示意图：注册流程（依据官方文档整理）" w="960" h="240" >}}

## 注册步骤（依据官方页面整理）

{{< shot src="/img/free/oracle/oracle-free-tier-page.webp" alt="Oracle Cloud Free Tier 官方页面截图" w="960" h="600" >}}

1. 打开官方免费页 {{< extlink "https://www.oracle.com/cloud/free/" "oracle.com/cloud/free" >}}，点击「Start for free」。
2. 在注册页选择**账单国家/地区**，填写姓名和邮箱，完成邮箱验证。

{{< shot src="/img/free/oracle/oracle-signup-page.webp" alt="Oracle Cloud Free Tier 注册页 Account Information 截图" w="960" h="600" >}}

3. 设置密码和云账户名（Cloud Account Name，也就是租户名，之后登录要用）。
4. 选择**主区域（Home Region）**。务必慎重，见下一节。
5. 填写地址和手机号，信息要和卡片账单信息一致、真实。
6. 添加信用卡完成验证，等待账户开通。官方 FAQ 提到，账户在所有服务和区域完成注册**可能需要几分钟**。

## 怎么选主区域

官方文档写得很清楚：主区域保存账户信息和身份资源，**租户创建后不能更改**（[Managing Regions](https://docs.oracle.com/en-us/iaas/Content/Identity/regions/managingregions.htm)）。Always Free 计算实例也**只能建在主区域**，所以选区等于选你免费机的机房。

- **按访客位置选。** 访客在海外（外贸站、海外用户），选靠近目标市场的区域；访客在国内，选离中国大陆较近的亚太区域。各区域到国内的线路本站**待实测**，不在这里下结论。
- **热门区域经常「Out of capacity」。** 官方 FAQ 承认，「out of host capacity」表示主区域暂时缺少 Always Free 机型，**补充容量可能需要几天**。经验分享{{< tbc >}}：论坛普遍反映东京、首尔、新加坡等亚太热门区域更难开出 A1。
- **多可用域更灵活。** 主区域有多个可用域（AD）时，开不出机可以换一个 AD 再试（官方建议）。
- 想用免费 Autonomous Database，先确认主区域是否支持（官方说明部分区域不支持）。

## 创建 A1 实例（依据官方教程整理）

官方教程：[Tutorial - Launching Your First Linux Instance](https://docs.oracle.com/en-us/iaas/Content/GSG/Reference/overviewworkflow.htm)。大致流程如下：

1. 控制台菜单 → **Compute → Instances → Create instance**。
2. **Image**：选标有「Always Free-eligible」的镜像，比如 Oracle Linux 或 Ubuntu。
3. **Shape**：选 **Ampere → VM.Standard.A1.Flex**，OCPU 和内存在 2 OCPU / 12 GB 的总额度内分配。只想要 1 台就直接 2 OCPU + 12 GB。
4. **Networking**：没有现成 VCN 就让向导新建一个，放在公有子网，勾选分配公网 IPv4。
5. **SSH keys**：上传你的公钥，或下载控制台生成的私钥并妥善保存。
6. **Boot volume**：默认约 50 GB，计入 200 GB 免费块存储。
7. 点击 Create，状态变成 Running 后用 `ssh ubuntu@公网IP`（Ubuntu 镜像）或 `ssh opc@公网IP`（Oracle Linux 镜像）登录。

> 如果报「Out of host capacity」：按官方建议换个可用域，或者过一段时间再试。经验分享{{< tbc >}}：有人用脚本反复调用 API 抢机，这可能触发频率限制，也可能违反服务条款，本站**不推荐**。

## 安全列表与防火墙：网站打不开先查这两层

Oracle 的流量要过**两层**：
1. **VCN 安全列表（Security List）或网络安全组（NSG）**：在 Networking → Virtual Cloud Networks → 子网 → Security List 里添加入站规则，比如 TCP 80、443（[官方文档：Security Lists](https://docs.oracle.com/en-us/iaas/Content/Network/Concepts/securitylists.htm)）。**只放行你需要的端口**，SSH 22 端口最好限制来源 IP。
2. **系统内防火墙**：Oracle 官方镜像默认启用了系统防火墙。Oracle Linux 用 `firewall-cmd`，Ubuntu 镜像需要检查 iptables 规则。经验分享{{< tbc >}}：不少用户反映安全列表放行了，网页还是打不开，原因就是镜像自带的 iptables 规则。

示例（Oracle Linux，放行 80/443）：

```bash
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

## 常见失败与坦诚建议

| 问题 | 官方说法 / 常见原因 | 建议 |
|---|---|---|
| **信用卡被拒** | 官方不接受带 PIN 的借记卡、虚拟卡、一次性卡、预付卡 | 换一张本人实体信用卡，**确保信息与卡片账单一致**；不要用虚拟卡或他人信息去绕过验证 |
| **开不出机（Out of capacity）** | 主区域临时缺少 Always Free 机型，补充可能要几天 | 换可用域、隔段时间再试；急用就直接买低价 VPS |
| **账户被暂停/终止** | 官方 FAQ：多账户、信息不真实、违反服务协议都可能被暂停或终止；**闲置 30 天以上**的账户可能被视为弃用 | 一人一号，信息真实，正常使用；重要数据**自己备份** |
| **实例被回收** | 官方：连续 7 天内 CPU 第 95 百分位使用率 < 20%、网络使用率 < 20%、内存使用率 < 20%（仅 A1）的实例**可能被回收** | 不要开了不用；认真跑项目，或者干脆删掉 |
| **试用期后机器没了** | 试用金开的付费资源到期回收；A1 总量超出免费额度会被禁用，30 天后删除 | 试用期结束前把 A1 总量控制在 2 OCPU / 12 GB 以内 |

{{< cta slug="raksmart" text="开不出机、怕被回收？低价付费款更省心：RakSmart 双11 秒杀 $1.99/月起" >}}

关于**升级为 Pay As You Go**：官方说明升级后 **Always Free 资源仍然免费**，只对超出部分计费，而且**升级后不能降级**（[官方 FAQ](https://www.oracle.com/cloud/free/faq/)）。经验分享{{< tbc >}}：有用户认为升级后开机更容易、账户也更不容易被清理，官方没有这样承诺。升级前务必设好预算提醒，避免误开付费资源。

## 常见问题

{{< faq >}}

## 免费不等于稳定

- **没有 SLA，也没有官方工单**（只用 Always Free 时），出问题只能靠社区论坛。
- **可能被回收或停用**：闲置回收和账户审核规则都写在官方文档里。
- **线路不保证**：到国内的延迟和晚高峰表现本站**待实测**。

所以我们的建议是：**拿甲骨文练手、做测试很划算；正式站点、客户业务，还是放在有工单支持、能按线路挑选的付费 VPS 上更省心。** 低价机一年的费用，往往比反复折腾免费机的时间成本低。

## 低价付费替代（含推广链接）

下面几家都是常见的入门选择，价格以官网为准，详细规则见对应文章。

{{< dealbox slug="racknerd" merchant="RackNerd" price="黑五价格待公布" validity="以官网活动页为准" limits="美国机房为主 · 普通线路" >}}

{{< dealbox slug="raksmart" merchant="RakSmart 双11秒杀" price="$1.99/月起" validity="11/11–11/17、11/25–11/30（北京时间）" limits="限量 · HDD · 不可叠加优惠券" when="2026-11-11T00:00:00+08:00/2026-11-17T23:59:59+08:00,2026-11-25T00:00:00+08:00/2026-11-30T23:59:59+08:00" >}}

{{< dealbox slug="bandwagonhost" merchant="搬瓦工 CN2 GIA-E" price="$89.99/季起" validity="常规方案，长期有效" limits="价格以结算页为准" >}}

{{< dealbox slug="vultr-credit" merchant="Vultr" price="新用户 $300 测试额度" validity="限时活动，截止日期未公布" limits="新账户 · 有效信用卡或 PayPal · 未用额度 30 天后过期" >}}

更多：[双11 VPS 优惠汇总](/deals/2026-double11-vps-deals/) · [免费/新用户赠金服务器汇总](/free/free-cloud-credits-2026/)

---

**参考来源**（核实于 2026-11-01）：
- Oracle 官方文档 · Always Free Resources：https://docs.oracle.com/en-us/iaas/Content/FreeTier/freetier_topic-Always_Free_Resources.htm
- Oracle Cloud Free Tier FAQ：https://www.oracle.com/cloud/free/faq/
- Oracle 官方文档 · Managing Regions：https://docs.oracle.com/en-us/iaas/Content/Identity/regions/managingregions.htm
