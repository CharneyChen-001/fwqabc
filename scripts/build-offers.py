#!/usr/bin/env python3
"""把各商家目录快照合并成统一套餐数据 data/offers.json。

原则（与 docs/merchant-catalog.md 一致）：
- 未知就是 null，不猜测地区、线路、库存、月价或优惠码。
- 小时价不乘小时数换算月价；只有目录里的官方月价，或已核实的固定周期总价按月数折算。
- NameSilo 是域名注册商，不进入比价。域名、邮箱、CDN、证书、机柜托管等非服务器条目也不进入。
- 购买链接只使用目录里已经写明的推广地址；能与 data/links.yaml 的现有 /go/ 目标精确对应时才填 aff_slug。

运行：python3 scripts/build-offers.py
"""
from __future__ import annotations

import json
import pathlib
import re
import urllib.parse

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

# 只映射目录里已经出现的国家/地区名称，不从机房代码推断。
COUNTRIES = {
    "美国": ("united-states", "美国"),
    "中国香港": ("hong-kong", "中国香港"),
    "香港": ("hong-kong", "中国香港"),
    "日本": ("japan", "日本"),
    "新加坡": ("singapore", "新加坡"),
    "荷兰": ("netherlands", "荷兰"),
    "德国": ("germany", "德国"),
    "英国": ("united-kingdom", "英国"),
    "澳大利亚": ("australia", "澳大利亚"),
    "加拿大": ("canada", "加拿大"),
    "韩国": ("south-korea", "韩国"),
    "法国": ("france", "法国"),
    "印度": ("india", "印度"),
    "波兰": ("poland", "波兰"),
    "阿联酋": ("united-arab-emirates", "阿联酋"),
    "新西兰": ("new-zealand", "新西兰"),
    "西班牙": ("spain", "西班牙"),
    "中国": ("china", "中国"),
    "墨西哥": ("mexico", "墨西哥"),
    "巴西": ("brazil", "巴西"),
    "南非": ("south-africa", "南非"),
    "以色列": ("israel", "以色列"),
    "瑞典": ("sweden", "瑞典"),
    "意大利": ("italy", "意大利"),
    "智利": ("chile", "智利"),
}

NOT_A_REGION = {
    "",
    "待核实",
    "待确认",
    "地区待核实",
    "国家待核实",
    "多个国家与地区",
    "按服务覆盖范围",
    "不适用",
}

MONTHS = {
    "monthly": 1,
    "quarterly": 3,
    "semiannually": 6,
    "annually": 12,
    "biennially": 24,
    "triennially": 36,
}

# 这些系列/类别不是服务器套餐。NameSilo 没有 catalog，这里再按 id 排除一次。
SKIP_SERIES = {
    "domain",
    "email",
    "cdn",
    "addons",
    "website",
    "network",
    "colocation",
}
SKIP_CATEGORY = {
    "域名",
    "CDN",
    "企业邮箱",
    "附加服务",
    "CDN 与安全",
    "网站服务",
    "网络服务",
    "机柜托管",
    "邮箱服务入口",
}

PROVIDERS = {
    "bandwagonhost": "搬瓦工",
    "vultr": "Vultr",
    "racknerd": "RackNerd",
    "raksmart": "RakSmart",
    "cloudcone": "CloudCone",
    "ethernetservers": "Ethernet Servers",
    "interserver": "InterServer",
}


def read_json(name):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def parse_links(text):
    """与 scripts/gen-redirects.py 相同的极简 YAML 解析，算出每个 slug 的跳转目标。"""
    data, cur = {}, None
    for raw in text.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        line = re.sub(r"\s+#.*$", "", raw.rstrip())
        if not raw.startswith(" "):
            cur = line.rstrip(":").strip()
            data[cur] = {}
        else:
            key, value = line.strip().split(":", 1)
            data[cur][key.strip()] = value.strip().strip("\"'")
    targets = {}
    for slug, item in data.items():
        landing, aff = item.get("landing", ""), item.get("aff", "")
        if not landing:
            continue
        if aff:
            template = item.get("aff_template") or landing
            target = template.format(
                aff=aff,
                landing=landing,
                landing_enc=urllib.parse.quote(landing, safe=""),
            )
        else:
            target = landing
        targets[slug] = target
    return targets


def canon_url(url):
    if not url:
        return ""
    parts = urllib.parse.urlsplit(url.strip())
    query = urllib.parse.parse_qsl(parts.query, keep_blank_values=True)
    query.sort()
    return urllib.parse.urlunsplit(
        (parts.scheme.lower(), parts.netloc.lower(), parts.path, urllib.parse.urlencode(query), "")
    )


def money(amount):
    if amount is None:
        return None
    value = float(amount)
    if value == 0:
        return "$0"
    # 小时价经常小于 0.1，保留到有意义的小数，避免显示成 $0.00。
    if abs(value) < 1:
        text = f"{value:.6f}".rstrip("0").rstrip(".")
        return f"${text}"
    if abs(value - round(value)) < 1e-9:
        return f"${int(round(value))}"
    return f"${value:.2f}"


def disk_label(disk_type, storage_type):
    for value in (disk_type, storage_type):
        if value and re.search(r"ssd|hdd|nvme|raid", str(value), re.I):
            return str(value)
    return None


def specs_text(cpu, ram_mb, disk_gb, disk_kind, traffic_gb, bandwidth_mbps):
    parts = []
    if isinstance(cpu, (int, float)):
        parts.append(f"{int(cpu) if float(cpu).is_integer() else cpu} 核")
    if isinstance(ram_mb, (int, float)):
        if int(ram_mb) % 1024 == 0:
            parts.append(f"{int(ram_mb) // 1024} GB 内存")
        else:
            parts.append(f"{int(ram_mb)} MB 内存")
    if isinstance(disk_gb, (int, float)):
        disk = f"{int(disk_gb) if float(disk_gb).is_integer() else disk_gb} GB"
        if disk_kind:
            disk += f" {disk_kind}"
        parts.append(disk)
    if isinstance(traffic_gb, (int, float)):
        traffic = int(traffic_gb) if float(traffic_gb).is_integer() else traffic_gb
        parts.append(f"{traffic} GB 流量")
    if isinstance(bandwidth_mbps, (int, float)):
        speed = int(bandwidth_mbps) if float(bandwidth_mbps).is_integer() else bandwidth_mbps
        parts.append(f"{speed} Mbps")
    return " / ".join(parts) or None


def detect_line(name, series_label):
    """只看产品名和系列名。备注里的“不能标为 CN2”不算线路。"""
    text = " ".join(part for part in (name, series_label) if part)
    if re.search(r"CN2\s*GIA|GIA\s*CN2", text, re.I):
        return "cn2-gia", "CN2 GIA"
    if re.search(r"CMIN2", text, re.I):
        return "cmin2", "CMIN2"
    if re.search(r"AS\s*9929|(?<!\d)9929(?!\d)", text, re.I):
        return "as9929", "AS9929"
    if re.search(r"\bCN2\b", text, re.I):
        return "cn2", "CN2"
    return None, None


def region_of(country):
    if country is None:
        return None, None
    label = str(country).strip()
    if not label or label in NOT_A_REGION or "待核实" in label or "待确认" in label:
        return None, None
    mapped = COUNTRIES.get(label)
    if not mapped:
        return label, None
    return mapped[1], mapped[0]


def split_city(city):
    """一个报价对应多个机房时，不把它们收成单一城市。"""
    if city is None:
        return None, None
    text = str(city).strip()
    if not text or text in NOT_A_REGION or "待核实" in text or "以配置页" in text or "无需选择" in text:
        return None, text or None
    if any(mark in text for mark in (" / ", "/", "、", "；", ";")):
        return None, text
    if text.count("·") >= 2:
        return None, text
    return text, None


def stock_of(value):
    """只有明确的可购/缺货才归一。未实测、待核实保持 null。"""
    if value is True:
        return "in", "可订购"
    if value is False:
        return "out", "暂缺货"
    if value in ("可部署", "可订购"):
        return "in", value
    if value in ("暂缺货", "缺货"):
        return "out", value
    if value in (None, ""):
        return None, None
    return None, str(value)


def pricing(period, period_label, amount_cents, price_hourly, price_monthly):
    """返回 price, monthly_usd, monthly_basis, price_text。不从小时价推月价。"""
    price = None
    if amount_cents is not None:
        price = amount_cents / 100
    elif period == "hourly" and price_hourly is not None:
        price = float(price_hourly)
    elif period == "monthly" and price_monthly is not None:
        price = float(price_monthly)

    monthly = None
    basis = None
    if price_monthly is not None and period == "hourly":
        monthly = float(price_monthly)
        basis = "official"
    elif period in MONTHS and amount_cents is not None:
        months = MONTHS[period]
        monthly = round(amount_cents / 100 / months, 4)
        basis = "official" if months == 1 else "period_divided"
    elif period == "monthly" and price_monthly is not None and amount_cents is None:
        monthly = float(price_monthly)
        basis = "official"
    return price, monthly, basis, money(price)


def blank_offer(**kwargs):
    offer = {
        "id": None,
        "provider": None,
        "provider_slug": None,
        "name": None,
        "kind": None,
        "region": None,
        "region_slug": None,
        "city": None,
        "datacenter": None,
        "line": None,
        "line_slug": None,
        "cpu": None,
        "ram_mb": None,
        "disk_gb": None,
        "disk_type": None,
        "traffic_gb": None,
        "bandwidth_mbps": None,
        "price": None,
        "price_text": None,
        "currency": "USD",
        "period": None,
        "period_label": None,
        "monthly_usd": None,
        "monthly_basis": None,
        "hourly_text": None,
        "stock": None,
        "stock_label": None,
        "promo_code": None,
        "checked_on": None,
        "aff_slug": None,
        "buy_url": None,
        "buy_rel": None,
        "specs": None,
        "location_note": None,
        "notes": None,
    }
    offer.update(kwargs)
    return offer


class Builder:
    def __init__(self):
        self.offers = []
        self.excluded = []
        self.link_targets = {
            slug: canon_url(url)
            for slug, url in parse_links((DATA / "links.yaml").read_text(encoding="utf-8")).items()
        }
        self.by_target = {}
        for slug, target in self.link_targets.items():
            # 同一个目标只保留一个 slug；namesilo 不参与比价。
            if slug == "namesilo":
                continue
            self.by_target.setdefault(target, slug)

    def buy(self, url):
        if not url or not str(url).startswith("https://"):
            return None, None, None
        slug = self.by_target.get(canon_url(url))
        rel = "sponsored nofollow noopener"
        if slug:
            return slug, None, rel
        return None, url, rel

    def add(self, offer):
        if not offer["id"] or not offer["name"] or not offer["provider_slug"]:
            raise SystemExit(f"不完整的套餐记录: {offer!r}")
        offer["specs"] = specs_text(
            offer["cpu"], offer["ram_mb"], offer["disk_gb"], offer["disk_type"],
            offer["traffic_gb"], offer["bandwidth_mbps"],
        )
        self.offers.append(offer)

    def skip(self, provider, reason, name):
        self.excluded.append({"provider": provider, "reason": reason, "name": name})

    def consider_product(self, provider_slug, series_id, category, name):
        if provider_slug == "namesilo":
            self.skip(provider_slug, "namesilo", name)
            return False
        if series_id in SKIP_SERIES or category in SKIP_CATEGORY:
            self.skip(provider_slug, "non-server", name)
            return False
        return True


def num(value):
    if value is None or value == "":
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return value
    return None


def build_bandwagon(builder, catalog):
    products = catalog["products"]
    periods = {item["id"]: item["label"] for item in catalog["periods"]}
    for series in catalog["series"]:
        for region in series["regions"]:
            region_name, region_slug = region_of(region.get("label"))
            for dc in region["datacenters"]:
                city, location_note = split_city(dc.get("city"))
                for plan in dc["plans"]:
                    spec = products[str(plan["product_id"])]
                    line_slug, line = detect_line(spec.get("name"), series.get("label"))
                    for offer in plan["offers"]:
                        price, monthly, basis, price_text = pricing(
                            offer.get("period"), periods.get(offer.get("period")),
                            offer.get("amount_cents"), None, None,
                        )
                        stock, stock_label = stock_of(offer.get("available"))
                        aff_slug, buy_url, buy_rel = builder.buy(offer.get("url"))
                        notes = None
                        ram = num(spec.get("ram_mb"))
                        if isinstance(ram, (int, float)) and int(ram) % 1024:
                            notes = "官方内存原值非整 GiB，未改写。"
                        builder.add(blank_offer(
                            id=f"bwh:{series['id']}:{dc['id']}:{plan['product_id']}:{offer['period']}",
                            provider=PROVIDERS["bandwagonhost"],
                            provider_slug="bandwagonhost",
                            name=spec.get("name"),
                            kind="VPS",
                            region=region_name,
                            region_slug=region_slug,
                            city=city,
                            datacenter=dc.get("id"),
                            line=line,
                            line_slug=line_slug,
                            cpu=num(spec.get("vcpu_count")),
                            ram_mb=ram,
                            disk_gb=num(spec.get("storage_gb")),
                            disk_type=None,
                            traffic_gb=num(spec.get("transfer_gb_per_month")),
                            bandwidth_mbps=num(spec.get("port_speed_mbps")),
                            price=price,
                            price_text=price_text,
                            period=offer.get("period"),
                            period_label=periods.get(offer.get("period")),
                            monthly_usd=monthly,
                            monthly_basis=basis,
                            stock=stock,
                            stock_label=stock_label,
                            promo_code=None,
                            checked_on=catalog.get("checked_on"),
                            aff_slug=aff_slug,
                            buy_url=buy_url,
                            buy_rel=buy_rel,
                            location_note=location_note,
                            notes=notes,
                        ))


def build_vultr(builder, catalog):
    def add_plan(plan, region):
        country = region.get("country_label") if region else None
        region_name, region_slug = region_of(country)
        city, location_note = split_city(region.get("city") if region else None)
        if region and region.get("id") and not location_note:
            location_note = None
        line_slug, line = detect_line(plan.get("name"), plan.get("series_label"))
        series_id = plan.get("series_id")
        if series_id == "metal":
            kind = "裸金属"
        elif series_id in ("vcg", "vdm"):
            kind = "GPU"
        else:
            kind = "云服务器"
        price, monthly, basis, price_text = pricing(
            "hourly", "按小时", None, plan.get("price_hourly"), plan.get("price_monthly"),
        )
        # 官方月价存在时，卡片主价格用官方月价，小时价另列。月价不是用小时价乘出来的。
        hourly_text = money(plan.get("price_hourly"))
        if plan.get("price_monthly") is not None:
            price = float(plan["price_monthly"])
            price_text = money(price)
            monthly = float(plan["price_monthly"])
            basis = "official"
        stock, stock_label = stock_of(plan.get("availability"))
        aff_slug, buy_url, buy_rel = builder.buy(plan.get("affiliate_url"))
        disk = disk_label(plan.get("disk_type"), plan.get("storage_type"))
        builder.add(blank_offer(
            id="vultr:" + plan["offer_key"],
            provider=PROVIDERS["vultr"],
            provider_slug="vultr",
            name=plan.get("name"),
            kind=kind,
            region=region_name,
            region_slug=region_slug,
            city=city,
            datacenter=region.get("id") if region else None,
            line=line,
            line_slug=line_slug,
            cpu=num(plan.get("vcpu_count")),
            ram_mb=num(plan.get("ram_mb")),
            disk_gb=num(plan.get("disk_gb")),
            disk_type=disk,
            traffic_gb=num(plan.get("bandwidth_gb")),
            bandwidth_mbps=None,
            price=price,
            price_text=price_text,
            period="hourly",
            period_label="按小时",
            monthly_usd=monthly,
            monthly_basis=basis,
            hourly_text=hourly_text,
            stock=stock,
            stock_label=stock_label,
            promo_code=None,
            checked_on=catalog.get("checked_on"),
            aff_slug=aff_slug,
            buy_url=buy_url,
            buy_rel=buy_rel,
            location_note=location_note,
            notes=None,
        ))

    for series in catalog["series"]:
        for region in series["regions"]:
            for plan in region["plans"]:
                add_plan(plan, region)
    for plan in catalog.get("unlisted_plans") or []:
        add_plan(plan, {})


def build_racknerd(builder, catalog):
    series = {item["id"]: item["label"] for item in catalog["series"]}
    for product in catalog["products"]:
        if not builder.consider_product("racknerd", product.get("series_id"), product.get("category"), product.get("name")):
            continue
        regions = product.get("regions") or []
        if regions:
            region_name, region_slug = region_of("美国")
            location_note = "配置页可选：" + "、".join(item.get("label") or "" for item in regions if item.get("label"))
            city = None
        else:
            region_name, region_slug, city, location_note = None, None, None, product.get("region_note")
        line_slug, line = detect_line(product.get("name"), series.get(product.get("series_id")))
        stock, stock_label = stock_of(product.get("availability"))
        traffic = num(product.get("bandwidth_gb")) if product.get("bandwidth_period") == "月" else None
        for offer in product["offers"]:
            price, monthly, basis, price_text = pricing(
                offer.get("period"), offer.get("label"), offer.get("amount_cents"), None, None,
            )
            aff_slug, buy_url, buy_rel = builder.buy(offer.get("affiliate_url"))
            builder.add(blank_offer(
                id=f"racknerd:{product['product_id']}:{offer['period']}",
                provider=PROVIDERS["racknerd"],
                provider_slug="racknerd",
                name=product.get("name"),
                kind=product.get("category"),
                region=region_name,
                region_slug=region_slug,
                city=city,
                datacenter=None,
                line=line,
                line_slug=line_slug,
                cpu=num(product.get("vcpu_count")),
                ram_mb=num(product.get("ram_mb")),
                disk_gb=num(product.get("storage_gb")),
                disk_type=disk_label(product.get("storage_type"), None),
                traffic_gb=traffic,
                bandwidth_mbps=num(product.get("port_mbps")),
                price=price,
                price_text=price_text,
                period=offer.get("period"),
                period_label=offer.get("label"),
                monthly_usd=monthly,
                monthly_basis=basis,
                stock=stock,
                stock_label=stock_label,
                promo_code=offer.get("promo_code") or offer.get("coupon") or None,
                checked_on=product.get("checked_on") or catalog.get("checked_on"),
                aff_slug=aff_slug,
                buy_url=buy_url,
                buy_rel=buy_rel,
                location_note=location_note,
                notes=None,
            ))


def build_generic(builder, catalog):
    provider_slug = catalog["id"]
    if provider_slug == "namesilo":
        builder.skip(provider_slug, "namesilo", catalog.get("merchant"))
        return
    series = {item["id"]: item.get("label") for item in catalog.get("series") or []}
    products = catalog["products"]
    rows = []
    for product in products:
        if product.get("deployments"):
            rows.extend(product["deployments"])
        else:
            rows.append(product)
    for product in rows:
        series_id = product.get("series_id")
        if not builder.consider_product(provider_slug, series_id, product.get("category"), product.get("name")):
            continue
        raw_city = (product.get("city") or "").strip()
        if raw_city in ("香港", "中国香港"):
            # 城市字段已经写明香港，比“中国”这个国家字段更具体，仍然来自目录原文。
            region_name, region_slug, city, city_note = "中国香港", "hong-kong", None, None
        else:
            region_name, region_slug = region_of(product.get("country"))
            city, city_note = split_city(product.get("city"))
        extra_note = product.get("region_note") or None
        placeholder = city_note and (
            city_note in NOT_A_REGION or "待核实" in city_note or "待确认" in city_note
            or "以配置页" in city_note or "无需选择" in city_note
        )
        if city_note and not placeholder and extra_note:
            location_note = f"{city_note} {extra_note}"
        elif city_note and not placeholder:
            location_note = city_note
        else:
            location_note = extra_note
        line_slug, line = detect_line(product.get("name"), series.get(series_id))
        stock, stock_label = stock_of(product.get("availability") or product.get("availability_status"))
        for offer in product.get("offers") or []:
            price, monthly, basis, price_text = pricing(
                offer.get("period"), offer.get("label"), offer.get("amount_cents"),
                offer.get("price_hourly"), offer.get("price_monthly"),
            )
            currency = offer.get("currency") or "USD"
            hourly_text = money(offer.get("price_hourly")) if offer.get("period") == "hourly" else None
            if offer.get("period") == "hourly" and offer.get("price_monthly") is not None:
                price = float(offer["price_monthly"])
                price_text = money(price)
                monthly = float(offer["price_monthly"])
                basis = "official"
            notes = []
            # 不用汇率把非美元标价换算成美元，避免和美元月价放在一起排序。
            if currency != "USD":
                monthly = None
                basis = None
                if price is not None:
                    price_text = f"{currency} {price:.2f}"
                notes.append("标价货币不是美元，未折成美元。")
            if offer.get("is_introductory"):
                notes.append("标价为首期价。")
            renewal = offer.get("renewal_amount_cents")
            if renewal is not None and offer.get("amount_cents") is not None and renewal != offer.get("amount_cents"):
                notes.append("同周期续费价不同，未把首期价当成续费价。")
            if offer.get("period") in ("quote", "unknown", "unit-monthly"):
                monthly = None
                basis = None
            aff_slug, buy_url, buy_rel = builder.buy(offer.get("affiliate_url"))
            promo = offer.get("promo_code") or offer.get("coupon") or offer.get("code") or None
            builder.add(blank_offer(
                id=f"{provider_slug}:{product.get('id')}:{offer.get('period')}",
                provider=catalog.get("merchant") or PROVIDERS.get(provider_slug),
                provider_slug=provider_slug,
                name=product.get("name"),
                kind=product.get("category"),
                region=region_name,
                region_slug=region_slug,
                city=city,
                datacenter=product.get("datacenter") or None,
                line=line,
                line_slug=line_slug,
                cpu=num(product.get("vcpu_count")),
                ram_mb=num(product.get("ram_mb")),
                disk_gb=num(product.get("storage_gb")),
                disk_type=disk_label(product.get("storage_type"), None),
                traffic_gb=num(product.get("bandwidth_gb")),
                bandwidth_mbps=num(product.get("port_mbps")),
                price=price,
                price_text=price_text,
                currency=offer.get("currency") or "USD",
                period=offer.get("period"),
                period_label=offer.get("label"),
                monthly_usd=monthly,
                monthly_basis=basis,
                hourly_text=hourly_text,
                stock=stock,
                stock_label=stock_label,
                promo_code=promo,
                checked_on=product.get("checked_on") or catalog.get("checked_on"),
                aff_slug=aff_slug,
                buy_url=buy_url,
                buy_rel=buy_rel,
                location_note=location_note,
                notes=" ".join(notes) or None,
            ))


def facet(items, slug_key, label_key):
    counts = {}
    labels = {}
    for item in items:
        slug = item.get(slug_key)
        if not slug:
            continue
        counts[slug] = counts.get(slug, 0) + 1
        labels[slug] = item.get(label_key) or slug
    return [
        {"slug": slug, "label": labels[slug], "count": counts[slug]}
        for slug in sorted(counts, key=lambda key: (-counts[key], labels[key]))
    ]


def write_pages(payload):
    servers = ROOT / "content" / "servers"
    providers = servers / "providers"
    regions = servers / "regions"
    lines = servers / "lines"
    for folder in (servers, providers, regions, lines):
        folder.mkdir(parents=True, exist_ok=True)

    def dump(path, title, description, **params):
        lines_out = ["---", f"title: {json.dumps(title, ensure_ascii=False)}", f"description: {json.dumps(description, ensure_ascii=False)}"]
        for key, value in params.items():
            if value is None:
                continue
            if isinstance(value, bool):
                lines_out.append(f"{key}: {str(value).lower()}")
            elif isinstance(value, (int, float)):
                lines_out.append(f"{key}: {value}")
            else:
                lines_out.append(f"{key}: {json.dumps(value, ensure_ascii=False)}")
        lines_out += ["generated_by: build-offers.py", "---", ""]
        path.write_text("\n".join(lines_out), encoding="utf-8")
        return path

    keep = set()
    meta = payload["meta"]
    keep.add(dump(
        servers / "_index.md",
        "服务器比价",
        "把已核实的套餐放在一起比较。可按地区、线路、价格、周期、库存和商家筛选。未知字段留空。",
        offer_count=meta["offer_count"],
        in_stock_count=meta["in_stock_count"],
        provider_count=meta["provider_count"],
        min_monthly_usd=meta["min_monthly_usd"],
    ))
    for item in payload["facets"]["providers"]:
        keep.add(dump(
            providers / f"{item['slug']}.md",
            f"{item['label']}套餐",
            f"{item['label']}已收录 {item['count']} 条报价。价格和库存以目录快照为准，未知项不补。",
            filter_provider=item["slug"],
            offer_count=item["count"],
        ))
    for item in payload["facets"]["regions"]:
        keep.add(dump(
            regions / f"{item['slug']}.md",
            f"{item['label']}服务器套餐",
            f"{item['label']}已收录 {item['count']} 条报价。只包含目录里明确写了该地区的套餐。",
            filter_region=item["slug"],
            offer_count=item["count"],
        ))
    for item in payload["facets"]["lines"]:
        keep.add(dump(
            lines / f"{item['slug']}.md",
            f"{item['label']}套餐",
            f"产品名或系列名明确写了 {item['label']} 的报价，共 {item['count']} 条。没有写明线路的套餐不会出现在这里。",
            filter_line=item["slug"],
            offer_count=item["count"],
        ))
    for folder in (providers, regions, lines):
        for path in folder.glob("*.md"):
            text = path.read_text(encoding="utf-8")
            if path not in keep and "generated_by: build-offers.py" in text:
                path.unlink()
    write_english_pages(payload)


REGION_EN = {
    "united-states": "United States",
    "hong-kong": "Hong Kong",
    "japan": "Japan",
    "singapore": "Singapore",
    "netherlands": "Netherlands",
    "germany": "Germany",
    "united-kingdom": "United Kingdom",
    "australia": "Australia",
    "canada": "Canada",
    "south-korea": "South Korea",
    "france": "France",
    "india": "India",
    "poland": "Poland",
    "united-arab-emirates": "United Arab Emirates",
    "new-zealand": "New Zealand",
    "spain": "Spain",
    "china": "China",
    "mexico": "Mexico",
    "brazil": "Brazil",
    "south-africa": "South Africa",
    "israel": "Israel",
    "sweden": "Sweden",
    "italy": "Italy",
    "chile": "Chile",
}
PROVIDER_EN = {
    "bandwagonhost": "BandwagonHost",
    "vultr": "Vultr",
    "racknerd": "RackNerd",
    "raksmart": "RakSmart",
    "cloudcone": "CloudCone",
    "ethernetservers": "Ethernet Servers",
    "interserver": "InterServer",
}
LINE_EN = {"cn2-gia": "CN2 GIA", "cmin2": "CMIN2", "as9929": "AS9929", "cn2": "CN2"}


def write_english_pages(payload):
    """英文落地页只翻译标题和筛选说明，套餐数字仍来自同一份 offers.json。"""
    root = ROOT / "content.en" / "servers"
    providers = root / "providers"
    regions = root / "regions"
    lines = root / "lines"
    for folder in (root, providers, regions, lines):
        folder.mkdir(parents=True, exist_ok=True)

    def dump(path, title, description, **params):
        out = ["---", f"title: {json.dumps(title, ensure_ascii=False)}", f"description: {json.dumps(description, ensure_ascii=False)}"]
        for key, value in params.items():
            if value is None:
                continue
            if isinstance(value, bool):
                out.append(f"{key}: {str(value).lower()}")
            elif isinstance(value, (int, float)):
                out.append(f"{key}: {value}")
            else:
                out.append(f"{key}: {json.dumps(value, ensure_ascii=False)}")
        out += ["generated_by: build-offers.py", "---", ""]
        path.write_text("\n".join(out), encoding="utf-8")
        return path

    keep = set()
    meta = payload["meta"]
    keep.add(dump(
        root / "_index.md",
        "Compare server plans",
        "Filter plans already checked against merchant catalogs. Unknown fields stay empty. This is not a live price or stock feed.",
        offer_count=meta["offer_count"],
        in_stock_count=meta["in_stock_count"],
        provider_count=meta["provider_count"],
        min_monthly_usd=meta["min_monthly_usd"],
    ))
    for item in payload["facets"]["providers"]:
        label = PROVIDER_EN.get(item["slug"], item["label"])
        keep.add(dump(
            providers / f"{item['slug']}.md",
            f"{label} plans",
            f"{item['count']} offers from the {label} catalog snapshot. Missing fields are not filled in.",
            filter_provider=item["slug"],
            offer_count=item["count"],
        ))
    for item in payload["facets"]["regions"]:
        label = REGION_EN.get(item["slug"], item["slug"])
        keep.add(dump(
            regions / f"{item['slug']}.md",
            f"{label} server plans",
            f"{item['count']} offers whose catalog entry names {label}. Plans without a stated region are not included.",
            filter_region=item["slug"],
            offer_count=item["count"],
        ))
    for item in payload["facets"]["lines"]:
        label = LINE_EN.get(item["slug"], item["label"])
        keep.add(dump(
            lines / f"{item['slug']}.md",
            f"{label} plans",
            f"{item['count']} offers whose product or series name states {label}. Offers that do not name a line are excluded.",
            filter_line=item["slug"],
            offer_count=item["count"],
        ))
    for folder in (providers, regions, lines):
        for path in folder.glob("*.md"):
            if path not in keep and "generated_by: build-offers.py" in path.read_text(encoding="utf-8"):
                path.unlink()


def assert_honest(offers):
    providers = {item["provider_slug"] for item in offers}
    if "namesilo" in providers:
        raise SystemExit("NameSilo 不应进入比价")
    kinds = {item["kind"] for item in offers}
    if "域名" in kinds:
        raise SystemExit("域名条目不应进入比价")
    raksmart_lines = [item for item in offers if item["provider_slug"] == "raksmart" and item["line"]]
    if raksmart_lines:
        raise SystemExit("RakSmart 目录写明不能直接标线路，但仍生成了线路")
    if not any(item["line_slug"] == "cn2-gia" for item in offers):
        raise SystemExit("搬瓦工 CN2 GIA 产品名没有被识别")
    for item in offers:
        if item["monthly_basis"] not in (None, "official", "period_divided"):
            raise SystemExit("未知的月价口径")
        if item["period"] == "hourly" and item["monthly_basis"] == "period_divided":
            raise SystemExit("小时价被折算成了月价")
        if item["stock"] not in (None, "in", "out"):
            raise SystemExit("库存被写成了未定义的值")
        if item["aff_slug"] and item["buy_url"]:
            raise SystemExit("aff_slug 与直链同时存在")
    ids = [item["id"] for item in offers]
    if len(ids) != len(set(ids)):
        raise SystemExit("套餐 id 重复")


def main():
    builder = Builder()
    build_bandwagon(builder, read_json("bandwagonhost_catalog.json"))
    build_vultr(builder, read_json("vultr_catalog.json"))
    build_racknerd(builder, read_json("racknerd_catalog.json"))
    for name in ("raksmart", "cloudcone", "ethernetservers", "interserver"):
        build_generic(builder, read_json(f"{name}_catalog.json"))
    if (DATA / "namesilo_catalog.json").exists():
        builder.skip("namesilo", "namesilo", "namesilo_catalog.json")

    # 核对日期新的在前；同一天按美元月价从低到高，没有月价的放后面。
    offers = sorted(builder.offers, key=lambda item: (
        -(int((item["checked_on"] or "0000-00-00").replace("-", ""))),
        item["monthly_usd"] is None,
        item["monthly_usd"] if item["monthly_usd"] is not None else 10**9,
        item["provider_slug"] or "",
        item["name"] or "",
        item["id"],
    ))
    assert_honest(offers)

    monthly_values = [item["monthly_usd"] for item in offers if item["monthly_usd"] is not None]
    period_labels = {
        "hourly": "按小时",
        "monthly": "月付",
        "quarterly": "季付",
        "semiannually": "半年付",
        "annually": "年付",
        "biennially": "两年付",
        "triennially": "三年付",
        "quote": "询价",
        "unknown": "周期未核实",
        "unit-monthly": "按量",
    }
    periods = {}
    for item in offers:
        if item["period"]:
            periods.setdefault(item["period"], period_labels.get(item["period"], item["period_label"] or item["period"]))
    payload = {
        "meta": {
            "offer_count": len(offers),
            "in_stock_count": sum(1 for item in offers if item["stock"] == "in"),
            "out_of_stock_count": sum(1 for item in offers if item["stock"] == "out"),
            "unknown_stock_count": sum(1 for item in offers if item["stock"] is None),
            "provider_count": len({item["provider_slug"] for item in offers}),
            "min_monthly_usd": min(monthly_values) if monthly_values else None,
            "excluded_count": len(builder.excluded),
            "excluded_reasons": {
                "namesilo": "域名注册商，不进入服务器比价",
                "non-server": "域名、邮箱、CDN、证书、网络服务、机柜托管等非服务器条目",
            },
            "principles": [
                "未知字段为 null，不猜测。",
                "小时价不乘小时数换算月价。",
                "monthly_basis=period_divided 表示用已核实的周期总价除以月数，只用于筛选排序。",
                "aff_slug 只在链接与现有 /go/ 目标完全一致时填写。",
            ],
        },
        "facets": {
            "providers": facet(offers, "provider_slug", "provider"),
            "regions": facet(offers, "region_slug", "region"),
            "lines": facet(offers, "line_slug", "line"),
            "periods": [
                {"slug": key, "label": periods[key], "count": sum(1 for item in offers if item["period"] == key)}
                for key in sorted(periods, key=lambda key: -sum(1 for item in offers if item["period"] == key))
            ],
            "stocks": [
                {"slug": "in", "label": "有货", "count": sum(1 for item in offers if item["stock"] == "in")},
                {"slug": "out", "label": "缺货", "count": sum(1 for item in offers if item["stock"] == "out")},
                {"slug": "unknown", "label": "库存未核实", "count": sum(1 for item in offers if item["stock"] is None)},
            ],
        },
        "offers": offers,
    }
    text = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    (DATA / "offers.json").write_text(text, encoding="utf-8")
    static_dir = ROOT / "static"
    static_dir.mkdir(exist_ok=True)
    (static_dir / "offers.json").write_text(text, encoding="utf-8")
    write_pages(payload)
    print(
        f"offers={len(offers)} providers={payload['meta']['provider_count']} "
        f"in_stock={payload['meta']['in_stock_count']} excluded={len(builder.excluded)} "
        f"lines={payload['facets']['lines']} bytes={len(text.encode('utf-8'))}"
    )


if __name__ == "__main__":
    main()
