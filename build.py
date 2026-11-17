#!/usr/bin/env python3
"""Builds the Anchor Point website.

    python3 build.py

Page copy lives in src/*.txt. Each page starts with a line `=== <slug>` followed by
`title:`, `desc:` and `nav:` lines, a blank line, then the page body (HTML).
The shared header, footer and <head> are defined once, here.

Assets that are optional until the company supplies them (the page adapts automatically
when the file is added and the site is rebuilt):
    assets/photos/<name>.jpg|.webp|.png   photographs (see {{photo:...}} in src/)
    assets/cv/Biniyam-Regassa-Merga-CV.pdf
"""
import html
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).parent

# ── Settings to complete before launch ──────────────────────────────────────
BASE_URL = ""        # e.g. "https://www.example.com" — enables canonical URLs, og:url and sitemap.xml
FORM_ENDPOINT = ""   # inquiry backend URL — the contact form does not submit until this is set
COMPANY_EMAIL = ""   # verified company email address — never invent one
TELEGRAM_USERNAME = ""  # the firm's Telegram username, without "@". When set, the contact form opens
                        # Telegram with the inquiry pre-written for the visitor to send. Never guess it.
CV_FILE = "assets/cv/Biniyam-Regassa-Merga-CV.pdf"
OG_IMAGE = ""        # e.g. "assets/og-image.jpg" once a share image exists
# ────────────────────────────────────────────────────────────────────────────

NAV = [("index", "Home"), ("about", "About Us"), ("services", "Services"), ("sectors", "Sectors"),
       ("projects", "Projects &amp; Experience"), ("insights", "Insights"), ("contact", "Contact")]

# Candidate portfolio from the existing website. VERIFY every name, location, value, length,
# period and role against project records before publication (brief Part 7 / Part 16).
# Role and period are intentionally absent until verified: (slug, name, location, length, value, role, period)
PROJECTS = [
    ("dessie-hayk", "Dessie&ndash;Hayk", "Kombolcha District", "69.2 km", "ETB 8.42 billion", "", ""),
    ("mente-home", "Mente&ndash;Home", "Jimma District", "3.87 km", "ETB 2.23 billion", "", ""),
    ("melka-jebdu", "Melka&ndash;Jebdu", "Dire Dawa District", "2.1 km", "ETB 1.69 billion", "", ""),
    ("azezo-gonder", "Azezo&ndash;Gonder", "Gonder District", "12 km", "ETB 1.42 billion", "", ""),
    ("woldia-town", "Woldia Town", "Kombolcha District", "7.525 km", "ETB 1.37 billion", "", ""),
    ("togochale-junction", "Togochale&ndash;Junction", "Dire Dawa District", "10.02 km", "ETB 769.1 million", "", ""),
    ("hossana", "Hossana", "Alemgena District", "5.125 km", "ETB 538.0 million", "", ""),
    ("kunzela", "Kunzela", "Debre Markos District", "21.8 km", "ETB 450.0 million", "", ""),
    ("sawla-kako", "Sawla&ndash;Kako", "Sodo District", "29.768 km", "ETB 433.6 million", "", ""),
    ("durame-durgi", "Durame&ndash;Durgi", "Shashemene District", "26.5 km", "ETB 188.5 million", "", ""),
]

MARK = ('<svg viewBox="0 0 44 44" aria-hidden="true"><rect width="44" height="44" rx="4" fill="#14283F"/>'
        '<path d="M22 8 11.5 35M22 8l10.5 27" stroke="#F7F6F2" stroke-width="2.6" stroke-linecap="round" fill="none"/>'
        '<circle cx="22" cy="26.5" r="2.6" fill="#B89A68"/></svg>')
MARK_LIGHT = MARK.replace('fill="#14283F"', 'fill="#FFFFFF"').replace('stroke="#F7F6F2"', 'stroke="#14283F"')

# Hero road animation: flowing dashed centre line, two travelling dots, rotating ring around the 15+ Years badge.
MOTIF = ('<svg class="road" viewBox="0 0 760 640" preserveAspectRatio="xMaxYMax meet" fill="none" aria-hidden="true">'
         '<defs><linearGradient id="rEdge" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#B89A68" stop-opacity="0"/>'
         '<stop offset="1" stop-color="#B89A68" stop-opacity=".6"/></linearGradient>'
         '<linearGradient id="rCore" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#B89A68"/><stop offset="1" stop-color="#DCC295"/></linearGradient>'
         '<radialGradient id="rGlow"><stop offset="0" stop-color="#B89A68" stop-opacity=".34"/><stop offset="1" stop-color="#B89A68" stop-opacity="0"/></radialGradient>'
         '<path id="circ" d="M-60,0 a60,60 0 1,1 120,0 a60,60 0 1,1 -120,0"/></defs>'
         '<circle cx="560" cy="86" r="210" fill="url(#rGlow)"/>'
         '<g transform="translate(0,120)">'
         '<path d="M520 0C470 160 240 260 60 520" stroke="url(#rEdge)" stroke-width="2"/>'
         '<path d="M600 0C580 170 470 300 420 520" stroke="url(#rEdge)" stroke-width="2"/>'
         '<path class="dash" d="M560 0C525 165 355 280 240 520" stroke="#B89A68" stroke-opacity=".7" stroke-width="2.5" stroke-dasharray="14 16"/>'
         '<circle class="car" r="5.5" fill="#EBD9B4"/><circle class="car c2" r="5.5" fill="#EBD9B4"/></g>'
         '<g class="badge" transform="translate(560,86)">'
         '<g><animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="18s" repeatCount="indefinite"/>'
         '<text class="ring"><textPath href="#circ">ROADS &#8226; BUILDINGS &#8226; STRUCTURES &#8226; </textPath></text></g>'
         '<circle r="40" fill="url(#rCore)"/>'
         '<text class="yrs" y="4" font-size="27">15+</text><text class="yrs" y="20" font-size="9" letter-spacing="1.4">YEARS</text></g></svg>')


def photo_path(name):
    for ext in ("jpg", "jpeg", "webp", "png"):
        if (ROOT / "assets" / "photos" / f"{name}.{ext}").exists():
            return f"assets/photos/{name}.{ext}"
    return ""


def photo(name, alt, cls="", eager=False):
    p = photo_path(name)
    if not p:
        return ""
    c = f' class="{cls}"' if cls else ""
    load = "" if eager else ' loading="lazy" decoding="async"'
    return f'<img{c} src="{p}" alt="{html.escape(alt, quote=True)}"{load}>'


def project_cards(count):
    out = []
    for slug, name, loc, length, value, role, period in PROJECTS[:count]:
        rows = [("Location", loc), ("Project type", "Road construction contract"), ("Length", length), ("Contract value", value)]
        if role:
            rows.append(("Professional role", role))
        if period:
            rows.append(("Period", period))
        dl = "".join(f"<div><dt>{k}</dt><dd>{v}</dd></div>" for k, v in rows)
        plain = html.unescape(name)
        out.append(f'<article class="proj">{photo("project-" + slug, plain + " road project")}'
                   f'<div class="proj-b"><p class="label">Selected Professional Experience</p><h3>{name}</h3><dl>{dl}</dl></div></article>')
    return '<div class="projects">' + "".join(out) + "</div>"


def expand(body):
    def ph(m):
        parts = m.group(1).split("|")
        name, alt = parts[0], parts[1] if len(parts) > 1 else ""
        cls = parts[2] if len(parts) > 2 else ""
        return photo(name, alt, cls, eager=(name == "hero"))
    body = re.sub(r"\{\{photo:([^}]+)\}\}", ph, body)
    body = re.sub(r"\{\{projects:(\d+|all)\}\}",
                  lambda m: project_cards(len(PROJECTS) if m.group(1) == "all" else int(m.group(1))), body)
    has_hero = bool(photo_path("hero"))
    body = body.replace("{{hero_class}}", "hero has-photo" if has_hero else "hero")
    body = body.replace("{{hero_motif}}", MOTIF)
    body = body.replace("{{leader_class}}", "leader" if photo_path("leadership-portrait") else "leader no-photo")
    cv = (f'<a class="btn solid" href="{CV_FILE}" download>Download CV (PDF)</a>' if (ROOT / CV_FILE).exists() else "")
    body = body.replace("{{cv}}", cv)
    email = (f'<div><dt>Email</dt><dd><a href="mailto:{COMPANY_EMAIL}">{COMPANY_EMAIL}</a></dd></div>' if COMPANY_EMAIL else "")
    body = body.replace("{{email}}", email)
    body = body.replace("{{endpoint}}", html.escape(FORM_ENDPOINT, quote=True))
    tg = TELEGRAM_USERNAME.strip().lstrip("@")
    body = body.replace("{{telegram}}", html.escape(tg, quote=True))
    body = body.replace("{{telegram_row}}", (f'<div><dt>Telegram</dt><dd><a href="https://t.me/{tg}" rel="noopener">@{tg}</a></dd></div>' if tg else ""))
    body = body.replace("{{submit_label}}", "Send Inquiry via Telegram" if (tg and not FORM_ENDPOINT) else "Submit Project Inquiry")
    return body


def page(slug, meta, body):
    file = f"{slug}.html"
    links = []
    for key, label in NAV:
        cur = ' aria-current="page"' if key == meta.get("nav") else ""
        links.append(f'<a href="{key}.html"{cur}>{label}</a>')
    links.append('<a href="contact.html" class="btn solid">Discuss a Project</a>')
    title, desc = html.escape(meta["title"], quote=True), html.escape(meta["desc"], quote=True)
    head = [f"<title>{title}</title>", f'<meta name="description" content="{desc}">',
            f'<meta property="og:title" content="{title}">', f'<meta property="og:description" content="{desc}">',
            '<meta property="og:type" content="website">', '<meta property="og:site_name" content="Anchor Point Engineers &amp; Consultants">']
    if BASE_URL:
        url = BASE_URL.rstrip("/") + "/" + ("" if slug == "index" else file)
        head += [f'<link rel="canonical" href="{url}">', f'<meta property="og:url" content="{url}">']
        if OG_IMAGE:
            head.append(f'<meta property="og:image" content="{BASE_URL.rstrip("/")}/{OG_IMAGE}">')
    if slug == "index":
        org = {"@context": "https://schema.org", "@type": "ProfessionalService",
               "name": "Anchor Point Engineers and Consultants",
               "description": meta["desc"],
               "address": {"@type": "PostalAddress", "addressLocality": "Addis Ababa", "addressRegion": "Bole", "addressCountry": "ET"},
               "telephone": ["+251911257592", "+251969151555"], "areaServed": "Ethiopia"}
        if BASE_URL:
            org["url"] = BASE_URL
        if COMPANY_EMAIL:
            org["email"] = COMPANY_EMAIL
        head.append('<script type="application/ld+json">' + json.dumps(org) + "</script>")
    email_li = f'<li><a href="mailto:{COMPANY_EMAIL}">{COMPANY_EMAIL}</a></li>' if COMPANY_EMAIL else ""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
{chr(10).join(head)}
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 44 44'%3E%3Crect width='44' height='44' rx='6' fill='%2314283F'/%3E%3Cpath d='M22 8 11.5 35M22 8l10.5 27' stroke='%23F7F6F2' stroke-width='3' stroke-linecap='round' fill='none'/%3E%3Ccircle cx='22' cy='26.5' r='2.8' fill='%23B89A68'/%3E%3C/svg%3E">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/site.css">
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<div class="topbar">
  <div class="wrap">
    <span class="tb-ai"><svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M12 2l1.9 5.6a4 4 0 0 0 2.5 2.5L22 12l-5.6 1.9a4 4 0 0 0-2.5 2.5L12 22l-1.9-5.6a4 4 0 0 0-2.5-2.5L2 12l5.6-1.9a4 4 0 0 0 2.5-2.5z"/></svg>AI-Enabled Engineering Consultancy</span>
    <a class="tb-np" href="https://northpoint-ai.com" target="_blank" rel="noopener"><span>In partnership with</span><img src="assets/northpoint-ai-logo-white.webp" alt="North Point AI" width="117" height="22"></a>
  </div>
</div>
<header class="hdr">
  <div class="wrap hdr-in">
    <a href="index.html" class="logo" aria-label="Anchor Point Engineers and Consultants — home">{MARK}<div><b>Anchor Point</b><span>Engineers &amp; Consultants</span></div></a>
    <button class="burger" id="burger" aria-label="Menu" aria-controls="nav" aria-expanded="false"><span></span><span></span><span></span></button>
    <nav class="nav" id="nav" aria-label="Main">{"".join(links)}</nav>
  </div>
</header>
<main id="main">
{expand(body).strip()}
</main>
<footer class="ftr">
  <div class="wrap">
    <div class="ftr-g">
      <div>
        <a href="index.html" class="logo">{MARK_LIGHT}<div><b>Anchor Point</b><span>Engineers &amp; Consultants</span></div></a>
        <p>Professional engineering, project management and infrastructure advisory services.</p>
      </div>
      <div>
        <h4>Quick links</h4>
        <ul>
          <li><a href="about.html">About Us</a></li>
          <li><a href="services.html">Services</a></li>
          <li><a href="sectors.html">Sectors</a></li>
          <li><a href="projects.html">Projects &amp; Experience</a></li>
          <li><a href="technology.html">Technology &amp; Innovation</a></li>
          <li><a href="contact.html">Contact</a></li>
        </ul>
      </div>
      <div>
        <h4>Contact</h4>
        <ul>
          <li>Bole, Addis Ababa, Ethiopia.</li>
          <li><a href="tel:+251911257592">+251 911 25 75 92</a></li>
          <li><a href="tel:+251969151555">+251 969 15 15 55</a></li>
          {email_li}
        </ul>
        <div class="ftr-more"><a href="leadership.html">Leadership</a><a href="training.html">Professional Training</a><a href="insights.html">Insights</a><a href="faq.html">FAQ</a></div>
      </div>
    </div>
    <div class="ftr-b">
      <b>Engineering expertise. Infrastructure that delivers.</b>
      <span>&copy; <span id="yr">2026</span> Anchor Point Engineers and Consultants. All rights reserved.</span>
      <span>Technology partnership with <a href="https://northpoint-ai.com" target="_blank" rel="noopener">North Point AI</a>.</span>
    </div>
  </div>
</footer>
<script>document.getElementById('yr').textContent=new Date().getFullYear()</script>
<script src="assets/site.js" defer></script>
</body>
</html>
"""


def main():
    pages = {}
    for src in sorted((ROOT / "src").glob("*.txt")):
        for chunk in re.split(r"^=== ", src.read_text(encoding="utf-8"), flags=re.M)[1:]:
            header, _, body = chunk.partition("\n\n")
            lines = header.strip().split("\n")
            meta = dict(l.split(": ", 1) for l in lines[1:])
            pages[lines[0].strip()] = (meta, body)
    for slug, (meta, body) in pages.items():
        (ROOT / f"{slug}.html").write_text(page(slug, meta, body), encoding="utf-8")
    robots = "User-agent: *\nAllow: /\n"
    if BASE_URL:
        base = BASE_URL.rstrip("/")
        urls = "".join(f"  <url><loc>{base}/{'' if s == 'index' else s + '.html'}</loc></url>\n" for s in pages)
        (ROOT / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + urls + "</urlset>\n")
        robots += f"Sitemap: {base}/sitemap.xml\n"
    (ROOT / "robots.txt").write_text(robots)
    print("built:", ", ".join(f"{s}.html" for s in pages))
    missing = [n for n in ["hero", "service-engineering", "service-project-management", "service-asset-management",
                           "service-contract-advisory", "leadership-portrait"] + ["project-" + p[0] for p in PROJECTS]
               if not photo_path(n)]
    if missing:
        print("photos not yet supplied:", ", ".join(missing))
    for label, ok in (("BASE_URL", BASE_URL), ("COMPANY_EMAIL", COMPANY_EMAIL),
                      ("contact form destination (TELEGRAM_USERNAME or FORM_ENDPOINT)", TELEGRAM_USERNAME or FORM_ENDPOINT),
                      ("CV PDF", (ROOT / CV_FILE).exists())):
        if not ok:
            print("not yet set:", label)


if __name__ == "__main__":
    main()
