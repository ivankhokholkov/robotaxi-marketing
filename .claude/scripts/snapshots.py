#!/usr/bin/env python3
"""Нормализация снимков первоисточников.
Чистит навигацию и пустоты, оригинал кладёт в _полные/ сжатым — доказательность сохраняется.
Запуск: python3 .claude/scripts/snapshots.py [check|clean|prune]"""
import sys, re, gzip, pathlib, shutil

ROOT = pathlib.Path(__file__).resolve().parents[2]
REF = ROOT / "knowledge" / "references"
FULL = REF / "_полные"
NOISE = re.compile(r'(cookie|подпис|подели|share this|войти|регистрац|все права защищ|©\s*\d{4}|читайте так|популярное|реклама на сайте)', re.I)

def clean_text(t: str):
    head, sep, body = t.partition("\n---\n")
    if not sep:                      # снимок без нашей шапки
        head, body = "", t
    out, blanks, dropped = [], 0, 0
    for line in body.split("\n"):
        s = line.strip()
        is_nav = bool(re.match(r'^\s*[-*]\s*\[', line)) and "](http" in line
        is_bare_link = bool(re.fullmatch(r'\[[^\]]*\]\([^)]*\)', s))
        if is_nav or is_bare_link or (s and NOISE.search(s) and len(s) < 120):
            dropped += 1
            continue
        if not s:
            blanks += 1
            if blanks > 1:
                continue
        else:
            blanks = 0
        out.append(line.rstrip())
    return (head + sep if sep else "") + "\n".join(out).strip() + "\n", dropped

def check():
    tot_before = tot_after = 0
    rows = []
    for f in sorted(REF.glob("*.md")):
        t = f.read_text(encoding="utf-8", errors="ignore")
        c, dropped = clean_text(t)
        tot_before += len(t); tot_after += len(c)
        if len(t) - len(c) > 2000:
            rows.append((len(t)//1024, len(c)//1024, dropped, f.name))
    print(f"снимков: {len(list(REF.glob('*.md')))}")
    print(f"сейчас: {tot_before/1024:.0f} КБ → после чистки: {tot_after/1024:.0f} КБ "
          f"(экономия {100*(1-tot_after/tot_before):.0f}%)")
    print("\nгде больше всего мусора:")
    for a, b, d, n in sorted(rows, reverse=True)[:8]:
        print(f"   {a:>4} → {b:>3} КБ, выброшено строк {d:>4}  {n[:60]}")

def clean():
    FULL.mkdir(exist_ok=True)
    before = after = 0; n = 0
    for f in sorted(REF.glob("*.md")):
        t = f.read_text(encoding="utf-8", errors="ignore")
        c, _ = clean_text(t)
        if len(c) >= len(t) - 200:      # чистить нечего
            continue
        gz = FULL / (f.name + ".gz")
        if not gz.exists():
            with gzip.open(gz, "wt", encoding="utf-8") as w:
                w.write(t)
        c = c.rstrip() + f"\n\n---\nСнимок нормализован: убраны навигация и пустые блоки. Полный оригинал: `knowledge/references/_полные/{f.name}.gz`\n"
        before += len(t); after += len(c); n += 1
        f.write_text(c, encoding="utf-8")
    print(f"нормализовано снимков: {n}")
    print(f"было {before/1024:.0f} КБ → стало {after/1024:.0f} КБ, экономия {before/1024-after/1024:.0f} КБ")

def prune():
    """Снимки, на которые не ссылается ни одна карточка."""
    used = set()
    for f in (ROOT/"knowledge").rglob("*.md"):
        if f.parent.name in ("references", "_полные"): continue
        t = f.read_text(encoding="utf-8", errors="ignore")
        used |= {m.group(1).strip() for m in re.finditer(r'\[\[([^\]|#]+)', t)}
        used |= {pathlib.Path(m.group(1)).stem for m in re.finditer(r'snapshot:\s*(\S+)', t)}
    orphans = [f for f in REF.glob("*.md") if f.stem not in used]
    print(f"снимков без ссылки из карточек: {len(orphans)}")
    for f in orphans: print("   ", f.name)
    if orphans and "--apply" in sys.argv:
        arch = REF/"_неиспользуемые"; arch.mkdir(exist_ok=True)
        for f in orphans: shutil.move(str(f), arch/f.name)
        print(f"перенесено в {arch.relative_to(ROOT)}")

if __name__ == "__main__":
    op = sys.argv[1] if len(sys.argv) > 1 else "check"
    {"check": check, "clean": clean, "prune": prune}[op]()
