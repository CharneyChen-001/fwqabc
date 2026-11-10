(function () {
  var form = document.getElementById("lines-form");
  var out = document.getElementById("lines-result");
  if (!form || !out || !window.NetworkRules) return;
  var en = (document.documentElement.lang || "").toLowerCase().indexOf("en") === 0;
  var prefix = en ? "/en" : "";

  function link(href, label) {
    var a = document.createElement("a");
    a.href = href;
    a.textContent = label;
    return a;
  }

  function render(id) {
    out.classList.remove("is-error");
    out.replaceChildren();
    var p = document.createElement("p");
    if (id === "cn2-gia") {
      p.textContent = en
        ? "The CN2 GIA page says this line is China Telecom CN2 (AS4809), usually more expensive, for sites whose visitors are mainly in China. This tool does not add a speed claim."
        : "CN2 GIA 线路页写的是：它一般指走中国电信 CN2（AS4809）的高等级线路，通常更贵，适合访客主要在国内的网站。这里不补充速度数据。";
      out.appendChild(p);
      out.appendChild(link(prefix + "/routes/cn2-gia/", en ? "CN2 GIA note" : "CN2 GIA 说明"));
      out.appendChild(document.createTextNode(" "));
      out.appendChild(link(prefix + "/servers/lines/cn2-gia/", en ? "Plans tagged CN2 GIA" : "目录里标明 CN2 GIA 的套餐"));
      return;
    }
    if (id === "as9929") {
      p.textContent = en
        ? "The 9929 page says AS9929 is a China Unicom backbone and is usually described as friendlier for Unicom visitors. The catalog does not currently tag AS9929 offers, so there is no line filter."
        : "9929 线路页写的是：AS9929 是联通高等级骨干，商家标注 9929 的方案通常对联通访客更友好。当前目录没有把套餐标成 AS9929，所以没有线路筛选。";
      out.appendChild(p);
      out.appendChild(link(prefix + "/routes/9929/", en ? "9929 note" : "9929 说明"));
      return;
    }
    if (id === "cmin2") {
      p.textContent = en
        ? "The CMIN2 page says it is China Mobile International, commonly AS58807, usually aimed at Mobile visitors. The catalog does not currently tag CMIN2 offers."
        : "CMIN2 线路页写的是：它是中国移动国际的线路，常见 AS58807，通常面向移动访客。当前目录没有把套餐标成 CMIN2。";
      out.appendChild(p);
      out.appendChild(link(prefix + "/routes/cmin2/", en ? "CMIN2 note" : "CMIN2 说明"));
      return;
    }
    if (id === "no-china-line") {
      p.textContent = en
        ? "These three notes are about return paths for visitors in mainland China. They do not say the same lines are useful when visitors are mostly elsewhere. No line is selected."
        : "这三篇线路说明谈的是面向中国大陆访客的回程。访客主要在大陆以外时，页面没有说该优先买这三条。这里不选线路。";
      out.appendChild(p);
      out.appendChild(link(prefix + "/servers/", en ? "Browse plans without a line filter" : "不按线路筛选，去看套餐"));
      return;
    }
    if (id === "unknown") {
      p.textContent = en
        ? "No line is selected. Read the three notes and match the carrier yourself. This tool will not guess."
        : "不确定就不选线路。请自己对照三篇说明，本工具不猜测。";
      out.appendChild(p);
      out.appendChild(link(prefix + "/routes/cn2-gia/", "CN2 GIA"));
      out.appendChild(document.createTextNode(" · "));
      out.appendChild(link(prefix + "/routes/9929/", "9929"));
      out.appendChild(document.createTextNode(" · "));
      out.appendChild(link(prefix + "/routes/cmin2/", "CMIN2"));
      return;
    }
    out.classList.add("is-error");
    out.textContent = en ? "Choose both fields." : "请把两项都选上。";
  }

  form.addEventListener("submit", function (event) {
    event.preventDefault();
    var data = new FormData(form);
    var result = window.NetworkRules.lookup({ isp: data.get("isp"), audience: data.get("audience") });
    render(result.ok ? result.id : "bad");
  });
})();
