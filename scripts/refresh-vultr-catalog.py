#!/usr/bin/env python3
"""从 Vultr 公开接口更新目录；无需密钥。保留官方价格，不换算月价。"""
import argparse
import concurrent.futures
import datetime as dt
import json
import pathlib
import sys
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
API = "https://api.vultr.com/v2/"
SERIES = {
    "vc2": ("基础云服务器", "共享 CPU 基础计算套餐。"),
    "vhf": ("高频云服务器", "高频 CPU 计算套餐。"),
    "vhp": ("高性能云服务器", "按官方 CPU 厂商区分配置。"),
    "voc": ("优化云服务器", "通用、计算、内存及存储优化配置，按套餐编号区分。"),
    "vx1": ("VX1 云服务器", "保留官方小时价与月价，按实例实际计费规则结算。"),
    "vcg": ("云 GPU", "GPU 配置以接口明确提供的型号与显存为准。"),
    "vdm": ("GPU 计算 VDM", "包括不同 GPU 部署配置；规格缺项请在官方控制台核对。"),
    "metal": ("裸金属服务器", "物理 CPU 与磁盘配置；核心数不等同于虚拟 CPU。"),
}
COUNTRIES = {"US":"美国","CA":"加拿大","MX":"墨西哥","BR":"巴西","CL":"智利","GB":"英国","DE":"德国","FR":"法国","NL":"荷兰","ES":"西班牙","IT":"意大利","PL":"波兰","SE":"瑞典","JP":"日本","KR":"韩国","SG":"新加坡","IN":"印度","AU":"澳大利亚","ZA":"南非","IL":"以色列"}
CITIES = {"ams":"阿姆斯特丹","atl":"亚特兰大","blr":"班加罗尔","bom":"孟买","cdg":"巴黎","cmh":"哥伦布","del":"新德里","dfw":"达拉斯","ewr":"新泽西","fra":"法兰克福","hnl":"檀香山","icn":"首尔","itm":"大阪","jnb":"约翰内斯堡","lax":"洛杉矶","lhr":"伦敦","man":"曼彻斯特","mci":"堪萨斯城","mad":"马德里","mel":"墨尔本","mex":"墨西哥城","mia":"迈阿密","nrt":"东京","ord":"芝加哥","sao":"圣保罗","scl":"圣地亚哥","sea":"西雅图","sgp":"新加坡","sjc":"硅谷","sto":"斯德哥尔摩","syd":"悉尼","tlv":"特拉维夫","waw":"华沙","yto":"多伦多"}


def fetch(url):
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme != "https" or parsed.netloc != "api.vultr.com":
        raise ValueError("拒绝非官方接口地址")
    req = urllib.request.Request(url, headers={"User-Agent": "fwqabc-catalog/1.0", "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=35) as response:
        return json.load(response)


def paged(path, key):
    endpoint = API + path
    url, values, seen = endpoint + "?per_page=500", [], set()
    while url:
        if url in seen:
            raise ValueError("分页出现循环")
        seen.add(url)
        result = fetch(url)
        values.extend(result[key])
        cursor = result.get("meta", {}).get("links", {}).get("next")
        url = endpoint + "?" + urllib.parse.urlencode({"per_page": 500, "cursor": cursor}) if cursor else None
    if len({x["id"] for x in values}) != len(values):
        raise ValueError("接口返回重复产品编号")
    return values


def collect():
    snapshot = {"checked_at": dt.datetime.now(dt.timezone.utc).isoformat(), "availability": {}, "availability_errors": {}}
    for key, path in [("plans", "plans"), ("plans_metal", "plans-metal"), ("regions", "regions")]:
        snapshot[key] = paged(path, key)
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        jobs = {pool.submit(fetch, API + "regions/" + rid + "/availability"): rid for rid in region_ids(snapshot)}
        for job in concurrent.futures.as_completed(jobs):
            rid = jobs[job]
            try:
                snapshot["availability"][rid] = job.result()
            except Exception as exc:
                snapshot["availability_errors"][rid] = type(exc).__name__
    return snapshot


def region_ids(snapshot):
    return {x["id"] for x in snapshot["regions"]} | {rid for plan in snapshot["plans"] + snapshot["plans_metal"] for rid in plan.get("locations", [])}


def build(snapshot, programs):
    regions = {x["id"]: x for x in snapshot["regions"]}
    normal = next(x["url"] for x in programs if x["id"] == "vultr-standard")
    campaign = next(x["url"] for x in programs if x["id"] == "vultr-credit")
    catalog = {"checked_on": snapshot["checked_at"][:10], "checked_at": snapshot["checked_at"], "currency": "USD", "affiliate_url": normal, "campaign_url": campaign,
               "source_urls": [API + "plans?per_page=500", API + "plans-metal?per_page=500", API + "regions?per_page=500"],
               "plan_count": len(snapshot["plans"]) + len(snapshot["plans_metal"]), "region_count": len(region_ids(snapshot)), "verified_region_count": len(regions),
               "unconfirmed_region_count": len(region_ids(snapshot) - regions.keys()), "unconfirmed_regions": sorted(region_ids(snapshot) - regions.keys()), "offer_count": 0,
               "availability_errors": snapshot.get("availability_errors", {}), "series": [], "unlisted_plans": []}
    groups = {}
    for raw, metal in [(x, False) for x in snapshot["plans"]] + [(x, True) for x in snapshot["plans_metal"]]:
        sid = "metal" if metal else raw["type"]
        title, desc = SERIES.get(sid, (sid, "官方新增系列，分类说明待核实。"))
        group = groups.setdefault(sid, {"id": sid, "label": title, "description": desc, "plan_count": 0, "regions": {}})
        group["plan_count"] += 1
        locations = set(raw.get("locations", []))
        for rid, available in snapshot["availability"].items():
            if raw["id"] in available.get("available_plans", []) or raw["id"] in available.get("available_vpc_only_plans", []):
                locations.add(rid)
        if not locations:
            locations = {"unconfirmed"}
        modes = []
        if raw.get("deploy_ondemand"):
            modes.append(("ondemand", "按需", ""))
        if raw.get("deploy_preemptible"):
            modes.append(("preemptible", "抢占", "_preemptible"))
        if not modes:
            modes = [("unknown", "部署方式待核实", "")]
        for rid in sorted(locations):
            region = regions.get(rid, {"id": rid, "city": "地区待确认", "country": "", "continent": ""})
            for mode, mode_label, suffix in modes:
                override = raw.get("location_cost", {}).get(rid, {})
                monthly_key, hourly_key = "monthly_cost" + suffix, "hourly_cost" + suffix
                notes = []
                if rid not in raw.get("locations", []) and rid != "unconfirmed":
                    notes.append("地区可用性来自库存接口。")
                if raw["id"].endswith("-v6"):
                    notes.append("仅 IPv6 套餐，购买前确认网络需求。")
                is_free = raw.get("monthly_cost") == 0 and raw.get("hourly_cost") == 0
                availability = "待核实"
                av = snapshot["availability"].get(rid)
                if rid == "unconfirmed":
                    availability = "未确认可用地区"
                elif av is not None:
                    availability = "可部署" if raw["id"] in av.get("available_plans", []) else "仅 VPC 可用" if raw["id"] in av.get("available_vpc_only_plans", []) else "暂缺货"
                if is_free:
                    availability = "免费资格待核实"
                    notes.append("特殊免费记录，不保证普通新账户可申请。")
                if mode == "preemptible":
                    notes.append("抢占实例可能被回收；库存接口未区分部署方式，须在控制台确认。")
                    if availability == "可部署":
                        availability = "抢占可用性待核实"
                if raw.get("gpu_brand") not in (None, "none") and not raw.get("gpu_type"):
                    notes.append("接口未完整列出 GPU 型号、数量或显存，需控制台核对。")
                if raw.get("invoice_type") == "hourly":
                    notes.append("官方月价仅供参考，实际按对应小时计费规则结算。")
                if mode == "unknown":
                    availability = "待核实"
                if rid != "unconfirmed" and rid not in regions:
                    availability = "地区信息待核实"
                    notes.append("套餐响应列有此地区代码，但官方地区列表未列出，国家、城市和购买范围待核实。")
                item = {"id": raw["id"], "offer_key": raw["id"] + ":" + rid + ":" + mode,
                        "name": raw["id"], "series_id": sid, "series_label": title,
                        "vcpu_count": raw.get("vcpu_count", raw.get("cpu_cores")), "cpu_kind": "物理核心" if metal else "vCPU",
                        "cpu_model": raw.get("cpu_model", raw.get("cpu_vendor", "")), "cpu_threads": raw.get("cpu_threads"),
                        "ram_mb": raw.get("ram"), "disk_gb": raw.get("disk"), "disk_count": raw.get("disk_count"),
                        "disk_type": raw.get("disk_type", raw.get("type")), "storage_type": raw.get("storage_type", ""),
                        "bandwidth_gb": raw.get("bandwidth"), "gpu_count": raw.get("gpu_count"), "gpu_type": raw.get("gpu_type", ""),
                        "gpu_vram_gb": raw.get("gpu_vram_gb"), "gpu_brand": raw.get("gpu_brand", "none"),
                        "price_monthly": override.get(monthly_key, raw.get(monthly_key)), "price_hourly": override.get(hourly_key, raw.get(hourly_key)),
                        "price_source": "地区专用价格" if monthly_key in override or hourly_key in override else "官方基础价格",
                        "invoice_type": raw.get("invoice_type", ""), "deployment_type": mode_label, "availability": availability,
                        "official_url": "https://www.vultr.com/pricing/", "affiliate_url": normal,
                        "source_url": API + ("plans-metal" if metal else "plans") + "?per_page=500", "notes": " ".join(notes)}
                if rid == "unconfirmed":
                    catalog["unlisted_plans"].append(item)
                else:
                    rg = group["regions"].setdefault(rid, {"id": rid, "city": ("米兰" if rid == "mxp" else CITIES.get(rid, region["city"])) if rid in regions else "城市待核实", "city_original": region["city"], "country": region["country"], "country_label": COUNTRIES.get(region["country"], region["country"]) if rid in regions else "国家待核实", "continent": region["continent"], "source_url": API + "regions/" + rid + "/availability", "plans": []})
                    rg["plans"].append(item)
                catalog["offer_count"] += 1
    for sid, group in groups.items():
        group["regions"] = sorted(group["regions"].values(), key=lambda r: (r["country"], r["id"]))
        catalog["series"].append(group)
    catalog["series"].sort(key=lambda g: list(SERIES).index(g["id"]) if g["id"] in SERIES else 99)
    return catalog


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", type=pathlib.Path, help="复用已保存的官方接口快照，不联网")
    parser.add_argument("--save-snapshot", type=pathlib.Path, help="将公开原始响应保存到指定路径")
    parser.add_argument("--retry-availability", action="store_true", help="仅重查快照中失败的地区库存")
    parser.add_argument("--output", type=pathlib.Path, default=ROOT / "data/vultr_catalog.json")
    args = parser.parse_args()
    snapshot = json.loads(args.snapshot.read_text(encoding="utf-8")) if args.snapshot else collect()
    if args.retry_availability:
        for rid in sorted(set(snapshot.get("availability_errors", {})) | (region_ids(snapshot) - snapshot["availability"].keys())):
            try:
                snapshot["availability"][rid] = fetch(API + "regions/" + rid + "/availability")
                snapshot["availability_errors"].pop(rid, None)
            except Exception as exc:
                snapshot["availability_errors"][rid] = type(exc).__name__
    if args.save_snapshot:
        args.save_snapshot.parent.mkdir(parents=True, exist_ok=True)
        args.save_snapshot.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    programs = json.loads((ROOT / "data/affiliate_programs.json").read_text(encoding="utf-8"))["programs"]
    catalog = build(snapshot, programs)
    args.output.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: catalog[k] for k in ("plan_count", "region_count", "offer_count", "availability_errors")}, ensure_ascii=False))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
