# 商家目录与推广链接维护

本地可筛选总表：`docs/商家产品与推广链接总表.xlsx`。表格只在本地维护，不纳入 Git 跟踪或推送。表内核验日期对应本次目录快照，更新数据后应重新导出表格。

## 数据与核验

- `data/bandwagonhost_catalog.json` 保存搬瓦工官方目录快照及准确的产品、机房、付款周期推广链接。
- `data/affiliate_programs.json` 保存公开推广编号、普通与活动入口及核实条件。不得放入密码、令牌、账户密钥。
- `data/vultr_catalog.json` 保存计算与裸金属套餐。按套餐接口与地区库存接口的并集确定地区；价格优先取地区覆盖值，不统一乘小时数换算月价。
- `data/vultr_services.json` 保存非计算服务的官方价格、单位、条件与来源。未知价格用 `null`，免费用真实的数字 `0`，两者不得混淆。
- `data/racknerd_catalog.json` 保存官方推广门户当前推荐的 11 款产品及 16 条付款周期报价。5 款 VPS 的地区与年付、两年付已核实，6 款共享/分销主机仅核实后台年价，不补猜测地区或流量周期。
- `data/raksmart_catalog.json` 与 `data/cloudcone_catalog.json` 保存已核实范围内的产品、服务入口及报价，不代表两家全站全部 SKU。物理服务器型号、未确定账期和未知库存保留原始说明，不补猜测值。
- `data/ethernetservers_catalog.json` 与 `data/interserver_catalog.json` 保存共享主机、VPS、存储、独服等官方目录快照。地区组表示官网列出的系列可选范围，不生成未经核实的机房与产品组合，也不承诺实时库存。
- Ethernet Servers 域名不参与推广，注册与续费报价分列，推广字段留空。InterServer 基础、VPS分类、网站主机分类入口均来自后台；不拼接未经验证的套餐或周期参数。
- InterServer 的首期优惠与同周期续费分别保存为 `amount_cents` 和 `renewal_amount_cents`；列表并列显示，导出时续费为独立数值列 `renewal_period_price`，不能把首期价当长期续费价。
- 库存是查询时的快照。特殊免费资格、抢占模式和未确认地区单独标注，不计为保证可购。
- Vultr 推广入口不预选套餐、地区或付款周期。官方页面能访问不等于已验证计佣。
- RackNerd 推广链接只预选产品。地区、系统和付款周期需在配置页选择，不能将四个地区展开成已预选机房的不同购买链接。共享/分销流量周期未注明，导出时月流量栏留空，原始流量写入备注。
- RakSmart 明细默认使用周期性推广入口，一次性入口另列在推广计划表；两种模式不可混用。CloudCone 使用后台基础推广入口。两家都不把自行拼接参数的产品深链标为已核实，官方产品地址与推广入口分列。
- CloudCone SC2 保留官方小时价及月价；常规 SSD VPS 的年付总价不改写成月付。CDN 配额周期未确认时不计入月流量，备份比例不转换为固定美元金额。没有明确账期或需询价的服务，周期价格留空并在备注说明。

## 更新流程

在 `dev` 分支操作。公开接口不需要账户密钥：

```powershell
python -B scripts/refresh-vultr-catalog.py --save-snapshot "$env:TEMP/vultr-api-snapshot.json"
```

若有地区查询失败，可复用快照，仅重查失败地区：

```powershell
python -B scripts/refresh-vultr-catalog.py --snapshot "$env:TEMP/vultr-api-snapshot.json" --retry-availability --save-snapshot "$env:TEMP/vultr-api-snapshot.json"
```

数据库等不能通过匿名接口取得全部套餐的服务，应逐项核对官方页面；无法确认的价格保留待核实或联系销售，不补猜测值。活动截止未公布时不标“长期有效”，每次发布前复核活动。

更新推广计划后同步检查 `data/links.yaml`，再生成跳转配置：

```powershell
python -B scripts/gen-redirects.py
```

用同一批数据生成表格中间数据，避免手工抄写两份价格：

```powershell
python -B scripts/export-merchant-catalog.py --output "$env:TEMP/merchant-catalog.json"
```

将导出数据交给电子表格生成器，更新四张工作表：产品与报价明细、商家与推广计划、活动与附加费用、核验与更新记录。保留完整 URL，可筛选、复制；价格与日期使用原生单元格类型。搬瓦工一行对应一个付款周期；Vultr 一行对应一个地区与部署方式，小时价和官方月价分别列出；RackNerd 一行对应一个产品和已核实付款周期，同一产品的年付、两年付可使用相同推广链接。

RakSmart 与 CloudCone 每行对应一个产品或服务及已核实的报价方式，询价入口也保留一行并明确标注。推广计划表分别保存 RakSmart 的周期性、一次性推广规则及 CloudCone 的首充返佣条件；返佣不作为购买者优惠或赠金填写。更新表格时保留既有记录、筛选、格式与完整链接。

RackNerd 后台推荐列表中仍有历史活动路径，不以当前核验年份改写活动年份。包含 RackNerd 的优惠码、返现等引流页面还需核对官方联盟条款，不能仅填写推广编号后直接发布。

## 统一比价数据

`python3 scripts/build-offers.py` 读取现有目录快照，写出 `data/offers.json` 和 `static/offers.json`，并刷新 `content/servers/` 下的商家、地区、线路页。小时价不乘成月价；线路只在产品名或系列名写明时才填；NameSilo、域名、邮箱、CDN 和机柜托管不进入比价。购买按钮只有在链接和 `data/links.yaml` 现有目标完全一致时才走 `/go/`，否则使用目录里已经核实的推广地址。

## 发布检查

执行 Hugo 构建并检查目录统计、地区差价、普通与活动链接、手机显示、键盘展开和无脚本可用性。确认分支名与提交信息后才能提交推送。先推 `dev`，验证后再合并 `main`。服务器使用已部署的 Caddy 配置路径，仓库生成的示例不能直接覆盖线上配置。

提交前同时检查表格不在 Git 跟踪列表中，且 `.gitignore` 覆盖本地表格；不能仅依赖手工不执行 `git add`。
