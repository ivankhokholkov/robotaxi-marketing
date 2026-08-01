#!/usr/bin/env python3
"""Создаёт стандартную папку кампании и копирует рабочие шаблоны."""

from __future__ import annotations

import argparse
import datetime as dt
import pathlib
import re
import shutil
import sys


БАННЕРЫ = pathlib.Path(__file__).resolve().parent
ПРОЕКТ = БАННЕРЫ.parent
ШАБЛОНЫ = БАННЕРЫ / "ПРОЦЕСС-GPT-IMAGE-2" / "ШАБЛОНЫ"
РЕЕСТР_СТИЛЕЙ = БАННЕРЫ / "СТИЛИ" / "registry.yaml"

РАЗДЕЛЫ = {
    "ads": "04_реклама",
    "content": "06_контент",
    "visuals": "07_визуалы",
}


def дата(value: str) -> str:
    try:
        return dt.date.fromisoformat(value).isoformat()
    except ValueError as exc:
        raise argparse.ArgumentTypeError("дата должна быть YYYY-MM-DD") from exc


def slug(value: str) -> str:
    normalized = re.sub(r"\s+", "-", value.strip())
    if not normalized or not re.fullmatch(r"[0-9A-Za-zА-Яа-яЁё_-]+", normalized):
        raise argparse.ArgumentTypeError(
            "slug может содержать буквы, цифры, дефис и подчёркивание"
        )
    return normalized


def данные_стиля(style_id: str) -> dict[str, str] | None:
    if not РЕЕСТР_СТИЛЕЙ.is_file():
        return None
    registry = РЕЕСТР_СТИЛЕЙ.read_text()
    block_match = re.search(
        rf"^  {re.escape(style_id)}:\s*$\n(?P<body>.*?)(?=^  [0-9A-Za-z_-]+:\s*$|\Z)",
        registry,
        re.MULTILINE | re.DOTALL,
    )
    if not block_match:
        return None
    body = block_match.group("body")
    result: dict[str, str] = {}
    for key in ("название", "guide", "contact_sheet", "examples"):
        value = re.search(rf'^    {key}:\s*"([^\"]+)"\s*$', body, re.MULTILINE)
        if value:
            result[key] = value.group(1)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Создать кампанию в правильном разделе РЕЗУЛЬТАТЫ"
    )
    parser.add_argument("--type", choices=РАЗДЕЛЫ, required=True)
    parser.add_argument("--slug", type=slug, required=True)
    parser.add_argument("--style", default="kinetic-moscow")
    parser.add_argument("--date", type=дата, default=dt.date.today().isoformat())
    parser.add_argument(
        "--root",
        type=pathlib.Path,
        default=ПРОЕКТ,
        help="корень robotaxi-marketing; нужен в основном для тестов",
    )
    args = parser.parse_args()

    style = данные_стиля(args.style)
    if not style:
        sys.exit(
            f"Неизвестный style id: {args.style}. "
            f"Добавьте утверждённый стиль в {РЕЕСТР_СТИЛЕЙ}"
        )

    campaign = (
        args.root.resolve()
        / "РЕЗУЛЬТАТЫ"
        / РАЗДЕЛЫ[args.type]
        / f"{args.date}_{args.slug}"
    )
    try:
        campaign.mkdir(parents=True, exist_ok=False)
    except FileExistsError:
        sys.exit(f"Кампания уже существует: {campaign}")

    directories = [
        "01_REFERENCES",
        "02_PROMPTS",
        "03_RAW/rejected",
        "04_FINAL",
        "05_QA/safe-zones",
        "05_QA/car-crops",
    ]
    for directory in directories:
        (campaign / directory).mkdir(parents=True)

    shutil.copy2(ШАБЛОНЫ / "БРИФ.md", campaign / "00_BRIEF.md")
    shutil.copy2(ШАБЛОНЫ / "QA.md", campaign / "05_QA" / "QA.md")

    manifest = (ШАБЛОНЫ / "MANIFEST.yaml").read_text()
    manifest = manifest.replace('кампания: ""', f'кампания: "{args.slug}"', 1)
    manifest = manifest.replace('дата: "YYYY-MM-DD"', f'дата: "{args.date}"', 1)
    manifest = manifest.replace('style_id: ""', f'style_id: "{args.style}"', 1)
    manifest = manifest.replace(
        'визуальная_линия: ""',
        f'визуальная_линия: "{style.get("название", args.style)}"',
        1,
    )
    manifest = manifest.replace(
        '  стиль: ""', f'  стиль: "{style.get("contact_sheet", "")}"', 1
    )
    (campaign / "MANIFEST.yaml").write_text(manifest)

    style_lines = [f"Style id: `{args.style}`."]
    for label, key in (
        ("Guide", "guide"),
        ("Contact sheet", "contact_sheet"),
        ("Принятые примеры", "examples"),
    ):
        if style.get(key):
            style_lines.append(f"- {label}: `{style[key]}`")
    (campaign / "01_REFERENCES" / "README.md").write_text(
        "# Референсы кампании\n\n"
        + "\n".join(style_lines)
        + "\n\n"
        + "Запишите здесь относительные пути, роль каждого файла, источник и права. "
        "Не копируйте всю библиотеку без необходимости.\n"
    )
    (campaign / "README.md").write_text(
        f"# {args.slug}\n\n"
        f"Дата: {args.date}.  \n"
        f"Раздел: {РАЗДЕЛЫ[args.type]}.  \n"
        f"Style id: `{args.style}`.  \n"
        "Статус: draft.\n\n"
        "## Следующий шаг\n\n"
        "1. Заполнить `00_BRIEF.md`.\n"
        "2. Записать референсы в `01_REFERENCES/README.md`.\n"
        "3. Сохранить полный промпт якоря в `02_PROMPTS/01_anchor.txt`.\n"
        "4. Генерировать только в `03_RAW/`.\n"
        "5. Переносить в `04_FINAL/` только после `05_QA/QA.md`.\n"
    )

    print(campaign)


if __name__ == "__main__":
    main()
