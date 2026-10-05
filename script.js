document.documentElement.classList.add('js');
document.getElementById('yr').textContent = new Date().getFullYear();

// Mobile menu
const burger = document.querySelector('.burger');
const menu = document.getElementById('menu');
const setMenu = open => {
  menu.classList.toggle('open', open);
  burger.setAttribute('aria-expanded', open);
};
burger.addEventListener('click', () => setMenu(!menu.classList.contains('open')));
menu.querySelectorAll('a').forEach(a => a.addEventListener('click', () => setMenu(false)));

// Fade-in on scroll
const items = document.querySelectorAll('.sec h2, .card, .why > div, .steps li, .slot, .quote, .cta .wrap');
items.forEach(el => el.classList.add('reveal'));
if ('IntersectionObserver' in window) {
  const io = new IntersectionObserver(entries => entries.forEach(e => {
    if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); }
  }), { threshold: 0.12 });
  items.forEach(el => io.observe(el));
} else items.forEach(el => el.classList.add('in'));

// Contact form validation
const form = document.getElementById('form');
const status = document.getElementById('status');
const rules = {
  name: v => v.trim().length >= 2 || 'Enter your name.',
  phone: v => /^(\+?234|0)\d{10}$/.test(v.replace(/[\s-]/g, '')) || 'Enter a valid Nigerian phone number, e.g. 09012345678.',
  email: v => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v) || 'Enter a valid email address.',
  service: v => v !== '' || 'Select a service.',
  message: v => v.trim().length >= 5 || 'Tell us a little about what you need.'
};

form.addEventListener('submit', async e => {
  e.preventDefault();
  status.className = 'status';
  status.textContent = '';
  let ok = true;
  form.querySelectorAll('.err').forEach(n => n.remove());
  for (const [name, check] of Object.entries(rules)) {
    const field = form.elements[name];
    const res = check(field.value);
    field.classList.toggle('invalid', res !== true);
    if (res !== true) {
      ok = false;
      const m = document.createElement('span');
      m.className = 'err';
      m.textContent = res;
      field.after(m);
    }
  }
  if (!ok) return;

  // Not connected yet: see instructions to add a free form service
  if (form.action.includes('YOUR_FORM_ID')) {
    status.textContent = 'Form checked. It is not connected to an email service yet, so nothing was sent. Please call 09049811269.';
    return;
  }
  try {
    const r = await fetch(form.action, { method: 'POST', body: new FormData(form), headers: { Accept: 'application/json' } });
    if (!r.ok) throw new Error();
    form.reset();
    status.className = 'status ok';
    status.textContent = 'Thank you. Your request has been sent. We will contact you soon.';
  } catch {
    status.textContent = 'Could not send your request. Please call 09049811269.';
  }
});
