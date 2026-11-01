# 商家目录与推广链接维护

本地可筛选总表：`docs/商家产品与推广链接总表.xlsx`。表格只在本地维护，不纳入 Git 跟踪或推送。表内核验日期对应本次目录快照，更新数据后应重新导出表格。

## 数据与核验

- `data/bandwagonhost_catalog.json` 保存搬瓦工官方目录快照及准确的产品、机房、付款周期推广链接。
- `data/affiliate_programs.json` 保存公开推广编号、普通与活动入口及核实条件。不得放入密码、令牌、账户密钥。
- `data/vultr_catalog.json` 保存计算与裸金属套餐。按套餐接口与地区库存接口的并集确定地区；价格优先取地区覆盖值，不统一乘小时数换算月价。
- `data/vultr_services.json` 保存非计算服务的官方价格、单位、条件与来源。未知价格用 `null`，免费用真实的数字 `0`，两者不得混淆。
- `data/racknerd_catalog.json` 保存官方推广门户当前推荐的 11 款产品及 16 条付款周期报价。5 款 VPS 的地区与年付、两年付已核实，6 款共享/分销主机仅核实后台年价，不补猜测地区或流量周期。
- 库存是查询时的快照。特殊免费资格、抢占模式和未确认地区单独标注，不计为保证可购。
- Vultr 推广入口不预选套餐、地区或付款周期。官方页面能访问不等于已验证计佣。
- RackNerd 推广链接只预选产品。地区、系统和付款周期需在配置页选择，不能将四个地区展开成已预选机房的不同购买链接。共享/分销流量周期未注明，导出时月流量栏留空，原始流量写入备注。

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

RackNerd 后台推荐列表中仍有历史活动路径，不以当前核验年份改写活动年份。包含 RackNerd 的优惠码、返现等引流页面还需核对官方联盟条款，不能仅填写推广编号后直接发布。

## 发布检查

执行 Hugo 构建并检查目录统计、地区差价、普通与活动链接、手机显示、键盘展开和无脚本可用性。确认分支名与提交信息后才能提交推送。先推 `dev`，验证后再合并 `main`。服务器使用已部署的 Caddy 配置路径，仓库生成的示例不能直接覆盖线上配置。

提交前同时检查表格不在 Git 跟踪列表中，且 `.gitignore` 覆盖本地表格；不能仅依赖手工不执行 `git add`。
