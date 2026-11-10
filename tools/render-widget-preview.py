#!/usr/bin/env python3
"""Render the real composer unit-test buffer as a review PNG (no terminal capture)."""
import json
import math
from pathlib import Path
import re
import subprocess
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
frame = json.loads((ROOT / 'output/native-buffers/composer.json').read_text())
font_path = subprocess.check_output(['fc-match', '-f', '%{file}', 'monospace'], text=True).strip()
font = ImageFont.truetype(font_path, 20)
small = ImageFont.truetype(font_path, 16)
cell_width = math.ceil(font.getlength('M'))
cell_height = 29
padding = 30
top = 84
canvas = Image.new('RGB', (frame['width'] * cell_width + padding * 2,
                           frame['height'] * cell_height + top + 74), '#121212')
draw = ImageDraw.Draw(canvas)
draw.text((padding, 22), 'codex-blue / actual composer test buffer', font=font, fill='#e0e0e0')
draw.text((padding, 53), 'Paper #A4CDFB   Ink #101820   Czech text rendered by Codex', font=small, fill='#aaaaaa')


def rgb(value, default):
    match = re.fullmatch(r'Rgb\((\d+),\s*(\d+),\s*(\d+)\)', value)
    if match:
        return tuple(map(int, match.groups()))
    return default


for index, cell in enumerate(frame['cells']):
    x = padding + (index % frame['width']) * cell_width
    y = top + (index // frame['width']) * cell_height
    ink = rgb(cell['fg'], (224, 224, 224))
    paper = rgb(cell['bg'], (18, 18, 18))
    if 'REVERSED' in cell['modifiers']:
        ink, paper = paper, ink
    draw.rectangle((x, y, x + cell_width - 1, y + cell_height - 1), fill=paper)
    if cell['text'].strip():
        draw.text((x, y + 2), cell['text'], font=font, fill=ink)
draw.text((padding, top + frame['height'] * cell_height + 16),
          'Native widget layout from the test harness; not a terminal screenshot.',
          font=small, fill='#aaaaaa')
canvas.save(ROOT / 'output/native-composer-preview.png')
print(ROOT / 'output/native-composer-preview.png')
