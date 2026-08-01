from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


ROOT = Path(__file__).resolve().parent
RAW = ROOT / "03_RAW"
FINAL = ROOT / "04_FINAL"
FINAL.mkdir(exist_ok=True)

FILES = [
    ("01_как-роботакси-видит-город.png", "01_как-роботакси-видит-город_1080x1350.png"),
    ("02_сенсоры-в-цифрах.png", "02_сенсоры-в-цифрах_1080x1350.png"),
    ("03_восприятие.png", "03_восприятие_1080x1350.png"),
    ("04_распознавание.png", "04_распознавание_1080x1350.png"),
    ("05_прогноз-и-план.png", "05_прогноз-и-план_1080x1350.png"),
    ("06_от-данных-к-движению.png", "06_от-данных-к-движению_1080x1350.png"),
]

target_w, target_h = 1080, 1350

for source_name, final_name in FILES:
    source = Image.open(RAW / source_name).convert("RGB")
    scale = target_h / source.height
    width = round(source.width * scale)
    resized = source.resize((width, target_h), Image.Resampling.LANCZOS)

    if width >= target_w:
        left = (width - target_w) // 2
        canvas = resized.crop((left, 0, left + target_w, target_h))
    else:
        left = (target_w - width) // 2
        right = target_w - width - left
        sample = min(96, width)
        left_profile = resized.crop((0, 0, sample, target_h)).resize(
            (1, target_h), Image.Resampling.BOX
        ).filter(ImageFilter.GaussianBlur(radius=18))
        right_profile = resized.crop((width - sample, 0, width, target_h)).resize(
            (1, target_h), Image.Resampling.BOX
        ).filter(ImageFilter.GaussianBlur(radius=18))
        canvas = Image.new("RGB", (target_w, target_h))
        if left:
            canvas.paste(left_profile.resize((left, target_h)), (0, 0))
        canvas.paste(resized, (left, 0))
        if right:
            canvas.paste(right_profile.resize((right, target_h)), (left + width, 0))

    canvas.save(FINAL / final_name, optimize=True)


tile_w, tile_h = 320, 400
gap, margin = 18, 24
sheet = Image.new("RGB", (margin * 2 + tile_w * 3 + gap * 2, margin * 2 + tile_h * 2 + gap), "#171717")
draw = ImageDraw.Draw(sheet)

for index, (_, final_name) in enumerate(FILES):
    image = Image.open(FINAL / final_name).convert("RGB").resize((tile_w, tile_h), Image.Resampling.LANCZOS)
    x = margin + (index % 3) * (tile_w + gap)
    y = margin + (index // 3) * (tile_h + gap)
    sheet.paste(image, (x, y))
    draw.rectangle((x, y, x + tile_w, y + tile_h), outline="#3a3a3a", width=2)

sheet.save(ROOT / "КОНТАКТНЫЙ-ЛИСТ.png", optimize=True)
