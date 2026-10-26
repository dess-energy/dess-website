import json, os, sys, re, html, glob, shutil, tempfile, datetime
SRC = os.path.dirname(os.path.abspath(__file__)) + '/'
BUILD = tempfile.mkdtemp(prefix='dess_build_')
O = BUILD + '/'
B = 'https://dess.com.ng'
E = lambda t: html.escape(str(t), quote=False)
EA = lambda t: html.escape(str(t), quote=True)
class BuildError(Exception): pass
def _hook(t, v, tb):
    if issubclass(t, BuildError):
        print('BUILD FAILED, nothing was changed on the website:', v); os._exit(1)
    sys.__excepthook__(t, v, tb)
sys.excepthook = _hook
def _load(name):
    try:
        with open(SRC + 'content/' + name, encoding='utf-8') as f: return json.load(f)
    except Exception as e:
        raise BuildError('Cannot read content/%s: %s' % (name, e))
C = {k: _load(k + '.json') for k in ('site', 'home', 'services', 'testimonials')}
S, HM = C['site'], C['home']
DEFAULT_ABOUT = {
 "eyebrow": "Our story",
 "heading": "Who we are and what we stand for",
 "background": [
  "DESS began in response to the challenge of unreliable electricity in Nigeria, and grew as customers asked for more. Today, Dabo Energy & Security Solutions is a technology and systems solutions company providing energy, security, connectivity, maintenance and technical consultation services.",
  "We operate from Kano and Mararaba, serve Abuja and Nasarawa from our Mararaba base, and accept enquiries across Nigeria. With 7+ years of experience, we approach every job the same way: understand the problem, recommend a practical solution, install and configure it properly, and keep supporting it."
 ],
 "founders": "",
 "expertise_label": "Our expertise",
 "expertise": [
  {
   "title": "CCTV and security systems",
   "text": "Design, installation, configuration and remote viewing setup, plus fault-finding on existing systems."
  },
  {
   "title": "Solar and backup power",
   "text": "Assessment-led design, equipment selection, installation, configuration and support."
  },
  {
   "title": "Maintenance and troubleshooting",
   "text": "Inspection, repairs where applicable, optimisation, upgrades and technical support."
  },
  {
   "title": "Technical consultation",
   "text": "Honest guidance on the right solution before you buy equipment or start installation."
  },
  {
   "title": "Starlink and connectivity",
   "text": "Installation, activation help, Wi-Fi and network setup, relocation and mounting."
  },
  {
   "title": "Access control and related systems",
   "text": "Intercoms, digital door locks, access control and electric fences, subject to assessment."
  }
 ],
 "mission_label": "Our mission",
 "mission": "To understand each customer's real problem and deliver the right technical solution, with dependable service and lasting value, and to stand by our work after installation.",
 "image": "",
 "image_alt": ""
}
DEFAULT_PHOTOS = {
 "hero": [{"image": "/hero-solar.jpg", "caption": "Solar power", "focus": "auto"}, {"image": "/cctv-gate.jpg", "caption": "CCTV & security", "focus": "auto"}, {"image": "/starlink-install.jpg", "caption": "Starlink connectivity", "focus": "auto"}],
 "service_cards": {
  "cctv": {"image": "/cctv-gate.jpg", "focus": "top", "alt": "Technician installing two CCTV cameras on a gate pillar"},
  "solar": {"image": "/solar-inverter.jpg", "focus": "upper", "alt": "Solar inverter and battery storage racks in a plant room"},
  "maintenance": {"image": "/solar-roof.jpg", "focus": "center", "alt": "Technician handling cabling on a rooftop solar array"},
  "consultation": {"image": "/technician.jpg", "focus": "top", "alt": "DESS technician on site in a safety helmet and vest"}},
 "service_pages": {
  "cctv": {"image": "/cctv-gate.jpg", "alt": "Technician installing two CCTV cameras on a gate pillar beside an electric fence"},
  "solar": {"image": "/solar-inverter.jpg", "alt": "Solar inverter and battery storage racks installed in a plant room"},
  "maintenance": {"image": "/technician.jpg", "alt": "DESS technician on site wearing a safety helmet and high-visibility vest"},
  "consultation": {"image": "", "alt": ""}},
 "gallery": [
  {"image": "/solar-inverter.jpg", "category": "Solar", "alt": "Solar inverter and battery storage racks installed in a plant room"},
  {"image": "/cctv-gate.jpg", "category": "CCTV", "alt": "Technician installing two CCTV cameras on a gate pillar beside an electric fence"},
  {"image": "/starlink-install.jpg", "category": "Starlink", "alt": "Technician on a ladder installing a Starlink dish on a building"}]}
PHO = _load('photos.json') if os.path.exists(SRC + 'content/photos.json') else DEFAULT_PHOTOS
AB = _load('about.json') if os.path.exists(SRC + 'content/about.json') else DEFAULT_ABOUT
FOCUS_KEYS = ('auto', 'top', 'upper', 'center', 'bottom')
def _imgx(v, label, required=True):
    if not v:
        _need(not required, label + ' needs a photo'); return
    _need(isinstance(v, str) and re.fullmatch(r'/(images/uploads/)?[A-Za-z0-9._-]+\.(jpg|jpeg|png|webp)', v), label + ': photo path is not allowed: ' + str(v))
    _need(os.path.exists(SRC + v.lstrip('/')), label + ': photo file is missing from the repository: ' + v)
FOCUS = {'auto': None, 'top': '50% 22%', 'upper': '50% 35%', 'center': '50% 50%', 'bottom': '50% 80%'}
def _need(cond, msg):
    if not cond: raise BuildError(msg)
def _text(v, label, maxlen=2500, required=True):
    _need(isinstance(v, str), label + ' must be text')
    _need(not required or v.strip(), label + ' cannot be empty')
    _need(len(v) <= maxlen, label + ' is too long')
    _need('<' not in v and '>' not in v, label + ' cannot contain < or > characters')
    return v.strip()
def validate_content():
    for k in ('phone_display','phone_e164','whatsapp_number','email','kano_address','mararaba_address','hours_main','hours_note','hours_short','hours_opens','hours_closes','facebook','instagram','x','tiktok'):
        _need(k in S, 'Settings: missing ' + k); _text(S[k], 'Settings ' + k, 200, k != 'hours_note')
    _need(re.fullmatch(r'\+\d{8,15}', S['phone_e164']), 'Settings: phone (international format) must look like +2349049811269')
    _need(re.fullmatch(r'\d{8,15}', S['whatsapp_number']), 'Settings: WhatsApp number must be digits only, e.g. 2349049811269')
    _need(re.fullmatch(r'[^@\s]+@[^@\s]+\.[^@\s]+', S['email']), 'Settings: email address looks wrong')
    _need(re.fullmatch(r'\d\d:\d\d', S['hours_opens']) and re.fullmatch(r'\d\d:\d\d', S['hours_closes']), 'Settings: opening and closing times must look like 09:00')
    for k in ('facebook','instagram','x','tiktok'): _need(S[k].startswith('https://'), 'Settings: %s link must start with https://' % k)
    for k in ('eyebrow','h1_line1','h1_gold','lead','about','cta_title','cta_text'): _text(HM.get(k), 'Homepage ' + k)
    _need(len(HM['stats']) == 4, 'Homepage: exactly 4 numbers are needed')
    for i, x in enumerate(HM['stats']): _text(x.get('display'), 'Homepage stat %d' % (i+1), 40); _text(x.get('label'), 'Homepage stat label %d' % (i+1), 120)
    _need(1 <= len(HM['why']) <= 12 and 1 <= len(HM['faq']) <= 40, 'Homepage: reasons/FAQ list size is not valid')
    for x in HM['why']: _text(x.get('title'), 'Why title', 120); _text(x.get('text'), 'Why text', 400)
    for x in HM['faq']: _text(x.get('q'), 'FAQ question', 200); _text(x.get('a'), 'FAQ answer', 1200)
    for sl in ('cctv','solar','maintenance','consultation'):
        v = C['services'].get(sl); _need(isinstance(v, dict), 'Services: missing ' + sl)
        _text(v.get('lead'), sl + ' intro', 600); _text(v.get('note'), sl + ' note', 600)
        _need(2 <= len(v.get('covers', [])) <= 12 and len(v.get('card_bullets', [])) == 3, 'Services: %s needs 2-12 covered items and exactly 3 card points' % sl)
        for t in v['covers'] + v['card_bullets']: _text(t, sl + ' list item', 200)
    _need(1 <= len(C['services'].get('additional', [])) <= 20, 'Services: additional list size is not valid')
    for t in C['services']['additional']: _text(t, 'Additional service', 120)
    for t in C['testimonials']['items']:
        _text(t.get('name'), 'Testimonial name', 60); _text(t.get('quote'), 'Testimonial quote', 500)
        _need(t.get('language', 'en') in ('en','ha','pcm'), 'Testimonial language must be en, ha or pcm')
    if S.get('phone2_e164') or S.get('phone2_display'):
        _need(re.fullmatch(r'\+\d{8,15}', S.get('phone2_e164', '')) and _text(S.get('phone2_display', ''), 'Second phone', 40), 'Settings: the second phone needs both a display number and an international number like +2348000000000')
    def _img(v, label, required=True):
        if not v:
            _need(not required, label + ' needs a photo'); return
        _need(isinstance(v, str) and re.fullmatch(r'/(images/uploads/)?[A-Za-z0-9._-]+\.(jpg|jpeg|png|webp)', v), label + ': photo path is not allowed: ' + str(v))
        _need(os.path.exists(SRC + v.lstrip('/')), label + ': photo file is missing from the repository: ' + v)
    _need(1 <= len(PHO['hero']) <= 6, 'Site photos: the homepage slideshow needs 1 to 6 photos')
    for i, h in enumerate(PHO['hero']): _img(h.get('image'), 'Slideshow photo %d' % (i + 1)); _text(h.get('caption'), 'Slideshow caption %d' % (i + 1), 60); _need(h.get('focus', 'auto') in FOCUS, 'Slideshow focus is not valid')
    for k in ('cctv', 'solar', 'maintenance', 'consultation'):
        v = PHO['service_cards'][k]; _img(v.get('image'), k + ' card photo'); _text(v.get('alt'), k + ' card photo description', 160); _need(v.get('focus', 'auto') in FOCUS, k + ' focus is not valid')
        v = PHO['service_pages'][k]; _img(v.get('image'), k + ' page photo', False); _text(v.get('alt', ''), k + ' page photo description', 160, False)
    _need(1 <= len(PHO['gallery']) <= 12, 'Site photos: the gallery needs 1 to 12 photos')
    _need(1 <= len(AB.get('background', [])) <= 6, 'Company story: add 1 to 6 background paragraphs')
    for x in AB['background']: _text(x, 'Company story paragraph', 1200)
    _text(AB.get('eyebrow'), 'Company story small heading', 60); _text(AB.get('heading'), 'Company story heading', 120); _text(AB.get('founders', '') or '', 'Company story founders line', 200, False)
    _text(AB.get('expertise_label'), 'Expertise heading', 60); _text(AB.get('mission_label'), 'Mission heading', 60); _text(AB.get('mission'), 'Mission', 700)
    _need(3 <= len(AB.get('expertise', [])) <= 8, 'Company story: add 3 to 8 expertise cards')
    for x in AB['expertise']: _text(x.get('title'), 'Expertise title', 80); _text(x.get('text'), 'Expertise text', 300)
    _imgx(AB.get('image'), 'Company story photo', False); _text(AB.get('image_alt', '') or '', 'Company story photo description', 160, False)
    _shots = C['testimonials'].get('screenshots') or []
    _need(len(_shots) <= 8, 'Testimonials: at most 8 WhatsApp screenshots')
    for i, g in enumerate(_shots): _img(g.get('image'), 'WhatsApp screenshot %d' % (i + 1)); _text(g.get('caption', '') or '', 'WhatsApp screenshot caption %d' % (i + 1), 80, False)
    for i, g in enumerate(PHO['gallery']): _img(g.get('image'), 'Gallery photo %d' % (i + 1)); _text(g.get('category'), 'Gallery category %d' % (i + 1), 30); _text(g.get('alt'), 'Gallery description %d' % (i + 1), 160)
try:
    validate_content()
except BuildError as _e:
    print('BUILD FAILED, nothing was changed on the website:', _e); sys.exit(1)
TEL = S['phone_e164']; WA = 'https://wa.me/' + S['whatsapp_number']; MAIL = S['email']
KBJSON = json.dumps({'faq': HM['faq'], 'why': HM['why'], 'about': {k: AB.get(k) for k in ('background', 'mission', 'expertise', 'founders')}}, ensure_ascii=False).replace('<', '\\u003c')
SITEJS = json.dumps({'wa': S['whatsapp_number'], 'phone': S['phone_display'], 'email': S['email'], 'phone2': S.get('phone2_display', '')}).replace('<', '\\u003c')
SOC=f'''<div class="social"><a href="{WA}" target="_blank" rel="noopener" aria-label="DESS on WhatsApp"><svg class="ico"><use href="#i-wa"/></svg></a><a href="https://www.facebook.com/daboenergy.ss" target="_blank" rel="noopener" aria-label="DESS on Facebook"><svg class="ico"><use href="#i-fb"/></svg></a><a href="https://www.instagram.com/dabo_energy_ss" target="_blank" rel="noopener" aria-label="DESS on Instagram"><svg class="ico"><use href="#i-ig"/></svg></a><a href="https://www.tiktok.com/@dabo_ess" target="_blank" rel="noopener" aria-label="DESS on TikTok"><svg class="ico"><use href="#i-tt"/></svg></a><a href="https://x.com/dabo_energy_ss" target="_blank" rel="noopener" aria-label="DESS on X"><svg class="ico"><use href="#i-x"/></svg></a></div>'''
from urllib.parse import quote
_Q=[('I need a CCTV system installed','Hello DESS, I need a CCTV / security system installed.'),('I need solar or backup power','Hello DESS, I need a solar / backup power system.'),('I need maintenance for an existing system','Hello DESS, I need maintenance for an existing system.'),('I need Starlink installation','Hello DESS, I need a Starlink installation.'),('I want a technical consultation','Hello DESS, I would like a technical consultation.')]
WAPOP='<button class="wafab" aria-label="Chat with the DESS assistant" aria-expanded="false" aria-controls="wapop"><svg class="ico"><use href="#i-chat"/></svg><b class="dot">1</b></button><div class="wapop" id="wapop" role="dialog" aria-label="DESS assistant" hidden><div class="wahead"><span class="av">D</span><div><strong>DESS Assistant</strong><small>Automated assistant &middot; answers from DESS information</small></div><button class="waclose" aria-label="Close chat">&times;</button></div><div class="wamsgs" id="wamsgs" aria-live="polite"></div><div class="wachips" id="wachips"></div><form class="wain" id="wain"><input id="wainput" type="text" placeholder="Type your question" autocomplete="off" aria-label="Type your question"><button type="submit" aria-label="Send">&rarr;</button></form><a class="start" id="wastart" href="https://wa.me/2349049811269" target="_blank" rel="noopener">Continue on WhatsApp</a></div>'
SPRITE='''<svg width="0" height="0" style="position:absolute" aria-hidden="true">
<symbol id="i-cam" viewBox="0 0 24 24"><path d="M3 8h12v8H3zM15 11l6-3v8l-6-3M8 16v4M5 20h6"/></symbol>
<symbol id="i-sun" viewBox="0 0 24 24"><circle cx="12" cy="12" r="4.5"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3M4.9 4.9l2.1 2.1M17 17l2.1 2.1M4.9 19.1L7 17M17 7l2.1-2.1"/></symbol>
<symbol id="i-wr" viewBox="0 0 24 24"><path d="M14.5 6.5a4 4 0 005 5L20 12l-8.5 8.5a2.1 2.1 0 01-3-3L17 9l-2.5-2.5zM15 3.5a4 4 0 00-1 5"/></symbol>
<symbol id="i-chat" viewBox="0 0 24 24"><path d="M4 5h16v11H9l-5 4zM8 9h8M8 12h5"/></symbol>
<symbol id="i-phone" viewBox="0 0 24 24"><path d="M6 3h4l2 5-2.5 1.5a11 11 0 005 5L16 12l5 2v4a2 2 0 01-2 2A16 16 0 014 5a2 2 0 012-2z"/></symbol>
<symbol id="i-wa" viewBox="0 0 24 24"><path d="M3 21l1.6-4.9A8.5 8.5 0 1112 20.5a8.4 8.4 0 01-4-1zM9 8.5c0 3 3 6 6 6l1-1.5-2-1-1 .8a4 4 0 01-2-2l.8-1-1-2z"/></symbol>
<symbol id="i-mail" viewBox="0 0 24 24"><path d="M3 6h18v12H3zM3 7l9 6 9-6"/></symbol>
<symbol id="i-pin" viewBox="0 0 24 24"><path d="M12 21s7-6.2 7-11a7 7 0 10-14 0c0 4.8 7 11 7 11z"/><circle cx="12" cy="10" r="2.5"/></symbol>
<symbol id="i-home" viewBox="0 0 24 24"><path d="M3 11l9-7 9 7v9H3zM9 20v-6h6v6"/></symbol>
<symbol id="i-shop" viewBox="0 0 24 24"><path d="M4 9l1.5-5h13L20 9M4 9v11h16V9M4 9a2.7 2.7 0 005.3 0 2.7 2.7 0 005.4 0 2.7 2.7 0 005.3 0M9 20v-5h6v5"/></symbol>
<symbol id="i-corp" viewBox="0 0 24 24"><path d="M4 7h16v12H4zM9 7V4h6v3M4 13h16"/></symbol>
<symbol id="i-bed" viewBox="0 0 24 24"><path d="M3 18V7M3 14h18v4M21 14v-3a3 3 0 00-3-3h-7v6M7.5 12a1.8 1.8 0 100-3.6 1.8 1.8 0 000 3.6"/></symbol>
<symbol id="i-edu" viewBox="0 0 24 24"><path d="M12 4L2 9l10 5 10-5zM6 11.5V16c0 1.5 3 3 6 3s6-1.5 6-3v-4.5M22 9v6"/></symbol>
<symbol id="i-health" viewBox="0 0 24 24"><path d="M5 3h14a2 2 0 012 2v14a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2zM12 8v8M8 12h8"/></symbol>
<symbol id="i-factory" viewBox="0 0 24 24"><path d="M3 20V10l6 4v-4l6 4V6h3v14zM3 20h18"/></symbol>
<symbol id="i-gov" viewBox="0 0 24 24"><path d="M3 9l9-5 9 5zM5 9v9M9 9v9M15 9v9M19 9v9M3 20h18"/></symbol>
<symbol id="i-hat" viewBox="0 0 24 24"><path d="M3 18h18M5 18a7 7 0 0114 0M12 6v5M9 8v3M15 8v3"/></symbol>
<symbol id="i-clock" viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></symbol>
<symbol id="i-fb" viewBox="0 0 24 24"><path d="M16 3h-2.5A4.5 4.5 0 009 7.5V21M5 12h10"/></symbol>
<symbol id="i-ig" viewBox="0 0 24 24"><path d="M7 3h10a4 4 0 014 4v10a4 4 0 01-4 4H7a4 4 0 01-4-4V7a4 4 0 014-4zM12 8a4 4 0 100 8 4 4 0 000-8zM17.5 6.5h.01"/></symbol>
<symbol id="i-tt" viewBox="0 0 24 24"><path d="M14 3v11a4 4 0 11-4-4M14 3c.4 2.7 2.2 4.4 5 4.6"/></symbol>
<symbol id="i-x" viewBox="0 0 24 24"><path d="M4 4h4l12 16h-4zM20 4l-7.5 8.5M4 20l7.5-8.5"/></symbol>
<symbol id="i-tick" viewBox="0 0 24 24"><path d="M5 12.5l4.5 4.5L19 7.5"/></symbol>
</svg>'''
def head(title,desc,path,extra='',ld=''):
    return f'''<!DOCTYPE html>
<html lang="en-NG">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
{extra}<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{B}{path}">
<meta property="og:type" content="website">
<meta property="og:locale" content="en_NG">
<meta property="og:url" content="{B}{path}">
<meta property="og:site_name" content="Dabo Energy &amp; Security Solutions">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="{B}/solar-roof.jpg">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#060a14">
<link rel="icon" href="/favicon.ico" sizes="48x48">
<link rel="icon" type="image/png" href="/favicon-48.png" sizes="48x48">
<link rel="icon" type="image/png" href="/favicon-192.png" sizes="192x192">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<script>document.documentElement.classList.add("js")</script>
<link rel="stylesheet" href="/style.css">
{ld}</head>
<body>
<a class="skip" href="#main">Skip to content</a>
{SPRITE}
<header class="nav"><div class="progress" aria-hidden="true"></div><div class="wrap nav-in">
<a href="/" class="brand" aria-label="DESS home"><img src="/logo.png" alt="DESS - Dabo Energy &amp; Security Solutions logo" width="900" height="174"></a>
<button class="burger" aria-label="Open menu" aria-expanded="false" aria-controls="menu"><span></span><span></span><span></span></button>
<nav id="menu" class="menu" aria-label="Main"><div class="drawer-head"><span>Menu</span><button type="button" class="drawer-x" aria-label="Close menu">&times;</button></div><a href="/" class="m-home">Home</a><a href="/#solutions">Solutions</a><a href="/#why">Why DESS</a><a href="/#projects">Projects</a><a href="/blog">Blog</a><a href="/#faq">FAQ</a><a href="/#contact">Contact</a><a href="/#contact" class="btn btn-gold nav-cta">Get a Free Consultation</a><div class="drawer-foot"><a href="/#contact" class="btn btn-gold">Get a Free Consultation</a><div class="dbtns"><a href="{WA}" class="btn btn-wa"><svg class="ico"><use href="#i-wa"/></svg>WhatsApp</a><a href="tel:{TEL}" class="btn btn-glass"><svg class="ico"><use href="#i-phone"/></svg>Call</a></div><p><a href="mailto:{MAIL}">{MAIL}</a><a href="tel:{TEL}">+234 904 981 1269</a></p>{SOC}</div></nav>
</div></header>
<div class="scrim" aria-hidden="true"></div>
<main id="main">
'''
FOOT=f'''</main>
<footer class="foot"><div class="wrap foot-in">
<div><a href="/" class="brand foot-logo"><img src="/logo.png" alt="DESS logo" width="900" height="174" loading="lazy"></a><p><strong>Dabo Energy &amp; Security Solutions</strong><br>A tech solution you can trust.</p></div>
<div><h3>Primary Services</h3><a href="/cctv">CCTV &amp; Security</a><a href="/solar">Solar Power Systems</a><a href="/maintenance">Maintenance</a><a href="/consultation">Technical Consultation</a></div>
<div><h3>Additional Services</h3><span>Starlink</span><span>Intercom</span><span>Access Control</span><span>Digital Door Locks</span><span>Electric Fence</span><span>Networking</span><span>Electrical Services</span></div>
<div><h3>Company</h3><a href="/#about">About DESS</a><a href="/#why">Why DESS</a><a href="/#projects">Projects</a><a href="/blog">Blog</a><a href="/#contact">Contact</a></div>
<div><h3>Contact</h3><a href="tel:{TEL}">+234 904 981 1269</a><a href="mailto:{MAIL}">{MAIL}</a><span>Mon to Sat, 9:00 AM to 5:00 PM</span><span>Kano</span><span>Mararaba / Abuja Service Area</span>
{SOC}</div>
</div><p class="copy">© <span id="yr">2026</span> Dabo Energy &amp; Security Solutions (DESS). All rights reserved. <a href="#">Back to top &uarr;</a></p></footer>
{WAPOP}
<script>window.DESS_SITE={SITEJS};</script>
<script type="application/json" id="dess-kb">{KBJSON}</script>
<script src="/script.js"></script>
</body></html>
'''
BTNS=f'<div class="btns"><a href="/#contact" class="btn btn-gold">Get a Free Consultation</a><a href="tel:{TEL}" class="btn btn-glass"><svg class="ico"><use href="#i-phone"/></svg>Call DESS</a><a href="{WA}" class="btn btn-glass"><svg class="ico"><use href="#i-wa"/></svg>Chat on WhatsApp</a></div>'
CTA=f'''<section class="cta"><div class="wrap"><h2>{E(HM["cta_title"])}</h2><p>{E(HM["cta_text"])}</p><div class="btns"><a href="/#contact" class="btn btn-gold">Get a Free Consultation</a><a href="{WA}" class="btn btn-glass"><svg class="ico"><use href="#i-wa"/></svg>WhatsApp DESS</a></div></div></section>
'''
STEPS=['Understand Requirements','Assess the Project','Recommend the Solution','Install &amp; Configure','Test &amp; Handover','Support &amp; Maintain']
def steps(l): return '<ol class="steps">'+''.join(f'<li class="step"><span>{i+1:02d}</span><h3>{s}</h3></li>' for i,s in enumerate(l))+'</ol>'
def ul(l): return '<ul class="ticks">'+''.join(f'<li><svg class="ico"><use href="#i-tick"/></svg>{x}</li>' for x in l)+'</ul>'

# ---------- service pages ----------
P=[
dict(slug='cctv',n='01',ic='i-cam',name='CCTV &amp; Security Systems',t='CCTV Installation &amp; Security Systems in Kano, Mararaba &amp; Abuja | DESS',
 d='Professional CCTV system design, installation, configuration and maintenance for homes, offices, hotels, schools, hospitals, factories and institutions across Nigeria.',
 lead='Surveillance systems planned around your premises, then installed and configured to a professional standard for homes, offices, hotels, schools, hospitals, factories, estates and institutions.',
 img='cctv-gate.jpg',alt='Technician installing two CCTV cameras on a gate pillar beside an electric fence',
 cov=['CCTV system design and planning','Camera supply and installation','DVR/NVR recording systems','Remote viewing and monitoring setup','Security system configuration','Maintenance, upgrades and troubleshooting'],
 rel='Often combined with access control, intercom and electric fence systems.',steps=STEPS),
dict(slug='solar',n='02',ic='i-sun',name='Solar Power Systems',t='Solar Installation &amp; Backup Power in Kano, Mararaba &amp; Abuja | DESS',
 d='Solar power system design, installation, inverter and battery storage setup, configuration and maintenance for homes and businesses across Nigeria.',
 lead='Solar and backup power systems designed around your requirements. We approach solar as a system, not a product sale.',
 img='solar-inverter.jpg',alt='Solar inverter and battery storage racks installed in a plant room',
 cov=['Solar panel installation','Inverter systems','Battery storage','Backup power systems','Solar system design','Configuration, maintenance, troubleshooting and upgrades'],
 rel='System capacity and performance depend on your load requirements and the equipment specified.',
 steps=['Assessment','System Design','Equipment Selection','Installation','Configuration','Support']),
dict(slug='maintenance',n='03',ic='i-wr',name='Maintenance',t='Solar &amp; CCTV Maintenance in Nigeria | DESS',
 d='Preventive maintenance, inspection, troubleshooting, upgrades and technical support for solar, CCTV, connectivity and other installed systems.',
 lead='Installation is not the end of the relationship. DESS supports existing systems so they keep performing, which matters most for commercial and institutional sites.',
 img='technician.jpg',alt='DESS technician on site wearing a safety helmet and high-visibility vest',
 cov=['Preventive maintenance','System inspection','Troubleshooting','Repairs where applicable','System optimization','Upgrades and technical support'],
 rel='Covers solar, CCTV, connectivity and other relevant installed technology.',steps=STEPS),
dict(slug='consultation',n='04',ic='i-chat',name='Technical Consultation',t='Technical Consultation: Solar, CCTV &amp; Connectivity Planning | DESS',
 d='Get expert technical guidance on solar power, CCTV and security planning, connectivity and installation before you buy equipment.',
 lead='Work out the right technical solution before you purchase equipment or begin installation. We act as a technical partner, not only an installer.',
 img=None,alt='',
 cov=['Solar power requirements','CCTV and security planning','Connectivity','System upgrades','Maintenance planning','Technology infrastructure and installation planning'],
 rel='Phone consultations are free. Site consultations are paid, and the price depends on the location. Consultation can lead into design, supply, installation and ongoing support.',
 steps=['Share Your Requirements','Review the Premises','Compare Options','Recommend a Plan'])]
for p in P:
    _sv = C['services'][p['slug']]; p['lead'] = E(_sv['lead']); p['cov'] = [E(x) for x in _sv['covers']]; p['rel'] = E(_sv['note'])
BUL = [[E(x) for x in C['services'][p['slug']]['card_bullets']] for p in P]
for p in P:
    _sp = PHO['service_pages'][p['slug']]; p['img'] = (_sp.get('image') or '').lstrip('/') or None; p['alt'] = EA(_sp.get('alt', ''))
for p in P:
    fig=f'<figure class="media"><img src="/{p["img"]}" alt="{p["alt"]}" loading="lazy" decoding="async"></figure>' if p['img'] else ''
    h=head(p['t'],p['d'],'/'+p['slug'])+f'''<section class="phero"><div class="wrap"><p class="eyebrow"><a href="/#solutions">Solutions</a> / {p['n']}</p><h1>{p['name']}</h1><p class="lead">{p['lead']}</p>{BTNS}</div></section>
<section class="sec"><div class="wrap split{'' if p['img'] else ' one'}"><div><h2>What this covers</h2>{ul(p['cov'])}<p class="note">{p['rel']}</p></div>{fig}</div></section>
<section class="sec dark"><div class="wrap"><h2>Our approach</h2>{steps(p['steps'])}</div></section>
<section class="sec"><div class="wrap"><h2>Also from DESS</h2><div class="chips">'''+''.join(f'<a href="/{q["slug"]}">{q["name"]}</a>' for q in P if q is not p)+'</div></div></section>\n'+CTA+FOOT
    open(O+p['slug']+'.html','w').write(h)

# ---------- blog ----------
DATE='2026-10-13'
BP=[
dict(slug='solar-sizing-guide',cat='Solar',img='solar-inverter.jpg',alt='Solar inverter and battery storage racks installed in a plant room',mins=3,
 title='How to size a solar and inverter system for your home or shop',
 d='A simple way to work out your power needs before you ask for a solar quotation: appliances, daily energy, peak load, battery backup and panels.',
 ex='Most solar problems come from sizing mistakes, not bad equipment. Here is a simple way to prepare before you ask for a quotation.',
 body="""<p>Most solar problems come from sizing mistakes, not bad equipment. A few minutes of preparation will help any installer design the right system for you.</p>
<h2>Step 1: List what you want to power</h2><p>Write down every appliance you want on solar: lights, fans, TVs, fridges, freezers, pumping machines, air conditioners and office equipment. Check each label for its power in watts and note how many hours it runs each day.</p>
<h2>Step 2: Work out your daily energy use</h2><p>Energy is watts multiplied by hours. A 100 W appliance running for 10 hours uses 1,000 Wh, or 1 kWh. Add up all your appliances to get a daily total. This number drives battery size and panel count.</p>
<h2>Step 3: Find your peak load</h2><p>Your inverter must handle everything that may run at the same time, plus the extra surge some motors draw when they start, such as air conditioners, pumps and freezers. An inverter that is too small will overload and trip, often at night.</p>
<h2>Step 4: Decide how long you want backup</h2><p>Battery capacity depends on how many hours you want to run without sunlight and which loads must stay on. Different battery types allow different usable capacity, so ask your installer for the usable figure, not just the label figure.</p>
<h2>Step 5: Check panels, roof and shade</h2><p>Panels must recharge the batteries and carry daytime loads. Roof space, shading and the sunshine available at your location all matter, which is why a site assessment is worth having.</p>
<h2>Common mistakes</h2><ul><li>Counting only the average load and ignoring starting surges.</li><li>Choosing the inverter first and the battery later without checking they match.</li><li>Adding appliances later without telling the installer.</li><li>Buying on price alone, without a load assessment.</li></ul>"""),
dict(slug='solar-maintenance-checklist',cat='Solar',img='solar-roof.jpg',alt='Technician handling cabling on a rooftop solar array',mins=3,
 title='A simple maintenance checklist for your solar and inverter system',
 d='What to check yourself, how to clean panels safely, and the warning signs that mean it is time to call a technician.',
 ex='Solar systems are low effort, not no effort. Here is what to check yourself and when to call a technician.',
 body="""<p>A solar system is low effort, not no effort. Regular checks help it keep performing and help you catch small faults before they become expensive ones.</p>
<h2>Checks you can do</h2><ul><li>Look at the panels for dust, bird droppings and new shade from trees or buildings.</li><li>Read the inverter display or app for error codes or warnings.</li><li>Notice unusual noise, smells or heat around the inverter and batteries.</li><li>Keep the equipment room dry, ventilated and free of dust and insects.</li></ul>
<h2>Cleaning panels safely</h2><p>Clean when the panels are cool, in the early morning or evening. Use clean water and a soft cloth or brush, and avoid abrasive tools and strong chemicals. Do not climb onto a roof without proper safety measures.</p>
<h2>Do not open the inverter or batteries</h2><p>Solar equipment can carry dangerous voltage even when it looks switched off. Leave internal work to a trained technician.</p>
<h2>Signs it is time to call a technician</h2><ul><li>The batteries drain faster than they used to.</li><li>The inverter trips or shows repeated errors.</li><li>You see damaged or loose cables, or notice a burning smell or swollen batteries. Switch off safely if you can and call for help.</li><li>Output is clearly lower than usual.</li></ul>
<h2>Professional inspections</h2><p>A technician can check connections, protection devices, settings and battery condition. How often depends on the system and the environment.</p>"""),
dict(slug='cctv-camera-planning',cat='CCTV',img='cctv-gate.jpg',alt='Technician installing two CCTV cameras on a gate pillar beside an electric fence',mins=3,
 title='How many CCTV cameras do you need? A simple planning guide',
 d='There is no single number. Plan CCTV coverage by walking your property, ranking priority areas and avoiding blind spots.',
 ex='There is no magic number of cameras. Here is how to plan coverage around your property instead.',
 body="""<p>There is no single right number of cameras. The right number depends on your property, your risks and what you want to see. Plan coverage first, then count cameras.</p>
<h2>Walk the property, day and night</h2><p>List every entrance and exit, the perimeter, parking, storage, reception or cash points and any dark corners. Note where lighting is poor, because night footage depends on it.</p>
<h2>Rank your priorities</h2><p>Start with the places where a problem would hurt most, usually entrances, gates and valuable stock or equipment. Then extend coverage outward so you do not leave blind spots between cameras.</p>
<h2>Think about field of view and height</h2><p>A wide camera covers more area but shows less detail. Cameras at gates and doors usually need to capture faces or vehicle details, so they need a closer view. Mount cameras out of easy reach and protect them from weather.</p>
<h2>Plan the recorder and storage</h2><p>More cameras, higher resolution and longer retention all need more storage. Decide how many days of footage you want to keep and size the recorder and hard drive for it.</p>
<h2>Power, cabling and remote viewing</h2><p>Plan cable routes and a reliable power supply. If you want to view cameras on your phone, you will need a stable internet connection at the site.</p>
<h2>Respect privacy</h2><p>Avoid filming private areas such as toilets or a neighbour's property, and consider placing signs where cameras operate.</p>"""),
dict(slug='cctv-common-problems',cat='CCTV',img='technician.jpg',alt='DESS technician on site wearing a safety helmet and high-visibility vest',mins=3,
 title='Common CCTV problems and when to call a technician',
 d='No picture, blurry images, recorder not saving, cameras offline: the usual causes, what is safe to check and when to get help.',
 ex='No picture, blurry footage or a recorder that is not saving? Here are the usual causes and what to do.',
 body="""<p>CCTV only helps if it works when you need it. These are the problems we see most often and what usually causes them.</p>
<h2>Common problems and likely causes</h2><ul><li><strong>No picture:</strong> a power supply fault, a damaged cable or a loose connector.</li><li><strong>Blurry or dark images:</strong> a dirty lens, spider webs, poor focus or poor lighting.</li><li><strong>Recorder not saving footage:</strong> a full or failed hard drive, wrong settings or a wrong date and time.</li><li><strong>Cameras going offline:</strong> unstable power, overheating or loose connections.</li><li><strong>Cannot view remotely:</strong> internet or router changes, or app and network settings.</li><li><strong>Damage or tampering:</strong> cameras moved, cables cut or hit by equipment.</li></ul>
<h2>What you can check safely</h2><p>Check that the power adapter and sockets are working, restart the recorder, and gently wipe the lens. Do not open the recorder or splice cables unless you are trained to.</p>
<h2>Why regular maintenance matters</h2><p>When part of a system stays down for a long time, the site loses coverage without anyone noticing. In our <a href="/#projects">featured Kaduna case study</a>, much of a system had been out of operation after tampering, leaving only three working cameras. Regular checks catch faults early.</p>
<h2>When to call a technician</h2><p>Call for help when faults repeat, when cameras have been damaged, or when you want to upgrade or add cameras to remove blind spots.</p>"""),
]
BLOGC = _load('blog.json') if os.path.exists(SRC + 'content/blog.json') else {'images': {}}
for _p in BP:
    _bi = (BLOGC.get('images') or {}).get(_p['slug'])
    if _bi:
        _imgx(_bi.get('image'), 'Blog photo (%s)' % _p['slug']); _text(_bi.get('alt'), 'Blog photo description (%s)' % _p['slug'], 160)
        _need(_bi.get('focus', 'auto') in FOCUS_KEYS, 'Blog photo focus is not valid')
        _p['img'] = _bi['image'].lstrip('/'); _p['alt'] = EA(_bi['alt'])
        _fv = FOCUS.get(_bi.get('focus') or 'auto'); _p['fs'] = (' style="object-position:%s"' % _fv) if _fv else ''
def card(p):
    return f'<a class="bcard" href="/blog-{p["slug"]}"><div class="bimg"><img src="/{p["img"]}" alt="{p["alt"]}"{p.get("fs","")} loading="lazy" decoding="async"></div><div class="bbody"><span class="btag">{p["cat"]}</span><h3>{p["title"]}</h3><p>{p["ex"]}</p><span class="more">Read the article</span></div></a>'
for i,p in enumerate(BP):
    ld='<script type="application/ld+json">'+json.dumps({"@context":"https://schema.org","@type":"BlogPosting","headline":p['title'].replace('&amp;','&'),"datePublished":DATE,"author":{"@type":"Organization","name":"Dabo Energy & Security Solutions"},"publisher":{"@type":"Organization","name":"Dabo Energy & Security Solutions","logo":{"@type":"ImageObject","url":B+"/logo-512.png"}},"mainEntityOfPage":B+"/blog-"+p['slug'],"image":B+"/"+p['img']},ensure_ascii=False)+'</script>\n'
    rel=''.join(card(q) for q in BP if q is not p)[:0]
    others=[q for q in BP if q['cat']==p['cat'] and q is not p]+[q for q in BP if q['cat']!=p['cat']]
    h=head(p['title']+' | DESS Blog',p['d'],'/blog-'+p['slug'],'',ld)+f'<section class="phero"><div class="wrap"><p class="eyebrow"><a href="/blog">Blog</a> / {p["cat"]}</p><h1>{p["title"]}</h1><p class="lead">{p["ex"]}</p><p class="ameta">{DATE.replace("2026-10-13","13 October 2026")} &middot; {p["mins"]} min read</p></div></section><section class="sec"><div class="wrap"><article class="prose"><figure class="afig"><img src="/{p["img"]}" alt="{p["alt"]}"{p.get("fs","")} loading="lazy" decoding="async"></figure>{p["body"]}<div class="acta"><h3>Need help with your {p["cat"].lower()} project?</h3><p>Tell us about your premises and what you need. Phone consultations are free; site consultations are paid and priced by location.</p><div class="btns"><a href="/#contact" class="btn btn-gold">Get a Free Consultation</a><a href="{WA}" class="btn btn-wa">WhatsApp DESS</a></div></div></article><h2 class="more-h">Keep reading</h2><div class="bgrid">{"".join(card(q) for q in others[:2])}</div></div></section>\n'+FOOT
    open(O+'blog-'+p['slug']+'.html','w').write(h)
h=head('DESS Blog | Practical Guides on Solar Power and CCTV in Nigeria','Practical guides on solar and inverter systems, CCTV planning and maintenance from Dabo Energy & Security Solutions (DESS).','/blog')+f'<section class="phero"><div class="wrap"><p class="eyebrow">DESS Blog</p><h1>Practical guides on solar and CCTV</h1><p class="lead">Plain-language advice from the DESS team on solar power, CCTV planning and keeping systems working.</p></div></section><section class="sec"><div class="wrap"><div class="bgrid">{"".join(card(p) for p in BP)}</div></div></section>\n'+CTA+FOOT
open(O+'blog.html','w').write(h)
BLOGSEC='<section class="sec tint" id="blog"><div class="wrap"><p class="eyebrow">From the blog</p><h2>Practical guides on solar and CCTV</h2><div class="bgrid">'+''.join(card(p) for p in [BP[0],BP[2],BP[3]])+'</div><p class="blog-more"><a href="/blog" class="btn btn-blue">View all articles</a></p></div></section>\n'
# ---------- home ----------
ld=json.dumps({"@context":"https://schema.org","@type":["LocalBusiness","Organization"],"name":"Dabo Energy & Security Solutions","alternateName":["DESS","DESS Nigeria","Dabo Energy and Security Solutions"],"slogan":"A tech solution you can trust.",
"description":"Energy, security and connectivity solutions: CCTV, solar power, maintenance and technical consultation for homes, businesses and institutions in Nigeria.",
"url":B+"/","logo":B+"/logo-512.png","image":B+"/solar-roof.jpg","telephone":TEL,"email":MAIL,
"areaServed":[{"@type":"State","name":"Kano"},{"@type":"State","name":"Nasarawa"},{"@type":"AdministrativeArea","name":"Abuja"},{"@type":"Country","name":"Nigeria"}],
"address":[{"@type":"PostalAddress","streetAddress":"No. 35 France Road, Sabon Gari","addressRegion":"Kano State","addressCountry":"NG"},{"@type":"PostalAddress","streetAddress":"Old Orange Market Street, Mararaba, Karu LGA","addressRegion":"Nasarawa State","addressCountry":"NG"}],
"openingHoursSpecification":[{"@type":"OpeningHoursSpecification","dayOfWeek":["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"],"opens":"09:00","closes":"17:00"}],"sameAs":["https://www.facebook.com/daboenergy.ss","https://www.instagram.com/dabo_energy_ss","https://x.com/dabo_energy_ss","https://www.tiktok.com/@dabo_ess"]},indent=1,ensure_ascii=False)
ver='<meta name="google-site-verification" content="Flggp0OAoR3ZLfkzdXoOFVyLNwlf65vivNqHBnzhyiU" />\n<meta name="google-site-verification" content="FNXQPSIhmZA32Rh-jYoWv8A7KRaA6-WDHWeEcsu5f3Y" />\n'
IMGS={'cctv':('cctv-gate.jpg','50% 22%','Technician installing two CCTV cameras on a gate pillar'),'solar':('solar-inverter.jpg','50% 35%','Solar inverter and battery storage racks in a plant room'),'maintenance':('solar-roof.jpg','50% 50%','Technician handling cabling on a rooftop solar array'),'consultation':('technician.jpg','50% 22%','DESS technician on site in a safety helmet and vest')}
IMGS = {k: (v['image'].lstrip('/'), FOCUS.get(v.get('focus') or 'auto') or '50% 50%', EA(v['alt'])) for k, v in PHO['service_cards'].items()}
def card(p,b):
    f,pos,alt=IMGS[p['slug']]
    return f'<article class="card pcard"><div class="cimg"><img src="/{f}" alt="{alt}" style="object-position:{pos}" loading="lazy" decoding="async"></div><div class="cbody"><span class="num">{p["n"]}</span><svg class="ico"><use href="#{p["ic"]}"/></svg><h3>{p["name"]}</h3><p>{p["lead"].split(". ")[0].rstrip(".")}.</p>{ul(b)}<a class="more" href="/{p["slug"]}">Explore {p["name"]}</a></div></article>'
SERVE=[('home','Residential'),('shop','Commercial'),('corp','Corporate'),('bed','Hospitality'),('edu','Education'),('health','Healthcare'),('factory','Industrial'),('gov','Government &amp; Institutions'),('hat','Construction &amp; Property')]
WHY=[('Technical approach','We design systems around your requirements, not around the equipment on the shelf.'),('Professional installation','Neat installation, correct configuration and a clean finish.'),('Equipment selection','We help you specify dependable equipment suited to the project.'),('Support beyond installation','Maintenance, troubleshooting and upgrades for systems we install.'),('Experience','Over seven years in the industry, with 150+ projects completed.'),('Customer-focused service','Clear communication from first enquiry to handover.')]
ADD=['Starlink installation and activation','Intercom installation','Digital door locks','Access control','Electric fence systems','Networking','Wi-Fi infrastructure','Electrical installation and maintenance']
BR=['Starlink','Hikvision','Dahua','TP-Link','Ubiquiti','Growatt','Felicity','MUST','Deye','Cell American']
Q=[('Ibrahim A.','“DESS did a very neat solar installation. Good service and professional team.”','en'),('Musa B.','“Aiki yayi kyau sosai. Sun gama komai cikin lokaci, kuma farashin ya yi kyau.”','ha'),('Amina S.','“DESS installed our CCTV perfectly. Very professional and reliable.”','en'),('Emeka O.','“These guys sabi wetin dem dey do. Fast service and clean installation.”','pcm')]
FAQ=[('Do you install solar systems?','Yes. DESS designs and installs solar and backup power systems, including panels, inverters and battery storage, configured to your requirements.'),
('Do you install CCTV systems for businesses?','Yes. We design and install CCTV systems for offices, shops, hotels, schools, hospitals, factories and estates, including DVR/NVR recording and remote viewing setup.'),
('Do you provide CCTV maintenance?','Yes. We inspect, troubleshoot, repair where applicable and upgrade existing CCTV systems.'),
('Can DESS handle large commercial projects?','DESS is equipped and positioned to take on commercial and institutional projects, from planning and system design to installation, configuration and support. Share your requirements and we will discuss the scope with you.'),
('Do you serve Abuja?','Yes. Our Mararaba base serves Nasarawa, Abuja and surrounding areas.'),
('Do you serve outside Kano and Abuja?','Yes. DESS can take on projects nationwide and outside Nigeria depending on requirements. Pricing may vary with location, logistics and scope.'),
('Do you install Starlink?','Yes. We handle Starlink equipment supply, installation, activation assistance, Wi-Fi and network configuration, relocation and mounting, troubleshooting and maintenance, and subscription enquiries. Contact us for current plan details and the purchase or renewal process.'),
('Do you provide maintenance after installation?','Yes. Maintenance and technical support are a core DESS service for solar, CCTV, connectivity and other installed systems.'),
('Can DESS provide technical consultation?','Yes. We can advise on the right solution before you buy equipment or begin installation.'),
('Is technical consultation free?','Phone consultations are free. Site consultations are paid, and the price depends on the location.'),
('Do you work with hotels, schools and hospitals?','We are equipped to serve these sectors. Requirements differ between them, so we begin by understanding your premises and needs.')]
def _fstyle(f):
    v = FOCUS.get(f or 'auto')
    return ' style="object-position:%s"' % v if v else ''
def _dims(path):
    try:
        from PIL import Image as _PI
        with _PI.open(SRC + path.lstrip('/')) as im: return ' width="%d" height="%d"' % im.size
    except Exception: return ''
HEROIMGS = ''.join('<img%s src="%s" alt=""%s data-cap="%s"%s>' % (' class="on"' if i == 0 else '', EA(h['image']), ' fetchpriority="high"' if i == 0 else ' loading="lazy"', EA(h['caption']), _fstyle(h.get('focus'))) for i, h in enumerate(PHO['hero']))
HERODOTS = '<div class="hero-dots" aria-hidden="true">' + '<i></i>' * len(PHO['hero']) + '<span class="cap">' + E(PHO['hero'][0]['caption']) + '</span></div>'
GALLERY = '\n'.join('<figure class="shot" data-category="%s"><img src="%s"%s loading="lazy" decoding="async" alt="%s"><figcaption>%s</figcaption></figure>' % (EA(g['category']), EA(g['image']), _dims(g['image']), EA(g['alt']), E(g['category'])) for g in PHO['gallery'])
def _shot(i, g):
    cap = (g.get('caption') or '').strip()
    alt = 'WhatsApp message from a customer' + (': ' + cap if cap else '') + ' (photo %d)' % (i + 1)
    return '<figure class="wa-card"><button type="button" class="wa-shot" data-full="%s" aria-label="Enlarge screenshot %d"><img src="%s"%s alt="%s" loading="lazy" decoding="async"></button>%s</figure>' % (EA(g['image']), i + 1, EA(g['image']), _dims(g['image']), EA(alt), ('<figcaption>%s</figcaption>' % E(cap)) if cap else '')
_SH = C['testimonials'].get('screenshots') or []
WASEC = ('<div class="wa-reviews"><h3 class="sub">Real messages from customers on WhatsApp</h3><div class="wa-row">' + ''.join(_shot(i, g) for i, g in enumerate(_SH)) + '</div></div>') if _SH else ''
def _about_html():
    ps = ''.join(('<p class="big">%s</p>' if i == 0 else '<p>%s</p>') % E(t) for i, t in enumerate(AB['background']))
    fo = ('<p class="founders">%s</p>' % E(AB['founders'])) if (AB.get('founders') or '').strip() else ''
    im = ('<figure class="co-img"><img src="%s"%s alt="%s" loading="lazy" decoding="async"></figure>' % (EA(AB['image']), _dims(AB['image']), EA(AB.get('image_alt', '')))) if AB.get('image') else ''
    xp = ''.join('<div class="xp"><span>%02d</span><h3>%s</h3><p>%s</p></div>' % (i + 1, E(x['title']), E(x['text'])) for i, x in enumerate(AB['expertise']))
    return '<section class="sec dark company" id="company"><div class="wrap"><p class="eyebrow">%s</p><h2>%s</h2><div class="co-grid%s"><div class="co-text">%s%s</div>%s</div><h3 class="sub co-sub">%s</h3><div class="xgrid">%s</div><div class="mission"><span class="mlabel">%s</span><p>%s</p></div></div></section>\n' % (E(AB['eyebrow']), E(AB['heading']), ' has-img' if im else '', ps, fo, im, E(AB['expertise_label']), xp, E(AB['mission_label']), E(AB['mission']))
ABOUTSEC = _about_html()
def _stat(x):
    d = str(x['display']).strip(); mm = re.fullmatch(r'(\d+)(\+?)', d)
    if mm: return '<div class="stat"><b data-count="%s" data-suffix="%s">%s</b><span>%s</span></div>' % (mm.group(1), mm.group(2), E(d), E(x['label']))
    return '<div class="stat"><b>%s</b><span>%s</span></div>' % (E(d), E(x['label']))
STATS = ''.join(_stat(x) for x in HM['stats'])
WHY = [(E(w['title']), E(w['text'])) for w in HM['why']]
FAQ = [(E(f['q']), E(f['a'])) for f in HM['faq']]
ADD = [E(x) for x in C['services']['additional']]
Q = [(E(t['name']), '\u201c' + E(t['quote']) + '\u201d', t.get('language', 'en')) for t in C['testimonials']['items'] if t.get('show', True)]
TL=[('Understand Requirements','We start with a conversation about your premises, your needs and your priorities.'),('Assess the Project','We review the site and the load or coverage required, in person where it is needed.'),('Recommend the Solution','You receive a clear recommendation on the system and equipment that suits the project.'),('Install &amp; Configure','Our technicians install and configure the system to a professional standard.'),('Test &amp; Handover','We test the system and walk you through how to use it.'),('Support &amp; Maintain','Maintenance, troubleshooting and upgrades stay available after handover.')]
TLH='<ol class="tl">'+''.join(f'<li><span class="n">{i+1:02d}</span><div><h3>{a}</h3><p>{b}</p></div></li>' for i,(a,b) in enumerate(TL))+'</ol>'
CASE='''<article class="case"><div class="case-v"><video controls playsinline preload="metadata" poster="/case-kaduna-poster.jpg" width="720" height="1280" aria-label="Video: CCTV restoration, system upgrade and ongoing maintenance at a construction company facility in Kaduna"><source src="/case-kaduna-cctv.mp4" type="video/mp4">Your browser cannot play this video.</video></div>
<div class="case-t"><p class="eyebrow">Featured case study</p><h3>CCTV restoration, system upgrade and ongoing maintenance</h3>
<div class="case-chips"><span>Construction company</span><span>Kaduna, Nigeria</span><span>CCTV &amp; Security</span></div>
<div class="case-body" id="case-body"><div class="case-b"><h4>The challenge</h4><p>At a CCECC facility in Kaduna State, much of the existing CCTV system had been out of operation for an extended period after heavy equipment tampered with the installation. Only three cameras still worked, leaving large gaps in coverage. The head of the facility engaged DESS to investigate and resolve the problem.</p></div>
<div class="case-b"><h4>Our approach: diagnose, restore, strengthen</h4><p>We troubleshot the faults, assessed the existing equipment and the site&rsquo;s surveillance needs, then recommended a practical solution to improve coverage and address blind spots.</p>
<ul class="ticks"><li><svg class="ico"><use href="#i-tick"/></svg><span><strong>System troubleshooting:</strong> identifying the faults behind the downtime</span></li><li><svg class="ico"><use href="#i-tick"/></svg><span><strong>Camera restoration:</strong> bringing cameras back online wherever feasible</span></li><li><svg class="ico"><use href="#i-tick"/></svg><span><strong>Equipment replacement:</strong> replacing selected outdated cameras</span></li><li><svg class="ico"><use href="#i-tick"/></svg><span><strong>Coverage expansion:</strong> adding cameras to cover unmonitored areas</span></li></ul></div>
<div class="case-b"><h4>The outcome: better coverage, stronger monitoring</h4><p>Through targeted repairs, strategic replacements and additional cameras, DESS helped restore the facility&rsquo;s surveillance capability and reduce blind spots. DESS continues to provide monthly maintenance checks to support the ongoing reliability of the system.</p></div>
<p class="case-end">We find the problem, deliver the solution, and stand by our work.</p></div><button type="button" class="case-btn" aria-expanded="false" aria-controls="case-body"><span>Read more</span></button></div></article>
'''
import os
from PIL import Image as _I
def _logo(n):
    f=n.lower().replace(' ','-')
    p=SRC+f'logo-{f}.jpg'
    if not os.path.exists(p): return f'<div class="logo"><b>{n}</b></div>'
    w,h=_I.open(p).size
    mh={'starlink':64,'felicity':62,'tp-link':50,'ubiquiti':52,'dahua':50,'deye':48,'cell-american':34,'hikvision':34,'growatt':44,'must':44}.get(f,44)
    return f'<div class="logo"><img src="/logo-{f}.jpg" alt="{n}" width="{w}" height="{h}" style="max-height:{mh}px" decoding="async"></div>'
LOGOS=''.join(_logo(b) for b in BR)
LOGOS2=LOGOS.replace('class="logo"','class="logo" aria-hidden="true"')

# ---------- project updates (from CMS) ----------
def _load_updates():
    items = []
    for pth in sorted(glob.glob(SRC + 'content/updates/*.json')):
        try:
            with open(pth, encoding='utf-8') as f: d = json.load(f)
        except Exception as e:
            raise BuildError('Cannot read %s: %s' % (os.path.basename(pth), e))
        if d.get('published', True) is False: continue
        name = os.path.basename(pth)[:-5]
        _need(re.fullmatch(r'[A-Za-z0-9._-]+', name), 'Update file name has unusual characters: ' + name)
        _text(d.get('title'), name + ' title', 120); _text(d.get('summary'), name + ' summary', 4000)
        _text(d.get('category', 'Other'), name + ' category', 40); _text(d.get('location', '') or '', name + ' location', 80, False)
        ph = d.get('photos') or []
        _need(len(ph) <= 12, name + ' has too many photos (max 12)')
        for x in ph:
            _need(isinstance(x, str) and re.fullmatch(r'/images/uploads/[A-Za-z0-9._-]+\.(jpg|jpeg|png|webp)', x), name + ': photo path is not allowed: ' + str(x))
            _need(os.path.exists(SRC + x.lstrip('/')), name + ': photo file is missing: ' + x)
        dt = (d.get('date') or '')[:10]
        if dt:
            try: datetime.date.fromisoformat(dt)
            except ValueError: raise BuildError(name + ': date is not valid')
        d.update(_id=name, _date=dt, photos=ph); items.append(d)
    items.sort(key=lambda d: d['_date'], reverse=True)
    return items
try:
    UPD = _load_updates()
except BuildError as _e:
    print('BUILD FAILED, nothing was changed on the website:', _e); sys.exit(1)
def _fmt(dt):
    return datetime.date.fromisoformat(dt).strftime('%-d %B %Y') if dt else ''
def _ucard(d):
    img = '<img src="%s" alt="%s" loading="lazy" decoding="async">' % (EA(d['photos'][0]), EA(d['title'])) if d['photos'] else ''
    short = d['summary'].strip().split('\n')[0]
    short = short if len(short) <= 150 else short[:147].rsplit(' ', 1)[0] + '...'
    return '<a class="bcard" href="/updates#%s"><div class="bimg%s">%s<span class="btag">%s</span></div><div class="bbody"><h3>%s</h3><p>%s</p><span class="more">Read more</span></div></a>' % (EA(d['_id']), '' if img else ' noimg', img, E(d.get('category', 'Other')), E(d['title']), E(short))
UPDSEC = ('<div class="upd"><h3 class="sub">Latest project updates</h3><div class="bgrid three">' + ''.join(_ucard(d) for d in UPD[:3]) + '</div><p style="margin-top:22px"><a class="btn btn-blue" href="/updates">View all updates</a></p></div>') if UPD else ''
H=head('DESS | Dabo Energy &amp; Security Solutions: CCTV, Solar &amp; Maintenance','DESS (Dabo Energy &amp; Security Solutions) provides CCTV, solar power, maintenance, technical consultation and Starlink services for homes, businesses and institutions in Kano, Abuja and across Nigeria.','/',ver,f'<script type="application/ld+json">\n{ld}\n</script>\n'+'<script type="application/ld+json">'+'{"@context": "https://schema.org", "@type": "WebSite", "name": "Dabo Energy & Security Solutions", "alternateName": ["DESS", "DESS Nigeria", "Dabo Energy and Security Solutions"], "url": "https://dess.com.ng/"}'+'</script>\n')
H+=f'''<section class="hero"><div class="hero-bg">{HEROIMGS}</div><div class="wrap hero-in"><div>
<p class="eyebrow">{E(HM["eyebrow"])}</p><h1>{E(HM["h1_line1"])} <span class="gold">{E(HM["h1_gold"])}</span></h1>
<p class="lead">{E(HM["lead"])}</p>{BTNS}{HERODOTS}</div></div></section>
<section class="stats" aria-label="DESS in numbers"><div class="wrap stats-in">{STATS}</div></section>
<section class="sec" id="solutions"><div class="wrap"><p class="eyebrow">Primary solutions</p><h2>Systems designed around your requirements</h2><div class="pgrid">{''.join(card(p,b) for p,b in zip(P,BUL))}</div></div></section>
<section class="sec dark" id="serve"><div class="wrap"><p class="eyebrow">Who we serve</p><h2>Built for homes, businesses and institutions</h2><div class="tiles">{''.join(f'<div class="tile"><span class="ti"><svg class="ico"><use href="#i-{k}"/></svg></span><b>{n}</b></div>' for k,n in SERVE)}</div></div></section>
<section class="sec" id="why"><div class="wrap"><p class="eyebrow" id="about">About DESS</p><h2>Why DESS</h2><p class="big">{E(HM["about"])}</p><div class="whygrid">{''.join(f'<div class="why"><h3>{a}</h3><p>{b}</p></div>' for a,b in WHY)}</div></div></section>
{ABOUTSEC}<section class="sec tint"><div class="wrap"><p class="eyebrow">Additional capabilities</p><h2>Related technical services</h2><div class="chips plain">{''.join(f'<span>{a}</span>' for a in ADD)}</div>
<h3 class="sub">Brands and technologies we work with include</h3><div class="mq"><div class="mq-track">{LOGOS}{LOGOS2}</div></div><p class="note">Logos are trademarks of their respective owners, shown to indicate the equipment we work with. They do not imply endorsement or official partnership. Equipment is specified according to project requirements.</p></div></section>
<section class="sec dark proc" id="process"><div class="wrap proc-in"><div class="proc-l"><p class="eyebrow">How we work</p><h2>From first conversation to handover</h2><p class="big">Six clear steps, so you always know what happens next.</p><a href="/#contact" class="btn btn-gold">Start with a free consultation</a></div>{TLH}</div></section>
<section class="sec" id="projects"><div class="wrap"><p class="eyebrow">Projects</p><h2>Our work</h2>{CASE}<div class="gallery">
{GALLERY}</div>
<!-- Future case study card: category, location, client type, scope, challenge, solution, result, photos/video -->
<p class="note">More project case studies will be added here.</p>{UPDSEC}</div></section>
<section class="sec tint" id="testimonials"><div class="wrap"><p class="eyebrow">Testimonials</p><h2>What customers say</h2><div class="quotes">{''.join(f'<blockquote class="quote"><p lang="{l}">{t}</p><cite>{n}</cite></blockquote>' for n,t,l in Q)}</div>{WASEC}</div></section>
<section class="sec dark globe-sec" id="coverage"><div class="wrap globe-in"><div><p class="eyebrow">Where we work</p><h2>Based in Kano and Mararaba. Working nationwide.</h2><ul class="locs"><li><b>Kano</b><span>No. 35 France Road, Sabon Gari, Kano State</span></li><li><b>Mararaba</b><span>Our base for projects across Nasarawa, Abuja and surrounding areas</span></li><li><b>Nationwide &amp; international</b><span>Projects elsewhere are quoted by location, logistics and scope</span></li></ul></div><div class="globe-wrap"><canvas id="globe" role="img" aria-label="Animated globe marking Kano, Abuja and Nasarawa in Nigeria"></canvas></div></div></section>
<section class="sec" id="faq"><div class="wrap narrow"><p class="eyebrow">FAQ</p><h2>Common questions</h2>{''.join(f'<details><summary>{q}</summary><p>{a}</p></details>' for q,a in FAQ)}</div></section>
{BLOGSEC}{CTA}<section class="sec tint" id="contact"><div class="wrap contact"><div><p class="eyebrow">Contact</p><h2>Let’s discuss your project</h2>
<p class="co"><strong>Dabo Energy &amp; Security Solutions (DESS)</strong></p>
<ul class="clist"><li><svg class="ico"><use href="#i-phone"/></svg><a href="tel:{TEL}">+234 904 981 1269</a></li><li class="wa"><svg class="ico"><use href="#i-wa"/></svg><a href="{WA}">WhatsApp: +234 904 981 1269</a></li><li><svg class="ico"><use href="#i-mail"/></svg><a href="mailto:{MAIL}">{MAIL}</a></li><li><svg class="ico"><use href="#i-clock"/></svg><span><strong>Monday to Saturday, 9:00 AM to 5:00 PM</strong><br>Sunday emergency work may be available by arrangement</span></li></ul>
<h3 class="sub">Locations</h3>
<ul class="clist"><li><svg class="ico"><use href="#i-pin"/></svg><span><strong>Kano</strong><br>No. 35 France Road, Sabon Gari, Kano State</span></li><li><svg class="ico"><use href="#i-pin"/></svg><span><strong>Mararaba</strong><br>Old Orange Market Street, Mararaba, Karu LGA, Nasarawa State</span></li></ul>
<p class="note">Mararaba is our base for projects across Nasarawa and Abuja. We also take on projects nationwide and internationally; pricing may vary with location, logistics and scope.</p></div>
<form id="form" action="https://formspree.io/f/xkjowdka" method="POST" novalidate>
<label>Name<input name="name" type="text" autocomplete="name" required></label>
<label>Phone Number<input name="phone" type="tel" autocomplete="tel" required></label>
<label>Email<input name="email" type="email" autocomplete="email" required></label>
<label>Service Needed<select name="service" required><option value="">Select a service</option><option>CCTV &amp; Security Systems</option><option>Solar Power Systems</option><option>Maintenance</option><option>Technical Consultation</option><option>Starlink / Connectivity</option><option>Other Technical Services</option></select></label>
<label>Message<textarea name="message" rows="4" required></textarea></label>
<button type="submit" class="btn btn-blue">Request Consultation</button><p class="status" id="status" role="status" aria-live="polite"></p><p class="or">Prefer WhatsApp?</p><a class="btn btn-wa" href="{WA}">Chat with DESS on WhatsApp</a></form></div></section>
'''+FOOT
open(O+'index.html','w').write(H)

if UPD:
    def _uitem(d):
        paras = ''.join('<p>%s</p>' % E(x.strip()) for x in d['summary'].split('\n') if x.strip())
        meta = ' &middot; '.join(x for x in [_fmt(d['_date']), E(d.get('category', 'Other')), E(d.get('location', '') or '')] if x)
        figs = ''.join('<figure><img src="%s" alt="%s" loading="lazy" decoding="async"></figure>' % (EA(p), EA('%s, photo %d' % (d['title'], i + 1))) for i, p in enumerate(d['photos']))
        return '<article class="upd-item" id="%s"><p class="meta2">%s</p><h2>%s</h2>%s%s</article>' % (EA(d['_id']), meta, E(d['title']), paras, ('<div class="upd-photos">' + figs + '</div>') if figs else '')
    open(O + 'updates.html', 'w').write(head('Project Updates | DESS', 'Latest solar, CCTV and connectivity project updates from Dabo Energy &amp; Security Solutions (DESS).', '/updates') + '<section class="phero"><div class="wrap"><p class="eyebrow">Projects</p><h1>Project updates</h1><p class="lead">Recent work from the DESS team.</p></div></section>\n<section class="sec"><div class="wrap narrow">' + ''.join(_uitem(d) for d in UPD) + '</div></section>\n' + CTA + FOOT)
else:
    open(O + 'updates.html', 'w').write(head('Project Updates | DESS', 'Project updates from Dabo Energy &amp; Security Solutions (DESS).', '/updates', '<meta name="robots" content="noindex">\n') + '<section class="phero"><div class="wrap"><p class="eyebrow">Projects</p><h1>Project updates</h1><p class="lead">New project updates will appear here soon.</p></div></section>\n' + CTA + FOOT)
urls=['/','/cctv','/solar','/maintenance','/consultation','/blog']+(['/updates'] if UPD else [])+['/blog-'+p['slug'] for p in BP]
open(O+'sitemap.xml','w').write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+''.join(f'  <url><loc>{B}{u}</loc><lastmod>2026-10-06</lastmod></url>\n' for u in urls)+'</urlset>\n')
open(O+'robots.txt','w').write(f'User-agent: *\nAllow: /\nDisallow: /admin/\n\nSitemap: {B}/sitemap.xml\n')

# ---------- apply Settings values, verify, publish ----------
DEF = {'phone_display': '+234 904 981 1269', 'phone_e164': '+2349049811269', 'whatsapp_number': '2349049811269', 'email': 'daboenergyss@gmail.com',
       'kano_address': 'No. 35 France Road, Sabon Gari, Kano State', 'mararaba_address': 'Old Orange Market Street, Mararaba, Karu LGA, Nasarawa State',
       'hours_main': 'Monday to Saturday, 9:00 AM to 5:00 PM', 'hours_note': 'Sunday emergency work may be available by arrangement', 'hours_short': 'Mon to Sat, 9:00 AM to 5:00 PM',
       'facebook': 'https://www.facebook.com/daboenergy.ss', 'instagram': 'https://www.instagram.com/dabo_energy_ss', 'x': 'https://x.com/dabo_energy_ss', 'tiktok': 'https://www.tiktok.com/@dabo_ess'}
def fix(t):
    if S.get('phone2_e164') and S.get('phone2_display'):
        p2e, p2d = S['phone2_e164'], E(S['phone2_display'])
        a1 = '<li><svg class="ico"><use href="#i-phone"/></svg><a href="tel:+2349049811269">+234 904 981 1269</a></li>'
        t = t.replace(a1, a1 + '<li><svg class="ico"><use href="#i-phone"/></svg><a href="tel:%s">%s</a></li>' % (p2e, p2d))
        t = t.replace('<a href="tel:+2349049811269">+234 904 981 1269</a><a href="mailto:daboenergyss@gmail.com">', '<a href="tel:+2349049811269">+234 904 981 1269</a><a href="tel:%s">%s</a><a href="mailto:daboenergyss@gmail.com">' % (p2e, p2d))
        t = t.replace('<a href="tel:+2349049811269">+234 904 981 1269</a></p>', '<a href="tel:+2349049811269">+234 904 981 1269</a><a href="tel:%s">%s</a></p>' % (p2e, p2d))
        t = t.replace('"telephone": "+2349049811269"', '"telephone": ["+2349049811269", "%s"]' % p2e)
    pairs = [('wa.me/' + DEF['whatsapp_number'], 'wa.me/' + S['whatsapp_number']), (DEF['phone_e164'], S['phone_e164']), (DEF['phone_display'], E(S['phone_display'])), (DEF['email'], S['email'])]
    for k in ('kano_address', 'mararaba_address', 'hours_main', 'hours_note', 'hours_short'): pairs.append((DEF[k], E(S[k])))
    for k in ('facebook', 'instagram', 'x', 'tiktok'): pairs.append((DEF[k], EA(S[k])))
    for k, tail in (('kano_address', ', Kano State'), ('mararaba_address', ', Nasarawa State')):
        old = DEF[k][:-len(tail)]; new = S[k][:-len(tail)] if S[k].endswith(tail) else S[k]
        pairs.append(('"streetAddress": "%s"' % old, '"streetAddress": "%s"' % new.replace('"', '')))
    pairs += [('"opens": "09:00"', '"opens": "%s"' % S['hours_opens']), ('"closes": "17:00"', '"closes": "%s"' % S['hours_closes'])]
    for a, b in pairs:
        if a != b: t = t.replace(a, b)
    return t
GENERATED = [f for f in os.listdir(O) if f.endswith(('.html', '.xml', '.txt'))]
for f in GENERATED:
    p = O + f
    with open(p, encoding='utf-8') as fh: t = fh.read()
    with open(p, 'w', encoding='utf-8') as fh: fh.write(fix(t))
def verify():
    for f in ('index.html', 'cctv.html', 'solar.html', 'maintenance.html', 'consultation.html', 'blog.html', 'sitemap.xml', 'robots.txt'):
        _need(os.path.exists(O + f), 'Build did not create ' + f)
    ids = set()
    for f in GENERATED:
        if not f.endswith('.html'): continue
        t = open(O + f, encoding='utf-8').read()
        _need(re.search(r'<title>[^<]{5,}</title>', t) and '<h1' in t and '</html>' in t, f + ': page structure looks broken')
        _need('{E(' not in t and '{S[' not in t and '{HM[' not in t and 'PASTE_' not in t, f + ': unfilled placeholder found')
        if f == 'index.html': ids = set(re.findall(r'id="([^"]+)"', t))
    for need in ('solutions', 'why', 'projects', 'faq', 'contact', 'testimonials', 'about'): _need(need in ids, 'Homepage section missing: ' + need)
    missing = {}
    for f in GENERATED:
        if not f.endswith('.html'): continue
        t = open(O + f, encoding='utf-8').read()
        for h in set(re.findall(r'(?:href|src|poster)="(/[^"#?]*)', t)):
            if h == '/': continue
            ok = os.path.exists(SRC + h.lstrip('/')) or os.path.exists(O + h.lstrip('/')) or os.path.exists(O + h.lstrip('/') + '.html') or os.path.exists(SRC + h.lstrip('/') + '.html')
            if not ok: missing.setdefault(h, []).append(f)
    _need(not missing, 'These files are missing from your GitHub repository. Please upload them to the main folder: ' + ', '.join(sorted(m.lstrip('/') for m in missing)))
try:
    verify()
except BuildError as e:
    print('BUILD FAILED, nothing was changed on the website:', e); shutil.rmtree(BUILD, ignore_errors=True); sys.exit(1)
if '--check' in sys.argv:
    print('CHECK OK (%d files, %d updates)' % (len(GENERATED), len(UPD)))
else:
    for f in GENERATED: shutil.copyfile(O + f, SRC + f)
    print('BUILD OK, published %d files' % len(GENERATED))
shutil.rmtree(BUILD, ignore_errors=True)
