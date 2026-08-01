#!/usr/bin/env bash
# Пересобирает index.html из блоков, подставляя значения из данные.yaml.
# Правишь данные.yaml или блок → запускаешь это → страница обновилась.
set -euo pipefail
cd "$(dirname "$0")"
python3 сборка.py
