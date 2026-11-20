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

  var modal = root.querySelector("[data-co-modal]");
  if (!modal) return;
  var dialog = modal.querySelector(".co-dialog");
  var title = modal.querySelector("#co-modal-title");
  var mail = modal.querySelector("[data-co-mail]");
  var copyBtn = modal.querySelector("[data-co-copy]");
  var copyStatus = modal.querySelector("[data-co-copy-status]");
  var lastFocus = null;
  var copyTimer = 0;

  function focusables() {
    return Array.prototype.filter.call(
      dialog.querySelectorAll("a[href], button:not([disabled])"),
      function (el) { return !el.closest("[hidden]"); }
    );
  }

  function openModal(trigger) {
    var name = trigger.getAttribute("data-ask-name") || "";
    title.textContent = (title.getAttribute("data-prefix") || "") + name;
    if (mail) mail.setAttribute("href", trigger.getAttribute("href"));
    if (copyStatus) copyStatus.textContent = "";
    lastFocus = trigger;
    modal.hidden = false;
    document.body.classList.add("co-modal-open");
    dialog.focus();
  }

  function closeModal() {
    if (modal.hidden) return;
    modal.hidden = true;
    document.body.classList.remove("co-modal-open");
    if (lastFocus && typeof lastFocus.focus === "function") lastFocus.focus();
  }

  root.addEventListener("click", function (event) {
    var ask = event.target.closest("a.co-ask");
    if (!ask || ask.hasAttribute("data-co-mail") || !root.contains(ask)) return;
    event.preventDefault();
    openModal(ask);
  });

  modal.addEventListener("click", function (event) {
    if (event.target.closest("[data-co-close]")) closeModal();
  });

  document.addEventListener("keydown", function (event) {
    if (modal.hidden) return;
    if (event.key === "Escape") {
      event.preventDefault();
      closeModal();
      return;
    }
    if (event.key !== "Tab") return;
    var items = focusables();
    if (!items.length) return;
    var first = items[0];
    var last = items[items.length - 1];
    if (event.shiftKey && (document.activeElement === first || document.activeElement === dialog)) {
      event.preventDefault();
      last.focus();
    } else if (!event.shiftKey && document.activeElement === last) {
      event.preventDefault();
      first.focus();
    }
  });

  if (copyBtn) {
    copyBtn.addEventListener("click", function () {
      var email = copyBtn.getAttribute("data-email") || "";
      var done = copyBtn.getAttribute("data-copied") || "";
      function show() {
        if (!copyStatus) return;
        copyStatus.textContent = done;
        window.clearTimeout(copyTimer);
        copyTimer = window.setTimeout(function () { copyStatus.textContent = ""; }, 2000);
      }
      function fallback() {
        var area = document.createElement("textarea");
        area.value = email;
        area.setAttribute("readonly", "");
        area.style.position = "fixed";
        area.style.left = "-999px";
        document.body.appendChild(area);
        area.select();
        try { document.execCommand("copy"); show(); } catch (err) { if (copyStatus) copyStatus.textContent = email; }
        area.remove();
      }
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(email).then(show).catch(fallback);
      } else {
        fallback();
      }
    });
  }
})();
