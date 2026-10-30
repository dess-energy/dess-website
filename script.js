document.documentElement.classList.add('js');
document.getElementById('yr').textContent = new Date().getFullYear();

// Mobile menu
const burger = document.querySelector('.burger');
const menu = document.getElementById('menu');
const scrim = document.querySelector('.scrim'), navEl = document.querySelector('.nav');
const setMenu = open => {
  menu.classList.toggle('open', open);
  burger.setAttribute('aria-expanded', open);
  if (scrim) scrim.classList.toggle('open', open);
  if (navEl) navEl.classList.toggle('menu-open', open);
  document.documentElement.classList.toggle('noscroll', open);
  if (open) { const x = menu.querySelector('.drawer-x'); if (x) setTimeout(() => x.focus(), 60); } else if (document.activeElement && menu.contains(document.activeElement)) burger.focus();
};
burger.addEventListener('click', () => setMenu(!menu.classList.contains('open')));
const dx = menu.querySelector('.drawer-x'); if (dx) dx.addEventListener('click', () => setMenu(false));
if (scrim) scrim.addEventListener('click', () => setMenu(false));
addEventListener('keydown', e => { if (e.key === 'Escape' && menu.classList.contains('open')) setMenu(false); });
menu.querySelectorAll('a').forEach(a => a.addEventListener('click', () => setMenu(false)));

// Fade-in on scroll
const items = document.querySelectorAll('.hero-in > div > *, .hero-media, .phero .wrap > *, .sec .eyebrow, .sec h2, .sec .big, .sec .sub, .sec .note, .sec .lead, .card, .why, .xp, .mission, .co-text > *, .co-img, .step, .tile, .shot, .bcard, .case-v, .case-t > *, .quote, .stat, .chips > *, details, .clist li, .contact form, .cta h2, .cta p, .cta .btns');
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
  const SITE = window.DESS_SITE || {};
  const WA = 'https://wa.me/' + (SITE.wa || '2349049811269') + '?text=', PH = SITE.phone || '+234 904 981 1269', EM = SITE.email || 'daboenergyss@gmail.com', PH2 = SITE.phone2 || '';
  const AI_URL = 'https://dess-assistant.iishaqman.workers.dev/'; // paste your Cloudflare Worker address here to switch on AI answers
  const KB = [
    ['fees', ['free consultation', 'free inspection', 'inspection fee', 'consultation fee', 'is it free', 'free of charge', 'charge for', 'assessment fee', 'free', 'site visit', 'site consultation', 'inspection'], 'Phone consultations are free. Site consultations are paid, and the price depends on the location, so the team will confirm it for your project. Tap Request a quote or call ' + PH + '.'],
    ['lead', ['callback', 'call me', 'call back', 'request a quote', 'get a quote', 'want a quote', 'need a quote', 'quote me', 'a quotation', 'book', 'visit my', 'come to my', 'how soon', 'urgent', 'assess my'], ''],
    ['price', ['price', 'prices', 'cost', 'how much', 'quote', 'quotation', 'estimate', 'budget', 'cheap', 'discount', 'nawa', 'farashi'], 'DESS pricing depends on the system, equipment, site conditions and location. We first understand what you need, then prepare a quotation. Tap Request a quote and I will collect your details, or call ' + PH + '.'],
    ['warranty', ['warranty', 'warranties', 'guarantee', 'after sales', 'after-sales'], 'Warranty is handled case by case. Applicable terms are confirmed in your project quotation and, where relevant, with the equipment manufacturer, so I cannot promise a standard warranty. Maintenance and technical support are also available after installation.'],
    ['hours', ['hours', 'opening', 'open', 'closed', 'weekend', 'sunday', 'saturday', 'what time', 'emergency', 'after hours', 'available'], 'Our working hours are Monday to Saturday, 9:00 AM to 5:00 PM. Sunday emergency work may be available by arrangement but is not guaranteed, so please call ' + PH + ' and the team will confirm availability.'],
    ['cctv', ['cctv', 'camera', 'surveillance', 'dvr', 'nvr', 'security system', 'monitoring', 'blind spot'], 'We design and install CCTV and security systems for homes, offices, hotels, schools, hospitals, factories, estates and institutions, and we also work on existing systems: troubleshooting, restoring faulty cameras, replacing old ones and adding cameras to reduce blind spots. What we can do on a specific system is confirmed after assessment. <a href="/cctv">See CCTV &amp; Security</a>'],
    ['solar', ['solar', 'inverter', 'battery', 'batteries', 'panel', 'backup power', 'generator', 'nepa', 'power supply'], 'We design and install solar and backup power systems: panels, inverters, battery storage, configuration, maintenance and upgrades. We cannot recommend a system size, runtime or price without your load information and an assessment. <a href="/solar">See Solar Power Systems</a>'],
    ['maintenance', ['maintenance', 'repair', 'fix', 'faulty', 'not working', 'stopped working', 'troubleshoot', 'servicing', 'upgrade'], 'Yes. We offer maintenance, troubleshooting, repairs where applicable, inspection and upgrades for solar, CCTV, connectivity and other installed systems. Scope, timing and cost depend on the system, the fault and the site. <a href="/maintenance">See Maintenance</a>'],
    ['consultation', ['consult', 'consultation', 'advice', 'advise', 'guidance', 'recommend', 'which system', 'what do i need', 'what size'], 'We can help you decide the right solution before you buy equipment or start installation: solar requirements, CCTV planning, connectivity, upgrades and installation planning. Phone consultations are free; site consultations are paid and priced by location. <a href="/consultation">See Technical Consultation</a>'],
    ['starlink', ['starlink', 'internet', 'wifi', 'wi-fi', 'network', 'networking', 'connectivity', 'router', 'subscription', 'renew', 'renewal', 'dish', 'relocation', 'mounting', 'activation'], 'Yes. Our Starlink services include equipment supply, installation, activation assistance, Wi-Fi and network configuration, relocation and mounting, troubleshooting and maintenance, and subscription enquiries. For current plans, prices and the purchase or renewal process, please contact the team. Speeds and availability depend on Starlink and local conditions.'],
    ['other', ['intercom', 'door lock', 'door locks', 'access control', 'electric fence', 'electrical'], 'Besides our main services, we also handle intercom systems, digital door locks, access control, electric fence systems, networking, Wi-Fi infrastructure and electrical installation and maintenance, subject to assessment.'],
    ['overview', ['what do you do', 'services', 'offer', 'provide', 'capabilities', 'what you do'], 'We provide CCTV and security systems, solar power systems, maintenance and technical consultation, plus Starlink supply, installation and subscription enquiries, intercoms, digital door locks, access control, electric fences, networking and Wi-Fi. <a href="/#solutions">Explore solutions</a>'],
    ['location', ['where', 'location', 'address', 'office', 'kano', 'abuja', 'mararaba', 'nasarawa', 'nationwide', 'international', 'outside', 'visit', 'state', 'my area', 'my town'], 'DESS operates from Kano (No. 35 France Road, Sabon Gari) and Mararaba (Old Orange Market Street, Karu LGA, Nasarawa State). Abuja is served from the Mararaba base. We accept enquiries across Nigeria and internationally; availability, travel and pricing depend on the location and project and are confirmed after we review your request.'],
    ['contact', ['contact', 'phone', 'call', 'number', 'email', 'whatsapp', 'reach', 'talk to', 'speak', 'human', 'person', 'agent'], 'The quickest way to reach us is by phone: ' + PH + (PH2 ? ' or ' + PH2 : '') + ' (Monday to Saturday, 9:00 AM to 5:00 PM). You can also email <a href="mailto:' + EM + '">' + EM + '</a> or tap Continue on WhatsApp below.'],
    ['experience', ['experience', 'years', 'trust', 'track record', 'how long', 'reliable', 'credible'], 'DESS has 7+ years of experience, 150+ projects completed and 500+ customers served. You can see our featured case study under Our work. <a href="/#projects">View projects</a>'],
    ['brands', ['brand', 'brands', 'hikvision', 'dahua', 'deye', 'growatt', 'ubiquiti', 'tp-link', 'felicity', 'must', 'cell american', 'dealer', 'authorised', 'authorized', 'partner'], 'Brands and technologies we work with include Starlink, Hikvision, Dahua, TP-Link, Ubiquiti, Growatt, Felicity, MUST, Deye and Cell American. This is not a claim of official partnership, and equipment is specified according to project requirements.'],
    ['sectors', ['hotel', 'school', 'hospital', 'factory', 'government', 'estate', 'shop', 'home', 'residential', 'business', 'company', 'university', 'clinic', 'developer', 'other provider', 'another company'], 'We serve homes, shops, offices, corporate organisations, hotels, schools, hospitals, factories, government and institutions, estates and property developers. We work on existing systems as well as new installations; whether we can take on a specific job is confirmed after assessment.'],
    ['case', ['case study', 'project', 'projects', 'example', 'kaduna', 'portfolio', 'previous work', 'video'], 'Our featured case study is a CCTV restoration, upgrade and ongoing maintenance job at a construction facility in Kaduna. <a href="/#projects">Watch it under Our work</a>'],
    ['unknown', ['financing', 'instalment', 'installment', 'delivery', 'payment plan', 'loan', 'credit', 'deposit', 'refund', 'payment', 'bank', 'account number', 'stock'], 'I do not have confirmed information on that, and I do not want to guess. Please ask the team by phone, and do not send money to any account unless the team confirms it directly.'],
    ['hello', ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening', 'sannu', 'how far'], 'Hello! I can answer questions about our services, locations and working hours, or collect your details for a quotation.'],
    ['thanks', ['thanks', 'thank you', 'nagode'], 'You are welcome! Anything else I can help with?']
  ];
  const DKB = (() => { try { return JSON.parse(document.getElementById('dess-kb').textContent); } catch (e) { return {}; } })();
  const AB = DKB.about || {};
  const esc2 = t => String(t || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  const aboutAns = esc2((AB.background && AB.background[0]) || 'DESS (Dabo Energy & Security Solutions) is a technology and systems solutions company providing energy, security, connectivity, maintenance and technical consultation services.') + (AB.founders ? ' ' + esc2(AB.founders) : '') + ' <a href="/#company">Read our story</a>';
  const expAns = 'Our expertise covers ' + ((AB.expertise || []).map(x => esc2(x.title).toLowerCase()).join(', ') || 'CCTV and security, solar and backup power, maintenance and technical consultation') + '. <a href="/#company">See the details</a>';
  const missionAns = esc2(AB.mission || 'To understand each customer\u2019s real problem and deliver the right technical solution, with dependable service and lasting value.');
  const whyAns = 'What people value about DESS: ' + ((DKB.why || []).map(x => esc2(x.title).toLowerCase()).join(', ') || 'a technical approach, professional installation and support beyond installation') + '. <a href="/#why">See why DESS</a>';
  const si = KB.findIndex(k => k[0] === 'sectors');
  KB.splice(si < 0 ? KB.length : si, 0,
    ['about', ['about us', 'about dess', 'who are you', 'who is dess', 'what is dess', 'background', 'our story', 'story', 'history', 'how did', 'began', 'founded', 'company profile', 'tell me about'], aboutAns],
    ['expertise', ['expertise', 'specialise', 'specialize', 'specialty', 'specialities', 'good at', 'skills', 'strengths'], expAns],
    ['mission', ['mission', 'vision', 'values', 'stand for', 'believe', 'commitment', 'purpose'], missionAns]);
  KB.push(
    ['process', ['process', 'how it works', 'how do you work', 'steps', 'procedure', 'how do i start', 'get started', 'what happens next'], 'Our process has six steps: understand your requirements, assess the project, recommend the solution, install and configure it, test and hand over, then support and maintain. To start, call ' + PH + ' or tap Request a quote. <a href="/#process">See the process</a>'],
    ['why', ['why choose', 'why should i', 'what makes you different', 'better than', 'advantages', 'benefits', 'why dess'], whyAns],
    ['schedule', ['maintenance plan', 'maintenance contract', 'regular maintenance', 'monthly maintenance', 'service contract', 'annual', 'schedule'], 'We provide maintenance and technical support. For regular visits, such as the monthly checks we carry out for one client in Kaduna, the team agrees the schedule with you after assessing the system. Call ' + PH + ' to discuss.'],
    ['unknown', ['job', 'jobs', 'vacancy', 'vacancies', 'career', 'careers', 'internship', 'apprentice', 'hiring', 'training', 'supply only', 'buy only', 'sell equipment', 'do you sell', 'spare parts', 'buy panels', 'buy cameras', 'buy inverter'], 'I do not have confirmed information on that, and I do not want to guess. Please ask the team by phone on ' + PH + '.'],
    ...(DKB.faq || []).map(f => ['faq', [...new Set(String(f.q).toLowerCase().split(/[^a-z]+/).filter(w => w.length > 3 && !['does', 'have', 'your', 'that', 'this', 'with', 'what', 'when', 'where', 'which', 'will', 'would', 'could', 'should', 'about', 'from', 'into', 'there', 'their', 'they', 'them', 'also', 'dess'].includes(w)))], esc2(f.a)]));
  const CHIPS = [['CCTV', 'CCTV installation'], ['Solar', 'Solar power'], ['Starlink', 'Starlink'], ['Maintenance', 'Maintenance'], ['Hours', 'Working hours'], ['Locations', 'Where are you located?'], ['Price', 'How much does it cost?'], ['Request a quote', 'request a quote']];
  const FALLBACK = 'I am not sure about that one. Tap Request a quote and I will collect your details for the team, or call ' + PH + '.';
  const esc = k => k.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const has = (t, k) => new RegExp('(^|[^a-z])' + esc(k) + 's?([^a-z]|$)').test(t);
  const FORM = 'https://formspree.io/f/xkjowdka';
  const find = q => { const t = q.toLowerCase(); let best = null, sc = 0; KB.forEach(([id, ks, a]) => { const n = ks.filter(k => has(t, k)).length; if (n > sc && (id !== 'faq' || n >= 2)) { sc = n; best = [id, a]; } }); return best; };
  const add = (cls, html, plain) => { const d = document.createElement('div'); d.className = 'm ' + cls; plain ? d.textContent = html : d.innerHTML = html; msgs.appendChild(d); msgs.scrollTop = msgs.scrollHeight; return d; };
  const link = (q, extra) => { start.href = WA + encodeURIComponent('Hello DESS, I was chatting with the website assistant' + (q ? ' about: ' + q : '') + '.' + (extra || '')); };
  const bot = t => add('b', t, true);
  let flow = null;
  const setChips = list => { chips.innerHTML = ''; list.forEach(([l, fn]) => { const b = document.createElement('button'); b.type = 'button'; b.textContent = l; b.addEventListener('click', fn); chips.appendChild(b); }); };
  const home = () => setChips(CHIPS.map(([l, q]) => [l, () => ask(q)]));
  const SERV = ['CCTV & Security', 'Solar Power', 'Starlink / Connectivity', 'Maintenance / Repair', 'Technical Consultation', 'Other'];
  const QS = ['Which service do you need?', 'What town or area is the job in?', 'Briefly, what is it about? For example: new installation, repair, replacement or upgrade, plus a short description.', 'What phone number should the team call you on? Phone is the quickest way for them to respond.', 'Your name? (optional, tap Skip to leave it out)'];
  const nextQ = () => { bot(QS[flow.i]); if (flow.i === 0) setChips(SERV.map(s => [s, () => step(s)])); else if (flow.i === 4) setChips([['Skip', () => step('skip')], ['Cancel', () => step('cancel')]]); else setChips([['Cancel', () => step('cancel')]]); };
  const startFlow = () => { flow = { i: 0, d: {} }; bot('Happy to help. I will collect a few details for the DESS team. Please do not share passwords or payment details. You can cancel at any time.'); nextQ(); };
  const confirm = () => { const d = flow.d; bot('Please check:\nService: ' + d.service + '\nLocation: ' + d.place + '\nDetails: ' + d.details + '\nPhone: ' + d.phone + (d.name ? '\nName: ' + d.name : '') + '\n\nMay I send these details to the DESS team so they can follow up with you?'); setChips([['Yes, send', () => { add('u', 'Yes, send', true); send(); }], ['No, cancel', () => step('cancel')]]); };
  const send = () => {
    const d = flow.d, fd = new FormData(); fd.append('name', d.name || 'Website assistant lead'); fd.append('phone', d.phone); fd.append('service', d.service); fd.append('message', 'Location: ' + d.place + '\nDetails: ' + d.details + '\nSource: website assistant');
    link('', ' Service: ' + d.service + '. Location: ' + d.place + '. Details: ' + d.details + '. Phone: ' + d.phone + '.'); flow = null; home();
    fetch(FORM, { method: 'POST', body: fd, headers: { Accept: 'application/json' } }).then(r => { if (!r.ok) throw 0; bot('Thank you. Your request has been sent to the DESS team so they can follow up on ' + d.phone + '. Working hours are Monday to Saturday, 9:00 AM to 5:00 PM. For anything urgent, please call ' + PH + '.'); }).catch(() => bot('Sorry, I could not send that just now. Please call ' + PH + ' or tap Continue on WhatsApp below; your details are already filled in.'));
  };
  const step = t => {
    t = t.trim(); if (!t) return; add('u', t, true);
    if (/^(cancel|stop|no|n)$/i.test(t)) { bot('No problem. Nothing was sent.'); flow = null; home(); return; }
    if (flow.i >= 5) { /^(yes|y|send|ok|okay)$/i.test(t) ? send() : bot('Please tap Yes, send, or type cancel.'); return; }
    const k = ['service', 'place', 'details', 'phone', 'name'][flow.i];
    if (k === 'phone') { if (!/^(\+?234|0)?\d{9,11}$/.test(t.replace(/[\s()-]/g, ''))) { bot('That does not look like a valid phone number. Please type it like 09012345678.'); return; } flow.d.phone = t; }
    else if (k === 'name') { if (!/^skip$/i.test(t)) flow.d.name = t.slice(0, 60); }
    else flow.d[k] = t.slice(0, 300);
    flow.i++; flow.i < 5 ? nextQ() : confirm();
  };
  const reply = q => {
    const d = add('b', '…');
    setTimeout(() => {
      const m = find(q);
      if (m && m[0] === 'lead') { d.remove(); startFlow(); return; }
      if (m) d.innerHTML = m[1];
      else if (AI_URL.indexOf('https://') === 0) { fetch(AI_URL, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ question: q }) }).then(r => r.json()).then(o => { if (o && o.answer) { d.textContent = o.answer; const s = document.createElement('small'); s.className = 'ai'; s.textContent = 'AI-generated answer. Please confirm details with our team.'; d.appendChild(s); } else d.textContent = FALLBACK; msgs.scrollTop = msgs.scrollHeight; }).catch(() => { d.textContent = FALLBACK; }); }
      else d.textContent = FALLBACK;
      link(q); msgs.scrollTop = msgs.scrollHeight;
    }, 450);
  };
  const ask = q => { q = q.trim(); if (!q) return; if (flow) { step(q); return; } add('u', q, true); reply(q); };
  home();
  form.addEventListener('submit', e => { e.preventDefault(); ask(input.value); input.value = ''; });
  let started = false;
  const set = o => { pop.hidden = !o; fab.setAttribute('aria-expanded', o); const d = fab.querySelector('.dot'); if (o) { if (d) d.remove(); if (!started) { started = true; add('b', 'Hello! I am the DESS assistant, an automated helper. Ask me about our services, locations or working hours, or tap Request a quote and I will collect your details for the DESS team.'); link(''); } setTimeout(() => input.focus(), 50); } };
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

(() => { // case study read more
  const c = document.querySelector('.case'); if (!c) return;
  const body = c.querySelector('.case-body'), btn = c.querySelector('.case-btn'); if (!body || !btn) return;
  const fit = () => { body.style.maxHeight = c.classList.contains('open') ? body.scrollHeight + 'px' : ''; };
  btn.addEventListener('click', () => { const o = c.classList.toggle('open'); btn.setAttribute('aria-expanded', o); btn.firstChild.textContent = o ? 'Show less' : 'Read more'; fit(); if (!o) c.scrollIntoView({ block: 'nearest', behavior: 'smooth' }); });
  addEventListener('resize', fit);
})();

(() => { // header turns solid on scroll
  const nav = document.querySelector('.nav'); if (!nav) return;
  const f = () => nav.classList.toggle('scrolled', scrollY > 16);
  addEventListener('scroll', f, { passive: true }); f();
})();

// lets iPhones show the pressed state on buttons and cards
document.addEventListener('touchstart', function () {}, { passive: true });

(() => { // enlarge WhatsApp screenshots
  document.addEventListener('click', e => {
    const b = e.target.closest && e.target.closest('.wa-shot'); if (!b) return;
    const box = document.createElement('div'); box.className = 'lightbox'; box.setAttribute('role', 'dialog'); box.setAttribute('aria-label', 'Screenshot');
    const im = document.createElement('img'); im.src = b.dataset.full; im.alt = b.querySelector('img').alt;
    const x = document.createElement('button'); x.type = 'button'; x.setAttribute('aria-label', 'Close'); x.textContent = '\u00d7';
    const close = () => { box.remove(); document.removeEventListener('keydown', onKey); b.focus(); };
    const onKey = ev => { if (ev.key === 'Escape') close(); };
    box.addEventListener('click', close); document.addEventListener('keydown', onKey);
    box.appendChild(im); box.appendChild(x); document.body.appendChild(box); x.focus();
  });
})();

(() => { // light / dark mode
  const root = document.documentElement, KEY = 'dess-theme';
  const sync = () => {
    const d = root.getAttribute('data-theme') === 'dark';
    document.querySelectorAll('.tc-name').forEach(n => { n.textContent = d ? 'Dark mode' : 'Light mode'; });
    document.querySelectorAll('.tc-btn').forEach(b => { b.textContent = d ? 'Switch to Light' : 'Switch to Dark'; });
    document.querySelectorAll('.theme-btn').forEach(b => b.setAttribute('aria-label', d ? 'Switch to light mode' : 'Switch to dark mode'));
    document.querySelectorAll('.theme-btn use, .tc-l use').forEach(u => u.setAttribute('href', d ? '#i-sun' : '#i-moon'));
  };
  document.addEventListener('click', e => {
    if (!e.target.closest('.tc-btn, .theme-btn')) return;
    const toDark = root.getAttribute('data-theme') !== 'dark';
    if (toDark) root.setAttribute('data-theme', 'dark'); else root.removeAttribute('data-theme');
    try { localStorage.setItem(KEY, toDark ? 'dark' : 'light'); } catch (err) {}
    sync();
  });
  sync();
})();
(() => { // highlight the current page or section in the menu
  const links = [...document.querySelectorAll('.menu > a[data-nav]')]; if (!links.length) return;
  const set = k => links.forEach(a => a.classList.toggle('active', a.dataset.nav === k));
  const p = location.pathname.replace(/\/$/, '') || '/';
  if (p === '/' || p === '/index.html') {
    set('home');
    if ('IntersectionObserver' in window) {
      const io = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting && scrollY >= 200) set(e.target.id); }), { rootMargin: '-45% 0px -50% 0px' });
      ['solutions', 'why', 'projects', 'faq', 'contact'].map(id => document.getElementById(id)).filter(Boolean).forEach(s => io.observe(s));
      addEventListener('scroll', () => { if (scrollY < 200) set('home'); }, { passive: true });
    }
  } else if (p.indexOf('/blog') === 0) set('blog');
  else if (['/cctv', '/solar', '/maintenance', '/consultation'].indexOf(p) > -1) set('solutions');
  else if (p.indexOf('/updates') === 0) set('projects');
})();
