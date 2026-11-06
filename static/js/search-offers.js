(function () {
  var input = document.getElementById("searchInput");
  var box = document.getElementById("offer-hits");
  var list = document.getElementById("offer-hit-list");
  var more = document.getElementById("offer-hit-more");
  if (!input || !box || !list) return;
  var offers = null;
  var loading = false;

  function el(tag, text) {
    var node = document.createElement(tag);
    if (text != null) node.textContent = text;
    return node;
  }

  function show(query) {
    if (!offers || query.length < 1) {
      box.hidden = true;
      list.replaceChildren();
      return;
    }
    var needle = query.toLowerCase();
    var hits = offers.filter(function (offer) {
      return [offer.name, offer.provider, offer.region, offer.city, offer.line, offer.promo_code, offer.kind, offer.specs].join(" ").toLowerCase().indexOf(needle) !== -1;
    }).slice(0, 6);
    list.replaceChildren();
    if (!hits.length) {
      box.hidden = true;
      return;
    }
    hits.forEach(function (offer) {
      var li = el("li");
      var link = document.createElement("a");
      var params = new URLSearchParams();
      params.set("q", query);
      if (offer.provider_slug) params.set("provider", offer.provider_slug);
      link.href = "/servers/?" + params.toString();
      var where = [offer.region, offer.line].filter(Boolean).join(" · ");
      link.textContent = (offer.provider || "") + " · " + (offer.name || "") + (where ? " · " + where : "") + (offer.price_text ? " · " + offer.price_text : "");
      li.appendChild(link);
      list.appendChild(li);
    });
    more.href = "/servers/?q=" + encodeURIComponent(query);
    box.hidden = false;
  }

  function ensure(query) {
    if (offers) {
      show(query);
      return;
    }
    if (loading) return;
    loading = true;
    fetch("/offers.json")
      .then(function (response) { return response.json(); })
      .then(function (data) {
        offers = data.offers || [];
        show(input.value.trim());
      })
      .catch(function () { loading = false; });
  }

  input.addEventListener("input", function () { ensure(input.value.trim()); });

  var params = new URLSearchParams(location.search);
  var initial = params.get("q");
  if (initial) {
    var tries = 0;
    var timer = setInterval(function () {
      tries += 1;
      if (!input.disabled) {
        if (input.value !== initial) input.value = initial;
        input.dispatchEvent(new Event("input", { bubbles: true }));
        ensure(initial);
      }
      var ready = document.querySelector("#searchResults li");
      if (ready || tries > 40) clearInterval(timer);
    }, 200);
  }
})();
