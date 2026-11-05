(function () {
  var root = document.getElementById("knowledge-list");
  if (!root) return;
  var cards = Array.prototype.slice.call(root.querySelectorAll("[data-knowledge]"));
  var groups = Array.prototype.slice.call(root.querySelectorAll("[data-knowledge-group]"));
  var search = document.getElementById("knowledge-q");
  var chips = Array.prototype.slice.call(document.querySelectorAll("[data-knowledge-filter]"));
  var current = "";

  function apply() {
    var query = (search && search.value || "").trim().toLowerCase();
    cards.forEach(function (card) {
      var typeOk = !current || card.getAttribute("data-knowledge") === current;
      var text = (card.getAttribute("data-text") || "").toLowerCase();
      card.hidden = !(typeOk && (!query || text.indexOf(query) !== -1));
    });
    groups.forEach(function (group) {
      var visible = group.querySelector("[data-knowledge]:not([hidden])");
      group.hidden = !visible;
    });
  }

  chips.forEach(function (chip) {
    chip.addEventListener("click", function () {
      current = chip.getAttribute("data-knowledge-filter") || "";
      chips.forEach(function (item) { item.classList.toggle("is-on", item === chip); });
      apply();
    });
  });
  if (search) search.addEventListener("input", apply);
})();
