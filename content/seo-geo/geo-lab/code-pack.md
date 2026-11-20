---
title: "GEO 标配代码包：robots.txt、llms.txt 与 JSON-LD"
date: 2026-11-20
lastmod: 2026-11-20
weight: 1
description: "robots.txt、llms.txt、Organization 和 Product/FAQ 的示例。示例里的价格、交期和地址是占位，待核实后换成你的数据。"
ShowToc: true
ShowReadingTime: false
---

买家在 ChatGPT Search、Perplexity 或 Google AI Overviews 里问同类供应商时，模型读到的是文本和实体关系，不是你的视觉排版。没有 llms.txt 和结构化数据时，导航、弹窗和脚本会占掉正文。下面四份是示例，把括号里的说明换成你的真实参数后再上线。部署不保证被推荐。

> 示例中的价格、交期、公差、电话、地址和网址都是**占位**。**参考，以你的报价单和证书为准，待核实。** 核对日期：2026-11-20。没有公开标价就删掉 `offers`。没有页面上可见的真实评价就不要写星级。

## 四份文件分别做什么

| 文件 | 放在哪 | 给谁看 | 解决什么 | 花费 |
| --- | --- | --- | --- | --- |
| robots.txt | `你的域名/robots.txt` | GPTBot、ClaudeBot、PerplexityBot、Google-Extended、Bingbot 等 | 避免插件默认把这些爬虫全部挡住 | 你的时间，大约几分钟 |
| llms.txt | `你的域名/llms.txt` | 会读取纯文本说明的检索 | 用短句写清产品、起订量、认证，少一些页面噪音 | 大约一刻钟，视你补参数的速度 |
| Organization + sameAs | 首页 | 知识图谱和消歧 | 把官网和你真实拥有的领英、视频、目录连成同一家公司 | 大约几分钟 |
| Product + FAQPage | 核心产品页 | 会读结构化字段的检索 | 让问句的答案和产品参数出现在同一页 | 每个核心页大约几分钟 |

「必须部署才能被推荐」不成立。这四份只解决「文件在不在、字段能不能被解析」。

## robots.txt

有的安全插件或防火墙会把 AI 爬虫当成采集器拦截。打开 `https://你的域名/robots.txt`，按你的站点改路径。下面是示例，不是唯一正确写法。名单会变，上线前对照各家文档。

```text
# robots.txt 示例。按你的后台路径修改。
User-agent: *
Allow: /
Disallow: /wp-admin/
Disallow: /cart/
Disallow: /checkout/

User-agent: GPTBot
Allow: /

User-agent: OAI-SearchBot
Allow: /

User-agent: ChatGPT-User
Allow: /

User-agent: ClaudeBot
Allow: /

User-agent: PerplexityBot
Allow: /

User-agent: Google-Extended
Allow: /

User-agent: Bingbot
Allow: /

Sitemap: https://www.yourdomain.com/sitemap.xml
```

`OAI-SearchBot` 常被描述为 ChatGPT 实时检索用的爬虫，`Bingbot` 是 Bing 的爬虫。两者被 `Disallow: /` 挡住时，依赖它们的检索可能抓不到正文。这是机制说明，不是「挡住就永远不会出现」的承诺。若你不希望某个爬虫使用内容，单独查该爬虫当时的官方说明。

## llms.txt

新建纯文本 `llms.txt`，放在根目录。下面用一家加工厂举例，整段替换成你的英文事实。不要写 best quality、world-leading、cheap price。能核对的是数字和专有名词：厂房面积、公差、交期、ISO 编号、设备型号。这些数字在示例里是假的。

```text
# [公司英文全称，例如 Shenzhen Example Precision Manufacturing Co., Ltd.]

> [一句话：工厂属性、工艺、认证、成立年份。例如：ISO 9001 certified OEM/ODM manufacturer of custom CNC machined parts in China since 2012.]

## Core Capabilities & Factory Facts
- **Business Type**: Direct source factory, OEM and ODM. 只有你确实不经贸易商时才写 No middleman.
- **Factory Location**: [城市与省份]
- **Facility Size & Equipment**: [厂房面积与设备，用你的固定资产清单]
- **Certifications**: [证书上的标准，例如 ISO 9001:2015。没有的不要写]
- **Minimum Order Quantity (MOQ)**: [报价单上的起订量]
- **Standard Lead Time**: [样品和批量的工作日，以你能做到的为准]
- **Tolerances & Quality Control**: [你检测报告里的公差，不要照抄 0.005 mm]

## Key Product Lines
- [产品线名称](https://www.yourdomain.com/products/category-1): [材质、范围、典型场景]
- [产品线名称](https://www.yourdomain.com/products/category-2): [材质、规格、认证]

## Commercial & Engineering Resources
- [Capabilities](https://www.yourdomain.com/capabilities): 设备和材质。
- [Quality](https://www.yourdomain.com/quality-control): 可下载的证书。没有就不要写这一行。
- [RFQ](https://www.yourdomain.com/contact): 回复时间写成你实际能做到的，不要照抄 12 小时。

## Official Contact & Entity Verification
- **Official Website**: https://www.yourdomain.com
- **RFQ Sales Email**: sales@yourdomain.com
- **LinkedIn Company Page**: https://www.linkedin.com/company/your-company-handle
```

## Organization 与 sameAs

放在首页。`sameAs` 只填你真实拥有的档案。电话、地址与联系页、营业信息一致。示例电话 `+86-755-12345678` 是假的。

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "@id": "https://www.yourdomain.com/#organization",
  "name": "你的公司英文全称",
  "alternateName": "品牌简称",
  "url": "https://www.yourdomain.com",
  "logo": "https://www.yourdomain.com/logo.png",
  "foundingDate": "2012",
  "description": "用一句话写认证和工艺。不要写无法核对的最高级。",
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "真实英文街道",
    "addressLocality": "城市",
    "addressRegion": "省份",
    "postalCode": "邮编",
    "addressCountry": "CN"
  },
  "contactPoint": {
    "@type": "ContactPoint",
    "telephone": "+86-000-0000-0000",
    "contactType": "sales",
    "email": "sales@yourdomain.com",
    "availableLanguage": ["English", "Chinese"]
  },
  "sameAs": [
    "https://www.linkedin.com/company/你的领英主页",
    "https://www.youtube.com/@你的频道",
    "https://www.wikidata.org/wiki/Q000000"
  ],
  "knowsAbout": [
    "CNC Machining",
    "Precision Metal Stamping"
  ]
}
</script>
```

## Product 与 FAQPage

放在你真正在卖的产品页。`lowPrice` 1.50、`highPrice` 85.00、`offerCount` 100 是占位，**不要原样上线**。没有公开标价就删除整个 `offers`。FAQ 的句子改成你的报价单。

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org/",
  "@graph": [
    {
      "@type": "Product",
      "name": "换成你的产品英文名",
      "image": [
        "https://www.yourdomain.com/images/part-1.jpg"
      ],
      "description": "材质、公差、检测。数字用你的工艺文件。",
      "sku": "YOUR-SKU",
      "mpn": "YOUR-MPN",
      "brand": {
        "@type": "Brand",
        "name": "你的品牌"
      },
      "manufacturer": {
        "@id": "https://www.yourdomain.com/#organization"
      },
      "material": "换成真实材质牌号",
      "offers": {
        "@type": "AggregateOffer",
        "url": "https://www.yourdomain.com/products/example",
        "priceCurrency": "USD",
        "lowPrice": "0.00",
        "highPrice": "0.00",
        "offerCount": "1",
        "availability": "https://schema.org/PreOrder"
      }
    },
    {
      "@type": "FAQPage",
      "mainEntity": [
        {
          "@type": "Question",
          "name": "What is the MOQ and lead time for this part?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "写成报价单上的起订量和工作日。不要保留示例里的 1 piece、50 pieces、3–5 天。"
          }
        },
        {
          "@type": "Question",
          "name": "What tolerances and certificates do you actually hold?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "只写证书上有的标准和检测报告里的公差。"
          }
        },
        {
          "@type": "Question",
          "name": "How does a buyer request a quote?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "写清收图纸的邮箱和你实际的回复时间。"
          }
        }
      ]
    }
  ]
}
</script>
```

## 上线后怎么核对

1. **文件能打开。** `/robots.txt` 和 `/llms.txt` 返回 200，内容是纯文本。WordPress 可以用只负责插入代码的插件，把 Organization 放在首页、Product 放在对应产品页，不必改主题。
2. **语法。** 用 Google 的 Rich Results Test 打开产品页。看到产品或 FAQ 被解析，只说明语法通过，不说明会展示。
3. **请求收录。** 在 Search Console 和 Bing Webmaster 对改过的 URL 请求编入索引。常见说法是 24–72 小时内被重新抓取，**待核实**，以你后台的抓取时间为准。

下一篇：[实体图谱与公开来源](/seo-geo/geo-lab/entity-sources/)。
