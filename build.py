#!/usr/bin/env python3
"""
Uso local:
    BIRTHDATE=2002-03-20 python3 build.py --user pedrohcml
    python3 build.py --user pedrohcml --uptime "24 years, 7 months"   # sem data de nascimento

A data de nascimento NÃO fica gravada no repositório: ela vem da variável de ambiente
BIRTHDATE (no GitHub Actions, de um secret).
"""
import argparse
import os
from datetime import date
from html import escape
import urllib.request
import json

ROOT = os.path.dirname(os.path.abspath(__file__))

HANDLE = "pedro@cavalcante"

INFO = [
    ("kv", "Role", "Software Developer"),
    ("kv", "Company", "Capgemini"),
    ("kv", "Uptime", "{uptime}"),
    ("kv", "Education", "B.Sc. Computer Science, UNIP"),
    ("kv", "Focus", "Data & AI, Dynamics 365 CE"),
    ("blank",),
    ("kv", "Languages.Programming", "Python, JavaScript, C#"),
    ("kv", "Languages.Real", "Portuguese, English, Spanish"),
    ("kv", "IDE", "Visual Studio Code, Jupyter"),
    ("kv", "Stack.Data", "Dataverse, PostgreSQL, MongoDB"),
    ("blank",),
    ("kv", "Hobbies.Computer", "Gaming, Machine Learning, NLP"),
    ("kv", "Hobbies.Real", "Mountaineering, Heraldry, Tabletop RPG"),
    ("kv", "Hobbies.Other", "Genealogy, Medieval History, Space"),
    ("blank",),
    ("section", "Contact"),
    ("kv", "Email.Personal", "phcmlima@gmail.com"),
    ("kv", "LinkedIn", "phcmlima"),
    ("kv", "GitHub", "pedrohcml"),
    ("blank",),
    ("section", "GitHub Stats"),
    ("kv", "Repos", "{repos}"),
    ("kv", "Stars", "{stars}"),
    ("kv", "Followers", "{followers}"),
]

FONT = "'Courier New', Consolas, 'DejaVu Sans Mono', monospace"
FONT_SIZE = 20
CHAR_W = 9.0
LINE_H = 20
COLS = 58

ART_FONT_SIZE = 8.7
ART_CHAR_W = 5.22
ART_LINE_H = 10.6

PAD = 22
PAD_TOP = 26
GAP = 26

RAMP = " .'`,:;-~+=*xoO#%@"
FLOOR = 4

THEMES = {
    "dark_mode.svg": dict(bg="#161b22", ascii="#c9d1d9", key="#ffa657", val="#a5d6ff", dots="#616e7f", rule="#c9d1d9"),
    "light_mode.svg": dict(bg="#f6f8fa", ascii="#24292f", key="#953800", val="#0a3069", dots="#c2cfde", rule="#24292f", invert=True),
}

def invert_ascii(rows: list) -> list:
    n = len(RAMP)
    table = {RAMP[k]: RAMP[FLOOR + (n - 1 - k)] for k in range(FLOOR, n)}
    return ["".join(table.get(c, c) for c in row) for row in rows]

def uptime_text(birth: date, today: date) -> str:
    years = today.year - birth.year
    months = today.month - birth.month
    if today.day < birth.day:
        months -= 1
    if months < 0:
        years -= 1
        months += 12
    return f"{years} years, {months} months"

def fetch_stats(user: str) -> dict:
    out = {"repos": "-", "stars": "-", "followers": "-"}
    headers = {"User-Agent": "profile-readme-builder"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    def get(url):
        with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=15) as r:
            return json.load(r)

    try:
        u = get(f"https://api.github.com/users/{user}")
        out["repos"] = str(u.get("public_repos", "-"))
        out["followers"] = str(u.get("followers", "-"))
        stars, page = 0, 1
        while True:
            repos = get(f"https://api.github.com/users/{user}/repos?per_page=100&page={page}")
            stars += sum(r.get("stargazers_count", 0) for r in repos if not r.get("fork"))
            if len(repos) < 100:
                break
            page += 1
        out["stars"] = str(stars)
    except Exception as exc:  # sem rede, limite de taxa, usuário inexistente...
        print(f"aviso: não consegui buscar estatísticas do GitHub ({exc})")
    return out

def build_info_lines(values: dict):
    """Devolve lista de linhas; cada linha é uma lista de (classe, texto)."""
    lines = [[("val", HANDLE + " "), ("rule", "-" * (COLS - len(HANDLE) - 1))]]
    for item in INFO:
        kind = item[0]
        if kind == "blank":
            lines.append([("dots", ".")])
        elif kind == "section":
            title = f"- {item[1]} "
            lines.append([("rule", title + "-" * (COLS - len(title)))])
        else:
            _, key, value = item
            value = value.format(**values)
            n = max(2, COLS - 5 - len(key) - len(value))
            lines.append([
                ("dots", ". "), ("key", key), ("rule", ":"),
                ("dots", " " + "." * n + " "), ("val", value),
            ])
    return lines

def render(theme: dict, ascii_rows: list, info_lines: list) -> str:
    art_w = max(len(r) for r in ascii_rows) * ART_CHAR_W
    art_h = len(ascii_rows) * ART_LINE_H
    info_h = len(info_lines) * LINE_H
    body_h = max(art_h, info_h)

    info_x = PAD + art_w + GAP
    width = int(info_x + COLS * CHAR_W + PAD)
    height = int(PAD_TOP + body_h + PAD - 6)
    art_y0 = PAD_TOP + (body_h - art_h) / 2        # centraliza a arte na vertical
    info_y0 = PAD_TOP + (body_h - info_h) / 2

    css = f"""
    text {{ font-family: {FONT}; white-space: pre; }}
    .ascii {{ fill: {theme['ascii']}; font-size: {ART_FONT_SIZE}px; font-weight: 700; }}
    .info {{ font-size: {FONT_SIZE}px; }}
    .key {{ fill: {theme['key']}; }}
    .val {{ fill: {theme['val']}; }}
    .dots {{ fill: {theme['dots']}; }}
    .rule {{ fill: {theme['rule']}; }}
    """
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        f"<style>{css}</style>",
        f'<rect width="100%" height="100%" rx="15" fill="{theme["bg"]}"/>',
    ]
    for i, row in enumerate(ascii_rows):
        y = art_y0 + (i + 1) * ART_LINE_H - 2
        parts.append(f'<text x="{PAD}" y="{y:.1f}" class="ascii" xml:space="preserve">{escape(row)}</text>')
    for i, segs in enumerate(info_lines):
        y = info_y0 + (i + 1) * LINE_H - 5
        spans = "".join(f'<tspan class="{c}">{escape(t)}</tspan>' for c, t in segs)
        parts.append(f'<text x="{info_x:.1f}" y="{y:.1f}" class="info" xml:space="preserve">{spans}</text>')
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--user", default=os.environ.get("GITHUB_USER", ""), help="usuário do GitHub (para as estatísticas)")
    ap.add_argument("--uptime", help='texto fixo, ex.: "24 years, 7 months"')
    args = ap.parse_args()

    if args.uptime:
        uptime = args.uptime
    elif os.environ.get("BIRTHDATE"):
        uptime = uptime_text(date.fromisoformat(os.environ["BIRTHDATE"]), date.today())
    else:
        ap.error("informe BIRTHDATE=AAAA-MM-DD no ambiente ou use --uptime")

    stats = fetch_stats(args.user) if args.user else {"repos": "-", "stars": "-", "followers": "-"}
    values = {"uptime": uptime, **stats}

    with open(os.path.join(ROOT, "ascii.txt"), encoding="utf-8") as f:
        ascii_rows = f.read().rstrip("\n").split("\n")
    info_lines = build_info_lines(values)

    for name, theme in THEMES.items():
        rows = invert_ascii(ascii_rows) if theme.get("invert") else ascii_rows
        with open(os.path.join(ROOT, name), "w", encoding="utf-8") as f:
            f.write(render(theme, rows, info_lines))
        print("gerado:", name)


if __name__ == "__main__":
    main()
