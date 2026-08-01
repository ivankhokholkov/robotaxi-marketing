#!/usr/bin/env python3
"""Собирает нашу страницу на дизайн-системе копии.

Шапка, подвал и подключение стилей берутся из уже собранной страницы
САЙТ/СТРАНИЦА/index.html — переписывать то, что работает, незачем.
Блоки свои, лежат в БЛОКИ/ и используют классы дизайн-системы:
вид совпадает с сайтом-референсом, тексты наши.

Запуск:   python3 САЙТ/ИСХОДНИКИ/сборка.py
Смотреть: cd САЙТ/СТРАНИЦА && python3 -m http.server 8901
"""
import hashlib
import os
import re

ЗДЕСЬ = os.path.dirname(os.path.abspath(__file__))
ОБРАЗЕЦ = os.path.join(ЗДЕСЬ, "..", "СТРАНИЦА", "index.html")
БЛОКИ = os.path.join(ЗДЕСЬ, "БЛОКИ")
ВЫХОД = os.path.join(ЗДЕСЬ, "..", "СТРАНИЦА", "index.html")


def кусок(текст, тег, маркер):
    """Вырезает элемент <тег>, внутри которого встречается маркер."""
    i = текст.index(маркер)
    начало = текст.rindex("<" + тег, 0, i)
    конец = текст.index("</" + тег + ">", i) + len(тег) + 3
    return текст[начало:конец]


def main():
    образец = open(ОБРАЗЕЦ, encoding="utf-8").read()

    стили = re.findall(r'<link[^>]*rel="stylesheet"[^>]*>', образец)
    стили = [s for s in стили if "/assets/" in s]

    # Версия по содержимому: без неё браузер держит старый своё.css и правки
    # «не применяются», хотя файл на диске новый.
    свой = os.path.join(ЗДЕСЬ, "..", "СТРАНИЦА", "своё.css")
    версия = hashlib.md5(open(свой, "rb").read()).hexdigest()[:8]

    шапка = кусок(образец, "header", "Header_header")
    подвал = кусок(образец, "footer", "Footer_footer")

    имена = sorted(f for f in os.listdir(БЛОКИ) if f.endswith(".html"))
    блоки = []
    for имя in имена:
        текст = open(os.path.join(БЛОКИ, имя), encoding="utf-8").read()
        блоки.append(f"<!-- блок: {имя} -->\n{текст}")

    страница = f"""<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<meta name="theme-color" content="#1a1a1a">
<title>Роботакси — черновик страницы</title>
{chr(10).join(стили)}
<link rel="stylesheet" href="своё.css?v={версия}">
</head>
<body>
<div class="Layout_layout__jFBDb">
{шапка}
<main>
{chr(10).join(блоки)}
</main>
{подвал}
</div>
<script src="скрипты.js"></script>
</body>
</html>
"""

    open(ВЫХОД, "w", encoding="utf-8").write(страница)

    метки = страница.count("[ПОДТВЕРДИТЬ")
    print(f"Собрано: {ВЫХОД}")
    print(f"Блоков: {len(имена)} — {', '.join(имена)}")
    print(f"Стилей подключено: {len(стили)}")
    if метки:
        print(f"\n⚠️  Меток [ПОДТВЕРДИТЬ...] на странице: {метки}")
        print("   Публиковать с ними нельзя. Снимает их заказчик.")


if __name__ == "__main__":
    main()
