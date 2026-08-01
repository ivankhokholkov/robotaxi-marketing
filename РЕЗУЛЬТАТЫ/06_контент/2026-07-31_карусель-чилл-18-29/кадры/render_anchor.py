from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import colorsys

SRC = Path('/Users/ivankhokholkov/.codex/generated_images/019fb727-ec0a-76f1-823a-8e1aea186fa3/exec-0365fb4a-3b74-4744-aae1-96a48d77673c.png')
OUT = Path('/Users/ivankhokholkov/Documents/Codex/2026-07-31/1-06-2026-07-31-18/outputs/01_sadis-i-vydohni_editorial_v3.png')
FONT = '/System/Library/Fonts/HelveticaNeue.ttc'

W, H = 1080, 1350


def font_for(text, maximum, start=166, index=10):
    size = start
    while size > 40:
        face = ImageFont.truetype(FONT, size, index=index)
        if ImageDraw.Draw(Image.new('RGB', (1, 1))).textlength(text, font=face) <= maximum:
            return face
        size -= 2
    return ImageFont.truetype(FONT, 40, index=index)


def spaced(draw, xy, text, font, fill, tracking):
    x, y = xy
    for char in text:
        draw.text((x, y), char, font=font, fill=fill)
        x += draw.textlength(char, font=font) + tracking


base = Image.open(SRC).convert('RGB')
crop_h = int(base.width * H / W)
base = base.crop((0, 0, base.width, crop_h)).resize((W, H), Image.Resampling.LANCZOS)

# Remove the unwanted red/orange tail-lamp glow while retaining natural blue-hour contrast.
pixels = base.load()
for y in range(H):
    for x in range(W):
        r, g, b = pixels[x, y]
        h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
        if s > 0.38 and v > 0.20 and (h < 0.07 or h > 0.95):
            pixels[x, y] = (int(r * 0.32), int(g * 0.78), min(255, int(b * 1.25 + 10)))

overlay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
od = ImageDraw.Draw(overlay)
# One quiet, square structural plane instead of a stack of decorative cards.
od.rectangle((48, 82, 925, 652), fill=(3, 18, 42, 196))
od.line((48, 82, 925, 82), fill=(56, 108, 183, 185), width=2)
od.line((48, 82, 48, 652), fill=(56, 108, 183, 185), width=2)
od.line((83, 115, 83, 615), fill=(82, 218, 198, 210), width=3)
# Small darkening behind the title edge, blended instead of a UI panel.
od.polygon([(0, 0), (510, 0), (340, 800), (0, 910)], fill=(2, 16, 38, 42))
base = Image.alpha_composite(base.convert('RGBA'), overlay)

draw = ImageDraw.Draw(base)
white = (247, 243, 235, 255)
teal = (93, 219, 199, 255)
navy = (3, 18, 42, 255)

x = 122
f1 = font_for('САДИСЬ', 740, 166)
f2 = font_for('И', 740, 166)
f3 = font_for('ВЫДОХНИ', 740, 166)
draw.text((x, 134), 'САДИСЬ', font=f1, fill=white)
draw.text((x, 294), 'И', font=f2, fill=white)
draw.text((x, 454), 'ВЫДОХНИ', font=f3, fill=teal)

# The teal baseline becomes one restrained physical link between statement and city.
word_w = draw.textlength('ВЫДОХНИ', font=f3)
line_y = 617
draw.line((x, line_y, min(W - 70, x + word_w + 110), line_y), fill=teal, width=5)
draw.ellipse((min(W - 62, x + word_w + 104), line_y - 6, min(W - 50, x + word_w + 116), line_y + 6), fill=teal)

small = ImageFont.truetype(FONT, 30, index=6)
spaced(draw, (82, 1224), 'МОСКВА', small, white, 10)
draw.line((82, 1282, 300, 1282), fill=(93, 219, 199, 255), width=3)

base.convert('RGB').save(OUT, quality=96)
print(OUT)
