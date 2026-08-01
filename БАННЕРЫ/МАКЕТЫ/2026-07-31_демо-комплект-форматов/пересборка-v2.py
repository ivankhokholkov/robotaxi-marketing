#!/usr/bin/env python3
"""Пересборка двух макетов демо-комплекта под требования площадок.

Оригиналы не трогаются: результат ложится рядом с суффиксом `-v2`.

Что делает и почему именно так. Композиции нарисованы генератором целиком,
отдельных слоёв нет — подвинуть внутри растра заголовок или автомобиль нельзя.
Единственная честная правка кодом — ужать композицию до разрешённой области и
достроить поля. Дальше правится только перегенерацией.

  03_urbanads-1080x450 → композиция ужимается до 984×410 и встаёт по центру,
  то есть целиком внутрь охранной зоны 990×410. Поля 48 px по бокам и 20 px
  сверху и снизу достраиваются растяжкой крайних пикселей и размываются: по
  справке UrbanAds за охранной зоной допустимо изображение, там не должно быть
  важной информации. Размытие снимает с полей и типографику, и резкие края.

  04_maps-1280x256 → композиция ужимается до 1160×232 и встаёт по центру.
  Слева и справа остаются ровно по 60 px фонового чёрного: справка Карт требует
  там «область без изображения» под пометку «Реклама» и сервисные элементы,
  поэтому поле заливается фоном, а не размытой картинкой.

Запуск: python3 БАННЕРЫ/МАКЕТЫ/2026-07-31_демо-комплект-форматов/пересборка-v2.py
"""
from __future__ import annotations

import os

import numpy as np
from PIL import Image, ImageFilter

ПАПКА = os.path.join(os.path.dirname(os.path.abspath(__file__)), "final")


def растянуть_поля(холст: Image.Image, вставка: Image.Image, dx: int, dy: int) -> Image.Image:
    """Достраивает поля вокруг вставки растяжкой её крайних пикселей."""
    W, H = холст.size
    w, h = вставка.size
    холст.paste(вставка, (dx, dy))
    if dx:
        холст.paste(вставка.crop((0, 0, 1, h)).resize((dx, h)), (0, dy))
        холст.paste(вставка.crop((w - 1, 0, w, h)).resize((W - dx - w, h)), (dx + w, dy))
    if dy:
        полоса = холст.crop((0, dy, W, dy + 1))
        холст.paste(полоса.resize((W, dy)), (0, 0))
        полоса = холст.crop((0, dy + h - 1, W, dy + h))
        холст.paste(полоса.resize((W, H - dy - h)), (0, dy + h))
    return холст


def размыть_поля(холст: Image.Image, dx: int, dy: int, радиус: int = 12) -> Image.Image:
    """Размывает всё, что вне охранной зоны, с мягким переходом на границе."""
    W, H = холст.size
    размытый = холст.filter(ImageFilter.GaussianBlur(радиус))
    маска = Image.new("L", (W, H), 255)
    маска.paste(0, (dx, dy, W - dx, H - dy))
    маска = маска.filter(ImageFilter.GaussianBlur(радиус // 2))
    return Image.composite(размытый, холст, маска)


def фоновый_цвет(im: Image.Image, полоса) -> tuple[int, int, int]:
    a = np.asarray(im.convert("RGB"))[polosa_slice(полоса)]
    return tuple(int(v) for v in np.median(a.reshape(-1, 3), axis=0))


def polosa_slice(полоса):
    x0, y0, x1, y1 = полоса
    return (slice(y0, y1), slice(x0, x1))


def urbanads() -> None:
    src = os.path.join(ПАПКА, "03_urbanads-1080x450.png")
    im = Image.open(src).convert("RGB")
    зона = (990, 410)
    k = min(зона[0] / im.width, зона[1] / im.height)
    w, h = round(im.width * k), round(im.height * k)
    dx, dy = (im.width - w) // 2, (im.height - h) // 2
    холст = Image.new("RGB", im.size, (0, 0, 0))
    холст = растянуть_поля(холст, im.resize((w, h), Image.Resampling.LANCZOS), dx, dy)
    холст = размыть_поля(холст, dx, dy)
    из_ = os.path.join(ПАПКА, "03_urbanads-1080x450-v2.png")
    холст.save(из_, optimize=True)
    print(f"{os.path.basename(из_)}: композиция {w}×{h}, поля {dx}×{dy} px, "
          f"масштаб {k:.4f}, вес {os.path.getsize(из_)/1024:.0f} КБ")


def maps() -> None:
    src = os.path.join(ПАПКА, "04_maps-1280x256.png")
    im = Image.open(src).convert("RGB")
    поле = 60
    k = (im.width - 2 * поле) / im.width
    w, h = round(im.width * k), round(im.height * k)
    dx, dy = (im.width - w) // 2, (im.height - h) // 2
    фон = фоновый_цвет(im, (0, 0, 30, im.height))
    холст = Image.new("RGB", im.size, фон)
    холст.paste(im.resize((w, h), Image.Resampling.LANCZOS), (dx, dy))
    из_ = os.path.join(ПАПКА, "04_maps-1280x256-v2.png")
    холст.save(из_, optimize=True)
    print(f"{os.path.basename(из_)}: композиция {w}×{h}, свободные поля {dx} px слева и справа, "
          f"фон {фон}, масштаб {k:.4f}, вес {os.path.getsize(из_)/1024:.0f} КБ")


if __name__ == "__main__":
    urbanads()
    maps()
