gsap.registerPlugin(ScrollTrigger);

/* Lenis setup */
try {
  const lenis = new Lenis({ duration: 1.1, smoothWheel: true });
  lenis.on('scroll', ScrollTrigger.update);
  gsap.ticker.add((t) => lenis.raf(t * 1000));
  gsap.ticker.lagSmoothing(0);
} catch (e) {}

/* Nav on scroll */
const nav = document.getElementById('nav');
ScrollTrigger.create({
  start: 'top -56',
  onUpdate(self) { nav.classList.toggle('scrolled', self.progress > 0); },
});

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

/* Section reveals */
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
