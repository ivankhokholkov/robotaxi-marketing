#!/usr/bin/env python3
"""Собирает index.html из блоков, подставляя значения из данные.yaml.

Смысл: значения живут в одном файле, блоки их подставляют. Поменять цифру —
одна правка в данные.yaml плюс пересборка. Без запуска навыка и без автора.

Запуск: bash build.sh   (или python3 сборка.py)
"""
import os
import re
import sys

try:
    import yaml
    def читать_значения(путь):
        return yaml.safe_load(open(путь, encoding="utf-8"))
except ImportError:
    # Своими руками, чтобы сборка не требовала установки библиотек.
    # Заказчик — маркетолог: «pip3 install pyyaml» на чистом маке упирается
    # в externally-managed-environment, и первый же шаг демо ломается.
    # Наш формат простой: вложенность отступами, значения — строки и числа.
    def читать_значения(путь):
        корень, стек = {}, [(-1, None)]
        for сырая in open(путь, encoding="utf-8"):
            строка = сырая.split("#")[0].rstrip() if not сырая.lstrip().startswith("#") else ""
            if not строка.strip():
                continue
            отступ = len(строка) - len(строка.lstrip())
            ключ, _, значение = строка.strip().partition(":")
            ключ, значение = ключ.strip(), значение.strip()
            while стек and стек[-1][0] >= отступ:
                стек.pop()
            родитель = стек[-1][1] if stack_ok(стек) else корень
            if родитель is None:
                родитель = корень
            if значение == "":
                новый = {}
                родитель[ключ] = новый
                стек.append((отступ, новый))
            else:
                родитель[ключ] = разобрать(значение)
        return корень

    def stack_ok(стек):
        return bool(стек) and стек[-1][1] is not None

    def разобрать(значение):
        if len(значение) > 1 and значение[0] == значение[-1] and значение[0] in "\"'":
            return значение[1:-1]
        if значение in ("null", "~", ""):
            return None
        if значение.lstrip("-").isdigit():
            return int(значение)
        if значение.startswith("[") and значение.endswith("]"):
            куски = [к.strip().strip("\"'") for к in значение[1:-1].split(",") if к.strip()]
            return куски
        return значение

HERE = os.path.dirname(os.path.abspath(__file__))
ДАННЫЕ = os.path.join(HERE, "данные.yaml")
БЛОКИ = os.path.join(HERE, "БЛОКИ")
ШАБЛОН = os.path.join(HERE, "шаблон.html")
ВЫХОД = os.path.join(HERE, "index.html")


def плоско(d, префикс=""):
    """{'тарифы': {'чилл': {'минут': 15}}} → {'тарифы.чилл.минут': 15}"""
    out = {}
    for k, v in (d or {}).items():
        ключ = f"{префикс}{k}"
        if isinstance(v, dict):
            out.update(плоско(v, ключ + "."))
        else:
            out[ключ] = v
    return out


def main():
    if not os.path.exists(ДАННЫЕ):
        sys.exit(f"нет файла значений: {ДАННЫЕ}")
    if not os.path.isdir(БЛОКИ):
        sys.exit(f"нет папки блоков: {БЛОКИ}")

    значения = плоско(читать_значения(ДАННЫЕ))

    блоки = sorted(f for f in os.listdir(БЛОКИ) if f.endswith(".html"))
    if not блоки:
        sys.exit("в БЛОКИ/ нет ни одного .html — собирать нечего")

    собрано = []
    пропущенные = {}
    метки = set()

    for имя in блоки:
        текст = open(os.path.join(БЛОКИ, имя), encoding="utf-8").read()

        def подставить(m):
            ключ = m.group(1).strip()
            if ключ not in значения:
                пропущенные.setdefault(имя, set()).add(ключ)
                return f"[НЕТ ЗНАЧЕНИЯ: {ключ}]"
            v = значения[ключ]
            if v is None:
                return ""
            s = str(v)
            if "[ПОДТВЕРДИТЬ" in s or "[ПРОВЕРИТЬ" in s:
                метки.add(f"{имя}: {ключ} = {s}")
            return s

        текст = re.sub(r"\{\{([^}]+)\}\}", подставить, текст)
        собрано.append(f"<!-- блок: {имя} -->\n{текст}")

    шаблон = open(ШАБЛОН, encoding="utf-8").read() if os.path.exists(ШАБЛОН) else \
        "<!doctype html>\n<html lang=ru>\n<head><meta charset=utf-8>\n" \
        "<meta name=viewport content=\"width=device-width,initial-scale=1\">\n" \
        "<meta name=robots content=\"noindex, nofollow\">\n" \
        "<link rel=stylesheet href=tokens.css>\n<title>{{сервис.название}}</title>\n" \
        "</head>\n<body>\n{{БЛОКИ}}\n</body>\n</html>\n"

    страница = shabl = шаблон.replace("{{БЛОКИ}}", "\n\n".join(собрано))
    страница = re.sub(r"\{\{([^}]+)\}\}",
                      lambda m: str(значения.get(m.group(1).strip(), "")), страница)

    open(ВЫХОД, "w", encoding="utf-8").write(страница)

    # ── отчёт сборки ──────────────────────────────────────────────────────────
    print(f"Собрано: {ВЫХОД}")
    print(f"Блоков: {len(блоки)} — {', '.join(блоки)}")

    if пропущенные:
        print("\n⚠️  Подстановки без значения в данные.yaml:")
        for имя, ключи in sorted(пропущенные.items()):
            for k in sorted(ключи):
                print(f"   {имя}: {{{{{k}}}}}")
        print("   На странице они видны как [НЕТ ЗНАЧЕНИЯ: ...] — это специально.")

    if метки:
        print("\n⚠️  На странице стоят неподтверждённые значения:")
        for m in sorted(метки):
            print(f"   {m}")
        print("   Публиковать с этими метками нельзя. Снимает их заказчик.")

    if not пропущенные and not метки:
        print("\nВсе значения подставлены, неподтверждённых нет.")

    return 1 if пропущенные else 0


if __name__ == "__main__":
    sys.exit(main())
