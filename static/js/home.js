    (function () {
      var root = document.getElementById("how-it-works");
      if (!root) return;

      var tabs = root.querySelectorAll("[data-audience-tab]");
      var flows = root.querySelectorAll("[data-flow]");

      function showFlow(name) {
        tabs.forEach(function (t) {
          t.setAttribute("aria-selected", String(t.dataset.audienceTab === name));
        });
        flows.forEach(function (f) { f.hidden = f.dataset.flow !== name; });
      }
      tabs.forEach(function (t) {
        t.addEventListener("click", function () { showFlow(t.dataset.audienceTab); });
      });

      flows.forEach(function (flow) {
        var nodes = flow.querySelectorAll("[data-step]");
        var panels = flow.querySelectorAll("[data-panel]");
        function select(n) {
          nodes.forEach(function (x) { x.setAttribute("aria-selected", String(x.dataset.step === n)); });
          panels.forEach(function (p) { p.hidden = p.dataset.panel !== n; });
        }
        nodes.forEach(function (x) {
          x.addEventListener("click", function () { select(x.dataset.step); });
        });
        select("1");
      });

      showFlow("seeker");
    })();