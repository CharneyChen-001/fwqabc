---
title: "Configuration floor"
description: "A vCPU and RAM floor by workload. The steps are assumptions, not a benchmark, and they do not read live prices."
---

## Formula and units

The only outputs are a **vCPU count** and **RAM in MB**. Page views are per month. API peak is requests per second. Blank means unknown, not zero.

| Workload | Floor | Step up (still an assumption) |
|---|---|---|
| Static site | 1 vCPU / 1024 MB | Above 100,000 monthly page views, RAM becomes 2048 MB |
| CMS (one site, with a database) | 1 vCPU / 2048 MB | Above 50,000 monthly page views, 2 vCPU / 4096 MB |
| Small JSON API | 2 vCPU / 2048 MB | Above 20 requests/second, RAM becomes 4096 MB; above 100 requests/second the sheet stops at one machine with 4 vCPU / 8192 MB |

The API row ignores page views. Above 10,000,000 page views per month, or above 1,000 requests/second, the sheet gives no size and does not estimate several machines.

Without JavaScript, use the table. With JavaScript, the form states the floor and links to catalog plans whose RAM and vCPU are both at least that floor. Plans with unknown RAM or vCPU are left out, because unknown is not the same as meeting the floor.
