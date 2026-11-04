"""将已复核的公开快照适配为旧站 CloudCone 目录；不联网、不修改数据库。"""
import argparse
from collections import defaultdict
from decimal import Decimal
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COUNTRIES = {'US': '美国', 'AU': '澳大利亚', 'NZ': '新西兰'}
SERIES = {
    'sc2': ('SC2 可扩展云服务器', '按小时累计计费，官方月价另列。', '已核对洛杉矶 DC1；配置页列出套餐，未实际下单。'),
    'vps': ('年付 SSD VPS', '按年预付，表中金额为完整付款周期总价。', '六档洛杉矶 DC4；SSD VPS 1 另有圣路易斯 DC1 售罄报价，分开列出。'),
    'dedicated': ('独立服务器', '按城市收录104种配置；零元售罄占位只保留资料。', '覆盖洛杉矶、墨尔本、悉尼、阿德莱德、珀斯与奥克兰。'),
    'email': ('企业邮箱', '套餐费用、存储及外发额度按整个组织共享，不是每用户单价。', '托管邮箱服务，不作为服务器机房地区分类。'),
    'cdn': ('CDN', '15档套餐；流量每月1日重置，付款周期与流量周期分开记录。', '按方案节点覆盖范围分类；核验时15个创建页均显示售罄。'),
    'domain': ('域名', '65种后缀的注册参考年价；官网划线价不代表续费价。', '域名注册不对应服务器机房，具体名称和最终费用以官网查询为准。'),
    'private': ('私有云', '独享基础设施、备份、高可用与灾难恢复等定制服务。', '按项目确定部署地区、资源与报价。'),
    'addons': ('备份与快照', 'SC2附加服务，备份与快照分别计费。', '随对应SC2实例使用，备份与快照均为整机恢复。'),
}
OLD_IDS = {
    '3ca54888-5216-59f9-bcc8-fb721081d64b': 'la-e3-1270v6',
    '6f1284f3-62ec-5fda-a911-64211542ac13': 'la-dual-e5-2697v2-128g',
    'bb6479e0-0d7d-5cdf-93c1-95b0ae9924b8': 'la-dual-e5-2697v2-256g',
    '676a5330-0a36-5734-8bad-0953031a385c': 'mel-e2136',
    'f0a1f3f6-52c8-5e6e-9954-8a44d97e1e58': 'mel-e3-1220v5',
    '020f90f7-8453-5aba-b723-765eee83e9aa': 'cdn-value-100',
    '0bddb075-be57-5e47-b390-bf3acf205a4f': 'cdn-value-500',
    'e2d19841-5d59-5917-a01e-2e3ed5c92a3c': 'cdn-value-1000',
    '063871f6-87c7-5fc9-9183-f5a80696e0fe': 'cdn-premium-100',
    '939062f6-7c8c-56b6-87d4-c395ce5e6021': 'cdn-premium-500',
    'c015b8cd-6cc0-56c1-9116-3a2fcd6f3678': 'private-cloud',
    '6248cd44-032d-528f-8cc3-2f0916c1cf58': 'sc2-auto-backup',
    '441055c8-2c28-5613-a225-29292727db70': 'sc2-snapshot',
}


def number(value):
    if value is None:
        return None
    value = Decimal(str(value))
    return int(value) if value == value.to_integral() else float(value)


def cents(value):
    return None if value is None else int(Decimal(str(value)) * 100)


def size(spec, key, target='GB'):
    value = spec.get(key + '_value')
    unit = spec.get(key + '_unit')
    factors = {'MB': Decimal(1) / 1024, 'MiB': Decimal(1) / 1024, 'GB': 1, 'GiB': 1, 'TB': 1024, 'TiB': 1024}
    if value is None or unit not in factors:
        return None
    value = Decimal(str(value)) * factors[unit]
    if key == 'disk' and spec.get('disk_measurement_scope') == 'per_disk':
        value *= spec.get('disk_count') or 1
    return number(value * (1024 if target == 'MB' else 1))


def slug(product):
    if product['id'] in OLD_IDS:
        return OLD_IDS[product['id']]
    category = product['category_code'].removeprefix('cloudcone-')
    if category in ('sc2', 'vps'):
        return product['name'].lower().replace(' ', '-')
    if category == 'email':
        return 'email-' + product['name'].split()[0].lower()
    if category == 'domain':
        return 'domain-' + product['domain']['tld'].lstrip('.')
    return category + '-' + product['id']


def purchase(offer):
    rank = {'offer': 0, 'deployment': 1, 'product': 2, 'category': 3, 'merchant': 4}
    links = sorted(offer.get('links', []), key=lambda link: (rank.get(link['scope'], 5), link['kind'] != 'affiliate'))
    return links[0] if links else {}


def offer_row(offer, product, catalog):
    model = offer['billing_model']
    amount = offer['quoted_amount']
    months = number(offer['term_count']) if offer['term_unit'] == 'month' else number(Decimal(str(offer['term_count'])) * 12) if offer['term_unit'] == 'year' else None
    if model == 'fixed':
        period, label = {1: ('monthly', '月付'), 3: ('quarterly', '季付'), 6: ('semiannually', '半年付'), 12: ('annually', '年付'), 24: ('biennially', '两年付')}.get(months, ('other', '按官方周期'))
    elif model == 'metered':
        period, label = ('hourly', '按小时计费') if offer['billing_unit'] == 'hour' else ('unit-monthly', '按用量计费')
    elif model == 'percentage':
        period, label = 'percentage', '按比例计费'
    else:
        period, label = 'quote', '联系商家询价'
    link = purchase(offer)
    result = {
        'id': offer['id'], 'period': period, 'label': label, 'currency': offer['currency'],
        'amount_cents': cents(amount), 'renewal_amount_cents': cents(offer['renewal_amount']),
        'price_hourly': number(offer['unit_price']) if period == 'hourly' else None,
        'price_monthly': number(offer['monthly_reference']),
        'unit_price': number(offer['unit_price']) if period != 'hourly' else None,
        'unit': (str(number(offer['percentage_rate'])) + '% 服务器月费') if model == 'percentage' else offer['billing_unit'] or '',
        'price_note': offer['price_note'] or '', 'source_date': offer['source_date'],
        'availability_status': offer['availability_status'],
        'purchase_url': link.get('url', '') if offer['availability_status'] != 'sold_out' else '',
        'link_kind': link.get('kind', 'official'), 'link_scope': catalog['link_scope'],
        'affiliate_url': catalog['affiliate_url'], 'program_id': 'cloudcone-standard',
    }
    domain = product.get('domain', {})
    if domain.get('source_date') == offer['source_date'] and Decimal(str(domain.get('display_price', 0))) == Decimal(str(amount or 0)):
        result['crossed_amount_cents'] = cents(domain.get('crossed_price'))
    return result


def convert(source, catalog):
    merchant = next(m for m in source['merchants'] if m['slug'] == 'cloudcone')
    products = [p for p in source['products'] if p['merchant_id'] == merchant['id']]
    offers_by_product = defaultdict(list)
    for offer in source['offers']:
        if offer['merchant_id'] == merchant['id']:
            offers_by_product[offer['product_id']].append(offer)
    rows = []
    for product in products:
        category = product['category_code'].removeprefix('cloudcone-')
        groups = defaultdict(list)
        for offer in offers_by_product[product['id']]:
            groups[offer['deployment_id']].append(offer)
        locations = [dict(values[0], offers=values) for values in groups.values()] if groups else [dict(location, offers=[]) for location in product.get('locations', [])]
        locations.sort(key=lambda location: (location.get('availability_status') == 'sold_out', location['region']))
        assert locations, '不能丢弃没有报价的产品：' + product['name']
        display_rows = []
        for index, location in enumerate(locations):
            spec = location.get('specs', product['specs'])
            region = location['region'].split(' · ', 1)
            country = COUNTRIES.get(region[0], '')
            city = region[-1]
            status = location['availability_status']
            offer_rows = [offer_row(o, product, catalog) for o in location['offers']]
            cpu = spec.get('cpu_model') or ''
            if cpu and spec.get('cpu_count') is not None:
                cpu += ' · ' + str(spec['cpu_count']) + ' 核'
            if spec.get('cpu_threads') is not None:
                cpu += ' · ' + str(spec['cpu_threads']) + ' 线程'
            transfer = '不限流量' if spec.get('transfer_unlimited') else ''
            if spec.get('transfer_value') is not None:
                transfer = str(number(spec['transfer_value'])) + ' ' + spec['transfer_unit'] + ' / ' + {'month': '月', 'year': '年', 'day': '天'}.get(spec['transfer_period'], spec['transfer_period'] or '周期未注明')
            if category == 'dedicated' and '网络二选一' in product['description']:
                transfer = '网络二选一，详见套餐说明'
            purchase_url = next((o['purchase_url'] for o in offer_rows if o['purchase_url']), '')
            display_rows.append({
                'id': slug(product) + (('-' + location['deployment_id'][:8]) if index else ''),
                'product_id': product['id'], 'deployment_id': location['deployment_id'],
                'series_id': category, 'category': {'sc2': '云服务器', 'vps': 'VPS', 'dedicated': '独立服务器', 'addons': '附加服务'}.get(category, SERIES[category][0]),
                'name': product['name'], 'country': country, 'city': city, 'datacenter': location.get('datacenter', ''),
                'vcpu_count': spec.get('cpu_count'), 'cpu_label': cpu,
                'ram_mb': size(spec, 'memory', 'MB'), 'storage_gb': size(spec, 'disk'), 'storage_type': spec.get('disk_type') or '',
                'bandwidth_gb': size(spec, 'transfer'), 'bandwidth_label': transfer, 'port_mbps': number(spec.get('port_mbps')),
                'spec_label': product['description'] if category not in ('sc2', 'vps', 'dedicated') else '',
                'region_note': '', 'notes': ' '.join(dict.fromkeys(filter(None, [
                    product['description'] if len(locations) == 1 else '',
                    location.get('price_note'),
                ]))),
                'availability': '核验时售罄' if status == 'sold_out' else '官网列出，库存以配置页为准', 'availability_status': status,
                'official_url': product['official_url'], 'purchase_url': purchase_url,
                'checked_on': max((o['source_date'] for o in location['offers']), default='2026-11-04'),
                'source_urls': [product['official_url']], 'offers': offer_rows,
            })
        rows.append({'id': slug(product), 'product_id': product['id'], 'name': product['name'], 'series_id': category, 'deployments': display_rows})
    order = {key: index for index, key in enumerate(SERIES)}
    rows.sort(key=lambda row: (order[row['series_id']], row['name']))
    catalog.update(products=rows, checked_on='2026-11-04', source_build_id=source['id'],
        currency_note='报价按行标注 USD（美元）或 AUD（澳元），不做汇率换算',
        scope_note='收录202项产品与服务、181条报价或询价记录。独立服务器覆盖六个城市，22项售罄零价占位仅展示资料。相同产品的不同地区报价分别展示；数据为核验快照。',
        product_count=len(rows), deployment_count=sum(len(p['deployments']) for p in rows))
    all_offers = [o for p in rows for d in p['deployments'] for o in d['offers']]
    priced = lambda o: any(o.get(k) is not None for k in ('amount_cents', 'price_hourly', 'unit_price'))
    catalog.update(offer_count=len(all_offers), priced_offer_count=sum(map(priced, all_offers)),
        priced_product_count=sum(any(priced(o) for d in p['deployments'] for o in d['offers']) for p in rows))
    catalog['series'] = [dict(id=key, label=value[0], description=value[1], region_note=value[2], product_count=sum(p['series_id'] == key for p in rows)) for key, value in SERIES.items()]
    catalog['source_urls'] = list(dict.fromkeys(catalog['source_urls'] + [p['official_url'] for p in products]))
    assert (catalog['product_count'], catalog['deployment_count'], catalog['offer_count']) == (202, 203, 181)
    assert sum(not d['offers'] for p in rows for d in p['deployments']) == 22
    return catalog


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('snapshot', type=Path, help='已复核的公开 snapshot.json')
    args = parser.parse_args()
    target = ROOT / 'data/cloudcone_catalog.json'
    source = json.loads(args.snapshot.read_text(encoding='utf-8'))
    result = convert(source, json.loads(target.read_text(encoding='utf-8')))
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: result[k] for k in ('product_count', 'deployment_count', 'offer_count', 'priced_product_count', 'priced_offer_count')}, ensure_ascii=False))
