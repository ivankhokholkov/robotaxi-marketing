#!/usr/bin/env bash
# Поддерживает связность папки. Дёшев: сверяет отметку времени и молчит, если менять нечего.
# Режимы: light — только навигация при изменениях; full — каталог, навигация, линт.
set -uo pipefail
ROOT="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "$0")/../.." && pwd)}"
MODE="${1:-light}"
STAMP="$ROOT/.claude/.wiki-stamp"
cd "$ROOT" || exit 0
[ -f ".claude/scripts/wiki.py" ] || exit 0

newest=$(find knowledge РЕЗУЛЬТАТЫ БАННЕРЫ ЛЕНДИНГ ПАМЯТЬ references -name "*.md" -newer "$STAMP" 2>/dev/null | head -1)

if [ "$MODE" = "full" ]; then
  python3 .claude/scripts/wiki.py index >/dev/null 2>&1
  python3 .claude/scripts/wiki.py hubs  >/dev/null 2>&1
  touch "$STAMP"
  echo "Связность пересобрана. Состояние базы:"
  python3 .claude/scripts/wiki.py lint 2>/dev/null | grep -E "ПРОСРОЧЕНЫ|Протухают|Сироты" | sed 's/^/  /'
  python3 .claude/scripts/wiki.py links 2>/dev/null | grep -E "битых|не ссылается" | sed 's/^/  /'
  exit 0
fi

# light: молчим, если ничего не менялось
[ -f "$STAMP" ] && [ -z "$newest" ] && exit 0
python3 .claude/scripts/wiki.py index >/dev/null 2>&1
python3 .claude/scripts/wiki.py hubs  >/dev/null 2>&1
touch "$STAMP"
echo "Навигация обновлена: появились новые материалы."
