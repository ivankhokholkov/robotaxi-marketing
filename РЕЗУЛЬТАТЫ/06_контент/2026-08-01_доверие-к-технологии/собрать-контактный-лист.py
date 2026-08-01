from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parent
FINAL = ROOT / "04_FINAL"
FILES = [
    FINAL / "01_доверие-начинается_1080x1350.png",
    FINAL / "02_камеры-лидары-радары_1080x1350.png",
    FINAL / "03_город-в-поле-зрения_1080x1350.png",
    FINAL / "04_технология-понятнее_1080x1350.png",
]

tile_w, tile_h = 432, 540
gap, margin = 24, 32
canvas = Image.new(
    "RGB",
    (margin * 2 + tile_w * 2 + gap, margin * 2 + tile_h * 2 + gap),
    "#171717",
)

for index, path in enumerate(FILES):
    image = Image.open(path).convert("RGB").resize((tile_w, tile_h), Image.Resampling.LANCZOS)
    x = margin + (index % 2) * (tile_w + gap)
    y = margin + (index // 2) * (tile_h + gap)
    canvas.paste(image, (x, y))

    draw = ImageDraw.Draw(canvas)
    draw.rounded_rectangle(
        (x - 1, y - 1, x + tile_w, y + tile_h),
        radius=8,
        outline="#343434",
        width=2,
    )

canvas.save(ROOT / "КОНТАКТНЫЙ-ЛИСТ.png", optimize=True)
