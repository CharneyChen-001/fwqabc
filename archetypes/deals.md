---
title: "{{ replace .File.ContentBaseName "-" " " | title }}"
date: {{ .Date }}
lastmod: {{ .Date }}
draft: true
merchant: ""
merchants: []
routes: []
deal_start: ""   # 北京时间
deal_end: ""
tags: []
categories: []
# 不编造价格和线路。未知就留空，或写 TODO。
---

## 活动时间（北京时间）

## 优惠总表

| 方案 | 配置 | 价格 | 线路 | 购买 |
|---|---|---|---|---|
| TODO | | | | |

## 点评

## 限制与坑

## 更新日志

- {{ now.Format "2006-01-02" }}：首次发布
