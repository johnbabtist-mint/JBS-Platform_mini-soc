#!/usr/bin/env bash
set -euo pipefail

echo "===== JBS Mini-SOC Public Validation Gate ====="

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SNIPPETS_DIR="$ROOT_DIR/snippets"

echo
echo "===== Python syntax checks ====="
python3 -m py_compile "$SNIPPETS_DIR/fastapi_route_example.py"
python3 -m py_compile "$SNIPPETS_DIR/policy_decision_example.py"
python3 -m py_compile "$SNIPPETS_DIR/pytest_policy_example.py"
python3 -m py_compile "$SNIPPETS_DIR/ai_llama_decision_example.py"

echo
echo "===== Deterministic policy sample run ====="
python3 "$SNIPPETS_DIR/policy_decision_example.py"

echo
echo "===== Optional local Llama/Ollama AI sample ====="
python3 "$SNIPPETS_DIR/ai_llama_decision_example.py"

echo
echo "===== Pytest sample ====="
PYTHONPATH="$SNIPPETS_DIR" pytest -q "$SNIPPETS_DIR/pytest_policy_example.py"

echo
echo "===== Result ====="
echo "Public code samples validated successfully."
