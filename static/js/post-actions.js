(function () {
  document.querySelectorAll("[data-copy-url]").forEach(function (button) {
    button.addEventListener("click", function () {
      var url = button.getAttribute("data-copy-url");
      var original = button.textContent;
      function done() {
        button.textContent = "已复制";
        setTimeout(function () { button.textContent = original; }, 2000);
      }
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(url).then(done).catch(function () { fallback(); });
        return;
      }
      fallback();
      function fallback() {
        var input = document.createElement("input");
        input.value = url;
        document.body.appendChild(input);
        input.select();
        try { document.execCommand("copy"); done(); } catch (error) { button.textContent = "复制失败"; }
        input.remove();
      }
    });
  });
})();
