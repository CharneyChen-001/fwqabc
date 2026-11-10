(function () {
  var app = document.getElementById("servers-app");
  var list = document.getElementById("offer-list");
  if (!app || !list) return;
  var PAGE = 24;
  var offers = [];
  var matched = [];
  var page = 1;
  var fields = ["f-q", "f-region", "f-line", "f-price", "f-min", "f-max", "f-min-ram", "f-min-cpu", "f-period", "f-stock", "f-provider", "f-sort"];

  function readForm() {
    return {
      q: document.getElementById("f-q").value.trim(),
      region: document.getElementById("f-region").value,
      line: document.getElementById("f-line").value,
      band: document.getElementById("f-price").value,
      min: document.getElementById("f-min").value,
      max: document.getElementById("f-max").value,
      minRam: document.getElementById("f-min-ram") ? document.getElementById("f-min-ram").value : "",
      minCpu: document.getElementById("f-min-cpu") ? document.getElementById("f-min-cpu").value : "",
      period: document.getElementById("f-period").value,
      stock: document.getElementById("f-stock").value,
      provider: document.getElementById("f-provider").value,
      sort: document.getElementById("f-sort").value || "updated"
    };
  }

  function applyInitial() {
    var params = new URLSearchParams(location.search);
    function pick(name, fallback) {
      return params.has(name) ? params.get(name) || "" : (fallback || "");
    }
    document.getElementById("f-q").value = pick("q", "");
    document.getElementById("f-region").value = pick("region", app.dataset.region || "");
    document.getElementById("f-line").value = pick("line", app.dataset.line || "");
    document.getElementById("f-price").value = pick("price", "");
    document.getElementById("f-min").value = pick("minPrice", "");
    document.getElementById("f-max").value = pick("maxPrice", "");
    if (document.getElementById("f-min-ram")) document.getElementById("f-min-ram").value = pick("minRam", "");
    if (document.getElementById("f-min-cpu")) document.getElementById("f-min-cpu").value = pick("minCpu", "");
    document.getElementById("f-period").value = pick("period", "");
    document.getElementById("f-stock").value = pick("stock", "");
    document.getElementById("f-provider").value = pick("provider", app.dataset.provider || "");
    document.getElementById("f-sort").value = pick("sort", "updated");
  }

  function inBand(monthly, band) {
    if (!band) return true;
    if (monthly == null) return false;
    if (band === "lt3") return monthly < 3;
    if (band === "3-5") return monthly >= 3 && monthly < 5;
    if (band === "5-10") return monthly >= 5 && monthly < 10;
    if (band === "10-20") return monthly >= 10 && monthly < 20;
    if (band === "20-50") return monthly >= 20 && monthly < 50;
    if (band === "gt50") return monthly >= 50;
    return true;
  }

  function match(offer, filter) {
    if (filter.q) {
      var blob = [offer.name, offer.provider, offer.kind, offer.region, offer.city, offer.line, offer.datacenter, offer.promo_code, offer.specs, offer.location_note, offer.notes].join(" ").toLowerCase();
      if (blob.indexOf(filter.q.toLowerCase()) === -1) return false;
    }
    if (filter.region && offer.region_slug !== filter.region) return false;
    if (filter.line && offer.line_slug !== filter.line) return false;
    if (filter.provider && offer.provider_slug !== filter.provider) return false;
    if (filter.period && offer.period !== filter.period) return false;
    if (filter.stock === "unknown") {
      if (offer.stock) return false;
    } else if (filter.stock && offer.stock !== filter.stock) return false;
    var priced = filter.band || filter.min !== "" || filter.max !== "";
    if (priced) {
      if (offer.monthly_usd == null) return false;
      if (filter.min !== "" && offer.monthly_usd < Number(filter.min)) return false;
      if (filter.max !== "" && offer.monthly_usd > Number(filter.max)) return false;
      if (!inBand(offer.monthly_usd, filter.band)) return false;
    }
    if (filter.minRam !== "") {
      var ramGb = Number(filter.minRam);
      if (!isFinite(ramGb) || ramGb < 0) return false;
      if (offer.ram_mb == null || offer.ram_mb < ramGb * 1024) return false;
    }
    if (filter.minCpu !== "") {
      var cpu = Number(filter.minCpu);
      if (!isFinite(cpu) || cpu < 0) return false;
      if (offer.cpu == null || offer.cpu < cpu) return false;
    }
    return true;
  }

  function sortOffers(items, mode) {
    var copy = items.slice();
    copy.sort(function (a, b) {
      if (mode === "price-asc" || mode === "price-desc") {
        var am = a.monthly_usd == null;
        var bm = b.monthly_usd == null;
        if (am && bm) return (a.name || "").localeCompare(b.name || "", "zh");
        if (am) return 1;
        if (bm) return -1;
        return mode === "price-asc" ? a.monthly_usd - b.monthly_usd : b.monthly_usd - a.monthly_usd;
      }
      var date = (b.checked_on || "").localeCompare(a.checked_on || "");
      if (date) return date;
      if (a.monthly_usd == null && b.monthly_usd != null) return 1;
      if (b.monthly_usd == null && a.monthly_usd != null) return -1;
      if (a.monthly_usd != null && b.monthly_usd != null && a.monthly_usd !== b.monthly_usd) return a.monthly_usd - b.monthly_usd;
      return (a.name || "").localeCompare(b.name || "", "zh");
    });
    return copy;
  }

  function el(tag, className, text) {
    var node = document.createElement(tag);
    if (className) node.className = className;
    if (text != null) node.textContent = text;
    return node;
  }

  var uiEn = (document.documentElement.lang || "").toLowerCase().indexOf("en") === 0;
  var regionEn = { "united-states": "United States", "hong-kong": "Hong Kong", japan: "Japan", singapore: "Singapore", netherlands: "Netherlands", germany: "Germany", "united-kingdom": "United Kingdom", australia: "Australia", canada: "Canada", "south-korea": "South Korea", france: "France", india: "India", poland: "Poland", "united-arab-emirates": "United Arab Emirates", "new-zealand": "New Zealand", spain: "Spain", china: "China", mexico: "Mexico", brazil: "Brazil", "south-africa": "South Africa", israel: "Israel", sweden: "Sweden", italy: "Italy", chile: "Chile" };
  var lineEn = { "cn2-gia": "CN2 GIA", cmin2: "CMIN2", as9929: "AS9929", cn2: "CN2" };
  var periodEn = { hourly: "Hourly", monthly: "Monthly", quarterly: "Quarterly", semiannually: "Semiannual", annually: "Annual", biennially: "Biennial", quote: "Quote", unknown: "Period not verified" };
  var kindEn = { "云服务器": "Cloud server", "裸金属": "Bare metal", "共享主机": "Shared hosting", "独立服务器": "Dedicated", "物理服务器": "Dedicated", "Linux 云 VPS": "Linux VPS", "存储型 VPS": "Storage VPS" };

  function stockNode(offer) {
    if (offer.stock === "in") return el("span", "stock stock-in", uiEn ? "In stock" : (offer.stock_label || "有货"));
    if (offer.stock === "out") return el("span", "stock stock-out", uiEn ? "Out of stock" : (offer.stock_label || "缺货"));
    return el("span", "stock stock-unknown", uiEn ? "Stock not verified" : "库存未核实");
  }

  function card(offer) {
    var article = el("article", "offer-card");
    var top = el("div", "offer-top");
    top.appendChild(el("h3", "", offer.name || (uiEn ? "Unnamed plan" : "未命名套餐")));
    top.appendChild(stockNode(offer));
    article.appendChild(top);
    var meta = el("p", "offer-meta");
    var provider = offer.provider || "";
    if (uiEn && offer.provider_slug === "bandwagonhost") provider = "BandwagonHost";
    meta.appendChild(el("span", "", provider));
    if (offer.kind && (!uiEn || kindEn[offer.kind] || offer.kind === "VPS" || offer.kind === "GPU")) {
      meta.appendChild(el("span", "", uiEn ? (kindEn[offer.kind] || offer.kind) : offer.kind));
    }
    if (offer.promo_code) meta.appendChild(el("span", "promo-code", (uiEn ? "Code " : "优惠码 ") + offer.promo_code));
    article.appendChild(meta);
    var price = el("p", "offer-price");
    price.appendChild(el("b", offer.price_text ? "" : "is-muted", offer.price_text || (uiEn ? "Price not verified" : "价格待核实")));
    if (offer.period) price.appendChild(el("span", "", uiEn ? (periodEn[offer.period] || offer.period) : (offer.period_label || offer.period)));
    if (offer.monthly_basis === "period_divided" && offer.monthly_usd != null) {
      price.appendChild(el("small", "", (uiEn ? "about $" : "折合 $") + Number(offer.monthly_usd).toFixed(2) + (uiEn ? "/mo" : "/月")));
    }
    if (offer.period === "hourly" && offer.hourly_text) price.appendChild(el("small", "", offer.hourly_text + (uiEn ? "/hour" : "/小时")));
    article.appendChild(price);
    var whereBits = uiEn
      ? [offer.region_slug && regionEn[offer.region_slug], offer.line_slug && lineEn[offer.line_slug]].filter(Boolean)
      : [offer.region, offer.city, offer.line].filter(Boolean);
    article.appendChild(el("p", "offer-where", whereBits.join(" · ") || (uiEn ? "Region and line not verified" : "地区与线路待核实")));
    var specs = offer.specs;
    if (uiEn) {
      var parts = [];
      if (offer.cpu != null) parts.push(offer.cpu + " vCPU");
      if (offer.ram_mb != null) parts.push((offer.ram_mb % 1024 === 0 ? (offer.ram_mb / 1024) + " GB RAM" : offer.ram_mb + " MB RAM"));
      if (offer.disk_gb != null) parts.push(offer.disk_gb + " GB" + (offer.disk_type ? " " + offer.disk_type : ""));
      specs = parts.join(" / ");
    }
    article.appendChild(el("p", "offer-specs", specs || (uiEn ? "Specs not verified" : "配置待核实")));
    if (!uiEn && offer.location_note) article.appendChild(el("p", "offer-note", offer.location_note));
    var foot = el("div", "offer-foot");
    if (offer.checked_on) {
      var time = el("time", "", (uiEn ? "Checked " : "核实 ") + offer.checked_on);
      time.dateTime = offer.checked_on;
      foot.appendChild(time);
    } else {
      foot.appendChild(el("span", "", uiEn ? "Check date missing" : "核实日期待核实"));
    }
    if (offer.aff_slug || offer.buy_url) {
      var link = el("a", "go-btn", uiEn ? "Buy" : "购买");
      link.href = offer.aff_slug ? "/go/" + offer.aff_slug + "/" : offer.buy_url;
      link.rel = offer.buy_rel || "sponsored nofollow noopener";
      link.target = "_blank";
      foot.appendChild(link);
    }
    article.appendChild(foot);
    return article;
  }

  function renderStats(items) {
    var stats = document.getElementById("servers-stats");
    if (!stats) return;
    var months = items.map(function (item) { return item.monthly_usd; }).filter(function (value) { return value != null; });
    var paid = months.filter(function (value) { return value > 0; });
    var providers = {};
    var instock = 0;
    items.forEach(function (item) {
      providers[item.provider_slug] = true;
      if (item.stock === "in") instock += 1;
    });
    function usd(value) {
      if (value === 0) return "$0";
      if (Math.abs(value - Math.round(value)) < 1e-6) return "$" + Math.round(value);
      return "$" + value.toFixed(2);
    }
    var en = (document.documentElement.lang || "").toLowerCase().indexOf("en") === 0;
    var text = (en ? "Plans " : "套餐 ") + items.length + (en ? " · in stock " : " · 有货 ") + instock + (en ? " · providers " : " · 商家 ") + Object.keys(providers).length;
    var enStats = (document.documentElement.lang || "").toLowerCase().indexOf("en") === 0;
    if (paid.length && paid.length !== months.length) text += (enStats ? " · paid monthly from " : " · 付费月价起 ") + usd(Math.min.apply(null, paid)) + (enStats ? " (a free tier also exists)" : "（另有免费档）");
    else if (months.length) text += (enStats ? " · monthly from " : " · 月价起 ") + usd(Math.min.apply(null, months));
    stats.textContent = text;
  }

  function render() {
    list.replaceChildren();
    if (!matched.length) {
      list.appendChild(el("p", "offer-empty", uiEn ? "No plans match. Widen the filters. Unknown RAM or vCPU is excluded when a minimum is set." : "没有符合条件的套餐。可以放宽筛选。设了内存或 vCPU 下限时，未知配置会被排除。"));
    } else {
      var start = (page - 1) * PAGE;
      matched.slice(start, start + PAGE).forEach(function (offer) { list.appendChild(card(offer)); });
    }
    var pages = Math.max(1, Math.ceil(matched.length / PAGE));
    var pager = document.getElementById("offer-pager");
    pager.hidden = matched.length <= PAGE;
    document.getElementById("offer-page").textContent = page + " / " + pages;
    document.getElementById("offer-prev").disabled = page <= 1;
    document.getElementById("offer-next").disabled = page >= pages;
    renderStats(matched);
  }

  function writeUrl() {
    var filter = readForm();
    var params = new URLSearchParams();
    if (filter.q) params.set("q", filter.q);
    if (filter.region && filter.region !== (app.dataset.region || "")) params.set("region", filter.region);
    else if (!app.dataset.region && filter.region) params.set("region", filter.region);
    if (filter.line && filter.line !== (app.dataset.line || "")) params.set("line", filter.line);
    if (filter.provider && filter.provider !== (app.dataset.provider || "")) params.set("provider", filter.provider);
    if (filter.period) params.set("period", filter.period);
    if (filter.stock) params.set("stock", filter.stock);
    if (filter.band) params.set("price", filter.band);
    if (filter.min !== "") params.set("minPrice", filter.min);
    if (filter.max !== "") params.set("maxPrice", filter.max);
    if (filter.minRam !== "") params.set("minRam", filter.minRam);
    if (filter.minCpu !== "") params.set("minCpu", filter.minCpu);
    if (filter.sort && filter.sort !== "updated") params.set("sort", filter.sort);
    var query = params.toString();
    history.replaceState(null, "", query ? "?" + query : location.pathname);
  }

  function refresh(resetPage) {
    if (resetPage) page = 1;
    var filter = readForm();
    matched = sortOffers(offers.filter(function (offer) { return match(offer, filter); }), filter.sort);
    render();
    writeUrl();
  }

  document.getElementById("servers-filters").addEventListener("input", function () { refresh(true); });
  document.getElementById("servers-filters").addEventListener("change", function () { refresh(true); });
  document.getElementById("f-reset").addEventListener("click", function () {
    fields.forEach(function (id) {
      var node = document.getElementById(id);
      node.value = id === "f-sort" ? "updated" : "";
    });
    if (app.dataset.region) document.getElementById("f-region").value = app.dataset.region;
    if (app.dataset.line) document.getElementById("f-line").value = app.dataset.line;
    if (app.dataset.provider) document.getElementById("f-provider").value = app.dataset.provider;
    refresh(true);
  });
  document.getElementById("offer-prev").addEventListener("click", function () {
    if (page > 1) { page -= 1; render(); list.scrollIntoView({ block: "start" }); }
  });
  document.getElementById("offer-next").addEventListener("click", function () {
    var pages = Math.ceil(matched.length / PAGE);
    if (page < pages) { page += 1; render(); list.scrollIntoView({ block: "start" }); }
  });

  fetch("/offers.json")
    .then(function (response) { if (!response.ok) throw new Error("offers"); return response.json(); })
    .then(function (data) {
      offers = data.offers || [];
      var note = document.querySelector(".servers-js-note");
      if (note) note.hidden = true;
      applyInitial();
      refresh(true);
    })
    .catch(function () {
      var note = document.querySelector(".servers-js-note");
      if (note) note.textContent = "套餐数据没有加载成功。下面仍是本页预先生成的最多 48 条。";
    });
})();
