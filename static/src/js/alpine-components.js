/**
 * Alpine.js components registered on alpine:init.
 * Loaded from base.html after Alpine core.
 */

/* ------------------------------------------------------------------
   Global reveal-on-scroll for elements with class="js-reveal".
   Mobile-safe:
     • rootMargin pulls the trigger point above the fold so content
       reveals as it scrolls in, not only after 15% is visible.
     • threshold array + low min => works on short mobile screens too.
     • Respects prefers-reduced-motion via CSS (see input.css).
-------------------------------------------------------------------- */
(function initReveal() {
  const run = () => {
    const els = document.querySelectorAll('.js-reveal:not(.is-visible)');
    if (!('IntersectionObserver' in window) || !els.length) {
      els.forEach((el) => el.classList.add('is-visible'));
      return;
    }
    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((e) => {
          if (e.isIntersecting) {
            e.target.classList.add('is-visible');
            io.unobserve(e.target);
          }
        });
      },
      { threshold: 0.08, rootMargin: '0px 0px -8% 0px' }
    );
    els.forEach((el) => io.observe(el));
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', run, { once: true });
  } else {
    run();
  }

  // Re-scan after HTMX swaps so new content animates in.
  document.body.addEventListener?.('htmx:afterSwap', run);
})();

document.addEventListener('alpine:init', () => {
  /* ---------- Reveal-on-scroll directive (Alpine wrapper) --------
     Legacy API used via x-data="reveal" :class="shown && '...'".
     Retained for backward compatibility.
  ------------------------------------------------------------------ */
  Alpine.data('reveal', () => ({
    shown: false,
    init() {
      const io = new IntersectionObserver(
        (entries) => {
          entries.forEach((e) => {
            if (e.isIntersecting) { this.shown = true; io.unobserve(e.target); }
          });
        },
        { threshold: 0.08, rootMargin: '0px 0px -8% 0px' }
      );
      io.observe(this.$el);
    },
  }));

  /* ---------- Counter animation ---------------------------------- */
  Alpine.data('counter', (target, { duration = 1600 } = {}) => ({
    current: 0,
    target,
    started: false,
    init() {
      const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
      if (reduce) { this.current = this.target; this.started = true; return; }
      const io = new IntersectionObserver(
        (entries) => {
          entries.forEach((e) => {
            if (e.isIntersecting && !this.started) {
              this.started = true;
              this.animate(duration);
              io.unobserve(e.target);
            }
          });
        },
        { threshold: 0.15, rootMargin: '0px 0px -10% 0px' }
      );
      io.observe(this.$el);
    },
    animate(duration) {
      const start = performance.now();
      const from = 0, to = this.target;
      const tick = (now) => {
        const t = Math.min(1, (now - start) / duration);
        // easeOutCubic
        const eased = 1 - Math.pow(1 - t, 3);
        this.current = Math.round(from + (to - from) * eased);
        if (t < 1) requestAnimationFrame(tick);
      };
      requestAnimationFrame(tick);
    },
  }));

  /* ---------- Video modal ---------------------------------------- */
  Alpine.data('videoModal', () => ({
    open: false,
    src: '',
    portrait: true,      // 9:16 by default (Instagram reel)
    embedCode: '',
    show(src, portrait = true, embedCode = '') {
      this.src = src || '';
      this.portrait = !!portrait;
      this.embedCode = embedCode || '';
      this.open = true;
      document.body.classList.add('overflow-hidden');
    },
    hide() {
      this.open = false;
      this.src = '';
      this.embedCode = '';
      document.body.classList.remove('overflow-hidden');
    },
  }));

  /* ---------- Abstract modal ------------------------------------- */
  Alpine.data('abstractModal', () => ({
    open: false,
    title: '',
    body: '',
    apa: '',
    link: '',
    pubmed: '',
    show(payload) {
      Object.assign(this, payload);
      this.open = true;
      document.body.classList.add('overflow-hidden');
    },
    hide() {
      this.open = false;
      document.body.classList.remove('overflow-hidden');
    },
  }));

  /* ---------- Cookie banner -------------------------------------- */
  Alpine.data('cookieBanner', () => ({
    accepted: true,
    init() {
      try {
        this.accepted = localStorage.getItem('cookieAccepted') === '1';
      } catch (_) { this.accepted = true; }
    },
    accept() {
      try { localStorage.setItem('cookieAccepted', '1'); } catch (_) {}
      this.accepted = true;
    },
  }));

  /* ---------- Mobile nav ----------------------------------------- */
  Alpine.data('mobileNav', () => ({
    open: false,
    toggle() {
      this.open = !this.open;
      document.body.classList.toggle('overflow-hidden', this.open);
    },
    close() {
      this.open = false;
      document.body.classList.remove('overflow-hidden');
    },
  }));

  /* ---------- Header scroll shadow ------------------------------- */
  Alpine.data('headerShadow', () => ({
    scrolled: false,
    init() {
      const update = () => { this.scrolled = window.scrollY > 12; };
      update();
      window.addEventListener('scroll', update, { passive: true });
    },
  }));
});
