#!/usr/bin/env python3
"""Каталог и линт контура знаний. Запуск: python3 .claude/scripts/wiki.py [index|lint|all]"""
import sys, re, pathlib, datetime, collections

ROOT = pathlib.Path(__file__).resolve().parents[2]
K = ROOT / "knowledge"
TODAY = datetime.date.today()
SECTIONS = {"market": "Рынок", "competitors": "Конкуренты", "regulation": "Регуляторика",
            "audience": "Аудитория", "barriers": "Барьеры", "channels": "Каналы и площадки"}

def cards():
    for d, ru in SECTIONS.items():
        for f in sorted((K / d).glob("*.md")):
            t = f.read_text(encoding="utf-8", errors="ignore")
            g = lambda p: (re.search(p, t, re.M).group(1).strip() if re.search(p, t, re.M) else "")
            yield dict(path=f, sec=d, ru=ru, title=g(r'^title:\s*(.+)$').strip('"'),
                       stale=g(r'^stale_after:\s*(\S+)'), conf=g(r'confidence:\s*(\w+)'),
                       snap=g(r'snapshot:\s*(\S+)'), body=t)

def build_index():
    rows = collections.defaultdict(list)
    for c in cards():
        rows[c["ru"]].append(c)
    out = ["# Каталог контура знаний", "",
           f"> Собран автоматически {TODAY}. Не править руками: перезапиши через `python3 .claude/scripts/wiki.py index`.",
           "", "Хабы-синтезы: [[правовая-рамка]], [[конкурентная-картина]], [[аудитория-и-барьеры]], [[требования-площадок]], [[методики-замера]]", ""]
    total = 0
    for ru in SECTIONS.values():
        if not rows[ru]: continue
        out += [f"## {ru}", ""]
        for c in sorted(rows[ru], key=lambda x: x["path"].stem):
            mark = " ⚠️ просрочена" if c["stale"] and c["stale"] < str(TODAY) else ""
            out.append(f"- [[{c['path'].stem}]] — {c['title'][:120]}{mark}")
            total += 1
        out.append("")
    snaps = len(list((K / "references").glob("*.md")))
    out += ["---", f"Карточек: {total}. Снимков первоисточников: {snaps}."]
    (K / "index.md").write_text("\n".join(out), encoding="utf-8")
    print(f"каталог собран: {total} карточек, {snaps} снимков")

def lint():
    stale, soon, nosnap, noconf, orphan = [], [], [], [], []
    all_cards = list(cards())
    names = {c["path"].stem for c in all_cards}
    # ссылки собираем со ВСЕХ страниц базы, включая хабы, иначе сиротами станут все
    linked = set()
    for f in K.rglob("*.md"):
        if f.parent.name == "references":
            continue
        for m in re.finditer(r'\[\[([^\]|#]+)', f.read_text(encoding="utf-8", errors="ignore")):
            linked.add(m.group(1).strip())
    for c in all_cards:
        if c["stale"]:
            if c["stale"] < str(TODAY): stale.append(c)
            elif c["stale"] < str(TODAY + datetime.timedelta(days=30)): soon.append(c)
        if not c["snap"]: nosnap.append(c)
        if not c["conf"]: noconf.append(c)
        if c["path"].stem not in linked: orphan.append(c)
    print(f"\n{'='*60}\nЛИНТ КОНТУРА ЗНАНИЙ, {TODAY}\n{'='*60}")
    def block(title, items, fmt):
        print(f"\n{title}: {len(items)}")
        for c in items[:12]: print("   ", fmt(c))
    block("🔴 ПРОСРОЧЕНЫ, перепроверить до использования", stale, lambda c: f"{c['path'].stem} (до {c['stale']})")
    block("🟡 Протухают в ближайший месяц", soon, lambda c: f"{c['path'].stem} (до {c['stale']})")
    block("Без снимка первоисточника", nosnap, lambda c: c['path'].stem)
    block("Без статуса достоверности", noconf, lambda c: c['path'].stem)
    block("Сироты: ни один хаб на них не ссылается", orphan, lambda c: c['path'].stem)
    print(f"\nВсего карточек: {len(all_cards)}")



def links():
    """Связность всей папки: битые викилинки и документы, на которые никто не ссылается."""
    SKIP = {".claude", ".obsidian", ".git"}
    # снимки — полноправные узлы графа: карточки на них ссылаются
    docs = [f for f in ROOT.rglob("*.md")
            if not any(part in SKIP for part in f.relative_to(ROOT).parts)]
    names = {f.stem: f for f in docs}
    linked, broken = set(), []
    for f in docs:
        for m in re.finditer(r'\[\[([^\]|#]+)', f.read_text(encoding="utf-8", errors="ignore")):
            tgt = m.group(1).strip()
            linked.add(tgt)
            if tgt not in names:
                broken.append((f.relative_to(ROOT), tgt))
    orphans = [f.relative_to(ROOT) for s, f in names.items()
               if s not in linked and f.name not in ("CLAUDE.md", "index.md", "log.md")
               and "knowledge/references" not in str(f.relative_to(ROOT))]
    NAV = {"index.md", "ГЛАВНАЯ.md"}
    sem = set()
    for f in docs:
        if f.name in NAV: continue
        for m in re.finditer(r'\[\[([^\]|#]+)', f.read_text(encoding="utf-8", errors="ignore")):
            if m.group(1).strip() in names: sem.add(m.group(1).strip())
    no_out = [f.relative_to(ROOT) for f in docs if f.name not in NAV
              and "knowledge/references" not in str(f.relative_to(ROOT))
              and not any(m.group(1).strip() in names for m in re.finditer(r'\[\[([^\]|#]+)', f.read_text(encoding="utf-8", errors="ignore")))]
    print(f"\n{'='*60}\nСВЯЗНОСТЬ ПАПКИ\n{'='*60}")
    print(f"\nдокументов всего: {len(docs)}")
    print(f"  со смысловыми входящими ссылками: {len(sem)}  ← главная метрика")
    print(f"  перечислено в автоиндексах: {len(linked & set(names))}  (перечисление — не связь)")
    print(f"  без единой исходящей ссылки: {len(no_out)}")
    print(f"\n🔴 битых викилинков: {len(broken)}")
    for f, t in broken[:10]: print(f"    {f} → [[{t}]]")
    print(f"\n🟡 документов, на которые никто не ссылается: {len(orphans)}")
    by_dir = {}
    for o in orphans: by_dir.setdefault(o.parts[0] if len(o.parts) > 1 else ".", []).append(o)
    for d, items in sorted(by_dir.items(), key=lambda x: -len(x[1])):
        print(f"    {d}: {len(items)}")
        for i in items[:3]: print(f"        {i}")



def hubs():
    """Пересобирает навигацию: индексы папок и главную. Связывает всё, что появилось."""
    SKIP = {".claude", ".obsidian", ".git"}

    def listing(folder, title, intro):
        d = ROOT / folder
        if not d.exists(): return 0
        items = sorted((f for f in d.rglob("*.md")
                        if f.name not in ("index.md", "CLAUDE.md") and "references" not in f.parts),
                       key=lambda f: str(f.relative_to(d)))
        out = [f"# {title}", "", intro, "",
               f"> Собрано автоматически. Обновить: `python3 .claude/scripts/wiki.py hubs`", ""]
        cur = None
        for f in items:
            sub = f.relative_to(d).parts[0] if len(f.relative_to(d).parts) > 1 else "—"
            if sub != cur:
                out += ["", f"## {sub}", ""]; cur = sub
            first = ""
            for line in f.read_text(encoding="utf-8", errors="ignore").splitlines():
                if line.startswith("# "): first = line[2:].strip(); break
            out.append(f"- [[{f.stem}]]{' — ' + first[:90] if first and first != f.stem else ''}")
        (d / "index.md").write_text("\n".join(out) + "\n", encoding="utf-8")
        return len(items)

    n1 = listing("РЕЗУЛЬТАТЫ", "Результаты работы", "Все материалы проекта. Статусы — в [[ЖУРНАЛ-РАБОТ]].")
    n2 = listing("БАННЕРЫ", "Медиасистема и макеты", "Правила генерации, требования площадок, макеты. Канон — [[2026-07-31_PRODUCTION-READY-МЕДИАСИСТЕМА]].")
    n3 = listing("ЛЕНДИНГ", "Лендинг", "Блоки страницы, дизайн-система и сборка.")

    main = f"""# Главная

Точка входа в проект. Всё остальное достижимо отсюда за один переход.

## Начать

- [[ПРИЁМКА-01-АВГУСТА]] — что обещали на встрече и что из этого есть, построчно
- [[ЧТО-НУЖНО-ОТ-ЗАКАЗЧИКА]] — вопросы, которые снимают метки с материалов
- [[ПЛАН-ДО-10-АВГУСТА]] — созвоны, что закрывается к сдаче
- [[СТАРТ]] — с чего начать работу
- [[КАРТА-СИСТЕМЫ]] — как устроена система целиком
- [[CLAUDE]] — профиль проекта: название, категория, зоны, тарифы, границы

## Память

- [[РЕШЕНИЯ]] — что решено и почему
- [[ГРАБЛИ]] — на чём обожглись
- [[ЖУРНАЛ-РАБОТ]] — что сделано, по одной строке на материал

## Знания

- [[index|Каталог контура фактов]] — {n1 and ''}карточки со ссылками на первоисточники
- [[СХЕМА]] — конвенции базы: слои, пороги, сроки годности
- Хабы-синтезы: [[правовая-рамка]], [[конкурентная-картина]], [[аудитория-и-барьеры]], [[требования-площадок]], [[методики-замера]]

## Ядро бренда

Что можно говорить и чего нельзя — папка `references/`:
[[АКТУАЛИЗАЦИЯ]], [[позиционирование]], [[стратегия-пилота]], [[тон-чилл]], [[тон-сити]], [[стоп-слова]], [[rtb-факты]], [[цели]]

## Работа

- Результаты: {n1} материалов, навигация в `РЕЗУЛЬТАТЫ/index.md`
- Медиасистема: {n2} документов, навигация в `БАННЕРЫ/index.md`
- Лендинг: {n3} документов

## Поддержание связности

```bash
python3 .claude/scripts/wiki.py        # каталог, линт, связность
python3 .claude/scripts/wiki.py hubs   # пересобрать навигацию
```

Запускается после каждой пачки материалов и раз в неделю целиком.
"""
    (ROOT / "ГЛАВНАЯ.md").write_text(main, encoding="utf-8")
    print(f"навигация пересобрана: результатов {n1}, баннеров {n2}, лендинга {n3}")



def arch():
    """Проверяет обязанности классов документов, а не наличие ссылок вообще."""
    SKIP = {".claude", ".obsidian", ".git"}
    # Служебная обвязка пачки и методички процесса — не материалы.
    # Источники материал называет один раз, в самом материале, а не в каждом README рядом с ним.
    SLUZHEBNYE = {"README.md", "IMPORTS.md", "QA.md", "ПРОМПТЫ.md", "00_BRIEF.md", "МАНИФЕСТ.md"}
    SLUZHEBNYE_PAPKI = ("ПРОЦЕСС-", "ШАБЛОНЫ", "СТИЛИ", "забраковано")

    def cls(f):
        s = str(f.relative_to(ROOT))
        if f.name in ("index.md", "ГЛАВНАЯ.md"): return "навигация"
        if f.name in SLUZHEBNYE or f.name.startswith("ШАБЛОН"): return "процесс"
        if any(p.startswith(SLUZHEBNYE_PAPKI) for p in f.relative_to(ROOT).parts[:-1]): return "процесс"
        if f.name == "CLAUDE.md" and f.parent != ROOT: return "контекст"
        if s.startswith("knowledge/ХАБЫ"): return "хаб"
        if s.startswith("knowledge/") and f.parent.name != "knowledge": return "карточка"
        if s.startswith("references/"): return "ядро"
        if s.startswith("ПАМЯТЬ/"): return "память"
        if s.startswith(("РЕЗУЛЬТАТЫ/", "БАННЕРЫ/", "ЛЕНДИНГ/")): return "материал"
        return "прочее"

    docs = [f for f in ROOT.rglob("*.md")
            if not any(p in SKIP for p in f.relative_to(ROOT).parts)
            and "knowledge/references" not in str(f.relative_to(ROOT))]
    bad = {"карточка": [], "хаб": [], "материал": [], "память": []}
    for f in docs:
        c = cls(f); t = f.read_text(encoding="utf-8", errors="ignore")
        links = {m.group(1).strip() for m in re.finditer(r'\[\[([^\]|#]+)', t)}
        if c == "карточка" and not any("Входит в хаб" in t for _ in [1]): bad["карточка"].append(f)
        if c == "хаб" and len(links) < 3: bad["хаб"].append(f)
        if c == "материал" and "Опирается на" not in t: bad["материал"].append(f)
        if c == "память" and not links: bad["память"].append(f)
    print(f"\n{'='*60}\nАРХИТЕКТУРА СВЯЗЕЙ\n{'='*60}")
    rules = {"карточка": "карточка обязана указывать свой хаб",
             "хаб": "хаб обязан связывать минимум три страницы",
             "материал": "материал обязан иметь блок «Опирается на»",
             "память": "решение или грабля обязаны ссылаться на то, чего касаются"}
    ok = True
    for c, items in bad.items():
        mark = "✅" if not items else "🔴"
        print(f"\n{mark} {rules[c]}: нарушений {len(items)}")
        for f in items[:6]: print("     ", f.relative_to(ROOT))
        if items: ok = False
    print("\nАрхитектура соблюдена." if ok else "\nЕсть нарушения — чинить до сдачи материала.")

if __name__ == "__main__":
    op = sys.argv[1] if len(sys.argv) > 1 else "all"
    if op in ("index", "all"): build_index()
    if op in ("hubs", "all"): hubs()
    if op in ("lint", "all"): lint()
    if op in ("links", "all"): links()
    if op in ("arch", "all"): arch()
