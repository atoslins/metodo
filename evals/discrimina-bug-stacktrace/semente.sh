#!/usr/bin/env bash
# Semeia o workspace do caso antes da execução.
set -euo pipefail
mkdir -p app
cat > app/__init__.py <<'FIM'

FIM
mkdir -p app
cat > app/users.py <<'FIM'
USUARIOS = {"ana": {"id": 1, "senha": "s3cr3t"}}


def get_user(nome):
    return USUARIOS.get(nome)


def login(nome, senha):
    user = get_user(nome)
    return user["senha"] == senha
FIM
mkdir -p tests
cat > tests/test_user.py <<'FIM'
from app.users import login


def test_login():
    assert login("Ana", "s3cr3t")
FIM
