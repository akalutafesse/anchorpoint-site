#!/usr/bin/env python3
"""Builds the Anchor Point website.

    python3 build.py

Page copy lives in src/pages.txt. Each page starts with a line `=== <slug>` followed by
`title:`, `desc:` and `nav:` lines, a blank line, then the page body (HTML).
The shared header, footer, <head>, icons, inquiry form and diagrams are defined once, here.

Tokens available in page bodies:
    {{i:name}}            line icon (see ICONS)
    {{road}}              animated hero road
    {{net}} {{imagine}} {{triad}} {{duo}}   the AI section: network visual, vision tiles, closing line, two logos
    {{projects:6|all}}    contract bar chart
    {{cta}} / {{cta:Heading text}}   closing section with the inquiry form
    {{form}} {{clist}}    the inquiry form / the contact details list on their own
    {{portrait}} {{cv}}   optional items, shown only when supplied
"""
import html
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).parent

# ── Settings to complete ────────────────────────────────────────────────────
BASE_URL = "https://anchorpointengineers.com"
FORM_ENDPOINT = ""      # URL of the form-to-Telegram service (see worker/). The form posts here.
TELEGRAM_USERNAME = ""  # alternative: the firm's Telegram username, without "@". Opens Telegram with
                        # the inquiry pre-written for the visitor to send. Never guess it.
COMPANY_EMAIL = ""      # verified company email address — never invent one
CV_FILE = "assets/cv/Biniyam-Regassa-Merga-CV.pdf"
PORTRAIT = "assets/photos/leadership-portrait.jpg"
OG_IMAGE = ""           # e.g. "assets/og-image.jpg" once a share image exists
# ────────────────────────────────────────────────────────────────────────────

NAV = [("about", "About"), ("services", "Services"), ("projects", "Projects"),
       ("technology", "AI Partnership"), ("contact", "Contact")]

# Candidate portfolio from the earlier website. VERIFY every name, location, value and length
# against project records. (name, location, km, ETB millions)
PROJECTS = [
    ("Dessie&ndash;Hayk", "Kombolcha District", 69.2, 8420.0),
    ("Mente&ndash;Home", "Jimma District", 3.87, 2230.0),
    ("Melka&ndash;Jebdu", "Dire Dawa District", 2.1, 1690.0),
    ("Azezo&ndash;Gonder", "Gonder District", 12, 1420.0),
    ("Woldia Town", "Kombolcha District", 7.525, 1370.0),
    ("Togochale&ndash;Junction", "Dire Dawa District", 10.02, 769.1),
    ("Hossana", "Alemgena District", 5.125, 538.0),
    ("Kunzela", "Debre Markos District", 21.8, 450.0),
    ("Sawla&ndash;Kako", "Sodo District", 29.768, 433.6),
    ("Durame&ndash;Durgi", "Shashemene District", 26.5, 188.5),
]

ICONS = {
    "ruler": "M4 17 17 4l3 3L7 20z M8 13l1.5 1.5 M11 10l1.5 1.5 M14 7l1.5 1.5",
    "clipboard": "M9 4h6v3H9z M7 5.5H5.5V20h13V5.5H17 M8.5 13l2 2 4-4.5",
    "road": "M8 3 4 21 M16 3l4 18 M12 4v3 M12 10.5v3 M12 17v3",
    "doc": "M7 3h7l4 4v14H7z M14 3v4h4 M9.5 12h6 M9.5 16h6",
    "gov": "M3 20h18 M5 20V10 M9 20V10 M15 20V10 M19 20V10 M3 10l9-6 9 6z",
    "chart": "M4 20h16 M7 20v-5 M12 20v-9 M17 20v-7 M5 9l5-4 4 3 5-5",
    "hardhat": "M4 17h16 M6 17v-2a6 6 0 0 1 12 0v2 M10 9.5V6h4v3.5",
    "globe": "M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18z M3 12h18 M12 3c3 3 3 15 0 18 M12 3c-3 3-3 15 0 18",
    "tower": "M5 21V7l7-4v18 M12 9h7v12 M3 21h18 M8.5 9v.01 M8.5 13v.01 M8.5 17v.01 M15.5 13v.01 M15.5 17v.01",
    "shield": "M12 3l7 3v5c0 5-3 8.5-7 10-4-1.5-7-5-7-10V6z M9 12l2 2 4-4",
    "layers": "M12 3 3 8l9 5 9-5z M3 12.5l9 5 9-5 M3 16.5l9 5 9-5",
    "spark": "M12 3l1.8 5.2a3 3 0 0 0 2 2L21 12l-5.2 1.8a3 3 0 0 0-2 2L12 21l-1.8-5.2a3 3 0 0 0-2-2L3 12l5.2-1.8a3 3 0 0 0 2-2z",
    "search": "M10.5 4a6.5 6.5 0 1 0 0 13 6.5 6.5 0 0 0 0-13z M20 20l-4.7-4.7",
    "calendar": "M4 6h16v14H4z M4 10h16 M8 3v4 M16 3v4",
    "calc": "M5 3h14v18H5z M8 7h8 M8.5 12v.01 M12 12v.01 M15.5 12v.01 M8.5 16v.01 M12 16v.01 M15.5 16v.01",
    "pulse": "M3 12h4l2.5-6 4 12 2.5-6h5",
    "report": "M6 3h12v18H6z M9 16v-3 M12 16V9 M15 16v-5",
    "users": "M9 11a3.5 3.5 0 1 0 0-7 3.5 3.5 0 0 0 0 7z M2.5 20c.5-3.5 3-5.5 6.5-5.5s6 2 6.5 5.5 M16 4.5a3.5 3.5 0 0 1 0 6.5 M18 14.8c2 .7 3.2 2.5 3.5 5.2",
    "target": "M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18z M12 7.5a4.5 4.5 0 1 0 0 9 4.5 4.5 0 0 0 0-9z M12 11.9v.2",
    "check": "M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18z M8 12.5l2.8 2.8L16 9.5",
    "bulb": "M9 18h6 M10 21h4 M12 3a6 6 0 0 0-3.5 10.9c.6.5 1 1.3 1 2.1h5c0-.8.4-1.6 1-2.1A6 6 0 0 0 12 3z",
    "pin": "M12 21s-6.5-5.8-6.5-11a6.5 6.5 0 0 1 13 0c0 5.2-6.5 11-6.5 11z M12 7.5a2.5 2.5 0 1 0 0 5 2.5 2.5 0 0 0 0-5z",
    "phone": "M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a1 1 0 0 1-1 1C10.7 20 4 13.3 4 5a1 1 0 0 1 1-1z",
    "clock": "M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18z M12 7v5l3.5 2",
    "cap": "M2 9l10-5 10 5-10 5z M6 11.5V16c1.5 1.5 3.5 2.5 6 2.5s4.5-1 6-2.5v-4.5 M22 9v5",
    "scale": "M12 4v16 M7 20h10 M5 7h14 M5 7l-2.5 6a2.8 2.8 0 0 0 5 0z M19 7l-2.5 6a2.8 2.8 0 0 0 5 0z",
    "alert": "M12 4 2.5 20h19z M12 10v4.5 M12 17.3v.2",
    "coins": "M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18z M14.5 9.5c-.5-1-1.4-1.5-2.5-1.5-1.5 0-2.5.9-2.5 2 0 2.8 5 1.5 5 4.3 0 1.1-1 2-2.5 2-1.2 0-2.1-.5-2.6-1.5 M12 6v2 M12 16.3V18",
    "eye": "M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12z M12 9a3 3 0 1 0 0 6 3 3 0 0 0 0-6z",
    "send": "M21 3 10 14 M21 3l-7 18-4-7-7-4z",
    "compass": "M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18z M15.5 8.5l-2 5-5 2 2-5z",
    "flag": "M5 21V4 M5 4h12l-2 4 2 4H5",
    "monitor": "M3 5h18v11H3z M9 20h6 M12 16v4",
    "handshake": "M3 8l4-2 5 2 5-2 4 2v7l-4 2 M3 8v7l5 4 4-2 M12 8l-3 3 2 2 3-2 3 3",
}

MARK = ('<svg viewBox="0 0 44 44" aria-hidden="true">'
        '<path d="M22 6 9.5 38M22 6l12.5 32" stroke="#14283F" stroke-width="3.2" stroke-linecap="round" fill="none"/>'
        '<circle cx="22" cy="27" r="3.4" fill="#B89A68"/></svg>')
MARK_LIGHT = MARK.replace('stroke="#14283F"', 'stroke="#FFFFFF"')
NP_LOGO = '<img src="assets/northpoint-ai-logo.webp" alt="North Point AI" width="760" height="143">'

# Hero road animation: flowing dashed centre line, two travelling dots, rotating ring around the 15+ Years badge.
ROAD = ('<svg class="road" viewBox="0 0 760 500" fill="none" aria-hidden="true">'
        '<defs><linearGradient id="rEdge" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#14283F" stop-opacity="0"/>'
        '<stop offset="1" stop-color="#14283F" stop-opacity=".34"/></linearGradient>'
        '<linearGradient id="rFill" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#14283F" stop-opacity="0"/>'
        '<stop offset="1" stop-color="#14283F" stop-opacity=".07"/></linearGradient>'
        '<linearGradient id="rCore" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#B89A68"/><stop offset="1" stop-color="#DCC295"/></linearGradient>'
        '<radialGradient id="rGlow"><stop offset="0" stop-color="#B89A68" stop-opacity=".26"/><stop offset="1" stop-color="#B89A68" stop-opacity="0"/></radialGradient>'
        '<path id="circ" d="M-60,0 a60,60 0 1,1 120,0 a60,60 0 1,1 -120,0"/></defs>'
        '<circle cx="380" cy="96" r="230" fill="url(#rGlow)"/>'
        '<path d="M366 132C352 300 250 420 30 580L730 580C510 420 408 300 394 132Z" fill="url(#rFill)"/>'
        '<path d="M366 132C352 300 250 420 30 580" stroke="url(#rEdge)" stroke-width="1.6"/>'
        '<path d="M394 132C408 300 510 420 730 580" stroke="url(#rEdge)" stroke-width="1.6"/>'
        '<path class="dash" d="M380 132L380 580" stroke="#B89A68" stroke-width="3" stroke-dasharray="14 16"/>'
        '<circle class="car" r="6" fill="#14283F"/><circle class="car c2" r="6" fill="#14283F"/>'
        '<g class="badge" transform="translate(380,96)">'
        '<g><animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="18s" repeatCount="indefinite"/>'
        '<text class="ring"><textPath href="#circ">ROADS &#8226; BUILDINGS &#8226; STRUCTURES &#8226; </textPath></text></g>'
        '<circle r="40" fill="url(#rCore)"/>'
        '<text class="yrs" y="4" font-size="27">15+</text><text class="yrs" y="20" font-size="9" letter-spacing="1.4">YEARS</text></g></svg>')


def network():
    """AI visual: a network of points that lights up, with a north star above it."""
    n = {"H": (70, 150), "A": (170, 262), "B": (305, 158), "C": (410, 276), "D": (500, 186), "E": (598, 292),
         "F": (700, 164), "G": (838, 250), "I": (935, 132), "N": (500, 58)}
    links = ["HB", "AB", "BD", "BC", "CD", "DN", "DF", "CE", "EF", "FG", "GI", "FI", "EG", "AC"]
    d = lambda k: f"M{n[k[0]][0]} {n[k[0]][1]}L{n[k[1]][0]} {n[k[1]][1]}"
    base = "".join(f'<path d="{d(k)}" stroke="#fff" stroke-opacity=".1"/>' for k in links)
    flow = "".join(f'<path class="flow" d="{d(k)}" stroke="url(#nG)" stroke-width="1.6"/>' for k in links)
    nodes = "".join(f'<circle class="node" cx="{x}" cy="{y}" r="4.5" fill="url(#nG)"/>' for k, (x, y) in n.items() if k != "N")
    routes = ["M70 150L305 158L500 186L500 58", "M170 262L410 276L598 292L838 250L935 132", "M935 132L700 164L500 186L410 276"]
    movers = "".join(f'<circle class="mover" r="3.4" fill="#fff" filter="url(#nB)"><animateMotion dur="{6 + i * 2}s" repeatCount="indefinite" path="{r}"/></circle>'
                     for i, r in enumerate(routes))
    star = ('<g transform="translate(500,58)"><circle r="46" fill="url(#nS)"/>'
            '<path class="star" d="M0-24C2.500-8 8-2.500 24 0 8 2.500 2.500 8 0 24-2.500 8-8 2.500-24 0-8-2.500-2.500-8 0-24Z" fill="#fff"/></g>')
    return ('<svg class="net" viewBox="0 0 1000 330" fill="none" aria-hidden="true"><defs>'
            '<linearGradient id="nG" x1="0" y1="0" x2="1000" y2="0" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#5EE0D8"/><stop offset=".5" stop-color="#8E7CFF"/><stop offset="1" stop-color="#F2C46D"/></linearGradient>'
            '<radialGradient id="nS"><stop offset="0" stop-color="#8E7CFF" stop-opacity=".55"/><stop offset="1" stop-color="#8E7CFF" stop-opacity="0"/></radialGradient>'
            '<filter id="nB" x="-200%" y="-200%" width="500%" height="500%"><feGaussianBlur stdDeviation="2.200"/><feMerge><feMergeNode/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>'
            + base + flow + nodes + movers + star + "</svg>")


NET = network().replace("2.500", "2.5").replace("2.200", "2.2")

def _im(title, text):
    return f'<div class="im"><h3>{title}</h3><p>{text}</p></div>'


def _im_group(label, tiles):
    return (f'<div class="im-g"><p class="im-k"><span class="spark">{label}</span></p>'
            f'<div class="im-row">{"".join(_im(t, p) for t, p in tiles)}</div></div>')


# Statements of ambition for AI in Ethiopian construction — not services delivered today.
IMAGINE = '<div class="imagine">' + _im_group("Engineering", [
    ("A design checked against every standard, overnight.",
     "Drawings and specifications compared with the design manuals clause by clause, with every gap listed by morning."),
    ("Every kilometre surveyed from a phone on the dashboard.",
     "Video from an ordinary vehicle turned into a map of potholes, cracks and blocked drains, district by district."),
    ("Quantities taken from the drawings, not from estimates.",
     "Bills of quantities measured automatically and checked against the design before the tender goes out."),
]) + _im_group("Project management", [
    ("A delay you can see months before it arrives.",
     "Schedules, the rainy season, right-of-way and material supply read together, pointing to what will slip next."),
    ("Next quarter&rsquo;s cement price, in today&rsquo;s budget.",
     "Cement, steel, bitumen and fuel prices tracked, so price escalation is forecast instead of discovered."),
    ("One screen that tells the truth about fifty projects.",
     "Progress, cost and risk across every district, built from site data and not from last month&rsquo;s report."),
]) + _im_group("Construction management", [
    ("A payment certificate checked in an hour, not a month.",
     "Measured quantities, rates and earlier payments verified line by line, ready for the engineer&rsquo;s decision."),
    ("Ten thousand pages, read before the first meeting.",
     "Every contract clause, letter and notice understood, with each deadline and conflict already found."),
    ("A site diary that writes itself.",
     "Photos, voice notes and equipment logs from remote sites become the daily record that settles claims."),
]) + ('<div class="im wide"><h3>Ask your project anything. In Amharic or English.</h3>'
      '<p>The whole history of a project, available to the people deciding its future.</p></div></div>')

TRIAD = '<p class="triad"><span>See further.</span><span>Decide sooner.</span><span>Build with confidence.</span></p>'


def icon(name):
    return (f'<svg class="i" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="{ICONS[name]}"/></svg>')


def tick(text):
    return f'<li>{icon("check")}<span>{text}</span></li>'


AP_LOGO = f'<span class="logo">{MARK}<span><b>Anchor Point</b><span>Engineers &amp; Consultants</span></span></span>'
NP_LINK_W = ('<a href="https://northpoint-ai.com" target="_blank" rel="noopener" aria-label="North Point AI website">'
             '<img src="assets/northpoint-ai-logo-white.webp" alt="North Point AI" width="760" height="143"></a>')

AP_LOGO_W = AP_LOGO.replace(MARK, MARK_LIGHT)
DUO = f'<div class="duo">{AP_LOGO_W}<i aria-hidden="true">&times;</i>{NP_LINK_W}</div>'


# From the firm's own earlier website. VERIFY against certificates and ERA records before relying on them.
RADIAL = """<div class="feature">
  <div class="feature-n"><b>ETB 40B</b></div>
  <div><h3>Addis Ababa radial road projects.</h3><p>Coordinated during the founder&rsquo;s service at the Ethiopian Roads Administration. Combined value: ETB 40 billion.</p></div>
</div>"""

INTL = """<div class="g4 intl">
  <div class="card"><span class="eyebrow">United Kingdom</span><h3>London</h3><p>Performance-Based Contracting Systems</p></div>
  <div class="card"><span class="eyebrow">Japan</span><h3>Hiroshima</h3><p>Road Maintenance, Knowledge Co-Creation Program</p><small>JICA &amp; Hiroshima International Center &middot; 2022</small></div>
  <div class="card"><span class="eyebrow">China</span><h3>Beijing</h3><p>Digital Transformation of Infrastructure Operation &amp; Maintenance</p><small>Ministry of Commerce of China &middot; 2023</small></div>
  <div class="card"><span class="eyebrow">United Arab Emirates</span><h3>Dubai</h3><p>Infrastructure Asset Management &amp; ISO 55000</p><small>ESAMI &middot; 2025</small></div>
</div>"""


def money(m):
    return f"ETB {m / 1000:.2f} billion" if m >= 1000 else f"ETB {m:.1f} million"


def project_bars(count):
    top = max(p[3] for p in PROJECTS)
    rows = []
    for name, loc, km, val in PROJECTS[:count]:
        pct = max(val / top * 100, 2.2)
        rows.append(f'<li><div class="bar-n"><b>{name}</b><span>{loc}</span></div>'
                    f'<div class="bar-t" aria-hidden="true"><i style="width:{pct:.1f}%"></i></div>'
                    f'<div class="bar-v">{money(val)}</div><div class="bar-k">{km:g} km</div></li>')
    return ('<div class="bars"><div class="bars-h" aria-hidden="true"><span>Road contract</span><span>Contract value</span><span></span><span>Length</span></div>'
            '<ul>' + "".join(rows) + "</ul></div>")


def form():
    tg = TELEGRAM_USERNAME.strip().lstrip("@")
    return f"""<form class="inq" id="inquiry" data-endpoint="{html.escape(FORM_ENDPOINT, quote=True)}" data-telegram="{html.escape(tg, quote=True)}" novalidate>
  <div class="f2">
    <div class="fg"><label for="f-name">Your name <i>*</i></label><input id="f-name" name="name" type="text" autocomplete="name" required><span class="err">Please enter your name.</span></div>
    <div class="fg"><label for="f-contact">Phone or email <i>*</i></label><input id="f-contact" name="contact" type="text" autocomplete="tel" required><span class="err">Please enter a phone number or email.</span></div>
  </div>
  <div class="fg"><label for="f-org">Organization <em>(optional)</em></label><input id="f-org" name="organization" type="text" autocomplete="organization"></div>
  <div class="fg"><label for="f-msg">How can we help? <i>*</i></label><textarea id="f-msg" name="message" required placeholder="A few lines about your project and where it is."></textarea><span class="err">Please tell us what you need.</span></div>
  <div class="hp" aria-hidden="true"><label for="f-web">Website</label><input id="f-web" name="website" type="text" tabindex="-1" autocomplete="off"></div>
  <button type="submit" class="btn solid" id="fsub">{icon("send")}<span>Send Inquiry</span></button>
  <div class="fmsg" id="fmsg" role="status" aria-live="polite"></div>
  <p class="fnote">We use your details only to reply to your inquiry.</p>
</form>"""


def contact_list():
    tg = TELEGRAM_USERNAME.strip().lstrip("@")
    rows = [f'<li>{icon("phone")}<span><a href="tel:+251911257592">+251 911 25 75 92</a><br><a href="tel:+251969151555">+251 969 15 15 55</a></span></li>']
    if COMPANY_EMAIL:
        rows.append(f'<li>{icon("send")}<span><a href="mailto:{COMPANY_EMAIL}">{COMPANY_EMAIL}</a></span></li>')
    if tg:
        rows.append(f'<li>{icon("send")}<span><a href="https://t.me/{tg}" rel="noopener">Telegram: @{tg}</a></span></li>')
    rows.append(f'<li>{icon("pin")}<span>Bole, Addis Ababa, Ethiopia</span></li>')
    rows.append(f'<li>{icon("clock")}<span>Monday&ndash;Friday, 8:00 AM&ndash;5:00 PM EAT</span></li>')
    return '<ul class="clist">' + "".join(rows) + "</ul>"


def cta(heading):
    return f"""<section class="sec cta" id="discuss">
  <div class="wrap">
    <div class="cta-g">
      <div>
        <span class="eyebrow">Start a Conversation</span>
        <h2>{heading}</h2>
        <p class="lead">Tell us briefly what you need. A member of our team will review it and contact you.</p>
        {contact_list()}
      </div>
      {form()}
    </div>
  </div>
</section>"""


def expand(body):
    body = re.sub(r"<!--.*?-->\n?", "", body, flags=re.S)
    body = re.sub(r"\{\{i:([a-z]+)\}\}", lambda m: icon(m.group(1)), body)
    body = re.sub(r"\{\{projects:(\d+|all)\}\}",
                  lambda m: project_bars(len(PROJECTS) if m.group(1) == "all" else int(m.group(1))), body)
    body = re.sub(r"\{\{cta:([^}]+)\}\}", lambda m: cta(m.group(1)), body)
    body = body.replace("{{cta}}", cta("Let&rsquo;s discuss your project."))
    body = body.replace("{{form}}", form()).replace("{{clist}}", contact_list())
    body = body.replace("{{road}}", ROAD).replace("{{net}}", NET).replace("{{imagine}}", IMAGINE)
    body = body.replace("{{triad}}", TRIAD).replace("{{duo}}", DUO)
    body = body.replace("{{radial}}", RADIAL).replace("{{intl}}", INTL)
    body = body.replace("{{nplogo}}", NP_LOGO)
    portrait = (f'<img class="portrait" src="{PORTRAIT}" alt="Eng. Biniyam Regassa Merga, Founder and Chief Executive Officer" loading="lazy">'
                if (ROOT / PORTRAIT).exists() else '<span class="portrait mono" aria-hidden="true">BR</span>')
    body = body.replace("{{portrait}}", portrait)
    cv = (f'<a class="btn line" href="{CV_FILE}" download>Download CV (PDF)</a>' if (ROOT / CV_FILE).exists() else "")
    body = body.replace("{{cv}}", cv)
    left = re.findall(r"\{\{[^}]*\}\}", body)
    if left:
        raise SystemExit(f"unknown tokens: {sorted(set(left))}")
    return body


def page(slug, meta, body):
    file = f"{slug}.html"
    links = []
    for key, label in NAV:
        cur = ' aria-current="page"' if key == meta.get("nav") else ""
        links.append(f'<a href="{key}.html"{cur}>{label}</a>')
    links.append('<a href="#inquiry" class="btn solid">Discuss a Project</a>')
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
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 44 44'%3E%3Crect width='44' height='44' rx='8' fill='%2314283F'/%3E%3Cpath d='M22 8 11.5 35M22 8l10.5 27' stroke='%23F7F6F2' stroke-width='3' stroke-linecap='round' fill='none'/%3E%3Ccircle cx='22' cy='26.5' r='2.8' fill='%23B89A68'/%3E%3C/svg%3E">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/site.css">
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="hdr">
  <div class="wrap hdr-in">
    <div class="brand">
      <a href="index.html" class="logo" aria-label="Anchor Point Engineers and Consultants — home">{MARK}<span><b>Anchor Point</b><span>Engineers &amp; Consultants</span></span></a>
      <a href="https://northpoint-ai.com" target="_blank" rel="noopener" class="with" aria-label="In partnership with North Point AI — opens northpoint-ai.com"><span>In partnership with</span>{NP_LOGO}</a>
    </div>
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
        <a href="index.html" class="logo">{MARK}<span><b>Anchor Point</b><span>Engineers &amp; Consultants</span></span></a>
        <p>Engineering, project management and infrastructure advisory services.</p>
        <a class="ftr-np" href="https://northpoint-ai.com" target="_blank" rel="noopener"><span>In partnership with</span><img src="assets/northpoint-ai-logo.webp" alt="North Point AI" width="760" height="143" loading="lazy"></a>
      </div>
      <div>
        <h4>Company</h4>
        <ul>
          <li><a href="about.html">About</a></li>
          <li><a href="leadership.html">Leadership</a></li>
          <li><a href="projects.html">Projects &amp; Experience</a></li>
          <li><a href="technology.html">AI Partnership</a></li>
          <li><a href="faq.html">FAQ</a></li>
        </ul>
      </div>
      <div>
        <h4>Services</h4>
        <ul>
          <li><a href="services.html">All Services</a></li>
          <li><a href="sectors.html">Who We Work With</a></li>
          <li><a href="training.html">Professional Training</a></li>
        </ul>
      </div>
      <div>
        <h4>Contact</h4>
        <ul>
          <li>Bole, Addis Ababa, Ethiopia</li>
          <li><a href="tel:+251911257592">+251 911 25 75 92</a></li>
          <li><a href="tel:+251969151555">+251 969 15 15 55</a></li>
          {email_li}
        </ul>
      </div>
    </div>
    <div class="ftr-b">
      <b>Engineering expertise. Infrastructure that delivers.</b>
      <span>&copy; <span id="yr">2026</span> Anchor Point Engineers and Consultants. All rights reserved.</span>
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
    for old in ROOT.glob("*.html"):
        if old.stem not in pages:
            old.unlink()
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
    for label, ok in (("COMPANY_EMAIL", COMPANY_EMAIL),
                      ("inquiry destination (FORM_ENDPOINT or TELEGRAM_USERNAME)", FORM_ENDPOINT or TELEGRAM_USERNAME),
                      ("CV PDF", (ROOT / CV_FILE).exists()), ("leadership portrait", (ROOT / PORTRAIT).exists())):
        if not ok:
            print("not yet set:", label)


if __name__ == "__main__":
    main()
