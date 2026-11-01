#!/usr/bin/env python3
"""将网站目录导出为统一表格数据，供 Excel 生成器使用；不联网。"""
import argparse
import collections
import json
import pathlib
import re
import sys
import urllib.parse

ROOT = pathlib.Path(__file__).resolve().parents[1]


def read(name):
    return json.loads((ROOT / "data" / name).read_text(encoding="utf-8"))


def export():
    bwh = read("bandwagonhost_catalog.json")
    vultr = read("vultr_catalog.json")
    services = read("vultr_services.json")
    programs = read("affiliate_programs.json")["programs"]
    normal = next(x for x in programs if x["id"] == "vultr-standard")
    rows, checks = [], []
    periods = {p["id"]: p["label"] for p in bwh["periods"]}
    for series in bwh["series"]:
        for region in series["regions"]:
            for dc in region["datacenters"]:
                for plan in dc["plans"]:
                    spec = bwh["products"][str(plan["product_id"]) ]
                    for offer in plan["offers"]:
                        parsed = urllib.parse.urlparse(offer["url"])
                        params = urllib.parse.parse_qs(parsed.query)
                        assert params["aff"] == [bwh["affiliate_id"]]
                        assert params["pid"] == [str(plan["product_id"])]
                        assert params["billingcycle"] == [offer["period"]]
                        assert any(re.fullmatch(r"configoption\[\d+\]", key) and value for key, value in params.items()), "机房参数缺失"
                        cart = urllib.parse.urlunparse(parsed._replace(path="/cart.php", query=urllib.parse.urlencode([(k,v) for k,values in params.items() if k != "aff" for v in values])))
                        price = offer["amount_cents"] / 100
                        rows.append({"record_id": f"bwh:{series['id']}:{dc['id']}:{plan['product_id']}:{offer['period']}",
                                     "merchant":"搬瓦工", "category":"VPS", "series":series["label"], "product_id":str(plan["product_id"]), "name":spec["name"],
                                     "country":region["label"], "city":dc["city"], "region_id":region["id"], "datacenter":dc["id"],
                                     "vcpu_count":spec["vcpu_count"], "ram_mb":spec["ram_mb"], "disk_gb":spec["storage_gb"], "disk_count":1,
                                     "bandwidth_gb":spec["transfer_gb_per_month"], "gpu_type":"", "gpu_count":None, "gpu_vram_gb":None,
                                     "currency":"USD", "billing_mode":"固定周期", "period":periods[offer["period"]], "period_price":price,
                                     "price_hourly":None, "price_monthly":price if offer["period"] == "monthly" else None, "unit_price":None, "unit":periods[offer["period"]],
                                     "official_url":bwh["source_url"], "purchase_url":cart, "affiliate_url":offer["url"], "program":"普通推广", "link_scope":"产品、机房、付款周期预选",
                                     "availability":"可订购" if offer["available"] else "暂缺货", "checked_on":bwh["checked_on"], "source_url":bwh["source_url"],
                                     "notes": "官方内存原值异常，待核实；未自动修正。" if spec["ram_mb"] % 1024 else "价格为整个付款周期总价。"})
    assert len(rows) == bwh["offer_count"]

    def add_vultr(plan, region):
        rows.append({"record_id":"vultr:" + plan["offer_key"], "merchant":"Vultr", "category":"裸金属" if plan["series_id"] == "metal" else "GPU" if plan["series_id"] in ("vcg","vdm") else "云服务器",
                     "series":plan["series_label"], "product_id":plan["id"], "name":plan["name"], "country":region.get("country_label", "待确认"), "city":region.get("city", "待确认"),
                     "region_id":region.get("id", ""), "datacenter":region.get("id", ""),
                     **{k:plan.get(k) for k in ("vcpu_count","ram_mb","disk_gb","disk_count","bandwidth_gb","gpu_type","gpu_count","gpu_vram_gb")},
                     "currency":"USD", "billing_mode":plan["deployment_type"], "period":"小时计费，官方月价另列", "period_price":None,
                     "price_hourly":plan["price_hourly"], "price_monthly":plan["price_monthly"], "unit_price":None, "unit":"实例",
                     "official_url":plan["official_url"], "purchase_url":"", "affiliate_url":plan["affiliate_url"], "program":"普通推广", "link_scope":normal["link_scope"],
                     "availability":plan["availability"], "checked_on":vultr["checked_on"], "source_url":plan["source_url"],
                     "notes": " ".join(filter(None, [plan["price_source"], "官方计费类型：" + plan["invoice_type"], "CPU口径：" + plan.get("cpu_kind", "vCPU"), plan["notes"], "库存来源：" + region.get("source_url", "未确认地区")]))})
    for series in vultr["series"]:
        for region in series["regions"]:
            for plan in region["plans"]:
                add_vultr(plan, region)
    for plan in vultr["unlisted_plans"]:
        add_vultr(plan, {})
    assert len(rows) - bwh["offer_count"] == vultr["offer_count"]
    for service in services["services"]:
        rows.append({"record_id":"vultr-service:" + service["id"], "merchant":"Vultr", "category":service["category"], "series":service["category"], "product_id":service["id"], "name":service["name"],
                     "country":"按官方支持范围", "city":"", "region_id":"", "datacenter":"", "currency":service.get("currency", "USD"),
                     "billing_mode":service["pricing_model"], "period":"按服务计费", "period_price":None,
                     "price_hourly":service.get("price_hourly"), "price_monthly":service.get("price_monthly"), "unit_price":service.get("unit_price"), "unit":service.get("unit", ""),
                     "official_url":service["official_url"], "purchase_url":"", "affiliate_url":normal["url"], "program":"普通推广", "link_scope":normal["link_scope"],
                     "availability":service["status"], "checked_on":services["checked_on"], "source_url":"\n".join(service["source_urls"]),
                     "notes":" ".join(filter(None, [service["description"], service["price_note"], service["region_note"], service.get("note", "")]))})
    assert len({r["record_id"] for r in rows}) == len(rows), "重复记录编号"
    campaign = next(p for p in programs if p["id"] == "vultr-credit")
    promotions = [{"merchant":"Vultr", "name":campaign["name"], "category":"推广活动", "billing_mode":"测试赠金", "price_monthly":None, "price_hourly":None, "unit_price":None, "unit":"额度，非现金", "credit_usd":300, "credit_days":30, "conditions":campaign["conditions"], "status":campaign["status"], "affiliate_url":campaign["url"], "source_url":campaign["source_url"], "checked_on":campaign["checked_on"], "notes":"活动截止日期未公布；不可把普通推广链接替换成活动链接后仍沿用旧条件。"}]
    for s in services["services"]:
        if s["category"] in ("附加费用", "附加服务"):
            promotions.append({"merchant":"Vultr", "name":s["name"], "category":s["category"], "billing_mode":s["pricing_model"], "price_monthly":s.get("price_monthly"), "price_hourly":s.get("price_hourly"), "unit_price":s.get("unit_price"), "unit":s.get("unit", ""), "conditions":s["price_note"], "status":s["status"], "affiliate_url":normal["url"], "source_url":"\n".join(s["source_urls"]), "checked_on":services["checked_on"], "notes":s.get("note", "")})
    checks.extend([
        {"merchant":"搬瓦工", "item":"已有购买组合", "status":"通过", "detail":f"{bwh['product_count']}款产品、{bwh['datacenter_count']}个机房、{bwh['offer_count']}条周期组合；保留完整原始推广链接。", "source_url":bwh["source_url"], "checked_on":bwh["checked_on"]},
        {"merchant":"搬瓦工", "item":"内存字段", "status":"待核实", "detail":"产品92、165–169的官方内存MB值非整GiB，保留原值并标注，不擅自纠正。", "source_url":bwh["source_url"], "checked_on":bwh["checked_on"]},
        {"merchant":"Vultr", "item":"套餐与地区覆盖", "status":"已采集", "detail":f"{vultr['plan_count']}条套餐记录，{vultr['region_count']}个地区代码（{vultr['verified_region_count']}个已列地区、{vultr['unconfirmed_region_count']}个信息待核实），{vultr['offer_count']}条地区与部署方式组合；并非均可购。", "source_url":"\n".join(vultr["source_urls"]), "checked_on":vultr["checked_on"]},
        {"merchant":"Vultr", "item":"小时价与月价", "status":"保留官方原值", "detail":"不以672或730小时统一换算。地区差价优先，GPU月度计费文档有口径差异，以控制台实际结算规则为准。", "source_url":"https://docs.vultr.com/support/platform/billing/how-are-gpu-products-billed-differently", "checked_on":vultr["checked_on"]},
        {"merchant":"Vultr", "item":"产品推广深链", "status":"未确认支持", "detail":"已确认的是普通/活动注册入口，不编造套餐、地区、周期预选参数；未实施计佣交易测试。", "source_url":normal["source_url"], "checked_on":normal["checked_on"]},
        {"merchant":"Vultr", "item":"旧VULTRMATCH文案", "status":"未沿用", "detail":"本次使用账户后台确认的300美元限时赠金；旧首充返赠活动未作为当前推广依据。", "source_url":campaign["source_url"], "checked_on":campaign["checked_on"]},
    ])
    for rid, error in vultr["availability_errors"].items():
        checks.append({"merchant":"Vultr", "item":"地区库存：" + rid, "status":"待核实", "detail":"本次接口查询失败："+error, "source_url":f"https://api.vultr.com/v2/regions/{rid}/availability", "checked_on":vultr["checked_on"]})
    for service in services["services"]:
        if service["status"] != "已核实":
            checks.append({"merchant":"Vultr", "item":service["name"], "status":service["status"], "detail":service["price_note"], "source_url":"\n".join(service["source_urls"]), "checked_on":services["checked_on"]})
    return {"checked_on":vultr["checked_on"], "products":rows, "programs":programs, "promotions":promotions, "checks":checks,
            "counts":{"bandwagonhost_offers":bwh["offer_count"], "vultr_offers":vultr["offer_count"], "vultr_services":len(services["services"]), "total_rows":len(rows)}}


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=pathlib.Path, required=True)
    args = parser.parse_args()
    result = export()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result["counts"], ensure_ascii=False))
