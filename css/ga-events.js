// Click tracking for Google Analytics.
// Events wait in the dataLayer until ga-load.js loads GA on the first interaction.
(function () {
    function send(name, params) {
        if (typeof gtag !== 'function') return;
        params.transport_type = 'beacon';
        gtag('event', name, params);
    }

    // Track folder this page is in: web, email, ops, marketing, admin, ai, or home
    var parts = location.pathname.split('/');
    var tracks = ['web', 'email', 'ops', 'marketing', 'admin', 'ai'];
    var track = 'home';
    parts.forEach(function (p) {
        if (tracks.indexOf(p) !== -1) track = p;
    });
    var page = (parts.pop() || 'index.html').replace('.html', '');

    document.addEventListener('click', function (e) {
        var a = e.target.closest ? e.target.closest('a[href]') : null;
        if (!a) return;
        var href = a.getAttribute('href');

        // Hub: which portfolio they picked
        if (a.dataset.track) {
            send('choose_track', { track: a.dataset.track });
            return;
        }

        // LinkedIn, from any page
        if (href.indexOf('linkedin.com') !== -1) {
            send('linkedin_click', { track: track, page: page });
            return;
        }

        // Track home: opening a case study
        if (href.indexOf('work/') === 0) {
            send('open_case_study', {
                track: track,
                case_study: href.replace('work/', '').replace('.html', '')
            });
            return;
        }

        // Case study: "See the work" links
        if (a.closest('.cs-body .links')) {
            send('see_work', {
                track: track,
                case_study: page,
                link_url: a.href,
                link_text: a.textContent.replace(/[\u2197\s]+$/, '').trim()
            });
        }
    });
})();
