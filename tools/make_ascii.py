#!/usr/bin/env python3
"""Gera ascii.txt a partir de uma foto (fundo removido, só você em ASCII).

    pip install opencv-python pillow numpy
    python tools/make_ascii.py caminho/da/foto.jpg

NÃO coloque a foto dentro do repositório público; use um caminho fora dele.

Os parâmetros de recorte abaixo foram ajustados para a foto original (400x400).
Se usar outra foto, ajuste CROP e o polígono TORSO.
"""
import argparse
import os

import cv2
import numpy as np

COLS, ROWS = 88, 50
CROP = (60, 38, 345, 368)                 # x0, y0, x1, y1 (proporção ~ COLS/ROWS * célula)
RAMP = " .'`,:;-~+=*xoO#%@"             # rampa suave: mantém os traços do rosto legíveis
SHARP = 0.8
FLOOR = 4                                  # nunca usar os caracteres mais fracos dentro da silhueta (cabelo/suéter escuros não somem)
GAMMA = 0.60                               # <1 clareia os tons escuros (suéter preto)
# polígono do tronco (suéter quase preto confunde o recorte automático)
TORSO = [(112, 285), (135, 318), (200, 330), (262, 315), (300, 298), (345, 302),
         (399, 335), (399, 399), (24, 399), (32, 380), (62, 345), (105, 318)]
CUT = [(90, 246), (135, 246), (138, 285), (142, 322), (60, 322), (60, 300)]  # sobra de fundo ao lado do pescoço


def person_mask(img):
    h, w = img.shape[:2]
    mask = np.zeros((h, w), np.uint8)
    bg = np.zeros((1, 65)); fg = np.zeros((1, 65))
    cv2.grabCut(img, mask, (20, 25, 360, 370), bg, fg, 8, cv2.GC_INIT_WITH_RECT)
    m = np.where((mask == 1) | (mask == 3), 255, 0).astype("uint8")
    t = np.zeros_like(m)
    cv2.fillPoly(t, [np.array(TORSO, np.int32)], 255)
    m = cv2.bitwise_or(m, t)
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
    cv2.fillPoly(m, [np.array(CUT, np.int32)], 0)
    return cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("photo")
    ap.add_argument("--out", default=os.path.join(os.path.dirname(__file__), "..", "ascii.txt"))
    args = ap.parse_args()

    img = cv2.imread(args.photo)
    if img is None:
        raise SystemExit(f"não consegui abrir {args.photo}")
    mask = person_mask(img)

    x0, y0, x1, y1 = CROP
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)[y0:y1, x0:x1]
    m = mask[y0:y1, x0:x1]

    gray = gray.astype(float)
    inside = gray[m > 0]
    lo, hi = np.percentile(inside, 1), np.percentile(inside, 99.5)
    a = np.clip((gray - lo) / (hi - lo), 0, 1) ** GAMMA
    a = cv2.GaussianBlur(a, (0, 0), 0.8)
    # nitidez (unsharp mask) para olhos, óculos e sorriso se destacarem
    a = np.clip(a + SHARP * (a - cv2.GaussianBlur(a, (0, 0), 3)), 0, 1)

    A = cv2.resize(a, (COLS, ROWS), interpolation=cv2.INTER_AREA)
    M = cv2.resize(m.astype(float) / 255, (COLS, ROWS), interpolation=cv2.INTER_AREA)
    n = len(RAMP)
    rows = []
    for y in range(ROWS):
        row = "".join(" " if M[y, x] < 0.45 else RAMP[FLOOR + min(n - 1 - FLOOR, int(A[y, x] * (n - FLOOR)))] for x in range(COLS))
        rows.append(row.rstrip())
    with open(args.out, "w", encoding="utf-8") as f:
        f.write("\n".join(rows) + "\n")
    print(f"ok: {COLS}x{ROWS} -> {os.path.normpath(args.out)}")


if __name__ == "__main__":
    main()
