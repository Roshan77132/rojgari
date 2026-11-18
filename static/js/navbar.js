(function () {
  var btn = document.getElementById("menu-btn");
  var menu = document.getElementById("mobile-menu");
  var iconOpen = document.getElementById("icon-open");
  var iconClose = document.getElementById("icon-close");
  if (!btn || !menu) return;
  btn.addEventListener("click", function () {
    var hidden = menu.classList.toggle("hidden");
    iconOpen.classList.toggle("hidden", !hidden);
    iconClose.classList.toggle("hidden", hidden);
    btn.setAttribute("aria-expanded", String(!hidden));
  });
})();