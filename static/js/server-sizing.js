(function () {
  var form = document.getElementById("sizing-form");
  var out = document.getElementById("sizing-result");
  if (!form || !out || !window.SizingRules) return;
  var en = (document.documentElement.lang || "").toLowerCase().indexOf("en") === 0;

  function text(key, extra) {
    var zh = {
      workload: "请选择一种工作负载。",
      pageviews: "月访问量要是 0 到 10000000 的整数，或者留空。",
      "pageviews-range": "超过 10000000 次/月已经超出这张表，不给配置。",
      rps: "峰值请求要是 0 到 1000 的整数，或者留空。",
      "rps-range": "超过 1000 次/秒已经超出这张表，不估计集群。",
      floor: "这是该类型的起步下限。",
      "static-views": "静态站月访问量超过 100000 次时，内存下限提到 2 GB。这是缓存假设，不是压测。",
      "cms-views": "CMS 月访问量超过 50000 次时，下限提到 2 vCPU / 4 GB。这是假设，不是压测。",
      "api-ignores-views": "API 这张表不使用月访问量，只使用每秒请求。",
      "api-rps-20": "API 峰值超过 20 次/秒时，内存下限提到 4 GB。",
      "api-top": "API 峰值超过 100 次/秒时，表内上限是单机 4 vCPU / 8 GB，不估计多机。"
    };
    var dict = {
      workload: "Choose a workload.",
      pageviews: "Monthly page views must be an integer from 0 to 10000000, or blank.",
      "pageviews-range": "Above 10,000,000 page views per month is outside this sheet. No size is given.",
      rps: "Peak requests must be an integer from 0 to 1000 per second, or blank.",
      "rps-range": "Above 1000 requests/second is outside this sheet. It does not estimate a cluster.",
      floor: "This is the floor for that workload.",
      "static-views": "Above 100,000 monthly page views, the static-site RAM floor becomes 2 GB. That is a cache assumption, not a benchmark.",
      "cms-views": "Above 50,000 monthly page views, the CMS floor becomes 2 vCPU / 4 GB. That is an assumption, not a benchmark.",
      "api-ignores-views": "For API, this sheet ignores page views and uses requests per second only.",
      "api-rps-20": "Above 20 requests/second, the API RAM floor becomes 4 GB.",
      "api-top": "Above 100 requests/second, the sheet stops at one machine with 4 vCPU / 8 GB. It does not estimate multiple machines."
    };
    return (en ? dict : zh)[key] || extra || key;
  }

  function render(result) {
    out.classList.remove("is-error");
    if (!result.ok) {
      out.classList.add("is-error");
      out.textContent = text(result.error);
      return;
    }
    var intro = en
      ? "Floor: at least " + result.vcpu + " vCPU and " + result.ramGb + " GB RAM. This is not a benchmark and does not promise the server will hold your traffic."
      : "起步：至少 " + result.vcpu + " vCPU、" + result.ramGb + " GB 内存。这不是压测结果，也不保证扛得住你的流量。";
    var notes = result.notes.map(text).join(" ");
    var href = (en ? "/en" : "") + "/servers/?minCpu=" + result.vcpu + "&minRam=" + result.ramGb + "&sort=price-asc";
    var link = en ? "Show catalog plans at or above this RAM and vCPU" : "查看目录里不低于该内存和 vCPU 的套餐";
    var caveat = en
      ? "Plans with unknown RAM or vCPU are omitted from that filter. Prices are catalog snapshots."
      : "内存或 vCPU 未知的套餐不会出现在这个筛选里。价格仍是目录快照。";
    out.replaceChildren();
    out.appendChild(document.createTextNode(intro + " "));
    var list = document.createElement("ul");
    result.notes.forEach(function (note) {
      var li = document.createElement("li");
      li.textContent = text(note);
      list.appendChild(li);
    });
    out.appendChild(list);
    var a = document.createElement("a");
    a.href = href;
    a.textContent = link;
    out.appendChild(a);
    var p = document.createElement("p");
    p.textContent = caveat;
    out.appendChild(p);
    if (!notes) return;
  }

  form.addEventListener("submit", function (event) {
    event.preventDefault();
    var data = new FormData(form);
    render(window.SizingRules.estimate({
      workload: data.get("workload"),
      pageviews: data.get("pageviews"),
      rps: data.get("rps")
    }));
  });
})();
