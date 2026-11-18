// Top Employers: continuous, smooth logo marquee (Swiper.js)
(function () {
  function initEmployersSwiper() {
    var el = document.querySelector(".employers-swiper");
    if (!el || typeof Swiper === "undefined") return;

    var wrapper = el.querySelector(".swiper-wrapper");
    var originals = Array.prototype.slice
      .call(wrapper.children)
      .filter(function (s) {
        return s.offsetWidth > 0; // ignore slides hidden by onerror (missing images)
      });
    if (!originals.length) return;

    var gap = 48; // same as spaceBetween below
    var setWidth = originals.reduce(function (sum, s) {
      return sum + s.offsetWidth + gap;
    }, 0);

    // Only 1-3 logos that already fit: show them once, no sliding
    // (otherwise one logo is repeated across the whole row).
    // CHANGED: 4 or more logos always slide.
    if (originals.length < 4 && setWidth <= el.clientWidth) {
      new Swiper(el, {
        slidesPerView: "auto",
        spaceBetween: gap,
        loop: false,
        allowTouchMove: false,
        autoplay: false,
      });
      return;
    }

    // CHANGED: at least 1 extra copy, so there is always something to loop into
    var copies = Math.max(1, Math.ceil((el.clientWidth * 2) / setWidth));
    for (var i = 0; i < copies; i++) {
      originals.forEach(function (s) {
        var clone = s.cloneNode(true);
        clone.setAttribute("aria-hidden", "true");
        clone.querySelectorAll("a").forEach(function (a) {
          a.setAttribute("tabindex", "-1");
        });
        wrapper.appendChild(clone);
      });
    }

    var reduceMotion = window.matchMedia(
      "(prefers-reduced-motion: reduce)"
    ).matches;

    var swiper = new Swiper(el, {
      loop: true,
      slidesPerView: "auto",
      spaceBetween: gap,
      freeMode: true,
      speed: 6000,
      allowTouchMove: false,
      autoplay: reduceMotion
        ? false
        : {
            delay: 0,
            disableOnInteraction: false,
          },
    });

    if (!reduceMotion) {
      el.addEventListener("mouseenter", function () {
        swiper.autoplay.stop();
      });
      el.addEventListener("mouseleave", function () {
        swiper.autoplay.start();
      });
    }
  }

  // 'load' (not DOMContentLoaded) so logo slides have their final width
  if (document.readyState === "complete") initEmployersSwiper();
  else window.addEventListener("load", initEmployersSwiper);
})();