#!/usr/bin/env python3
"""Draw a proposed palette, not an executed Codex widget or terminal capture."""
import json
from pathlib import Path
import subprocess
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
PROFILE = {
    'enabled': True, 'paper': '#D9EBFF', 'ink': '#000000',
    'emphasis_ink': '#A64200', 'hint_ink': '#164E82',
    'cursor': 'terminal', 'cursor_text': 'auto', 'user_text_bold': False,
}
CURSOR = '#008000'
CURSOR_TEXT = PROFILE['paper']  # Kitty cursor_text_color background.
font_path = subprocess.check_output(['fc-match', '-f', '%{file}', 'monospace'], text=True).strip()
bold_path = subprocess.check_output(['fc-match', '-f', '%{file}', 'monospace:style=Bold'], text=True).strip()
font = ImageFont.truetype(font_path, 24)
bold = ImageFont.truetype(bold_path, 24)
small = ImageFont.truetype(font_path, 18)
heading = ImageFont.truetype(bold_path, 25)
canvas = Image.new('RGB', (1280, 646), '#101214')
draw = ImageDraw.Draw(canvas)
ink, paper = PROFILE['ink'], PROFILE['paper']
white, muted = '#E2E6EA', '#A6AFB8'
step = font.getlength('M')
row_height = 36


def text(position, value, color=white, face=font):
    draw.text(position, value, fill=color, font=face)


def runs(x, y, segments):
    for value, color, face in segments:
        text((x, y), value, color, face)
        x += face.getlength(value)


text((30, 24), 'codex-blue / selected input palette', face=heading)
text((30, 66), 'Illustrative mock-up - not a terminal capture or a native widget render.', muted, small)

# An ordinary submitted message provides context for the editable area below.
draw.rectangle((24, 111, 1255, 186), fill=paper)
text((40, 130), '› Pale-blue paper, black ink; orange for styled elements.', ink)
text((30, 212), '• Example input with the proposed color controls:', white, small)

hint = ' ↓ Back to bottom · esc '
hint_width = font.getlength(hint)
hint_x = (canvas.width - hint_width) / 2
hint_y = 264
draw.rectangle((hint_x - 8, hint_y - 5, hint_x + hint_width + 8, hint_y + 34), fill=paper)
text((hint_x, hint_y), hint, PROFILE['hint_ink'], font)

panel = (24, 310, 1255, 437)
draw.rectangle(panel, fill=paper)
x, y = 40, 332
segments = [
    ('› Please review ', ink, font),
    ('[Image #1]', PROFILE['emphasis_ink'], bold),
    (' and ', ink, font),
    ('@FirstZ80', PROFILE['emphasis_ink'], bold),
    (', then continue.', ink, font),
]
runs(x, y, segments)
text((x + step * 2, y + row_height), 'Keep this input text at normal weight.', ink)
# A block cursor over the c in "continue", drawn last as a terminal would overlay it.
prefix = '› Please review [Image #1] and @FirstZ80, then '
cursor_x = x + sum(face.getlength(value) for value, _, face in segments[:-1]) + font.getlength(', then ')
draw.rectangle((int(cursor_x), y, int(cursor_x + step) - 1, y + row_height - 1), fill=CURSOR)
text((cursor_x, y), 'c', CURSOR_TEXT)
text((30, 456), 'Black ink stays normal weight; orange elements are bold.', muted, small)

# Exact colors below the panel make the proposed values easy to reproduce.
items = [
    ('paper', paper), ('ink', ink), ('emphasis', PROFILE['emphasis_ink']),
    ('hint', PROFILE['hint_ink']), ('Kitty cursor', CURSOR),
]
for index, (label, color) in enumerate(items):
    sx = 30 + index * 248
    draw.rectangle((sx, 510, sx + 24, 534), fill=color, outline='#7A848C')
    text((sx + 34, 509), label, white, small)
    text((sx + 34, 538), color, muted, small)
text((30, 596), 'cursor = "terminal": Kitty supplies the green; codex-blue does not override it.', muted, small)
output = ROOT / 'output/next-palette-orange-blue-green-preview.png'
canvas.save(output)
(ROOT / 'drafts/colors-next-orange-blue.example.json').write_text(json.dumps(PROFILE, indent=2) + '\n')
(ROOT / 'output/next-palette-orange-blue-green-preview.json').write_text(json.dumps({
    'kind': 'design-mock-up-not-native-render', 'profile': PROFILE,
    'terminal_cursor': CURSOR, 'terminal_cursor_text': CURSOR_TEXT,
    'font_regular': Path(font_path).name, 'font_bold': Path(bold_path).name,
    'note': 'Color/profile example only; this renderer does not run the CLI or change live settings.',
}, indent=2) + '\n')
print(output)
