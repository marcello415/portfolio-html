// Load Google Analytics only after a real visitor interacts with the page.
// Link scanners and bots that just load the page never trigger these events,
// so they don't get counted as visits.
(function () {
    var loaded = false;
    var events = ['scroll', 'mousemove', 'touchstart', 'keydown', 'click'];

    function loadGA() {
        if (loaded) return;
        loaded = true;
        events.forEach(function (e) {
            window.removeEventListener(e, loadGA, true);
        });
        var s = document.createElement('script');
        s.async = true;
        s.src = 'https://www.googletagmanager.com/gtag/js?id=G-LQWW2RXWQE';
        document.head.appendChild(s);
    }

    events.forEach(function (e) {
        window.addEventListener(e, loadGA, { passive: true, capture: true });
    });
})();
