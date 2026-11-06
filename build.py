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
    ("blank",),
    ("kv", "Hobbies.Computer", "Gaming, Machine Learning, NLP"),
    ("kv", "Hobbies.Real", "Mountaineering, Heraldry, Tabletop RPG"),
    ("kv", "Hobbies.Other", "Genealogy, Medieval History, Space"),
    ("blank",),
    ("section", "Contact"),
    ("kv", "Email.Personal", "phcmlima@gmail.com"),
    ("kv", "LinkedIn", "phcmlima")
]

FONT = "'Courier New', Consolas, 'DejaVu Sans Mono', monospace"
FONT_SIZE = 16
CHAR_W = 9.6
LINE_H = 20
COLS = 58
ASCII_X = 15
INFO_X = 400
PAD_TOP = 30

THEMES = {
    "dark_mode.svg": dict(bg="#161b22", ascii="#c9d1d9", key="#ffa657", val="#a5d6ff", dots="#616e7f", rule="#c9d1d9"),
    "light_mode.svg": dict(bg="#f6f8fa", ascii="#24292f", key="#953800", val="#0a3069", dots="#c2cfde", rule="#24292f"),
}

def uptime_text(birth: date, today: date) -> str:
    years = today.year - birth.year
    months = today.month - birth.month
    if today.day < birth.day:
        months -= 1
    if months < 0:
        years -= 1
        months += 12
    return f"{years} years, {months} months"

def build_info_lines(values: dict):
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
    rows = max(len(ascii_rows), len(info_lines))
    width = int(INFO_X + COLS * CHAR_W + 20)
    height = PAD_TOP + rows * LINE_H + 10
    css = f"""
    text {{ font-family: {FONT}; font-size: {FONT_SIZE}px; white-space: pre; }}
    .ascii {{ fill: {theme['ascii']}; }}
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
        y = PAD_TOP + i * LINE_H
        parts.append(f'<text x="{ASCII_X}" y="{y}" class="ascii" xml:space="preserve">{escape(row)}</text>')
    for i, segs in enumerate(info_lines):
        y = PAD_TOP + i * LINE_H
        spans = "".join(f'<tspan class="{c}">{escape(t)}</tspan>' for c, t in segs)
        parts.append(f'<text x="{INFO_X}" y="{y}" xml:space="preserve">{spans}</text>')
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

    values = {"uptime": uptime}

    with open(os.path.join(ROOT, "ascii.txt"), encoding="utf-8") as f:
        ascii_rows = f.read().rstrip("\n").split("\n")
    info_lines = build_info_lines(values)

    for name, theme in THEMES.items():
        with open(os.path.join(ROOT, name), "w", encoding="utf-8") as f:
            f.write(render(theme, ascii_rows, info_lines))
        print("gerado:", name)


if __name__ == "__main__":
    main()
