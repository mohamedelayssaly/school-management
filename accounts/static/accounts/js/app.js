document.addEventListener('DOMContentLoaded', function () {
    var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  
    document.querySelectorAll('[data-count]').forEach(function (el) {
      var target = parseInt(el.getAttribute('data-count'), 10);
      if (isNaN(target) || reduce) { return; }
      var start = null;
      function step(timestamp) {
        if (start === null) { start = timestamp; }
        var progress = Math.min((timestamp - start) / 900, 1);
        el.textContent = Math.round(target * (1 - Math.pow(1 - progress, 3)));
        if (progress < 1) { requestAnimationFrame(step); }
      }
      el.textContent = '0';
      requestAnimationFrame(step);
    });
  
    var toggle = document.getElementById('menu-toggle');
    if (toggle) {
      toggle.addEventListener('click', function () {
        document.body.classList.toggle('menu-open');
      });
    }
  });