#!/usr/bin/env python3
"""Копирует выбранный результат Codex imagegen в кампанию без перезаписи."""

from __future__ import annotations

import argparse
import datetime as dt
import pathlib
import shutil
import sys


STAGES = {
    "raw": "03_RAW",
    "rejected": "03_RAW/rejected",
    "reference": "01_REFERENCES",
    "final": "04_FINAL",
}


def image_type(path: pathlib.Path) -> str | None:
    head = path.read_bytes()[:16]
    if head.startswith(b"\x89PNG\r\n\x1a\n"):
        return ".png"
    if head.startswith(b"\xff\xd8\xff"):
        return ".jpg"
    if head[:4] == b"RIFF" and head[8:12] == b"WEBP":
        return ".webp"
    return None


def safe_name(value: str, fallback_suffix: str) -> str:
    name = pathlib.Path(value)
    if name.name != value or value in {".", ".."}:
        raise argparse.ArgumentTypeError("name должен быть одним именем файла без пути")
    if not name.suffix:
        return value + fallback_suffix
    if name.suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp"}:
        raise argparse.ArgumentTypeError("разрешены PNG, JPG, JPEG и WEBP")
    return value


def next_version(path: pathlib.Path) -> pathlib.Path:
    if not path.exists():
        return path
    version = 2
    while True:
        candidate = path.with_name(f"{path.stem}-v{version}{path.suffix}")
        if not candidate.exists():
            return candidate
        version += 1


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Сохранить результат $imagegen внутри кампании"
    )
    parser.add_argument("--source", type=pathlib.Path, required=True)
    parser.add_argument("--campaign", type=pathlib.Path, required=True)
    parser.add_argument("--name", required=True)
    parser.add_argument("--stage", choices=STAGES, default="raw")
    args = parser.parse_args()

    source = args.source.expanduser().resolve()
    campaign = args.campaign.expanduser().resolve()

    if not source.is_file():
        sys.exit(f"Исходное изображение не найдено: {source}")
    detected = image_type(source)
    if not detected:
        sys.exit(f"Файл не распознан как PNG, JPG или WEBP: {source}")
    if not campaign.is_dir() or not (campaign / "00_BRIEF.md").is_file():
        sys.exit(
            "Папка кампании не распознана: сначала создайте её через "
            "БАННЕРЫ/новая-кампания.py"
        )

    try:
        filename = safe_name(args.name, detected)
    except argparse.ArgumentTypeError as exc:
        sys.exit(str(exc))

    requested_suffix = pathlib.Path(filename).suffix.lower()
    if requested_suffix == ".jpeg":
        requested_suffix = ".jpg"
    if requested_suffix != detected:
        sys.exit(
            f"Расширение имени {pathlib.Path(filename).suffix} не совпадает "
            f"с фактическим типом изображения {detected}"
        )

    destination_dir = campaign / STAGES[args.stage]
    destination_dir.mkdir(parents=True, exist_ok=True)
    destination = next_version(destination_dir / filename)
    shutil.copy2(source, destination)

    log = campaign / "IMPORTS.md"
    if not log.exists():
        log.write_text(
            "# Импорт результатов генерации\n\n"
            "| Время | Стадия | Исходник | Файл в кампании |\n"
            "|---|---|---|---|\n"
        )
    source_text = str(source).replace("|", "\\|")
    destination_text = str(destination.relative_to(campaign)).replace("|", "\\|")
    with log.open("a") as file:
        file.write(
            f"| {dt.datetime.now().isoformat(timespec='seconds')} | {args.stage} | "
            f"`{source_text}` | `{destination_text}` |\n"
        )

    print(destination)


if __name__ == "__main__":
    main()
