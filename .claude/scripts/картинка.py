#!/usr/bin/env python3
"""Генерация изображения через Polza AI (POST /api/v1/media).

Ключ берётся из окружения POLZA_AI_API_KEY или из файла .env
(ищется в корне проекта и на уровень выше). В проект ключ не кладётся.

Модели по назначению:
  openai/gpt-5.4-image-2                — базовая генерация (4 ₽/1K, 7 ₽/2K)
  google/gemini-3.1-flash-image-preview — генерация с референсами (4,8 ₽),
                                          до 10 картинок на входе: канон машины,
                                          стиль-референсы

Примеры:
  python3 .claude/scripts/картинка.py --model openai/gpt-5.4-image-2 \
      --prompt "тёмный вечерний московский двор, мягкий бирюзовый свет" \
      --ar 3:4 --out кадр.png

  python3 .claude/scripts/картинка.py --model google/gemini-3.1-flash-image-preview \
      --prompt-file промпт.txt --ref фото-машины-1.jpg --ref фото-машины-2.jpg \
      --ar 3:4 --out кадр.png

Каждый вызов печатает стоимость из ответа API и дописывает строку в
БАННЕРЫ/ЖУРНАЛ-ГЕНЕРАЦИЙ.md (дата, модель, стоимость, файл, промпт первой строкой).
"""
from __future__ import annotations

import argparse
import base64
import datetime as dt
import json
import mimetypes
import os
import pathlib
import sys
import urllib.request

API = "https://polza.ai/api/v1/media"
КОРЕНЬ = pathlib.Path(__file__).resolve().parents[2]


def ключи() -> list[tuple[str, str]]:
    """Все источники ключа по порядку, а не первый попавшийся.

    Протухший ключ в ~/.zshrc перекрывает рабочий из .env, и запрос падает с 401
    там, где ключ вообще-то есть. См. ПАМЯТЬ/ГРАБЛИ.md.
    """
    найдено: list[tuple[str, str]] = []
    if os.environ.get("POLZA_AI_API_KEY"):
        найдено.append(("переменная окружения", os.environ["POLZA_AI_API_KEY"]))
    for env in (КОРЕНЬ / ".env", КОРЕНЬ.parent / ".env", КОРЕНЬ.parent.parent / ".env"):
        if env.is_file():
            for line in env.read_text().splitlines():
                if line.startswith("POLZA_AI_API_KEY="):
                    найдено.append((str(env), line.split("=", 1)[1].strip()))
    if not найдено:
        sys.exit("Нет ключа POLZA_AI_API_KEY: задайте переменную окружения "
                 "или положите .env рядом с папкой проекта (в сам проект ключ не кладём).")
    return найдено


def как_data_uri(путь: str) -> str:
    p = pathlib.Path(путь)
    mime = mimetypes.guess_type(p.name)[0] or "image/png"
    return f"data:{mime};base64," + base64.b64encode(p.read_bytes()).decode()


def main() -> None:
    ap = argparse.ArgumentParser(description="Генерация изображения через Polza")
    ap.add_argument("--model", required=True)
    ap.add_argument("--prompt")
    ap.add_argument("--prompt-file")
    ap.add_argument("--ar", default="3:4", help="aspect_ratio, напр. 1:1, 3:4, 16:9")
    ap.add_argument("--resolution", help="image_resolution: 1K, 2K, 4K (если модель умеет)")
    ap.add_argument("--ref", action="append", default=[],
                    help="референс-файл (можно несколько), уйдёт как data URI")
    ap.add_argument("--out", required=True, help="куда сохранить PNG/JPG")
    a = ap.parse_args()

    if not a.prompt and not a.prompt_file:
        ap.error("нужен --prompt или --prompt-file")
    промпт = a.prompt or pathlib.Path(a.prompt_file).read_text().strip()

    вход: dict = {"prompt": промпт, "aspect_ratio": a.ar}
    if a.resolution:
        вход["image_resolution"] = a.resolution
    if a.ref:
        вход["image_urls"] = [как_data_uri(r) for r in a.ref]

    тело = json.dumps({"model": a.model, "input": вход}).encode()
    источники = ключи()
    последняя = ""
    for откуда, ключ in источники:
        req = urllib.request.Request(API, data=тело, headers={
            "Authorization": f"Bearer {ключ}",
            "Content-Type": "application/json",
        })
        try:
            with urllib.request.urlopen(req, timeout=300) as r:
                ответ = json.load(r)
        except urllib.error.HTTPError as e:
            последняя = f"{e.code}: {e.read().decode()[:400]}"
            if e.code in (401, 403) and len(источники) > 1:
                print(f"ключ из «{откуда}» не принят ({e.code}), пробую следующий",
                      file=sys.stderr)
                continue
            sys.exit(f"Ошибка API. Ключ из «{откуда}». {последняя}")
        print(f"ключ взят из «{откуда}»", file=sys.stderr)
        break
    else:
        sys.exit(f"Ни один из {len(источники)} найденных ключей не принят. "
                 f"Последняя ошибка — {последняя}")

    if ответ.get("status") != "completed" or not ответ.get("data"):
        sys.exit(f"Генерация не завершилась: {json.dumps(ответ, ensure_ascii=False)[:500]}")

    url = ответ["data"][0]["url"]
    цена = ответ.get("usage", {}).get("cost_rub", "?")
    out = pathlib.Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(url, timeout=120) as r:
        out.write_bytes(r.read())

    журнал = КОРЕНЬ / "БАННЕРЫ" / "ЖУРНАЛ-ГЕНЕРАЦИЙ.md"
    if not журнал.exists():
        журнал.write_text(
            "# Журнал генераций изображений\n\n"
            "Пишется автоматически скриптом `.claude/scripts/картинка.py`. "
            "Одна строка — одна генерация, с ценой из ответа API.\n\n"
            "| Дата | Модель | ₽ | Файл | Промпт (первая строка) |\n|---|---|---|---|---|\n")
    первая = промпт.splitlines()[0][:90]
    with журнал.open("a") as f:
        f.write(f"| {dt.date.today()} | {a.model} | {цена} | "
                f"{out.relative_to(КОРЕНЬ) if out.is_relative_to(КОРЕНЬ) else out} | {первая} |\n")

    print(f"готово: {out}  ({цена} ₽, {ответ['model']})")


if __name__ == "__main__":
    main()
