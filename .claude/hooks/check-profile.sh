#!/usr/bin/env bash
memory_brief() {
  ROOT="${CLAUDE_PROJECT_DIR:-.}"
  [ -f "$ROOT/.claude/scripts/wiki.py" ] || return 0
  echo ""
  echo "ПАМЯТЬ ПРОЕКТА"
  python3 "$ROOT/.claude/scripts/wiki.py" lint 2>/dev/null | grep -E "ПРОСРОЧЕНЫ|Протухают|Сироты|Всего карточек" | sed 's/^/  /'
  [ -f "$ROOT/ПАМЯТЬ/РЕШЕНИЯ.md" ] && echo "  решений записано: $(grep -c '^## ' "$ROOT/ПАМЯТЬ/РЕШЕНИЯ.md")"
  [ -f "$ROOT/ПАМЯТЬ/ГРАБЛИ.md" ] && echo "  граблей записано: $(grep -c '^\*\*' "$ROOT/ПАМЯТЬ/ГРАБЛИ.md")"
  [ -f "$ROOT/knowledge/log.md" ] && echo "  журнал знаний: $(grep -E '^## ' "$ROOT/knowledge/log.md" | tail -1)"
  echo "  навигация: ГЛАВНАЯ.md | пересобрать связи: python3 .claude/scripts/wiki.py"
}

# Проверяет, заполнен ли профиль проекта. Пишет в stdout — текст попадает в контекст сессии.
set -uo pipefail

PROFILE="${CLAUDE_PROJECT_DIR:-.}/CLAUDE.md"

if [[ ! -f "$PROFILE" ]]; then
  echo "ПРОФИЛЬ ПРОЕКТА НЕ НАСТРОЕН."
  echo "Файл ${PROFILE} не найден."
  echo "Прежде чем делать любую содержательную работу, запусти навык setup — он задаст несколько вопросов и создаст профиль."
  memory_brief
  exit 0
fi

# Ищем ТОЛЬКО строки-поля: «- **Название:** `[PLACEHOLDER: ...]`».
# Прозаические упоминания «[PLACEHOLDER:...]» в шапке и в пояснениях — не поля,
# и в отчёт попадать не должны: человек читает их как незаполненные и путается.
# Имена переменных только латиницей: bash не принимает кириллицу в идентификаторах.
fields=$(grep -nE '^- \*\*.*\[PLACEHOLDER' "$PROFILE" 2>/dev/null)

if [[ -n "$fields" ]]; then
  count=$(printf '%s\n' "$fields" | grep -c .)
  echo "ПРОФИЛЬ ПРОЕКТА ЗАПОЛНЕН НЕ ДО КОНЦА."
  echo "В ${PROFILE} осталось незаполненных полей: ${count}"
  printf '%s\n' "$fields" | head -25
  echo "Пока они не заполнены, материалы выпускать нельзя. Запусти навык setup."
  memory_brief
  exit 0
fi

echo "Профиль проекта загружен: ${PROFILE}"

# Метки [ПОДТВЕРДИТЬ] работу не блокируют — материал с ними собирается,
# а публикация нет. Жёсткого гейта под них нет намеренно, поэтому их
# просто пересчитываем вслух: молчащая метка забывается за две сессии.
confirm=$(grep -cE '\[ПОДТВЕРДИТЬ' "$PROFILE" 2>/dev/null || true)
if [[ "${confirm:-0}" -gt 0 ]]; then
  echo "Незакрытых меток [ПОДТВЕРДИТЬ] в профиле: ${confirm}. Материал собирается, публикация — нет."
  grep -nE '^- \*\*.*\[ПОДТВЕРДИТЬ' "$PROFILE" 2>/dev/null | head -10
fi

memory_brief
exit 0

