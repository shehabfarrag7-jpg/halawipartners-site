#!/usr/bin/env python3
"""Builds the Halawi & Partners site from content/ and media/ into public/.
Edit content through the CMS at /admin, or edit the JSON files directly."""
import json, os, html, re, shutil, datetime, glob
from PIL import Image, ImageOps
import markdown

ROOT = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.join(ROOT, 'public')
CONTENT = os.path.join(ROOT, 'content')
DOMAIN = 'https://halawipartners.com'

def load(name):
    with open(os.path.join(CONTENT, name), encoding='utf-8') as fh:
        return json.load(fh)

def tel(p):
    return re.sub(r'[^0-9+]', '', p or '')

SETTINGS = load('settings.json')
LI_CO = SETTINGS['linkedin_company']
LI_SF = SETTINGS['linkedin_ceo']
EMAIL_S, EMAIL_K = SETTINGS['cairo_email'], SETTINGS['sidon_email']
PHONE_S, PHONE_K = SETTINGS['cairo_phone'], SETTINGS['sidon_phone']
PHONE_S_RAW, PHONE_K_RAW = tel(PHONE_S), tel(PHONE_K)
NAME_S, NAME_K = SETTINGS['cairo_name'], SETTINGS['sidon_name']
ROLE_S, ROLE_K = SETTINGS['cairo_role'], SETTINGS['sidon_role']
YEAR = datetime.date.today().year
import hashlib
CSS_V = hashlib.md5(open(os.path.join(ROOT, 'static', 'assets', 'site.css'), 'rb').read()).hexdigest()[:10]
CF_TOKEN = SETTINGS.get('cloudflare_analytics_token') or ''
ANALYTICS = (f"""<script defer src="https://static.cloudflareinsights.com/beacon.min.js" data-cf-beacon='{{"token": "{CF_TOKEN}"}}'></script>""" if CF_TOKEN else '')

e = html.escape

def dims(name, w=800):
    p = f'{SITE}/assets/img/{name}-{w}.webp'
    im = Image.open(p)
    return im.size

def img(name, alt, sizes='(max-width: 900px) 100vw, 50vw', cls='', loading='lazy', root='../'):
    w, h = dims(name, 800)
    big = f'{SITE}/assets/img/{name}-1600.webp'
    srcset = f'{root}assets/img/{name}-800.webp 800w'
    if os.path.exists(big):
        bw, _ = Image.open(big).size
        srcset += f', {root}assets/img/{name}-1600.webp {bw}w'
    c = f' class="{cls}"' if cls else ''
    return (f'<img{c} src="{root}assets/img/{name}-800.webp" srcset="{srcset}" sizes="{sizes}" '
            f'width="{w}" height="{h}" alt="{e(alt)}" loading="{loading}" decoding="async">')

NAV = [('services/', 'Services'), ('steel-detailing/', 'Steel detailing'), ('projects/', 'Projects'), ('insights/', 'Insights'), ('about/', 'About')]

ORG = {
    '@context': 'https://schema.org',
    '@type': 'ProfessionalService',
    '@id': DOMAIN + '/#org',
    'name': 'Halawi & Partners',
    'url': DOMAIN + '/',
    'logo': DOMAIN + '/assets/brand/logo-navy-128.png',
    'image': DOMAIN + '/assets/brand/og-image.png',
    'description': 'Multidisciplinary engineering and architectural practice in Sidon, Lebanon and Cairo, Egypt: steel detailing for US fabricators, structural engineering, piping design, pipe stress analysis, static equipment, BIM coordination, and architectural and MEP design.',
    'email': EMAIL_S,
    'telephone': PHONE_S_RAW,
    'foundingDate': '2023',
    'areaServed': ['United States', 'Middle East', 'Europe'],
    'sameAs': [LI_CO],
    'address': [
        {'@type': 'PostalAddress', 'addressLocality': 'Sidon', 'addressRegion': 'South Governorate', 'addressCountry': 'LB'},
        {'@type': 'PostalAddress', 'addressLocality': 'Cairo', 'addressRegion': 'Cairo Governorate', 'addressCountry': 'EG'},
    ],
    'founder': [
        {'@type': 'Person', 'name': NAME_K, 'jobTitle': ROLE_K, 'email': EMAIL_K, 'telephone': PHONE_K_RAW},
        {'@type': 'Person', 'name': NAME_S.replace('Eng. ', ''), 'jobTitle': ROLE_S, 'email': EMAIL_S, 'telephone': PHONE_S_RAW, 'sameAs': [LI_SF]},
    ],
    'knowsAbout': ['Steel detailing', 'Shop drawings', 'Erection drawings', 'Tekla Structures', 'AISC 360', 'AISC 303 Code of Standard Practice', 'OSHA 1926 Subpart R', 'Structural engineering', 'Piping design', 'Pipe stress analysis', 'Caesar II', 'Static equipment design', 'Pressure vessel design', 'BIM coordination', 'Architectural design', 'MEP design', 'Fire-fighting systems'],
}

def page(path, title, desc, body, root, extra_ld=None, current=None, og_type='website'):
    canon = DOMAIN + '/' + path
    lds = [ORG] + (extra_ld or [])
    ld = '\n'.join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in lds)
    nav = ''.join(f'<a href="{root}{href}"{" aria-current=\"page\"" if href == current else ""}>{label}</a>' for href, label in NAV)
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{canon}">
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="Halawi &amp; Partners">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{canon}">
<meta property="og:image" content="{DOMAIN}/assets/brand/og-image.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#0A1F3D">
<link rel="icon" href="{root}assets/brand/favicon-32.png" sizes="32x32" type="image/png">
<link rel="apple-touch-icon" href="{root}assets/brand/apple-touch-icon.png">
<link rel="preload" href="{root}assets/fonts/source-serif-4-var.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="{root}assets/fonts/barlow-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{root}assets/site.css?v={CSS_V}">
{ld}
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="site-head">
  <div class="wrap">
    <a class="brand" href="{root or './'}" aria-label="Halawi &amp; Partners home"><img src="{root}assets/brand/logo-navy-128.png" width="351" height="128" alt="Halawi &amp; Partners"></a>
    <button class="menu-btn" type="button" aria-expanded="false" aria-controls="nav">Menu</button>
    <nav class="nav" id="nav" aria-label="Main">{nav}<a class="btn btn-markup" href="{root}contact/">Request a quote</a></nav>
  </div>
</header>
<main id="main">
{body}
</main>
{footer(root)}
<script>
(function(){{var b=document.querySelector('.menu-btn'),n=document.getElementById('nav');if(!b)return;b.addEventListener('click',function(){{var o=n.classList.toggle('open');b.setAttribute('aria-expanded',o?'true':'false');b.textContent=o?'Close':'Menu';}});}})();
</script>
{ANALYTICS}
</body>
</html>
'''

def footer(root):
    return f'''<footer class="site-foot">
  <div class="wrap">
    <div class="cols">
      <div>
        <a class="brand" href="{root or './'}"><img src="{root}assets/brand/logo-white-128.png" width="351" height="128" alt="Halawi &amp; Partners"></a>
        <p>A multidisciplinary engineering and architectural practice: steel detailing, structural, piping, equipment, BIM, architectural and MEP design.</p>
      </div>
      <div>
        <h2>Sidon office</h2>
        <ul><li>Sidon, Lebanon</li><li>{e(NAME_K)}, {e(ROLE_K)}</li><li><a href="mailto:{EMAIL_K}">{EMAIL_K}</a></li><li><a href="tel:{PHONE_K_RAW}">{PHONE_K}</a></li></ul>
      </div>
      <div>
        <h2>Cairo office</h2>
        <ul><li>Cairo, Egypt</li><li>{e(NAME_S)}, {e(ROLE_S)}</li><li><a href="mailto:{EMAIL_S}">{EMAIL_S}</a></li><li><a href="tel:{PHONE_S_RAW}">{PHONE_S}</a></li></ul>
      </div>
      <div>
        <h2>Pages</h2>
        <ul><li><a href="{root}steel-detailing/">Steel detailing</a></li><li><a href="{root}services/">Services</a></li><li><a href="{root}projects/">Projects</a></li><li><a href="{root}insights/">Insights</a></li><li><a href="{root}about/">About</a></li><li><a href="{root}contact/">Contact</a></li><li><a href="{LI_CO}" rel="noopener">LinkedIn</a></li></ul>
      </div>
    </div>
    <div class="legal"><span>© {YEAR} Halawi &amp; Partners</span><span>Sidon, Lebanon and Cairo, Egypt</span></div>
  </div>
</footer>'''

def sheet(inner, compact=False, cols='ABCDEF', rows='1234'):
    tb = ''.join(f'<span>{c}</span>' for c in cols)
    sb = ''.join(f'<span>{r}</span>' for r in rows)
    return f'''<section class="sheet{' compact' if compact else ''}">
  <div class="frame"><div class="border">
    <div class="bubbles top" aria-hidden="true">{tb}</div>
    <div class="bubbles side" aria-hidden="true">{sb}</div>
    {inner}
  </div></div>
</section>'''

STEEL_CTA = ('Send us a set of drawings', 'Contract drawings, specifications and your shop standards are enough to start. We come back with a scope, a schedule and our first questions.')

def cta_band(root, heading='Tell us about your project', text='Send the drawings, specifications or a short description of the scope. We come back with an approach, a schedule and our first questions.'):
    return f'''<section class="band ink">
  <div class="wrap cta">
    <div><h2>{heading}</h2><p class="lede" style="margin-top:14px">{text}</p></div>
    <div class="acts"><a class="btn btn-markup" href="{root}contact/">Request a quote</a><a class="btn btn-line" href="mailto:{EMAIL_S}?subject=Project%20enquiry">Email us</a></div>
  </div>
</section>'''

# ---------------------------------------------------------------- data
DELIVERABLES = [
    ('E0', 'Anchor rod and embed plans', 'Rod sizes, projections and locations, so the field crew can set them before any steel arrives.'),
    ('E1+', 'Erection plans, elevations and details', 'Piece marks, bolt counts and connection references the erector works from.'),
    ('A', 'Shop and assembly drawings', 'Every beam, column and brace with dimensions, holes, welds and cut lengths.'),
    ('W', 'Single-part drawings', 'Plates, angles and fittings for the cutting and drilling floor.'),
    ('BOM', 'Material lists and reports', 'Mill orders, cut lists and bolt lists taken straight from the model.'),
    ('NC', 'CNC files (DSTV/NC1) and DXF', 'Files your saw, drill line and plasma table read directly.'),
]

STEPS = [
    ('Send the documents', 'Contract drawings, specifications and your shop standards.'),
    ('Scope and RFIs', 'We review the set, agree scope and schedule, and send written RFIs.'),
    ('Model', 'The structure is modeled in Tekla Structures with every connection.'),
    ('Check', 'A second engineer checks the model and every sheet.'),
    ('Approval', 'Drawings go out for approval and come back with comments.'),
    ('Release', 'Revisions are clouded and drawings released with CNC files.'),
]

GENERAL_STEPS = [
    ('Send the documents', 'Drawings, specifications, standards and the schedule you are working to.'),
    ('Scope and questions', 'We review the set, agree scope and schedule, and send written questions early.'),
    ('Model and design', 'The structure, plant or building is modeled in 3D and designed to the governing codes.'),
    ('Coordinate', 'Disciplines are checked against each other and clashes resolved in the model.'),
    ('Check', 'A second engineer checks every calculation, model and sheet.'),
    ('Issue', 'Drawings, reports and fabrication files are issued, then revised to your comments.'),
]

def stem(path):
    return os.path.splitext(os.path.basename(path or ''))[0]

SERVICES = []
for sv in load('services.json')['services']:
    link = (sv.get('link_url') or '').lstrip('/')
    SERVICES.append(dict(slug=sv['slug'], name=sv['name'], img=stem(sv['image']), src=sv['image'], alt=sv.get('alt', ''),
                         short=sv.get('summary', ''), lede=sv.get('intro', ''), items=sv.get('items') or [],
                         codes=sv.get('codes') or None, more=(link, sv.get('link_label') or sv['name']) if link else None))

DETAIL_TYPES = [
    'Commercial and hotel framing',
    'Industrial buildings and warehouses',
    'Pipe racks and equipment supports',
    'Substation structures',
    'Automated rack buildings',
    'Miscellaneous steel: stairs, rails, ladders and platforms',
]

EXPORTS = [
    'CNC files (DSTV/NC1) for saws and drill lines',
    'DXF files for plate cutting',
    'Bills of material, cut lists and bolt lists',
    'IFC models for coordination with other trades',
    'Model review in Trimble Connect',
]

CODES = ['AISC 360-22', 'AISC 303-22', 'RCSC', 'AWS D1.1', 'OSHA 1926 Subpart R', 'Tekla Structures 2026', 'Trimble Connect']

CATEGORIES = ['Steel structures', 'Piping and equipment', 'Pipe stress analysis']
PROJECTS = []
for f in sorted(glob.glob(os.path.join(CONTENT, 'projects', '*.json'))):
    with open(f, encoding='utf-8') as fh:
        d = json.load(fh)
    imgs = [i if isinstance(i, str) else i.get('image', '') for i in (d.get('images') or [])]
    imgs = [i for i in imgs if i]
    if not imgs:
        continue
    PROJECTS.append(dict(name=d['title'], category=d.get('category') or CATEGORIES[0], client=d.get('client') or None,
                         loc=d.get('location') or None, weight=d.get('metric_value') or None, wlabel=d.get('metric_label') or 'Weight',
                         scope=(d.get('scope') or '').rstrip('.'), img=[stem(i) for i in imgs], srcs=imgs, alt=d.get('alt') or d['title'],
                         order=float(d.get('order') or 999), home=bool(d.get('show_on_home'))))
PROJECTS.sort(key=lambda p: (CATEGORIES.index(p['category']) if p['category'] in CATEGORIES else 99, p['order']))
STEEL_PROJECTS = [p for p in PROJECTS if p['category'] == 'Steel structures']
PIPING_PROJECTS = [p for p in PROJECTS if p['category'] == 'Piping and equipment']
STRESS_PROJECTS = [p for p in PROJECTS if p['category'] == 'Pipe stress analysis']
HOME_PROJECTS = sorted([p for p in PROJECTS if p['home']], key=lambda p: p['order'])[:3] or PROJECTS[:3]

def nice_date(d):
    return f'{d.strftime("%B")} {d.day}, {d.year}'

INSIGHTS = []
for f in glob.glob(os.path.join(CONTENT, 'insights', '*.json')):
    with open(f, encoding='utf-8') as fh:
        d = json.load(fh)
    if d.get('draft'):
        continue
    date = datetime.date.fromisoformat(str(d.get('date') or datetime.date.today().isoformat())[:10])
    upd = datetime.date.fromisoformat(str(d['updated'])[:10]) if d.get('updated') else date
    INSIGHTS.append(dict(slug=stem(f), title=d['title'], desc=d.get('description') or '', summary=d.get('summary') or d.get('description') or '',
                         date=date, updated=max(date, upd), body=markdown.markdown(d.get('body') or '', extensions=['sane_lists'])))
INSIGHTS.sort(key=lambda a: (a['date'], a['title']), reverse=True)

def post_list(items, root):
    return '<ul class="posts">' + ''.join(
        f'''<li><a href="{root}insights/{a['slug']}/"><span class="when">{nice_date(a['date'])}</span><h3>{e(a['title'])}</h3><p>{e(a['summary'])}</p></a></li>'''
        for a in items) + '</ul>'

CLIENTS = []
for c in load('clients.json')['clients']:
    c = {'name': c} if isinstance(c, str) else c
    if c.get('name'):
        CLIENTS.append({'name': c['name'], 'logo': c.get('logo') or None})

def make_client_logos():
    """Client logos keep their transparency: 360px-wide WebP files."""
    out = os.path.join(SITE, 'assets', 'img', 'clients')
    os.makedirs(out, exist_ok=True)
    for c in CLIENTS:
        if not c['logo']:
            continue
        path = os.path.join(ROOT, c['logo'].lstrip('/'))
        if not os.path.exists(path):
            raise SystemExit(f"Missing client logo: {c['logo']}")
        im = Image.open(path).convert('RGBA')
        if im.width > 360:
            im = im.resize((360, round(im.height * 360 / im.width)), Image.LANCZOS)
        c['file'] = stem(c['logo']) + '.webp'
        c['size'] = im.size
        im.save(os.path.join(out, c['file']), quality=90, method=6)

def clients_block(root):
    tiles = ''.join(
        f'''<li><img src="{root}assets/img/clients/{c['file']}" width="{c['size'][0]}" height="{c['size'][1]}" alt="{e(c['name'])}" loading="lazy" decoding="async"></li>'''
        for c in CLIENTS if c.get('file'))
    names = [c['name'] for c in CLIENTS if not c.get('file')]
    more = f'''<p class="clients-more"><span>Also</span> {' · '.join(e(n) for n in names)}</p>''' if names else ''
    return (f'<ul class="logos">{tiles}</ul>' if tiles else '') + more
COUNTRIES = SETTINGS['countries']
FAQ = [(q['question'], q['answer']) for q in load('faq.json')['faq']]

def make_images():
    """Create 800px and 1600px WebP versions of every image used on the site."""
    out = os.path.join(SITE, 'assets', 'img')
    os.makedirs(out, exist_ok=True)
    srcs = {sv['src'] for sv in SERVICES} | {s for p in PROJECTS for s in p['srcs']}
    for src in sorted(srcs):
        path = os.path.join(ROOT, src.lstrip('/'))
        if not os.path.exists(path):
            raise SystemExit(f'Missing image: {src}')
        im = ImageOps.exif_transpose(Image.open(path)).convert('RGB')
        name = stem(src)
        for w in (800, 1600):
            if w == 1600 and im.width < 1200:
                continue
            ww = min(w, im.width)
            im.resize((ww, round(im.height * ww / im.width)), Image.LANCZOS).save(os.path.join(out, f'{name}-{w}.webp'), quality=80, method=6)

def facts(p):
    rows = []
    if p.get('client'): rows.append(('Client', p['client']))
    if p.get('loc'): rows.append(('Location', p['loc']))
    if p.get('weight'): rows.append((p.get('wlabel', 'Weight'), p['weight']))
    return '<dl class="facts">' + ''.join(f'<dt>{k}</dt><dd>{e(v)}</dd>' for k, v in rows) + '</dl>'

def proj_block(p, root):
    """Same layout as before: one image, or two side by side. Extra images open in the viewer."""
    pics = p['img']
    def alt(i):
        return p['alt'] if i == 0 else f"{p['alt']} (view {i + 1})"
    ratios = [dims(n)[0] / dims(n)[1] for n in pics[:2]]
    pair = len(ratios) == 2 and max(ratios) / min(ratios) <= 1.35 and sum(ratios) <= 3.2
    shown = pics[:2] if pair else pics[:1]
    if pair:
        imgs = ''.join(f'<div class="cell" style="--ar:{r:.3f}">{img(n, alt(i), sizes="(max-width: 900px) 50vw, 30vw", root=root)}</div>'
                       for i, (n, r) in enumerate(zip(shown, ratios)))
    else:
        imgs = img(shown[0], alt(0), sizes='(max-width: 900px) 100vw, 60vw', root=root)
    gallery = []
    for i, n in enumerate(pics):
        big = f'{SITE}/assets/img/{n}-1600.webp'
        src = f'{root}assets/img/{n}-1600.webp' if os.path.exists(big) else f'{root}assets/img/{n}-800.webp'
        gallery.append({'s': src, 'a': alt(i)})
    more = (f'<button class="gal-btn" type="button">View all {len(pics)} photos</button>' if len(pics) > len(shown) else '')
    data = html.escape(json.dumps(gallery, ensure_ascii=False), quote=True)
    return f'''<article class="proj">
  <div class="pics{' pair' if pair else ''}" data-gallery="{data}">{imgs}{more}</div>
  <div><h3>{e(p['name'])}</h3>{facts(p)}<p>{e(p['scope'])}.</p></div>
</article>'''

def row(items, root):
    out = []
    for p in items:
        w, h = dims(p['img'][0])
        out.append(f'<div class="cell" style="--ar:{w/h:.3f}">' + fig(p, root, cls='', sizes='(max-width: 900px) 100vw, 33vw') + '</div>')
    return '<div class="proj-row">' + ''.join(out) + '</div>'

def fig(p, root, cls='cover', sizes='(max-width: 900px) 100vw, 40vw'):
    meta = ' · '.join(x for x in [p.get('client'), p.get('loc'), p.get('weight')] if x)
    return f'''<figure class="fig {cls}">{img(p['img'][0], p['alt'], sizes=sizes, root=root)}
  <figcaption><div class="name">{e(p['name'])}</div><div class="meta">{e(meta)}</div></figcaption></figure>'''

# ---------------------------------------------------------------- pages
def home():
    r = ''
    tb = f"""<dl class="titleblock" aria-label="Project title block">
      <div class="wide firm"><img src="assets/brand/logo-white-64.png" width="176" height="64" alt=""><dd>Engineering and architectural practice</dd></div>
      <div class="wide"><dt>Disciplines</dt><dd>Steel detailing, structural, piping, stress analysis, static equipment, BIM, architectural and MEP design</dd></div>
      <div><dt>Main focus</dt><dd>Steel detailing for US fabricators</dd></div>
      <div><dt>Checked by</dt><dd>A second engineer, every sheet</dd></div>
      <div><dt>Offices</dt><dd>Sidon, Lebanon and Cairo, Egypt</dd></div>
      <div><dt>Ahead of US time</dt><dd>7 to 10 hours</dd></div>
    </dl>"""
    hero = sheet(f"""<div class="hero-grid">
      <div>
        <h1>{e(SETTINGS["hero_title"])}</h1>
        <div class="dim" aria-hidden="true"><span class="ln"></span><span class="lbl">eight disciplines, one coordinated model</span></div>
        <p class="lede">{e(SETTINGS["hero_lede"])}</p>
        <div class="hero-actions"><a class="btn btn-markup" href="contact/">Request a quote</a><a class="btn btn-line" href="services/">Our services</a></div>
      </div>
      {tb}
    </div>""")
    items = []
    for sv in SERVICES:
        w, h = dims(sv['img'])
        items.append(f"""<a class="item" href="services/#{sv['slug']}">
        <span class="thumb"><img src="assets/img/{sv['img']}-800.webp" width="{w}" height="{h}" alt="" loading="lazy" decoding="async"></span>
        <span class="txt"><h3>{sv['name']}</h3><p>{e(sv['short'])}</p></span></a>""")
    rows = ''.join(f'<tr><td class="mark"><span>{m}</span></td><td><strong>{t}</strong></td><td class="what">{w}</td></tr>' for m, t, w in DELIVERABLES)
    steps = ''.join(f'<li><h3>{t}</h3><p>{d}</p></li>' for t, d in GENERAL_STEPS)
    mix = HOME_PROJECTS
    body = f"""{hero}
<section class="band">
  <div class="wrap">
    <div class="head"><h2>What we do</h2><p class="lede">Structures, plant piping, equipment and buildings, modeled and coordinated by one team, so every question is answered by the people who drew the work.</p></div>
    <div class="svc-index">{''.join(items)}</div>
  </div>
</section>
<section class="band alt">
  <div class="wrap">
    <div class="head"><h2>Steel detailing for US fabricators</h2><p class="lede">Our main focus. One model and one coordinated set, in the sheet series your shop already knows, checked before it reaches your floor.</p></div>
    <table class="index">
      <caption>Drawing index for a typical structural steel package</caption>
      <thead><tr><th scope="col">Series</th><th scope="col">Drawing</th><th scope="col">What it gives your shop</th></tr></thead>
      <tbody>{rows}</tbody>
    </table>
    <p class="more"><a href="steel-detailing/">How we detail steel for US fabricators</a></p>
  </div>
</section>
<section class="band">
  <div class="wrap">
    <div class="head"><h2>Selected projects</h2><p class="lede">A sample of our work, not the full list: pipe racks, substations, industrial buildings, boiler packages, plant piping and stress analysis for clients in {COUNTRIES}.</p></div>
    {row(mix, r)}
    <p class="more"><a href="projects/">See more of our projects</a></p>
  </div>
</section>
<section class="band alt">
  <div class="wrap">
    <div class="head"><h2>How a project runs</h2><p class="lede">Our offices are 7 to 10 hours ahead of US time, so comments you send at the end of your day are worked while your office is closed.</p></div>
    <ol class="steps">{steps}</ol>
  </div>
</section>
<section class="band">
  <div class="wrap">
    <div class="head"><h2>Clients in nine countries</h2><p class="lede">Fabricators, contractors, consultants and owners in {COUNTRIES}.</p></div>
    {clients_block(r)}
  </div>
</section>
{guides_band(r)}
{cta_band(r)}"""
    return page('', 'Halawi & Partners | Steel Detailing and Engineering Services for US Fabricators',
                'Outsourced steel detailing in Tekla Structures for US fabricators, to AISC and OSHA Subpart R, plus structural, piping, BIM and MEP engineering services.',
                body, r, current=None)

def guides_band(root, alt=True, heading='Guides for US fabricators', limit=3):
    if not INSIGHTS:
        return ''
    return f'''<section class="band{' alt' if alt else ''}">
  <div class="wrap">
    <div class="head"><h2>{heading}</h2><p class="lede">Practical notes from our detailing work: what to send, what to check, and what the codes ask for.</p></div>
    {post_list(INSIGHTS[:limit], root)}
    <p class="more"><a href="{root}insights/">All articles</a></p>
  </div>
</section>'''

def steel():
    r = '../'
    hero = sheet(f'''<p class="crumbs"><a href="../">Home</a> / Steel detailing</p>
      <h1>Steel detailing services for US fabricators</h1>
      <p class="lede">Outsource your structural and miscellaneous steel detailing: complete packages in Tekla Structures, from the anchor rod plan to the CNC files, drawn to your shop standards and checked before release.</p>
      <div class="hero-actions"><a class="btn btn-markup" href="../contact/">Send drawings for a quote</a></div>''', compact=True)
    rows = ''.join(f'<tr><td class="mark"><span>{m}</span></td><td><strong>{t}</strong></td><td class="what">{w}</td></tr>' for m, t, w in DELIVERABLES)
    codes = ''.join(f'<li>{c}</li>' for c in CODES)
    faqs = FAQ
    faq_html = ''.join(f'<details><summary>{q}</summary><p>{a}</p></details>' for q, a in faqs)
    faq_ld = {'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in faqs]}
    svc_ld = {'@context': 'https://schema.org', '@type': 'Service', 'serviceType': 'Structural steel detailing', 'provider': {'@id': DOMAIN + '/#org'}, 'areaServed': 'United States',
              'description': 'Anchor rod plans, erection drawings, shop and assembly drawings, single-part drawings, material lists and CNC files in Tekla Structures, detailed to AISC 360-22, AISC 303-22, RCSC, AWS D1.1 and OSHA 1926 Subpart R.'}
    crumbs_ld = {'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [{'@type': 'ListItem', 'position': 1, 'name': 'Home', 'item': DOMAIN + '/'}, {'@type': 'ListItem', 'position': 2, 'name': 'Steel detailing', 'item': DOMAIN + '/steel-detailing/'}]}
    checks = [
        'Model checking and clash detection before any drawing is produced',
        'Connection checks against the design forces and the AISC Manual',
        'An independent check of every sheet by a second engineer',
        'Bolt, weld and material lists reconciled with the model',
        'Field-fit items, safety cable holes and erection aids reviewed against OSHA Subpart R',
    ]
    body = f'''{hero}
<section class="band">
  <div class="wrap">
    <div class="head"><h2>What you receive</h2><p class="lede">One model, one coordinated set. The sheet series match the way US shops and erectors are used to reading a package.</p></div>
    <table class="index"><caption>Drawing index for a typical structural steel package</caption>
      <thead><tr><th scope="col">Series</th><th scope="col">Drawing</th><th scope="col">What it gives your shop</th></tr></thead><tbody>{rows}</tbody></table>
    <div class="split" style="margin-top:56px">
      <div><h3 style="margin-bottom:14px">Structures we detail</h3><ul class="ticks">{''.join(f'<li>{x}</li>' for x in DETAIL_TYPES)}</ul></div>
      <div><h3 style="margin-bottom:14px">Files from the same model</h3><ul class="ticks">{''.join(f'<li>{x}</li>' for x in EXPORTS)}</ul></div>
    </div>
  </div>
</section>
<section class="band alt">
  <div class="wrap split">
    <div>
      <h2>Detailed to US codes and to your shop</h2>
      <p class="lede" style="margin-top:18px">We detail to the contract documents and the codes they reference, and to the way your shop works: your Tekla templates, title block, piece marks, bolt conventions and preferred connections.</p>
      <ul class="codes" style="margin-top:26px">{codes}</ul>
    </div>
    <div>
      <h3 style="margin-bottom:14px">What we check before release</h3>
      <ul class="ticks">{''.join(f'<li>{c}</li>' for c in checks)}</ul>
      <p class="note">"Approved" doesn't mean "correct": the reviewer checks design intent, checking every hole is our job.</p>
    </div>
  </div>
</section>
<section class="band">
  <div class="wrap">
    <div class="head"><h2>How a job runs</h2><p class="lede">Every question goes out as a written RFI, every comment is tracked to the model, and every sheet is checked before it leaves the office.</p></div>
    <ol class="steps">{''.join(f'<li><h3>{t}</h3><p>{d}</p></li>' for t, d in STEPS)}</ol>
  </div>
</section>
<section class="band alt">
  <div class="wrap">
    <div class="head"><h2>Steel projects</h2><p class="lede">A few of the structures we have modeled and detailed, out of many more.</p></div>
    {row(STEEL_PROJECTS[:3], r)}
    <p class="more"><a href="../projects/">All projects</a></p>
  </div>
</section>
<section class="band">
  <div class="wrap">
    <div class="head single"><h2>Questions fabricators ask us</h2></div>
    <div class="faq">{faq_html}</div>
  </div>
</section>
{guides_band(r)}
{cta_band(r, *STEEL_CTA)}'''
    return page('steel-detailing/', 'Steel Detailing Services for US Fabricators in Tekla Structures | Halawi & Partners',
                'Outsourced structural and miscellaneous steel detailing in Tekla Structures: anchor rod plans, erection and shop drawings, CNC files, to AISC 360, AISC 303, RCSC, AWS D1.1 and OSHA Subpart R.',
                body, r, extra_ld=[svc_ld, faq_ld, crumbs_ld], current='steel-detailing/')

def services():
    r = '../'
    jump = ''.join(f'<li><a href="#{sv["slug"]}">{sv["name"]}</a></li>' for sv in SERVICES)
    hero = sheet(f"""<p class="crumbs"><a href="../">Home</a> / Services</p>
      <h1>Engineering and design services</h1>
      <p class="lede">Eight disciplines under one roof, from offices in Sidon, Lebanon and Cairo, Egypt. Use one of them, or let one team carry a project from design to fabrication drawings.</p>
      <ul class="jump" aria-label="Services on this page">{jump}</ul>""", compact=True)
    out = []
    for sv in SERVICES:
        cl = f'<ul class="codes">{"".join(f"<li>{c}</li>" for c in sv["codes"])}</ul>' if sv['codes'] else ''
        more = f'<p class="more" style="margin-top:22px"><a href="../{sv["more"][0]}">{sv["more"][1]}</a></p>' if sv['more'] else ''
        out.append(f"""<section id="{sv['slug']}">
      <div><h2>{sv['name']}</h2><p class="lede">{e(sv['lede'])}</p><ul class="ticks" style="margin-top:20px">{''.join(f'<li>{e(i)}</li>' for i in sv['items'])}</ul>{cl}{more}</div>
      <div class="pic">{img(sv['img'], sv['alt'], sizes='(max-width: 900px) 100vw, 45vw', root=r)}</div>
    </section>""")
    body = f"""{hero}
<section class="band">
  <div class="wrap eng">{''.join(out)}</div>
</section>
{cta_band(r)}"""
    svc_ld = {'@context': 'https://schema.org', '@type': 'ItemList', 'name': 'Halawi & Partners services',
              'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'item': {'@type': 'Service', 'name': sv['name'], 'description': sv['short'], 'provider': {'@id': DOMAIN + '/#org'}, 'url': f'{DOMAIN}/services/#{sv["slug"]}'}} for i, sv in enumerate(SERVICES)]}
    crumbs_ld = {'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [{'@type': 'ListItem', 'position': 1, 'name': 'Home', 'item': DOMAIN + '/'}, {'@type': 'ListItem', 'position': 2, 'name': 'Services', 'item': DOMAIN + '/services/'}]}
    return page('services/', 'Engineering Services: Steel Detailing, Structural, Piping, BIM, Architectural and MEP | Halawi & Partners',
                'Steel detailing, structural engineering in steel and concrete, piping design to ASME B31, Caesar II stress analysis, pressure vessels and tanks, BIM coordination, and architectural and MEP design.',
                body, r, extra_ld=[svc_ld, crumbs_ld], current='services/')

VIEWER = """<div class="lb" id="lb" hidden role="dialog" aria-modal="true" aria-label="Project photos">
  <button class="lb-x" type="button" aria-label="Close">Close</button>
  <button class="lb-nav lb-prev" type="button" aria-label="Previous photo">&#8249;</button>
  <figure><img alt=""><figcaption><span class="lb-n"></span> <span class="lb-cap"></span></figcaption></figure>
  <button class="lb-nav lb-next" type="button" aria-label="Next photo">&#8250;</button>
</div>
<script>
(function(){
  var lb=document.getElementById('lb'); if(!lb) return;
  var im=lb.querySelector('img'), n=lb.querySelector('.lb-n'), cap=lb.querySelector('.lb-cap'), items=[], i=0, last=null;
  function show(k){ i=(k+items.length)%items.length; im.src=items[i].s; im.alt=items[i].a; cap.textContent=items[i].a; n.textContent=(i+1)+' / '+items.length;
    lb.querySelector('.lb-prev').hidden=lb.querySelector('.lb-next').hidden=items.length<2; }
  function open(list,k,from){ items=list; last=from; show(k); lb.hidden=false; document.body.style.overflow='hidden'; lb.querySelector('.lb-x').focus(); }
  function close(){ lb.hidden=true; document.body.style.overflow=''; if(last) last.focus(); }
  document.querySelectorAll('.proj .pics[data-gallery]').forEach(function(box){
    var list; try{ list=JSON.parse(box.getAttribute('data-gallery')); }catch(e){ return; }
    box.querySelectorAll('img').forEach(function(img,k){ img.tabIndex=0; img.setAttribute('role','button');
      img.addEventListener('click',function(){ open(list,k,img); });
      img.addEventListener('keydown',function(ev){ if(ev.key==='Enter'||ev.key===' '){ ev.preventDefault(); open(list,k,img); } }); });
    var b=box.querySelector('.gal-btn'); if(b) b.addEventListener('click',function(){ open(list,0,b); });
  });
  lb.querySelector('.lb-x').addEventListener('click',close);
  lb.querySelector('.lb-prev').addEventListener('click',function(){ show(i-1); });
  lb.querySelector('.lb-next').addEventListener('click',function(){ show(i+1); });
  lb.addEventListener('click',function(ev){ if(ev.target===lb) close(); });
  document.addEventListener('keydown',function(ev){ if(lb.hidden) return;
    if(ev.key==='Escape') close(); else if(ev.key==='ArrowLeft') show(i-1); else if(ev.key==='ArrowRight') show(i+1); });
  var x0=null; lb.addEventListener('touchstart',function(ev){ x0=ev.touches[0].clientX; },{passive:true});
  lb.addEventListener('touchend',function(ev){ if(x0===null) return; var dx=ev.changedTouches[0].clientX-x0; if(Math.abs(dx)>40) show(i+(dx<0?1:-1)); x0=null; });
})();
</script>"""

def projects():
    r = '../'
    hero = sheet(f'''<p class="crumbs"><a href="../">Home</a> / Projects</p>
      <h1>Selected projects</h1>
      <p class="lede">A sample of our work for clients in {COUNTRIES}: steel structures, plant piping and stress analysis. It is a selection, not the full list of projects we have delivered.</p>''', compact=True)
    def group(title, sub, items):
        return f'''<h2 class="group-title">{title} <span>{sub}</span></h2><div class="proj-list">{''.join(proj_block(p, r) for p in items)}</div>'''
    body = f'''{hero}
<section class="band"><div class="wrap">{group('Steel structures', 'A selection', STEEL_PROJECTS)}</div></section>
<section class="band alt"><div class="wrap">{group('Piping and equipment', 'A selection', PIPING_PROJECTS)}</div></section>
<section class="band"><div class="wrap">{group('Pipe stress analysis', 'A selection', STRESS_PROJECTS)}</div></section>
{VIEWER}
{cta_band(r, 'More examples on request', 'This page shows a selection of our work. Tell us what you are building and we will send examples and references closer to your project.')}'''
    crumbs_ld = {'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [{'@type': 'ListItem', 'position': 1, 'name': 'Home', 'item': DOMAIN + '/'}, {'@type': 'ListItem', 'position': 2, 'name': 'Projects', 'item': DOMAIN + '/projects/'}]}
    return page('projects/', 'Selected Projects: Pipe Racks, Substations, Industrial Steel and Plant Piping | Halawi & Partners',
                'A selection of our steel detailing and engineering projects, including a 516-ton Intel pipe rack, 220 kV substations, automated rack buildings, boiler packages and Caesar II stress analysis.',
                body, r, extra_ld=[crumbs_ld], current='projects/')

def about():
    r = '../'
    hero = sheet('''<p class="crumbs"><a href="../">Home</a> / About</p>
      <h1>Two offices, one engineering team</h1>
      <p class="lede">Halawi &amp; Partners is a multidisciplinary engineering and architectural practice founded in 2023 in Sidon, Lebanon, with its engineering office in Cairo, Egypt.</p>''', compact=True)
    body = f'''{hero}
<section class="band">
  <div class="wrap split">
    <div>
      <h2>What we do</h2>
      <p class="lede" style="margin-top:18px">Steel detailing for US fabricators is our main focus. Around it, the same team provides structural engineering, piping design, pipe stress analysis, static equipment design, BIM coordination, and architectural and MEP design.</p>
      <p>That means one team can take a project from design to fabrication drawings: the structure, the piping and the services are modeled and coordinated together, and questions are answered by the people who drew the work.</p>
    </div>
    <div>
      <ul class="figures" style="margin-top:6px"><li><b>9</b>countries</li><li><b>15+</b>clients</li><li><b>2</b>offices</li></ul>
    </div>
  </div>
</section>
<section class="band ink">
  <div class="wrap">
    <div class="head"><h2>The partners</h2><p class="lede">Write to either partner directly.</p></div>
    <div class="people">
      <div class="person"><h3>{e(NAME_K)}</h3><p class="role">{e(ROLE_K)}, Sidon, Lebanon</p><ul><li><a href="mailto:{EMAIL_K}">{EMAIL_K}</a></li><li><a href="tel:{PHONE_K_RAW}">{PHONE_K}</a></li></ul></div>
      <div class="person"><h3>{e(NAME_S)}</h3><p class="role">{e(ROLE_S)}, Cairo, Egypt</p><ul><li><a href="mailto:{EMAIL_S}">{EMAIL_S}</a></li><li><a href="tel:{PHONE_S_RAW}">{PHONE_S}</a></li><li><a href="{LI_SF}" rel="noopener">LinkedIn profile</a></li></ul></div>
    </div>
  </div>
</section>
<section class="band alt">
  <div class="wrap">
    <div class="head"><h2>Clients</h2><p class="lede">Fabricators, contractors and owners in {COUNTRIES}.</p></div>
    {clients_block(r)}
  </div>
</section>
{cta_band(r)}'''
    crumbs_ld = {'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [{'@type': 'ListItem', 'position': 1, 'name': 'Home', 'item': DOMAIN + '/'}, {'@type': 'ListItem', 'position': 2, 'name': 'About', 'item': DOMAIN + '/about/'}]}
    return page('about/', 'About Halawi & Partners | Engineering Offices in Sidon and Cairo',
                'Halawi & Partners is a multidisciplinary engineering and architectural practice in Sidon, Lebanon and Cairo, Egypt, focused on steel detailing for US fabricators.',
                body, r, extra_ld=[crumbs_ld], current='about/')

def contact():
    r = '../'
    hero = sheet('''<p class="crumbs"><a href="../">Home</a> / Contact</p>
      <h1>Request a quote</h1>
      <p class="lede">Tell us about the job. The form opens your email app with the details filled in, ready to attach the drawings.</p>''', compact=True)
    body = f'''{hero}
<section class="band">
  <div class="wrap split">
    <form class="form" id="quote" novalidate>
      <div><label for="f-name">Your name</label><input id="f-name" name="name" autocomplete="name" required></div>
      <div><label for="f-company">Company</label><input id="f-company" name="company" autocomplete="organization" required></div>
      <div><label for="f-email">Email</label><input id="f-email" name="email" type="email" autocomplete="email" required></div>
      <div><label for="f-phone">Phone (optional)</label><input id="f-phone" name="phone" type="tel" autocomplete="tel"></div>
      <div class="full"><label for="f-service">Service</label>
        <select id="f-service" name="service">
          <option>Steel detailing (shop and erection drawings)</option>
          <option>Miscellaneous steel</option>
          <option>Structural engineering</option>
          <option>Piping design or stress analysis</option>
          <option>Static equipment</option>
          <option>BIM coordination</option>
          <option>Architectural or MEP design</option>
        </select></div>
      <div class="full"><label for="f-project">Project, location and approximate tonnage</label><input id="f-project" name="project"></div>
      <div class="full"><label for="f-msg">Scope and schedule</label><textarea id="f-msg" name="message" required></textarea>
        <p class="hint">Attach the contract drawings, specifications and your shop standards to the email that opens.</p></div>
      <div class="full"><button class="btn btn-markup" type="submit">Open email with these details</button><p class="form-status" role="status" aria-live="polite"></p></div>
    </form>
    <div>
      <h2 style="font-size:30px">What to send</h2>
      <ul class="ticks" style="margin-top:16px"><li>Contract drawings, PDF or DWG</li><li>Specifications and addenda</li><li>Your shop standards or a sample set</li><li>The schedule you are working to</li></ul>
      <h2 style="font-size:30px;margin-top:36px">Or write directly</h2>
      <p style="margin-top:12px"><strong>{e(NAME_S)}</strong>, Cairo<br><a href="mailto:{EMAIL_S}">{EMAIL_S}</a><br><a href="tel:{PHONE_S_RAW}">{PHONE_S}</a> · <a href="https://wa.me/{PHONE_S_RAW.lstrip('+')}" rel="noopener">WhatsApp</a></p>
      <p><strong>{e(NAME_K)}</strong>, Sidon<br><a href="mailto:{EMAIL_K}">{EMAIL_K}</a><br><a href="tel:{PHONE_K_RAW}">{PHONE_K}</a></p>
      <p><a href="{LI_CO}" rel="noopener">Halawi &amp; Partners on LinkedIn</a></p>
    </div>
  </div>
</section>
<script>
(function(){{
  var f=document.getElementById('quote'), s=f.querySelector('.form-status');
  f.addEventListener('submit', function(ev){{
    ev.preventDefault();
    var miss=[].slice.call(f.querySelectorAll('[required]')).filter(function(x){{return !x.value.trim();}});
    var em=f.elements.email;
    if(miss.length){{ s.textContent='Fill in '+miss.map(function(x){{return f.querySelector('label[for="'+x.id+'"]').textContent.toLowerCase();}}).join(', ')+' to continue.'; miss[0].focus(); return; }}
    if(!/^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$/.test(em.value.trim())){{ s.textContent='Enter an email address like name@company.com.'; em.focus(); return; }}
    var v=function(n){{return f.elements[n].value.trim();}};
    var body='Name: '+v('name')+'\\nCompany: '+v('company')+'\\nEmail: '+v('email')+(v('phone')?'\\nPhone: '+v('phone'):'')+'\\nService: '+v('service')+(v('project')?'\\nProject: '+v('project'):'')+'\\n\\n'+v('message')+'\\n\\n(Drawings attached)';
    var url='mailto:{EMAIL_S}?cc={EMAIL_K}&subject='+encodeURIComponent('Quote request: '+v('company'))+'&body='+encodeURIComponent(body);
    s.textContent='Your email app is opening with the request filled in. Attach the drawings and send.';
    window.location.href=url;
  }});
}})();
</script>'''
    crumbs_ld = {'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [{'@type': 'ListItem', 'position': 1, 'name': 'Home', 'item': DOMAIN + '/'}, {'@type': 'ListItem', 'position': 2, 'name': 'Contact', 'item': DOMAIN + '/contact/'}]}
    return page('contact/', 'Request a Steel Detailing Quote | Halawi & Partners',
                'Send contract drawings, specifications and your shop standards for a steel detailing or engineering quote. Email, phone and WhatsApp for our Cairo and Sidon offices.',
                body, r, extra_ld=[crumbs_ld], current='contact/')

def insights_index():
    r = '../'
    hero = sheet('''<p class="crumbs"><a href="../">Home</a> / Insights</p>
      <h1>Insights for steel fabricators</h1>
      <p class="lede">Practical notes from our detailing and engineering work: outsourcing detailing, US codes, and the files your shop and erector need.</p>''', compact=True)
    body = f'''{hero}
<section class="band">
  <div class="wrap">
    {post_list(INSIGHTS, r)}
  </div>
</section>
{cta_band(r, *STEEL_CTA)}'''
    list_ld = {'@context': 'https://schema.org', '@type': 'Blog', 'name': 'Halawi & Partners Insights', 'url': DOMAIN + '/insights/', 'publisher': {'@id': DOMAIN + '/#org'},
               'blogPost': [{'@type': 'BlogPosting', 'headline': a['title'], 'url': f'{DOMAIN}/insights/{a["slug"]}/', 'datePublished': a['date'].isoformat()} for a in INSIGHTS]}
    crumbs_ld = {'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [{'@type': 'ListItem', 'position': 1, 'name': 'Home', 'item': DOMAIN + '/'}, {'@type': 'ListItem', 'position': 2, 'name': 'Insights', 'item': DOMAIN + '/insights/'}]}
    return page('insights/', 'Steel Detailing Insights for US Fabricators | Halawi & Partners',
                'Practical articles on outsourcing steel detailing, OSHA Subpart R, AISC requirements and Tekla Structures deliverables for US steel fabricators.',
                body, r, extra_ld=[list_ld, crumbs_ld], current='insights/')

def article(a):
    r = '../../'
    url = f'{DOMAIN}/insights/{a["slug"]}/'
    hero = sheet(f'''<p class="crumbs"><a href="../../">Home</a> / <a href="../">Insights</a></p>
      <h1 class="post-title">{e(a['title'])}</h1>
      <p class="lede">{e(a['desc'])}</p>
      <p class="byline">Halawi &amp; Partners · <time datetime="{a['date'].isoformat()}">{nice_date(a['date'])}</time></p>''', compact=True)
    others = [x for x in INSIGHTS if x['slug'] != a['slug']][:3]
    more = f'''<section class="band alt">
  <div class="wrap">
    <div class="head single"><h2>More for fabricators</h2></div>
    {post_list(others, r)}
  </div>
</section>''' if others else ''
    body = f'''{hero}
<section class="band">
  <div class="wrap"><article class="prose">{a['body']}</article>
    <p class="more"><a href="../../steel-detailing/">How we detail steel for US fabricators</a></p>
  </div>
</section>
{more}
{cta_band(r, *STEEL_CTA)}'''
    post_ld = {'@context': 'https://schema.org', '@type': 'BlogPosting', 'headline': a['title'], 'description': a['desc'], 'url': url, 'mainEntityOfPage': url,
               'datePublished': a['date'].isoformat(), 'dateModified': a['updated'].isoformat(), 'inLanguage': 'en-US',
               'image': DOMAIN + '/assets/brand/og-image.png', 'author': {'@id': DOMAIN + '/#org'}, 'publisher': {'@id': DOMAIN + '/#org'}}
    crumbs_ld = {'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
        {'@type': 'ListItem', 'position': 1, 'name': 'Home', 'item': DOMAIN + '/'},
        {'@type': 'ListItem', 'position': 2, 'name': 'Insights', 'item': DOMAIN + '/insights/'},
        {'@type': 'ListItem', 'position': 3, 'name': a['title'], 'item': url}]}
    return page(f'insights/{a["slug"]}/', f'{a["title"]} | Halawi & Partners', a['desc'], body, r,
                extra_ld=[post_ld, crumbs_ld], current='insights/', og_type='article')

def notfound():
    body = sheet('''<h1>This sheet isn't in the set</h1>
      <p class="lede">The page you asked for doesn't exist. Go back to the home page or see our projects.</p>
      <div class="hero-actions"><a class="btn btn-markup" href="/">Home page</a><a class="btn btn-line" href="/projects/">Projects</a></div>''', compact=True)
    return page('404.html', 'Page not found | Halawi & Partners', 'Page not found.', body, '/', current=None).replace('<link rel="canonical" href="https://halawipartners.com/404.html">', '<meta name="robots" content="noindex">')

PAGES = {'index.html': home, 'steel-detailing/index.html': steel, 'services/index.html': services,
         'projects/index.html': projects, 'insights/index.html': insights_index, 'about/index.html': about,
         'contact/index.html': contact, '404.html': notfound}

if __name__ == '__main__':
    if os.path.exists(SITE):
        shutil.rmtree(SITE)
    shutil.copytree(os.path.join(ROOT, 'static'), SITE)
    for d in ('steel-detailing', 'services', 'projects', 'insights', 'about', 'contact'):
        os.makedirs(os.path.join(SITE, d), exist_ok=True)
    make_images()
    make_client_logos()
    for path, fn in PAGES.items():
        with open(os.path.join(SITE, path), 'w', encoding='utf-8') as fh:
            fh.write(fn())
    for a in INSIGHTS:
        os.makedirs(os.path.join(SITE, 'insights', a['slug']), exist_ok=True)
        with open(os.path.join(SITE, 'insights', a['slug'], 'index.html'), 'w', encoding='utf-8') as fh:
            fh.write(article(a))
    today = datetime.date.today().isoformat()
    urls = [(u, today) for u in ['', 'services/', 'steel-detailing/', 'projects/', 'insights/', 'about/', 'contact/']]
    urls += [(f'insights/{a["slug"]}/', a['updated'].isoformat()) for a in INSIGHTS]
    pri = {'': '1.0', 'services/': '0.9', 'steel-detailing/': '0.9'}
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + ''.join(
        f'  <url><loc>{DOMAIN}/{u}</loc><lastmod>{d}</lastmod><priority>{pri.get(u, "0.7")}</priority></url>\n' for u, d in urls) + '</urlset>\n'
    with open(os.path.join(SITE, 'sitemap.xml'), 'w') as fh:
        fh.write(sm)
    print('built', len(PAGES), 'pages,', len(INSIGHTS), 'articles,', len(PROJECTS), 'projects')
