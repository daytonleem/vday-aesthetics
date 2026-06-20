const gsapOK = (typeof gsap !== 'undefined' && typeof ScrollTrigger !== 'undefined');
if (gsapOK) gsap.registerPlugin(ScrollTrigger);

/* Lenis setup */
if (gsapOK) {
  try {
    const lenis = new Lenis({ duration: 1.1, smoothWheel: true });
    lenis.on('scroll', ScrollTrigger.update);
    gsap.ticker.add((t) => lenis.raf(t * 1000));
    gsap.ticker.lagSmoothing(0);
  } catch (e) {}
}

/* Nav on scroll */
const nav = document.getElementById('nav');
if (gsapOK) {
  ScrollTrigger.create({
    start: 'top -56',
    onUpdate(self) { nav.classList.toggle('scrolled', self.progress > 0); },
  });
} else {
  window.addEventListener('scroll', () => {
    nav.classList.toggle('scrolled', window.scrollY > 56);
  });
}

/* Mobile nav dropdown */
const navToggle = document.getElementById('navToggle');
const navLinks = document.getElementById('navLinks');
if (navToggle && navLinks) {
  navToggle.addEventListener('click', () => {
    const isOpen = navLinks.classList.toggle('open');
    navToggle.classList.toggle('open', isOpen);
    navToggle.setAttribute('aria-expanded', isOpen);
  });
  navLinks.querySelectorAll('a').forEach((link) => {
    link.addEventListener('click', () => {
      navLinks.classList.remove('open');
      navToggle.classList.remove('open');
      navToggle.setAttribute('aria-expanded', 'false');
    });
  });
}

/* Hide the floating WhatsApp button once it would overlap the footer's own social icons */
const waFloat = document.querySelector('.wa-float');
const footer = document.getElementById('footer');
if (waFloat && footer) {
  const footerVisibilityObserver = new IntersectionObserver((entries) => {
    waFloat.classList.toggle('footer-visible', entries[0].isIntersecting);
  }, { rootMargin: '0px 0px -120px 0px' });
  footerVisibilityObserver.observe(footer);
}

/* FAQ accordion */
document.querySelectorAll('.faq-q').forEach((btn) => {
  btn.addEventListener('click', () => {
    const item = btn.closest('.faq-item');
    const isOpen = item.classList.contains('open');

    document.querySelectorAll('.faq-item.open').forEach((i) => {
      i.classList.remove('open');
      i.querySelector('.faq-q').setAttribute('aria-expanded', 'false');
      i.querySelector('.faq-a').style.maxHeight = '0px';
    });

    if (!isOpen) {
      item.classList.add('open');
      btn.setAttribute('aria-expanded', 'true');
      const answer = item.querySelector('.faq-a');
      answer.style.maxHeight = answer.scrollHeight + 'px';
    }
  });
});

/* Section reveals */
if (gsapOK) {
  document.querySelectorAll('.reveal').forEach((el) => {
    ScrollTrigger.create({
      trigger: el,
      start: 'top 90%',
      end: 'bottom top',
      onEnter()     { el.classList.add('in'); },
      onLeave()     { el.classList.remove('in'); },
      onEnterBack() { el.classList.add('in'); },
      onLeaveBack() { el.classList.remove('in'); },
    });
  });
} else {
  document.querySelectorAll('.reveal').forEach((el) => el.classList.add('in'));
}
