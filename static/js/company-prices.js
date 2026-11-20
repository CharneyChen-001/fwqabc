(function () {
  var root = document.querySelector("[data-co-prices]");
  if (!root) return;
  var q = root.querySelector("[data-co-q]");
  var g = root.querySelector("[data-co-g]");
  var count = root.querySelector("[data-co-count]");
  var cards = Array.prototype.slice.call(root.querySelectorAll("[data-co-item]"));
  var groups = Array.prototype.slice.call(root.querySelectorAll("[data-co-group]"));
  function apply() {
    var query = (q.value || "").trim().toLowerCase();
    var group = g.value;
    var n = 0;
    cards.forEach(function (card) {
      var okG = !group || card.getAttribute("data-group") === group;
      var hay = card.getAttribute("data-search") || "";
      var okQ = !query || hay.indexOf(query) !== -1;
      var show = okG && okQ;
      card.hidden = !show;
      if (show) n += 1;
    });
    groups.forEach(function (sec) {
      var any = Array.prototype.some.call(sec.querySelectorAll("[data-co-item]"), function (card) {
        return !card.hidden;
      });
      sec.hidden = !any;
    });
    if (count) count.textContent = String(n);
  }
  q.addEventListener("input", apply);
  g.addEventListener("change", apply);
  root.querySelector("[data-co-reset]").addEventListener("click", function () {
    q.value = "";
    g.value = "";
    apply();
  });
})();
