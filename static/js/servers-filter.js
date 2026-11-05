(function () {
  var app = document.getElementById("servers-app");
  var list = document.getElementById("offer-list");
  if (!app || !list) return;
  var PAGE = 24;
  var offers = [];
  var matched = [];
  var page = 1;
  var fields = ["f-q", "f-region", "f-line", "f-price", "f-min", "f-max", "f-period", "f-stock", "f-provider", "f-sort"];

  function readForm() {
    return {
      q: document.getElementById("f-q").value.trim(),
      region: document.getElementById("f-region").value,
      line: document.getElementById("f-line").value,
      band: document.getElementById("f-price").value,
      min: document.getElementById("f-min").value,
      max: document.getElementById("f-max").value,
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

  function stockNode(offer) {
    if (offer.stock === "in") return el("span", "stock stock-in", offer.stock_label || "有货");
    if (offer.stock === "out") return el("span", "stock stock-out", offer.stock_label || "缺货");
    return el("span", "stock stock-unknown", "库存未核实");
  }

  function card(offer) {
    var article = el("article", "offer-card");
    var top = el("div", "offer-top");
    top.appendChild(el("h3", "", offer.name || "未命名套餐"));
    top.appendChild(stockNode(offer));
    article.appendChild(top);
    var meta = el("p", "offer-meta");
    meta.appendChild(el("span", "", offer.provider || ""));
    if (offer.kind) meta.appendChild(el("span", "", offer.kind));
    if (offer.promo_code) meta.appendChild(el("span", "promo-code", "优惠码 " + offer.promo_code));
    article.appendChild(meta);
    var price = el("p", "offer-price");
    price.appendChild(el("b", offer.price_text ? "" : "is-muted", offer.price_text || "价格待核实"));
    if (offer.period_label) price.appendChild(el("span", "", offer.period_label));
    if (offer.monthly_basis === "period_divided" && offer.monthly_usd != null) {
      price.appendChild(el("small", "", "折合 $" + Number(offer.monthly_usd).toFixed(2) + "/月"));
    }
    if (offer.period === "hourly" && offer.hourly_text) price.appendChild(el("small", "", offer.hourly_text + "/小时"));
    article.appendChild(price);
    var where = [offer.region, offer.city, offer.line].filter(Boolean).join(" · ");
    article.appendChild(el("p", "offer-where", where || "地区与线路待核实"));
    article.appendChild(el("p", "offer-specs", offer.specs || "配置待核实"));
    if (offer.location_note) article.appendChild(el("p", "offer-note", offer.location_note));
    var foot = el("div", "offer-foot");
    if (offer.checked_on) {
      var time = el("time", "", "核实 " + offer.checked_on);
      time.dateTime = offer.checked_on;
      foot.appendChild(time);
    } else {
      foot.appendChild(el("span", "", "核实日期待核实"));
    }
    if (offer.aff_slug || offer.buy_url) {
      var link = el("a", "go-btn", "购买");
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
    var text = "套餐 " + items.length + " · 有货 " + instock + " · 商家 " + Object.keys(providers).length;
    if (paid.length && paid.length !== months.length) text += " · 付费月价起 " + usd(Math.min.apply(null, paid)) + "（另有免费档）";
    else if (months.length) text += " · 月价起 " + usd(Math.min.apply(null, months));
    stats.textContent = text;
  }

  function render() {
    list.replaceChildren();
    if (!matched.length) {
      list.appendChild(el("p", "offer-empty", "没有符合条件的套餐。可以放宽筛选，或去商家目录看原始报价。"));
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
