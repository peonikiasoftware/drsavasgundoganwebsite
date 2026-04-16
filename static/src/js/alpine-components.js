/**
 * Alpine.js components registered on alpine:init.
 * Loaded from base.html after Alpine core.
 */

document.addEventListener('alpine:init', () => {
  /* ---------- Reveal-on-scroll directive --------------------------
     Usage: <div x-data x-intersect:enter="...">  OR
            class="reveal" + the reveal() watcher below.
  ------------------------------------------------------------------ */
  Alpine.data('reveal', () => ({
    shown: false,
    init() {
      const io = new IntersectionObserver((entries) => {
        entries.forEach((e) => {
          if (e.isIntersecting) { this.shown = true; io.unobserve(e.target); }
        });
      }, { threshold: 0.15 });
      io.observe(this.$el);
    },
  }));

  /* ---------- Counter animation ---------------------------------- */
  Alpine.data('counter', (target, { duration = 1600 } = {}) => ({
    current: 0,
    target,
    started: false,
    init() {
      const io = new IntersectionObserver((entries) => {
        entries.forEach((e) => {
          if (e.isIntersecting && !this.started) {
            this.started = true;
            this.animate(duration);
            io.unobserve(e.target);
          }
        });
      }, { threshold: 0.3 });
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
    embedCode: '',
    show(src, embedCode = '') {
      this.src = src || '';
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
