#!/usr/bin/env python3
"""
Render animated SVG profile cards for Zeniwui into cards/<theme>/.
Supports three themes: terminal, blueprint, editorial.
All animations use pure CSS keyframes inside standalone SVGs (no JS, no external requests).
"""
import argparse
import datetime
import json
import os
from html import escape

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(ROOT, "data", "contributions.json")
CARDS_DIR = os.path.join(ROOT, "cards")

FONT_SANS = "system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
FONT_MONO = "ui-monospace, 'SFMono-Regular', Menlo, Consolas, monospace"
FONT_SERIF = "Georgia, 'Times New Roman', serif"

THEMES = {
    "terminal": {
        "bg": "#0d0b14",
        "card": "#161224",
        "card_alt": "#1f1933",
        "border": "#342952",
        "text": "#f3effa",
        "text_soft": "#d6cceb",
        "muted": "#9b8cb8",
        "primary": "#c084fc",
        "accent": "#e879f9",
        "accent2": "#a78bfa",
        "heat": ["#1b152b", "#3b1f6e", "#6d28d9", "#9333ea", "#c084fc"],
        "radius": 14,
        "title_font": FONT_MONO,
    },
    "blueprint": {
        "bg": "#0a192f",
        "card": "#112240",
        "card_alt": "#162d50",
        "border": "#1e3a5f",
        "text": "#e2e8f0",
        "text_soft": "#cbd5e1",
        "muted": "#94a3b8",
        "primary": "#38bdf8",
        "accent": "#f59e0b",
        "accent2": "#34d399",
        "heat": ["#112240", "#0c4a6e", "#0284c7", "#38bdf8", "#7dd3fc"],
        "radius": 10,
        "title_font": FONT_SANS,
    },
    "editorial": {
        "bg": "#f4f4f0",
        "card": "#ffffff",
        "card_alt": "#eaeae4",
        "border": "#dcdcd7",
        "text": "#111111",
        "text_soft": "#2d2d30",
        "muted": "#5c5c62",
        "primary": "#2563eb",
        "accent": "#ef4444",
        "accent2": "#eab308",
        "heat": ["#e5e7eb", "#bfdbfe", "#60a5fa", "#2563eb", "#1d4ed8"],
        "radius": 16,
        "title_font": FONT_SERIF,
    },
}

TERMINAL_PALETTES = {
    "lila-obsidian": THEMES["terminal"],
    "tokyo-violet": {
        **THEMES["terminal"],
        "bg": "#0f1020",
        "card": "#17192e",
        "card_alt": "#1f223d",
        "border": "#2e3359",
        "text": "#eef0ff",
        "text_soft": "#c8cde8",
        "muted": "#8890b5",
        "primary": "#bb9af7",
        "accent": "#7dcfff",
        "accent2": "#9d7cd8",
        "heat": ["#1b1e36", "#37306b", "#5b42a6", "#8b5cf6", "#bb9af7"],
    },
    "amethyst-rose": {
        **THEMES["terminal"],
        "bg": "#120b18",
        "card": "#1c1126",
        "card_alt": "#261733",
        "border": "#3f2654",
        "text": "#fdf4ff",
        "text_soft": "#e9d5ff",
        "muted": "#a88bb8",
        "primary": "#e879f9",
        "accent": "#f472b6",
        "accent2": "#a855f7",
        "heat": ["#21132b", "#4a1959", "#7e22ce", "#c026d3", "#e879f9"],
    },
    "emerald-matrix": {
        **THEMES["terminal"],
        "bg": "#0d1117",
        "card": "#161b22",
        "card_alt": "#1c2128",
        "border": "#30363d",
        "text": "#e6edf3",
        "text_soft": "#c9d1d9",
        "muted": "#8b949e",
        "primary": "#3fb950",
        "accent": "#58a6ff",
        "accent2": "#d2a8ff",
        "heat": ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"],
    },
    "tokyo-cyan": {
        **THEMES["terminal"],
        "bg": "#0b1220",
        "card": "#111c30",
        "card_alt": "#172540",
        "border": "#243b61",
        "text": "#ecf6ff",
        "text_soft": "#c4dcf2",
        "muted": "#7d99ba",
        "primary": "#38bdf8",
        "accent": "#2dd4bf",
        "accent2": "#818cf8",
        "heat": ["#142138", "#114b73", "#0284c7", "#38bdf8", "#7dd3fc"],
    },
    "tokyo-amber": {
        **THEMES["terminal"],
        "bg": "#14110f",
        "card": "#1e1916",
        "card_alt": "#28211d",
        "border": "#42362e",
        "text": "#fcf6ee",
        "text_soft": "#e6d8c5",
        "muted": "#a3917d",
        "primary": "#fbbf24",
        "accent": "#fb923c",
        "accent2": "#fde68a",
        "heat": ["#241d18", "#5c3814", "#9a5812", "#d97706", "#fbbf24"],
    },
    "tokyo-crimson": {
        **THEMES["terminal"],
        "bg": "#120d14",
        "card": "#1c1420",
        "card_alt": "#261b2b",
        "border": "#442c47",
        "text": "#fdf2f5",
        "text_soft": "#ebd0d9",
        "muted": "#a68492",
        "primary": "#fb7185",
        "accent": "#38bdf8",
        "accent2": "#fda4af",
        "heat": ["#221626", "#5c1b30", "#9f1239", "#e11d48", "#fb7185"],
    },
    "tokyo-emerald": {
        **THEMES["terminal"],
        "bg": "#0b1412",
        "card": "#11201d",
        "card_alt": "#172b27",
        "border": "#244740",
        "text": "#ecfdf5",
        "text_soft": "#c3e8dc",
        "muted": "#7aa398",
        "primary": "#34d399",
        "accent": "#22d3ee",
        "accent2": "#a3e635",
        "heat": ["#132622", "#14533e", "#047857", "#10b981", "#34d399"],
    },
    "tokyo-sakura": {
        **THEMES["terminal"],
        "bg": "#13111c",
        "card": "#1c1929",
        "card_alt": "#252136",
        "border": "#3c3557",
        "text": "#fdf4ff",
        "text_soft": "#e2d6f5",
        "muted": "#9c8fb8",
        "primary": "#f472b6",
        "accent": "#60a5fa",
        "accent2": "#c084fc",
        "heat": ["#201c30", "#5b244e", "#9d174d", "#db2777", "#f472b6"],
    },
    "royal-plum": {
        **THEMES["terminal"],
        "bg": "#23022E",
        "card": "#2f093d",
        "card_alt": "#3c114d",
        "border": "#573280",
        "text": "#EFF8E2",
        "text_soft": "#CECFC7",
        "muted": "#ADA8B6",
        "primary": "#EFF8E2",
        "accent": "#ADA8B6",
        "accent2": "#CECFC7",
        "heat": ["#330d42", "#573280", "#7c52a8", "#ADA8B6", "#EFF8E2"],
    },
    "sunset-teal": {
        **THEMES["terminal"],
        "bg": "#233D4D",
        "card": "#2b495c",
        "card_alt": "#33566b",
        "border": "#619B8A",
        "text": "#f6f8f5",
        "text_soft": "#d7e3dc",
        "muted": "#a3bfb7",
        "primary": "#A1C181",
        "accent": "#FE7F2D",
        "accent2": "#FCCA46",
        "heat": ["#2c4b5e", "#619B8A", "#A1C181", "#FCCA46", "#FE7F2D"],
    },
    "midnight-cobalt": {
        **THEMES["terminal"],
        "bg": "#0D1317",
        "card": "#101D42",
        "card_alt": "#162654",
        "border": "#232ED1",
        "text": "#eef7fa",
        "text_soft": "#c8d8ee",
        "muted": "#8299bd",
        "primary": "#89D2DC",
        "accent": "#6564DB",
        "accent2": "#a5b4fc",
        "heat": ["#101D42", "#232ED1", "#4749d6", "#6564DB", "#8b8af5"],
    },
}

BASE_CSS = """
@keyframes rise{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:none}}
@keyframes fade{from{opacity:0}to{opacity:1}}
@keyframes grow{from{transform:scaleY(0)}to{transform:scaleY(1)}}
@keyframes pop{0%{opacity:0;transform:scale(.4)}70%{opacity:1;transform:scale(1.12)}100%{opacity:1;transform:none}}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.25}}
@keyframes blink{0%,49%{opacity:1}50%,100%{opacity:0}}
@keyframes nudge{0%,100%{transform:none}50%{transform:translateX(5px)}}
@keyframes flow{to{stroke-dashoffset:-28}}
@keyframes tilein{0%{opacity:0;transform:translateY(26px) scale(.94)}65%{opacity:1;transform:translateY(-3px) scale(1.01)}100%{opacity:1;transform:none}}
@keyframes sheen{0%{transform:translateX(-300px) skewX(-20deg)}28%,100%{transform:translateX(520px) skewX(-20deg)}}
.r{opacity:0;animation:rise .7s cubic-bezier(.2,.7,.2,1) both;transform-box:fill-box}
.f{opacity:0;animation:fade .6s ease-out both}
.g{transform-box:fill-box;transform-origin:bottom;transform:scaleY(0);animation:grow .75s cubic-bezier(.2,.7,.2,1) both}
.p{opacity:0;transform-box:fill-box;transform-origin:center;animation:pop .45s ease-out both}
.live{animation:pulse 1.8s ease-in-out infinite}
.cur{animation:blink 1.05s steps(1) infinite}
.n{transform-box:fill-box;animation:nudge 1.8s ease-in-out infinite}
.fl{stroke-dasharray:6 8;animation:flow 1.4s linear infinite}
.ti{opacity:0;transform-box:fill-box;animation:tilein .8s cubic-bezier(.2,.8,.2,1) both}
.sh{animation:sheen 5.5s ease-in-out infinite}
@media (prefers-reduced-motion:reduce){
  .r,.f,.g,.p,.live,.cur,.n,.fl,.ti{animation:none!important;opacity:1!important;transform:none!important}
  .sh{display:none}
}
"""

REPOS = [
    {
        "slug": "gestor-pedidos-miel",
        "tag": "BACKEND · AUTOMATIZACIÓN",
        "title": "gestor-pedidos-miel",
        "lines": [
            "Aplicación para gestionar pedidos de",
            "una tienda online y enviar avisos",
            "automáticos por WhatsApp.",
        ],
        "tech": "Backend · WhatsApp · Automatización",
    },
    {
        "slug": "vrp",
        "tag": "JAVA · INVESTIGACIÓN iScOp",
        "title": "vrp",
        "lines": [
            "Implementación en Java de algoritmos",
            "de optimización y planificación en",
            "prácticas con iScOp (UniOvi).",
        ],
        "tech": "Java · Optimización · UniOvi",
    },
    {
        "slug": "landing-pcu",
        "tag": "WEB · COMUNIDAD UNIOVI",
        "title": "landing-pcu",
        "lines": [
            "Página web de la Asociación de",
            "Programación Competitiva de la",
            "Universidad de Oviedo.",
        ],
        "tech": "Web · Programación Competitiva",
    },
]

STACK_COLS = [
    ("01 // LENGUAJES", ["Java", "PHP", "C++", "Python"]),
    ("02 // BACKEND & DATOS", ["Spring", "Laravel", "MySQL", "PostgreSQL"]),
    ("03 // WORKFLOW", ["Git", "GitHub", "Automatización", "APIs REST"]),
]

MONTH_NAMES_ES = {
    "01": "Ene", "02": "Feb", "03": "Mar", "04": "Abr",
    "05": "May", "06": "Jun", "07": "Jul", "08": "Ago",
    "09": "Sep", "10": "Oct", "11": "Nov", "12": "Dic",
}


def svg_doc(w: int, h: int, title: str, desc: str, body: str, extra_css: str = "") -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" role="img" aria-labelledby="title desc">'
        f'<title id="title">{escape(title)}</title>'
        f'<desc id="desc">{escape(desc)}</desc>'
        f'<style>{BASE_CSS}{extra_css}</style>'
        f'{body}</svg>'
    )


def _blueprint_grid(t: dict, w: int, h: int, step: int = 40) -> str:
    lines = []
    for x in range(step, w, step):
        lines.append(f'<line x1="{x}" y1="0" x2="{x}" y2="{h}" stroke="{t["border"]}" stroke-width="1" opacity="0.35"/>')
    for y in range(step, h, step):
        lines.append(f'<line x1="0" y1="{y}" x2="{w}" y2="{y}" stroke="{t["border"]}" stroke-width="1" opacity="0.35"/>')
    return "".join(lines)


def _card_frame(theme_name: str, t: dict, w: int, h: int) -> str:
    r = t["radius"]
    bg = f'<rect width="{w}" height="{h}" rx="{r}" fill="{t["bg"]}" stroke="{t["border"]}" stroke-width="1.5"/>'
    if theme_name == "blueprint":
        return bg + f'<g clip-path="url(#clip)">{_blueprint_grid(t, w, h)}</g>'
    return bg


def render_hero(theme_name: str, t: dict, stats: dict) -> str:
    w, h = 1200, 360
    r = t["radius"]
    clip = f'<defs><clipPath id="clip"><rect width="{w}" height="{h}" rx="{r}"/></clipPath></defs>'
    frame = _card_frame(theme_name, t, w, h)

    # Left identity block
    badge_text = "EPI GIJÓN · UNIOVI"
    left = (
        f'<g transform="translate(56,52)">'
        f'<g class="r" style="animation-delay:0ms">'
        f'<rect width="232" height="32" rx="16" fill="{t["card"]}" stroke="{t["border"]}"/>'
        f'<circle cx="20" cy="16" r="5" fill="{t["primary"]}" class="live"/>'
        f'<text x="36" y="21" font-family="{FONT_MONO}" font-size="14" font-weight="600" fill="{t["text_soft"]}" letter-spacing="1">{badge_text}</text>'
        f'</g>'
        f'<text x="0" y="106" font-family="{t["title_font"]}" font-size="60" font-weight="700" fill="{t["text"]}" class="r" style="animation-delay:80ms">Xen'
        f'<tspan font-family="{FONT_MONO}" font-size="30" font-weight="500" fill="{t["primary"]}"> // Zeniwui</tspan></text>'
        f'<text x="0" y="150" font-family="{FONT_SANS}" font-size="22" font-weight="600" fill="{t["accent"]}" class="r" style="animation-delay:150ms">Ingeniería Informática · Backend &amp; Automatización</text>'
        f'<text x="0" y="192" font-family="{FONT_SANS}" font-size="19" fill="{t["text_soft"]}" class="r" style="animation-delay:210ms">Desarrollo sistemas backend, APIs y</text>'
        f'<text x="0" y="220" font-family="{FONT_SANS}" font-size="19" fill="{t["text_soft"]}" class="r" style="animation-delay:240ms">automatización de procesos.</text>'
        f'<text x="0" y="254" font-family="{FONT_SANS}" font-size="19" fill="{t["muted"]}" class="r" style="animation-delay:270ms">Código limpio para problemas reales.</text>'
        f'</g>'
    )

    # Right theme-specific animated centerpiece
    total = stats.get("total_contributions", 0)
    streak = stats.get("current_streak", 0)

    if theme_name == "terminal":
        right = (
            f'<g transform="translate(700,40)"><g class="r" style="animation-delay:180ms">'
            f'<rect width="444" height="280" rx="12" fill="{t["card"]}" stroke="{t["border"]}" stroke-width="1.5"/>'
            f'<rect width="444" height="38" rx="12" fill="{t["card_alt"]}"/>'
            f'<rect y="26" width="444" height="12" fill="{t["card_alt"]}"/>'
            f'<circle cx="22" cy="19" r="6" fill="#ff5f56"/>'
            f'<circle cx="42" cy="19" r="6" fill="#ffbd2e"/>'
            f'<circle cx="62" cy="19" r="6" fill="#27c93f"/>'
            f'<text x="222" y="24" text-anchor="middle" font-family="{FONT_MONO}" font-size="14" fill="{t["muted"]}">zeniwui@epi-gijon:~</text>'
            f'<g font-family="{FONT_MONO}" font-size="17" transform="translate(22,74)">'
            f'<text y="0" fill="{t["primary"]}" class="f" style="animation-delay:260ms">$ whoami</text>'
            f'<text y="28" fill="{t["text"]}" class="f" style="animation-delay:380ms">xen // backend &amp; automation</text>'
            f'<text y="66" fill="{t["primary"]}" class="f" style="animation-delay:520ms">$ cat stack.conf</text>'
            f'<text y="94" fill="{t["accent"]}" class="f" style="animation-delay:640ms">java · spring · php · laravel · python</text>'
            f'<text y="132" fill="{t["primary"]}" class="f" style="animation-delay:780ms">$ gh status --year</text>'
            f'<text y="160" fill="{t["text_soft"]}" class="f" style="animation-delay:900ms">{total} contribs · {streak}d streak</text>'
            f'<text y="192" fill="{t["primary"]}" class="f" style="animation-delay:1020ms">$ <tspan class="cur" fill="{t["text"]}">█</tspan></text>'
            f'</g></g></g>'
        )
    elif theme_name == "blueprint":
        right = (
            f'<g transform="translate(700,40)"><g class="r" style="animation-delay:180ms">'
            f'<rect width="444" height="280" rx="10" fill="{t["card"]}" stroke="{t["border"]}" stroke-width="1.5"/>'
            f'<text x="20" y="30" font-family="{FONT_MONO}" font-size="14" fill="{t["primary"]}" letter-spacing="1.5">SYS // BACKEND PIPELINE</text>'
            f'<text x="424" y="30" text-anchor="end" font-family="{FONT_MONO}" font-size="14" fill="{t["accent"]}">{total} OPS</text>'
            f'<line x1="20" y1="44" x2="424" y2="44" stroke="{t["border"]}"/>'
            # Animated flow connectors
            f'<path d="M 134 114 L 180 114" stroke="{t["primary"]}" stroke-width="2.5" class="fl"/>'
            f'<path d="M 310 114 L 356 114" stroke="{t["accent"]}" stroke-width="2.5" class="fl"/>'
            f'<path d="M 245 148 L 245 190" stroke="{t["accent2"]}" stroke-width="2.5" class="fl"/>'
            # Nodes
            f'<g class="p" style="animation-delay:300ms"><rect x="24" y="80" width="110" height="68" rx="8" fill="{t["card_alt"]}" stroke="{t["primary"]}" stroke-width="1.5"/>'
            f'<text x="79" y="110" text-anchor="middle" font-family="{FONT_MONO}" font-size="15" font-weight="700" fill="{t["text"]}">CLIENT</text>'
            f'<text x="79" y="132" text-anchor="middle" font-family="{FONT_MONO}" font-size="13" fill="{t["muted"]}">HTTP / WA</text></g>'
            f'<g class="p" style="animation-delay:460ms"><rect x="180" y="80" width="130" height="68" rx="8" fill="{t["card_alt"]}" stroke="{t["accent"]}" stroke-width="1.5"/>'
            f'<text x="245" y="110" text-anchor="middle" font-family="{FONT_MONO}" font-size="15" font-weight="700" fill="{t["text"]}">API CORE</text>'
            f'<text x="245" y="132" text-anchor="middle" font-family="{FONT_MONO}" font-size="13" fill="{t["muted"]}">Spring/Laravel</text></g>'
            f'<g class="p" style="animation-delay:620ms"><rect x="356" y="80" width="68" height="68" rx="8" fill="{t["card_alt"]}" stroke="{t["primary"]}" stroke-width="1.5"/>'
            f'<text x="390" y="110" text-anchor="middle" font-family="{FONT_MONO}" font-size="15" font-weight="700" fill="{t["text"]}">DB</text>'
            f'<text x="390" y="132" text-anchor="middle" font-family="{FONT_MONO}" font-size="13" fill="{t["muted"]}">SQL</text></g>'
            f'<g class="p" style="animation-delay:780ms"><rect x="135" y="190" width="220" height="58" rx="8" fill="{t["card_alt"]}" stroke="{t["accent2"]}" stroke-width="1.5"/>'
            f'<text x="245" y="216" text-anchor="middle" font-family="{FONT_MONO}" font-size="15" font-weight="700" fill="{t["accent2"]}">AUTOMATION &amp; VRP</text>'
            f'<text x="245" y="236" text-anchor="middle" font-family="{FONT_MONO}" font-size="13" fill="{t["muted"]}">Java · Python · C++</text></g>'
            f'</g></g>'
        )
    else:  # editorial
        pillars = [
            ("01", "BACKEND", "Java · Spring · PHP · Laravel", t["primary"], 220),
            ("02", "AUTOMATION", "Scripts · APIs · WhatsApp Bots", t["accent"], 360),
            ("03", "ALGORITHMS", "VRP · iScOp · C++ · Python", t["accent2"], 500),
        ]
        items = []
        for idx, (num, label, sub, col, delay) in enumerate(pillars):
            yy = idx * 92
            items.append(
                f'<g transform="translate(0,{yy})"><g class="ti" style="animation-delay:{delay}ms">'
                f'<rect width="430" height="78" rx="12" fill="{t["card"]}" stroke="{t["border"]}" stroke-width="1.5"/>'
                f'<rect width="8" height="78" rx="4" fill="{col}"/>'
                f'<text x="26" y="34" font-family="{FONT_MONO}" font-size="14" font-weight="700" fill="{col}" letter-spacing="1.2">{num} · {label}</text>'
                f'<text x="26" y="59" font-family="{FONT_SANS}" font-size="18" font-weight="600" fill="{t["text"]}">{sub}</text>'
                f'</g></g>'
            )
        right = f'<g transform="translate(714,48)">{"".join(items)}</g>'

    return svg_doc(
        w, h,
        "Xen (Zeniwui) — Ingeniería Informática, Backend y Automatización",
        "Tarjeta principal de perfil de Xen (Zeniwui) con resumen de enfoque técnico y datos en vivo.",
        clip + frame + left + right,
    )


def render_heatmap(theme_name: str, t: dict, stats: dict) -> str:
    w, h = 1200, 236
    r = t["radius"]
    clip = f'<defs><clipPath id="clip"><rect width="{w}" height="{h}" rx="{r}"/></clipPath></defs>'
    frame = _card_frame(theme_name, t, w, h)

    total = stats.get("total_contributions", 0)
    streak = stats.get("current_streak", 0)
    days = stats.get("days", [])

    header = (
        f'<g transform="translate(46,40)">'
        f'<text x="0" y="0" font-family="{t["title_font"]}" font-size="24" font-weight="700" fill="{t["text"]}">Actividad en GitHub</text>'
        f'<text x="1108" y="0" text-anchor="end" font-family="{FONT_MONO}" font-size="18" fill="{t["muted"]}">'
        f'<tspan fill="{t["primary"]}" font-weight="700">{total}</tspan> contribuciones · racha <tspan fill="{t["accent"]}" font-weight="700">{streak}d</tspan></text>'
        f'</g>'
    )

    # Group days into columns (weeks starting Sunday)
    if days:
        first_dt = datetime.date.fromisoformat(days[0]["date"])
        pad = (first_dt.weekday() + 1) % 7  # Sunday=0
    else:
        pad = 0

    cells_svg = []
    month_labels = []
    seen_months = set()
    cell, gap = 17, 4
    step = cell + gap
    start_x, start_y = 46, 62

    for i, d in enumerate(days):
        pos = i + pad
        col = pos // 7
        row = pos % 7
        if col >= 53:
            continue
        x = start_x + col * step
        y = start_y + row * step
        lvl = max(0, min(4, int(d.get("level", 0))))
        fill = t["heat"][lvl]
        delay = min(900, col * 15)
        cls = "p" if lvl == 4 else "f"
        cells_svg.append(
            f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="4" '
            f'fill="{fill}" class="{cls}" style="animation-delay:{delay}ms"/>'
        )
        ym = d["date"][:7]
        if row == 0 and ym not in seen_months and col < 51:
            seen_months.add(ym)
            m_label = MONTH_NAMES_ES.get(d["date"][5:7], d["date"][5:7])
            month_labels.append(
                f'<text x="{x}" y="220" font-family="{FONT_MONO}" font-size="15" fill="{t["muted"]}">{m_label}</text>'
            )

    return svg_doc(
        w, h,
        f"Mapa de contribuciones de Zeniwui ({total} contribuciones)",
        "Grafo anual animado con las contribuciones diarias reales en GitHub.",
        clip + frame + header + "".join(cells_svg) + "".join(month_labels),
    )


def render_activity(theme_name: str, t: dict, stats: dict) -> str:
    w, h = 1200, 260
    r = t["radius"]
    clip = f'<defs><clipPath id="clip"><rect width="{w}" height="{h}" rx="{r}"/></clipPath></defs>'
    frame = _card_frame(theme_name, t, w, h)

    total = stats.get("total_contributions", 0)
    curr = stats.get("current_streak", 0)
    longest = stats.get("longest_streak", 0)
    best = stats.get("best_day", {"count": 0, "date": "-"})
    monthly = stats.get("monthly", [])[-12:]
    max_m = max((m["count"] for m in monthly), default=1) or 1

    left = (
        f'<g transform="translate(56,48)">'
        f'<text x="0" y="0" font-family="{t["title_font"]}" font-size="24" font-weight="700" fill="{t["text"]}">Pulso Mensual</text>'
        f'<g transform="translate(0,48)"><g class="r" style="animation-delay:120ms">'
        f'<text y="0" font-family="{FONT_MONO}" font-size="15" fill="{t["muted"]}">TOTAL 12 MESES</text>'
        f'<text y="34" font-family="{FONT_SANS}" font-size="34" font-weight="700" fill="{t["primary"]}">{total}</text>'
        f'</g></g>'
        f'<g transform="translate(0,124)"><g class="r" style="animation-delay:220ms">'
        f'<text y="0" font-family="{FONT_MONO}" font-size="15" fill="{t["muted"]}">RACHA ACTUAL / MÁX</text>'
        f'<text y="34" font-family="{FONT_SANS}" font-size="30" font-weight="700" fill="{t["text"]}">{curr}d <tspan fill="{t["muted"]}" font-size="22">/ {longest}d</tspan></text>'
        f'</g></g>'
        f'<g transform="translate(0,192)"><g class="r" style="animation-delay:320ms">'
        f'<text y="0" font-family="{FONT_MONO}" font-size="15" fill="{t["muted"]}">MEJOR DÍA: <tspan fill="{t["accent"]}" font-weight="700">{best["count"]} contribs</tspan> ({best["date"]})</text>'
        f'</g></g></g>'
    )

    # Monthly bar chart
    bars = []
    chart_x, chart_y, chart_h = 410, 62, 134
    col_w = 61
    for i, m in enumerate(monthly):
        cnt = m["count"]
        bh = max(6, int((cnt / max_m) * chart_h))
        bx = chart_x + i * col_w
        by = chart_y + (chart_h - bh)
        is_peak = cnt == max_m and cnt > 0
        fill = t["accent"] if is_peak else t["primary"]
        lbl = MONTH_NAMES_ES.get(m["month"][5:7], m["month"][5:7])
        delay = 140 + i * 55
        bars.append(
            f'<g>'
            f'<rect x="{bx + 10}" y="{by}" width="34" height="{bh}" rx="6" fill="{fill}" class="g" style="animation-delay:{delay}ms"/>'
            f'<text x="{bx + 27}" y="{by - 8}" text-anchor="middle" font-family="{FONT_MONO}" font-size="15" fill="{t["text_soft"]}" class="f" style="animation-delay:{delay + 200}ms">{cnt}</text>'
            f'<text x="{bx + 27}" y="{chart_y + chart_h + 24}" text-anchor="middle" font-family="{FONT_MONO}" font-size="15" fill="{t["muted"]}">{lbl}</text>'
            f'</g>'
        )

    return svg_doc(
        w, h,
        "Resumen mensual de actividad y rachas de Zeniwui",
        "Gráfica animada de barras mensuales con racha actual, racha máxima y mejor día.",
        clip + frame + left + "".join(bars),
    )


def render_repo_card(theme_name: str, t: dict, repo: dict, idx: int) -> str:
    w, h = 400, 240
    r = t["radius"]
    clip = f'<defs><clipPath id="clip"><rect width="{w}" height="{h}" rx="{r}"/></clipPath></defs>'
    frame = _card_frame(theme_name, t, w, h)
    accent_cycle = [t["primary"], t["accent"], t["accent2"]]
    col = accent_cycle[idx % len(accent_cycle)]
    delay = idx * 140

    top_bar = ""
    if theme_name == "editorial":
        top_bar = f'<rect width="{w}" height="6" rx="3" fill="{col}" clip-path="url(#clip)"/>'

    lines_svg = []
    for li, line in enumerate(repo["lines"]):
        lines_svg.append(
            f'<text x="28" y="{116 + li * 25}" font-family="{FONT_SANS}" font-size="18" fill="{t["text_soft"]}">{escape(line)}</text>'
        )

    body = (
        f'<g class="ti" style="animation-delay:{delay}ms">'
        f'{top_bar}'
        f'<text x="28" y="42" font-family="{FONT_MONO}" font-size="14" font-weight="700" fill="{col}" letter-spacing="0.8">{escape(repo["tag"])}</text>'
        f'<text x="28" y="76" font-family="{t["title_font"]}" font-size="25" font-weight="700" fill="{t["text"]}">{escape(repo["title"])}</text>'
        f'{"".join(lines_svg)}'
        f'<line x1="28" y1="192" x2="372" y2="192" stroke="{t["border"]}"/>'
        f'<text x="28" y="218" font-family="{FONT_MONO}" font-size="14" fill="{t["muted"]}">{escape(repo["tech"])}</text>'
        f'<text x="368" y="218" text-anchor="end" font-family="{FONT_MONO}" font-size="20" font-weight="700" fill="{col}" class="n">→</text>'
        f'</g>'
    )

    return svg_doc(
        w, h,
        f"Proyecto {repo['title']}",
        " ".join(repo["lines"]),
        clip + frame + body,
    )


def render_stack(theme_name: str, t: dict) -> str:
    w, h = 1200, 210
    r = t["radius"]
    clip = f'<defs><clipPath id="clip"><rect width="{w}" height="{h}" rx="{r}"/></clipPath></defs>'
    frame = _card_frame(theme_name, t, w, h)

    header = (
        f'<text x="56" y="46" font-family="{t["title_font"]}" font-size="24" font-weight="700" fill="{t["text"]}">Stack Tecnológico</text>'
    )

    cols_svg = []
    accents = [t["primary"], t["accent"], t["accent2"]]
    for idx, (heading, items) in enumerate(STACK_COLS):
        cx = 56 + idx * 376
        col = accents[idx % len(accents)]
        pills = []
        for pi, item in enumerate(items):
            px = (pi % 2) * 168
            py = 30 + (pi // 2) * 44
            pills.append(
                f'<rect x="{px}" y="{py}" width="156" height="34" rx="8" fill="{t["card"]}" stroke="{t["border"]}"/>'
                f'<circle cx="{px + 16}" cy="{py + 17}" r="4" fill="{col}"/>'
                f'<text x="{px + 30}" y="{py + 23}" font-family="{FONT_SANS}" font-size="18" font-weight="600" fill="{t["text_soft"]}">{escape(item)}</text>'
            )
        cols_svg.append(
            f'<g transform="translate({cx},74)"><g class="r" style="animation-delay:{idx * 130}ms">'
            f'<text x="0" y="14" font-family="{FONT_MONO}" font-size="15" font-weight="700" fill="{col}" letter-spacing="1">{escape(heading)}</text>'
            f'{"".join(pills)}'
            f'</g></g>'
        )

    return svg_doc(
        w, h,
        "Stack tecnológico de Zeniwui",
        "Lenguajes, frameworks backend, bases de datos y herramientas principales.",
        clip + frame + header + "".join(cols_svg),
    )


def generate_theme(theme_name: str, stats: dict, out_dir: str | None = None, palette: dict | None = None):
    t = palette or THEMES[theme_name]
    target_dir = out_dir or os.path.join(CARDS_DIR, theme_name)
    os.makedirs(target_dir, exist_ok=True)

    outputs = {
        "hero.svg": render_hero(theme_name, t, stats),
        "heatmap.svg": render_heatmap(theme_name, t, stats),
        "activity.svg": render_activity(theme_name, t, stats),
        "stack.svg": render_stack(theme_name, t),
    }
    for idx, repo in enumerate(REPOS):
        outputs[f"repo-{repo['slug']}.svg"] = render_repo_card(theme_name, t, repo, idx)

    for fname, content in outputs.items():
        with open(os.path.join(target_dir, fname), "w", encoding="utf-8") as f:
            f.write(content)
    print(f"Generated {len(outputs)} SVGs for theme '{theme_name}' in {target_dir}")


def main():
    parser = argparse.ArgumentParser(description="Render animated SVG cards for Zeniwui.")
    parser.add_argument(
        "--theme",
        choices=["all", "terminal", "blueprint", "editorial"],
        default="all",
        help="Theme to generate (default: all)",
    )
    parser.add_argument(
        "--palette",
        choices=list(TERMINAL_PALETTES.keys()),
        default="lila-obsidian",
        help="Color palette for terminal theme",
    )
    parser.add_argument(
        "--out-dir",
        default=None,
        help="Optional custom output directory",
    )
    args = parser.parse_args()

    with open(DATA_PATH, "r", encoding="utf-8") as f:
        stats = json.load(f)

    themes = list(THEMES.keys()) if args.theme == "all" else [args.theme]
    for name in themes:
        pal = TERMINAL_PALETTES[args.palette] if name == "terminal" else None
        generate_theme(name, stats, out_dir=args.out_dir, palette=pal)


if __name__ == "__main__":
    main()
