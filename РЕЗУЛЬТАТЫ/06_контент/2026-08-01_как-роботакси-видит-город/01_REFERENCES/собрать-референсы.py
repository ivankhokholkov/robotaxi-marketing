from pathlib import Path

from PIL import Image, ImageDraw


SOURCES = [
    (Path("/Users/ivankhokholkov/Library/Containers/com.wiheads.paste/Data/tmp/images/Safari 2026-08-01 11.39.25.png"), (90, 130, 970, 1007)),
    (Path("/Users/ivankhokholkov/Library/Containers/com.wiheads.paste/Data/tmp/images/Safari 2026-08-01 11.39.28.png"), (105, 145, 980, 1015)),
    (Path("/Users/ivankhokholkov/Library/Containers/com.wiheads.paste/Data/tmp/images/Safari 2026-08-01 11.39.32.png"), (64, 148, 940, 1316)),
    (Path("/Users/ivankhokholkov/Library/Containers/com.wiheads.paste/Data/tmp/images/Safari 2026-08-01 11.39.36.png"), (34, 114, 910, 842)),
    (Path("/Users/ivankhokholkov/Library/Containers/com.wiheads.paste/Data/tmp/images/Safari 2026-08-01 11.39.44.png"), (86, 155, 962, 1025)),
    (Path("/Users/ivankhokholkov/Library/Containers/com.wiheads.paste/Data/tmp/images/Safari 2026-08-01 11.39.48.png"), (122, 145, 1000, 1312)),
    (Path("/Users/ivankhokholkov/Library/Containers/com.wiheads.paste/Data/tmp/images/Safari 2026-08-01 11.39.52.png"), (72, 80, 944, 955)),
]

tile_w, tile_h = 420, 520
gap, margin = 18, 24
canvas = Image.new("RGB", (margin * 2 + tile_w * 4 + gap * 3, margin * 2 + tile_h * 2 + gap), "#171717")
draw = ImageDraw.Draw(canvas)

for index, (path, crop_box) in enumerate(SOURCES):
    image = Image.open(path).convert("RGB").crop(crop_box)
    image.thumbnail((tile_w, tile_h), Image.Resampling.LANCZOS)
    x = margin + (index % 4) * (tile_w + gap)
    y = margin + (index // 4) * (tile_h + gap)
    px = x + (tile_w - image.width) // 2
    py = y + (tile_h - image.height) // 2
    canvas.paste(image, (px, py))
    draw.rectangle((x, y, x + tile_w, y + tile_h), outline="#343434", width=2)

canvas.save(Path(__file__).with_name("editorial-yandex-reference-sheet.png"), optimize=True)
