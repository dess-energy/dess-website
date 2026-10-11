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
const items = document.querySelectorAll('.hero-in > div > *, .hero-media, .phero .wrap > *, .sec .eyebrow, .sec h2, .sec .big, .sec .sub, .sec .note, .sec .lead, .card, .why, .step, .tile, .shot, .case-v, .case-t > *, .quote, .stat, .chips > *, details, .clist li, .contact form, .cta h2, .cta p, .cta .btns');
const idx = new Map();
items.forEach(el => {
  el.classList.add('reveal');
  const n = idx.get(el.parentNode) || 0; idx.set(el.parentNode, n + 1);
  el.style.transitionDelay = Math.min(n, 5) * 70 + 'ms';
});
const show = el => { el.classList.add('in'); setTimeout(() => { el.style.transitionDelay = ''; }, 1200); };
if ('IntersectionObserver' in window) {
  const io = new IntersectionObserver(entries => entries.forEach(e => {
    if (e.isIntersecting) { show(e.target); io.unobserve(e.target); }
  }), { threshold: 0.08, rootMargin: '0px 0px -30px 0px' });
  items.forEach(el => io.observe(el));
} else items.forEach(show);

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

form && form.addEventListener('submit', async e => {
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

/* ===== v4 premium layer ===== */
(() => { // scroll progress
  const bar = document.querySelector('.progress'); if (!bar) return;
  const f = () => { const h = document.documentElement.scrollHeight - innerHeight; bar.style.width = (h > 0 ? scrollY / h * 100 : 0) + '%'; };
  addEventListener('scroll', () => requestAnimationFrame(f), { passive: true }); f();
})();
(() => { // headline word reveal
  const wrap = el => {
    let i = 0;
    const walk = n => [...n.childNodes].forEach(c => {
      if (c.nodeType === 3) {
        const f = document.createDocumentFragment();
        c.textContent.split(/(\s+)/).forEach(t => {
          if (!t) return;
          if (/^\s+$/.test(t)) f.appendChild(document.createTextNode(' '));
          else { const w = document.createElement('span'); w.className = 'w'; w.setAttribute('aria-hidden', 'true'); const s = document.createElement('span'); s.style.setProperty('--i', i++); s.textContent = t; w.appendChild(s); f.appendChild(w); }
        });
        n.replaceChild(f, c);
      } else if (c.nodeType === 1) walk(c);
    });
    el.setAttribute('aria-label', el.textContent.trim()); walk(el); el.classList.add('sx');
  };
  document.querySelectorAll('h1, .sec h2, .cta h2').forEach(wrap);
})();
(() => { // hero background slideshow + height up to the consultation button
  const hero = document.querySelector('.hero'); if (!hero) return;
  const im = [...hero.querySelectorAll('.hero-bg img')], dots = [...hero.querySelectorAll('.hero-dots i')], cap = hero.querySelector('.hero-dots .cap'); let k = 0;
  const go = n => { k = n % im.length; im.forEach((x, i) => x.classList.toggle('on', i === k)); dots.forEach((d, i) => { d.classList.remove('on'); if (i === k) { void d.offsetWidth; d.classList.add('on'); } }); if (cap) cap.textContent = im[k].dataset.cap; };
  go(0); setInterval(() => go(k + 1), 5000);
  const btn = hero.querySelector('.btn');
  const set = () => { const r = hero.getBoundingClientRect(); hero.style.setProperty('--bgh', Math.round(btn.getBoundingClientRect().bottom - r.top + 46) + 'px'); };
  set(); addEventListener('resize', set); addEventListener('load', set); setTimeout(set, 1500);
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(set);
})();
(() => { // count-up numbers
  const els = [...document.querySelectorAll('[data-count]')]; if (!els.length) return;
  if (matchMedia('(prefers-reduced-motion: reduce)').matches || !('IntersectionObserver' in window)) return;
  const run = el => { const n = +el.dataset.count, s = el.dataset.suffix || '', t0 = performance.now(); const f = t => { const p = Math.min((t - t0) / 1700, 1), e = 1 - Math.pow(1 - p, 3); el.textContent = Math.round(n * e) + s; if (p < 1) requestAnimationFrame(f); }; requestAnimationFrame(f); };
  els.forEach(e => { e.textContent = '0' + (e.dataset.suffix || ''); });
  const io = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) { run(e.target); io.unobserve(e.target); } }), { threshold: .6 });
  els.forEach(e => io.observe(e));
})();
(() => { // process highlight
  const li = [...document.querySelectorAll('.tl li')]; if (!li.length || !('IntersectionObserver' in window)) return;
  const io = new IntersectionObserver(es => es.forEach(e => e.target.classList.toggle('active', e.isIntersecting)), { rootMargin: '-38% 0px -38% 0px' });
  li.forEach(l => io.observe(l)); li[0].classList.add('active');
})();
(() => { // DESS assistant (free, answers only from approved DESS facts)
  const fab = document.querySelector('.wafab'), pop = document.getElementById('wapop'); if (!fab || !pop) return;
  const msgs = document.getElementById('wamsgs'), chips = document.getElementById('wachips'), form = document.getElementById('wain'), input = document.getElementById('wainput'), start = document.getElementById('wastart');
  const WA = 'https://wa.me/2349049811269?text=', PH = '+234 904 981 1269';
  const KB = [
    ['price', ['price', 'prices', 'cost', 'how much', 'quote', 'quotation', 'estimate', 'budget', 'cheap', 'discount', 'nawa', 'farashi'], 'Cost depends on the scope of the project, the equipment chosen and the location, so we advise after understanding your requirements. For a quote, tap Continue on WhatsApp and share a few details about your premises.'],
    ['cctv', ['cctv', 'camera', 'surveillance', 'dvr', 'nvr', 'security system', 'monitoring'], 'We design and install CCTV and security systems for homes, offices, hotels, schools, hospitals, factories, estates and institutions. That covers camera installation, DVR/NVR recording, remote viewing setup, configuration, maintenance and upgrades. <a href="/cctv">See CCTV &amp; Security</a>'],
    ['solar', ['solar', 'inverter', 'battery', 'batteries', 'panel', 'backup power', 'generator', 'nepa', 'power supply'], 'We design and install solar and backup power systems: panels, inverters, battery storage, configuration, maintenance and upgrades. We assess your needs first, then design the system and select the equipment. <a href="/solar">See Solar Power Systems</a>'],
    ['maintenance', ['maintenance', 'repair', 'fix', 'faulty', 'not working', 'stopped working', 'troubleshoot', 'servicing', 'upgrade'], 'Yes. We offer preventive maintenance, inspection, troubleshooting, repairs where applicable, optimisation and upgrades for solar, CCTV, connectivity and other installed systems. <a href="/maintenance">See Maintenance</a>'],
    ['consultation', ['consult', 'consultation', 'advice', 'advise', 'guidance', 'recommend', 'which system', 'what do i need', 'what size'], 'We can help you decide the right solution before you buy equipment or start installation: solar requirements, CCTV planning, connectivity, upgrades and installation planning. <a href="/consultation">See Technical Consultation</a>'],
    ['starlink', ['starlink', 'internet', 'wifi', 'wi-fi', 'network', 'networking', 'connectivity', 'router'], 'Yes. We handle Starlink installation, activation and configuration, connectivity setup and technical support, plus networking and Wi-Fi infrastructure.'],
    ['other', ['intercom', 'door lock', 'door locks', 'access control', 'electric fence', 'electrical'], 'Besides our four main services, we also handle intercom installation, digital door locks, access control, electric fence systems, networking, Wi-Fi infrastructure and electrical installation and maintenance.'],
    ['overview', ['what do you do', 'services', 'offer', 'provide', 'capabilities', 'what you do'], 'Our four main services are CCTV &amp; Security, Solar Power Systems, Maintenance and Technical Consultation. We also do Starlink, intercoms, digital door locks, access control, electric fences, networking, Wi-Fi and electrical work. <a href="/#solutions">Explore solutions</a>'],
    ['location', ['where', 'location', 'address', 'office', 'kano', 'abuja', 'mararaba', 'nasarawa', 'nationwide', 'international', 'outside', 'visit', 'state'], 'We operate in Kano (No. 35 France Road, Sabon Gari) and Mararaba (Old Orange Market Street, Karu LGA, Nasarawa State). Mararaba is our base for projects across Nasarawa and Abuja. We also take on projects nationwide and internationally; pricing may vary with location, logistics and scope.'],
    ['contact', ['contact', 'phone', 'call', 'number', 'email', 'whatsapp', 'reach', 'talk to', 'speak', 'human', 'person', 'agent'], 'You can call or WhatsApp us on ' + PH + ', or email <a href="mailto:daboenergyss@gmail.com">daboenergyss@gmail.com</a>. Tap Continue on WhatsApp below to message the team now.'],
    ['experience', ['experience', 'years', 'how many projects', 'customers', 'trust', 'track record', 'how long', 'reliable'], 'DESS has 7+ years of experience, 150+ projects completed and 500+ customers served. You can read customer feedback in the testimonials section.'],
    ['brands', ['brand', 'brands', 'hikvision', 'dahua', 'deye', 'growatt', 'ubiquiti', 'tp-link', 'felicity', 'must', 'cell american', 'dealer', 'authorised', 'authorized', 'partner'], 'Brands and technologies we work with include Starlink, Hikvision, Dahua, TP-Link, Ubiquiti, Growatt, Felicity, MUST, Deye and Cell American. Equipment is specified according to project requirements.'],
    ['sectors', ['hotel', 'school', 'hospital', 'factory', 'government', 'estate', 'shop', 'home', 'residential', 'business', 'company', 'university', 'clinic', 'developer'], 'We serve homes, shops, offices, corporate organisations, hotels, schools, hospitals, factories, government and institutions, estates and property developers. Requirements differ by sector, so we start by understanding your premises and needs.'],
    ['case', ['case study', 'project', 'projects', 'example', 'kaduna', 'portfolio', 'previous work', 'video'], 'Our featured case study is a CCTV restoration, upgrade and monthly maintenance job at a construction facility in Kaduna. <a href="/#projects">Watch it under Our work</a>'],
    ['hours', ['hours', 'opening', 'open', 'closed', 'weekend', 'available', 'what time'], 'I do not have our opening hours yet. For the fastest reply, message the team on WhatsApp or call ' + PH + '.'],
    ['unknown', ['warranty', 'guarantee', 'financing', 'instalment', 'installment', 'delivery', 'payment plan', 'loan', 'credit'], 'I do not have confirmed information on that, and I do not want to guess. Please ask our team directly on WhatsApp.'],
    ['hello', ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening', 'sannu', 'how far'], 'Hello! I can answer questions about our CCTV, solar, maintenance, Starlink and consultation services, our locations and how to reach us.'],
    ['thanks', ['thanks', 'thank you', 'nagode'], 'You are welcome! Anything else I can help with? You can also continue on WhatsApp anytime.']
  ];
  const CHIPS = [['CCTV', 'CCTV installation'], ['Solar', 'Solar power'], ['Maintenance', 'Maintenance'], ['Starlink', 'Starlink'], ['Consultation', 'Technical consultation'], ['Locations', 'Where are you located?'], ['Price', 'How much does it cost?'], ['Contact', 'Contact details']];
  const FALLBACK = 'I am not sure about that one. Our team can answer directly: tap Continue on WhatsApp below.';
  const esc = k => k.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const has = (t, k) => new RegExp('(^|[^a-z])' + esc(k) + 's?([^a-z]|$)').test(t);
  const find = q => { const t = q.toLowerCase(); let best = null, sc = 0; KB.forEach(([id, ks, a]) => { const n = ks.filter(k => has(t, k)).length; if (n > sc) { sc = n; best = a; } }); return best; };
  const add = (cls, html, plain) => { const d = document.createElement('div'); d.className = 'm ' + cls; plain ? d.textContent = html : d.innerHTML = html; msgs.appendChild(d); msgs.scrollTop = msgs.scrollHeight; return d; };
  const link = q => { start.href = WA + encodeURIComponent('Hello DESS, I was chatting with the website assistant' + (q ? ' about: ' + q : '') + '.'); };
  const reply = (q, done) => { const d = add('b', '…'); setTimeout(() => { const a = find(q); if (a) { d.innerHTML = a; msgs.scrollTop = msgs.scrollHeight; } else if (window.DESS_AI_ENDPOINT) { fetch(window.DESS_AI_ENDPOINT, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ question: q }) }).then(r => r.json()).then(j => { d.textContent = j.answer || FALLBACK; }).catch(() => { d.textContent = FALLBACK; }); } else d.textContent = FALLBACK; link(q); msgs.scrollTop = msgs.scrollHeight; }, 450); };
  const ask = q => { q = q.trim(); if (!q) return; add('u', q, true); reply(q); };
  CHIPS.forEach(([l, q]) => { const b = document.createElement('button'); b.type = 'button'; b.textContent = l; b.addEventListener('click', () => ask(q)); chips.appendChild(b); });
  form.addEventListener('submit', e => { e.preventDefault(); ask(input.value); input.value = ''; });
  let started = false;
  const set = o => { pop.hidden = !o; fab.setAttribute('aria-expanded', o); const d = fab.querySelector('.dot'); if (o) { if (d) d.remove(); if (!started) { started = true; add('b', 'Hello! I am the DESS assistant, an automated helper. Ask me about our services, locations or how to reach us, or pick a topic below. For quotes, I will point you to our team on WhatsApp.'); link(''); } setTimeout(() => input.focus(), 50); } };
  fab.addEventListener('click', () => set(pop.hidden));
  pop.querySelector('.waclose').addEventListener('click', () => { set(false); fab.focus(); });
  addEventListener('keydown', e => { if (e.key === 'Escape' && !pop.hidden) set(false); });
})();
(() => { // live-looking globe with breathing zoom
  const c = document.getElementById('globe'); if (!c) return;
  const x = c.getContext('2d'), D = Math.PI / 180, mo = matchMedia('(prefers-reduced-motion: reduce)').matches;
  let S = 0, la0 = 10, lo0 = 8, last = 0, raf = 0;
  const size = () => { S = c.clientWidth; const d = Math.min(devicePixelRatio || 1, 2); c.width = S * d; c.height = S * d; x.setTransform(d, 0, 0, d, 0, 0); };
  const dots = [], N = 1100; for (let i = 0; i < N; i++) dots.push([Math.asin(1 - 2 * (i + .5) / N) / D, (i * 137.508) % 360 - 180]);
  const P = [{ n: 'Kano', la: 27, lo: 6, dx: 22, dy: -30, r: 0 }, { n: 'Abuja', la: 8, lo: -16, dx: -22, dy: -26, r: 1 }, { n: 'Nasarawa', la: -8, lo: 24, dx: 22, dy: 30, r: 2 }];
  const pj = (la, lo) => { la *= D; lo *= D; const a = la0 * D, dl = lo - lo0 * D; return [Math.cos(la) * Math.sin(dl), Math.cos(a) * Math.sin(la) - Math.sin(a) * Math.cos(la) * Math.cos(dl), Math.sin(a) * Math.sin(la) + Math.cos(a) * Math.cos(la) * Math.cos(dl)]; };
  function draw(t) {
    last = t; lo0 = 8 + (mo ? 0 : 26 * Math.sin(t / 5200));
    const cx = S / 2, cy = S / 2, R0 = S * .4, R = R0; x.clearRect(0, 0, S, S);
    [[1.34, .42, -.5, 1700], [1.22, .36, .55, 2300]].forEach(([a, b, rot, sp], k) => {
      x.save(); x.translate(cx, cy); x.rotate(rot); x.strokeStyle = 'rgba(120,170,255,.24)'; x.lineWidth = 1; x.beginPath(); x.ellipse(0, 0, R0 * a, R0 * b, 0, 0, 7); x.stroke();
      const u = t / sp * (k ? -1 : 1); x.fillStyle = k ? '#f5b301' : '#6fb0ff'; x.shadowColor = x.fillStyle; x.shadowBlur = 12; x.beginPath(); x.arc(Math.cos(u) * R0 * a, Math.sin(u) * R0 * b, 3.2, 0, 7); x.fill(); x.restore();
    });
    const g = x.createRadialGradient(cx - R * .3, cy - R * .35, R * .1, cx, cy, R); g.addColorStop(0, '#16315f'); g.addColorStop(1, '#070d1c');
    x.fillStyle = g; x.beginPath(); x.arc(cx, cy, R, 0, 7); x.fill(); x.strokeStyle = 'rgba(90,150,255,.5)'; x.lineWidth = 1.2; x.stroke();
    x.lineWidth = .7; x.strokeStyle = 'rgba(110,170,255,.18)';
    const line = pts => { x.beginPath(); let on = false; pts.forEach(([la, lo]) => { const p = pj(la, lo); if (p[2] > 0) { const X = cx + p[0] * R, Y = cy - p[1] * R; on ? x.lineTo(X, Y) : x.moveTo(X, Y); on = true; } else on = false; }); x.stroke(); };
    for (let la = -75; la <= 75; la += 20) { const a = []; for (let lo = -180; lo <= 180; lo += 3) a.push([la, lo]); line(a); }
    for (let lo = -180; lo < 180; lo += 15) { const a = []; for (let la = -88; la <= 88; la += 3) a.push([la, lo]); line(a); }
    dots.forEach(([la, lo]) => { const p = pj(la, lo); if (p[2] > 0) { x.fillStyle = `rgba(140,190,255,${.12 + .5 * p[2]})`; x.fillRect(cx + p[0] * R, cy - p[1] * R, 1.5, 1.5); } });
    x.save(); x.setLineDash([5, 6]); x.lineDashOffset = -t / 60; x.strokeStyle = '#f5b301'; x.lineWidth = 1.5;
    [[0, 1], [1, 2]].forEach(([i, j]) => { x.beginPath(); for (let s = 0; s <= 1.001; s += .05) { const p = pj(P[i].la + (P[j].la - P[i].la) * s, P[i].lo + (P[j].lo - P[i].lo) * s), l = 1 + .06 * Math.sin(Math.PI * s); const X = cx + p[0] * R * l, Y = cy - p[1] * R * l; s ? x.lineTo(X, Y) : x.moveTo(X, Y); } x.stroke(); });
    x.restore();
    P.forEach(o => {
      const p = pj(o.la, o.lo); if (p[2] < .08) return; const X = cx + p[0] * R, Y = cy - p[1] * R, ph = ((t / 1400) + o.r * .33) % 1;
      x.strokeStyle = `rgba(245,179,1,${(1 - ph) * .6})`; x.lineWidth = 1.5; x.beginPath(); x.arc(X, Y, 4 + ph * 22, 0, 7); x.stroke();
      x.fillStyle = '#f5b301'; x.shadowColor = '#f5b301'; x.shadowBlur = 14; x.beginPath(); x.arc(X, Y, 4.2, 0, 7); x.fill(); x.shadowBlur = 0;
      x.strokeStyle = 'rgba(255,255,255,.5)'; x.lineWidth = 1; x.beginPath(); x.moveTo(X, Y); x.lineTo(X + o.dx, Y + o.dy); x.stroke();
      x.font = '600 12px system-ui,sans-serif'; const w = x.measureText(o.n).width + 16, bx = Math.max(4, Math.min(S - w - 4, o.dx > 0 ? X + o.dx : X + o.dx - w)), by = Y + o.dy - 11;
      x.fillStyle = 'rgba(6,10,20,.88)'; x.beginPath(); x.roundRect ? x.roundRect(bx, by, w, 22, 11) : x.rect(bx, by, w, 22); x.fill(); x.strokeStyle = 'rgba(245,179,1,.6)'; x.stroke();
      x.fillStyle = '#fff'; x.textBaseline = 'middle'; x.fillText(o.n, bx + 8, by + 11.5);
    });
  }
  size(); addEventListener('resize', () => { size(); draw(last); });
  if (mo) { draw(0); return; }
  const loop = t => { draw(t); raf = requestAnimationFrame(loop); };
  new IntersectionObserver(es => es.forEach(e => { cancelAnimationFrame(raf); if (e.isIntersecting) raf = requestAnimationFrame(loop); })).observe(c);
  draw(0);
})();
