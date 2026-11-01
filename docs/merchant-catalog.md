# 商家目录与推广链接维护

当前可筛选总表：`docs/商家产品与推广链接总表.xlsx`。表内核验日期对应本次目录快照，更新数据后应重新导出表格。

## 数据与核验

- `data/bandwagonhost_catalog.json` 保存搬瓦工官方目录快照及准确的产品、机房、付款周期推广链接。
- `data/affiliate_programs.json` 保存公开推广编号、普通与活动入口及核实条件。不得放入密码、令牌、账户密钥。
- `data/vultr_catalog.json` 保存计算与裸金属套餐。按套餐接口与地区库存接口的并集确定地区；价格优先取地区覆盖值，不统一乘小时数换算月价。
- `data/vultr_services.json` 保存非计算服务的官方价格、单位、条件与来源。未知价格用 `null`，免费用真实的数字 `0`，两者不得混淆。
- 库存是查询时的快照。特殊免费资格、抢占模式和未确认地区单独标注，不计为保证可购。
- Vultr 推广入口不预选套餐、地区或付款周期。官方页面能访问不等于已验证计佣。

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

将导出数据交给电子表格生成器，生成四张工作表：产品与报价明细、商家与推广计划、活动与附加费用、核验与更新记录。保留完整 URL，可筛选、复制；价格与日期使用原生单元格类型。搬瓦工一行对应一个付款周期；Vultr 一行对应一个地区与部署方式，小时价和官方月价分别列出。

## 发布检查

执行 Hugo 构建并检查目录统计、地区差价、普通与活动链接、手机显示、键盘展开和无脚本可用性。确认分支名与提交信息后才能提交推送。先推 `dev`，验证后再合并 `main`。服务器使用已部署的 Caddy 配置路径，仓库生成的示例不能直接覆盖线上配置。
