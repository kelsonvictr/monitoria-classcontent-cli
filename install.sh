#!/usr/bin/env bash
# MonitorIA — Instalador automático
# Uso:
#   curl -sSL https://raw.githubusercontent.com/kelsonvictr/monitoria-classcontent-cli/main/install.sh | bash
#
# O que faz:
#   - Checa Python 3.10+
#   - Baixa o MonitorIA em ~/.monitoria/app/
#   - Cria venv isolado ali (não polui seu sistema)
#   - Expõe o comando 'monitoria' globalmente em ~/.local/bin/monitoria
#   - Adiciona ~/.local/bin ao PATH se ainda não estiver
#
# Depois é só usar 'monitoria login' / 'monitoria init' / 'monitoria watch .'
# em qualquer terminal — sem precisar ativar venv.

set -euo pipefail

# ─── Cores ───────────────────────────────────────────────
if [[ -t 1 ]]; then
    C_BLUE='\033[0;34m'
    C_GREEN='\033[0;32m'
    C_YELLOW='\033[0;33m'
    C_RED='\033[0;31m'
    C_RESET='\033[0m'
    C_BOLD='\033[1m'
else
    C_BLUE='' C_GREEN='' C_YELLOW='' C_RED='' C_RESET='' C_BOLD=''
fi

info() { printf "${C_BLUE}▶${C_RESET} %s\n" "$*"; }
ok()   { printf "${C_GREEN}✓${C_RESET} %s\n" "$*"; }
warn() { printf "${C_YELLOW}⚠${C_RESET}  %s\n" "$*"; }
die()  { printf "${C_RED}✗${C_RESET} %s\n" "$*" >&2; exit 1; }

# ─── Config ──────────────────────────────────────────────
REPO_URL="https://github.com/kelsonvictr/monitoria-classcontent-cli.git"
INSTALL_DIR="$HOME/.monitoria/app"
BIN_DIR="$HOME/.local/bin"
SHIM_PATH="$BIN_DIR/monitoria"

printf "\n${C_BOLD}🤖 MonitorIA — Instalador${C_RESET}\n\n"

# ─── 1. Python 3.10+ ─────────────────────────────────────
info "Verificando Python 3.10+..."
if command -v python3 >/dev/null 2>&1; then
    PY=python3
elif command -v python >/dev/null 2>&1; then
    PY=python
else
    die "Python não encontrado. Instale em https://python.org/downloads (versão 3.10 ou superior)."
fi

PY_OK=$("$PY" -c 'import sys; print("ok" if sys.version_info >= (3,10) else "no")' 2>/dev/null || echo "no")
if [[ "$PY_OK" != "ok" ]]; then
    PY_VERSION=$("$PY" --version 2>&1 || echo "?")
    die "Python 3.10+ é necessário. Detectado: $PY_VERSION. Atualize em https://python.org/downloads"
fi
ok "$("$PY" --version) encontrado"

# ─── 2. Git ──────────────────────────────────────────────
info "Verificando Git..."
command -v git >/dev/null 2>&1 || die "Git não encontrado. Instale em https://git-scm.com/downloads"
ok "$(git --version | head -n1) encontrado"

# ─── 3. Clone ou update ──────────────────────────────────
mkdir -p "$(dirname "$INSTALL_DIR")"
if [[ -d "$INSTALL_DIR/.git" ]]; then
    info "MonitorIA já instalado — atualizando..."
    git -C "$INSTALL_DIR" pull --ff-only --quiet \
        || die "Falha ao atualizar. Apague $INSTALL_DIR e rode o instalador de novo."
    ok "Repositório atualizado"
else
    info "Baixando MonitorIA para $INSTALL_DIR..."
    git clone --quiet "$REPO_URL" "$INSTALL_DIR" \
        || die "Falha ao clonar $REPO_URL"
    ok "Repositório baixado"
fi

# ─── 4. Venv ─────────────────────────────────────────────
if [[ ! -d "$INSTALL_DIR/.venv" ]]; then
    info "Criando ambiente virtual..."
    "$PY" -m venv "$INSTALL_DIR/.venv" || die "Falha ao criar venv"
    ok "Ambiente virtual criado"
fi

# ─── 5. Instala pacote ───────────────────────────────────
info "Instalando dependências (pode levar ~1 min)..."
"$INSTALL_DIR/.venv/bin/pip" install --quiet --upgrade pip
"$INSTALL_DIR/.venv/bin/pip" install --quiet -e "$INSTALL_DIR"
ok "MonitorIA instalado"

# ─── 6. Shim global ──────────────────────────────────────
mkdir -p "$BIN_DIR"
cat > "$SHIM_PATH" << 'SHIM'
#!/usr/bin/env bash
# MonitorIA shim — delega para o venv isolado em ~/.monitoria/app
exec "$HOME/.monitoria/app/.venv/bin/monitoria" "$@"
SHIM
chmod +x "$SHIM_PATH"
ok "Comando 'monitoria' disponível em $SHIM_PATH"

# ─── 7. PATH ─────────────────────────────────────────────
PATH_NEEDS_UPDATE=1
case ":$PATH:" in
    *":$BIN_DIR:"*) PATH_NEEDS_UPDATE=0 ;;
esac

if [[ "$PATH_NEEDS_UPDATE" -eq 1 ]]; then
    # Adiciona em todos os rc files relevantes de uma vez pra não perder em nenhum shell
    RC_UPDATED=""
    for RC in "$HOME/.zshrc" "$HOME/.bashrc" "$HOME/.bash_profile" "$HOME/.profile"; do
        # Só adiciona no que já existe (evita criar arquivo errado)
        if [[ -f "$RC" ]] && ! grep -q "\.local/bin" "$RC" 2>/dev/null; then
            {
                echo ""
                echo "# Added by MonitorIA installer"
                echo 'export PATH="$HOME/.local/bin:$PATH"'
            } >> "$RC"
            RC_UPDATED="$RC_UPDATED $RC"
        fi
    done

    # Se nenhum rc existe, cria pelo menos um baseado no shell atual
    if [[ -z "$RC_UPDATED" ]]; then
        case "$(basename "${SHELL:-bash}")" in
            zsh)  DEFAULT_RC="$HOME/.zshrc" ;;
            bash) DEFAULT_RC="$HOME/.bashrc" ;;
            *)    DEFAULT_RC="$HOME/.profile" ;;
        esac
        {
            echo "# Added by MonitorIA installer"
            echo 'export PATH="$HOME/.local/bin:$PATH"'
        } >> "$DEFAULT_RC"
        RC_UPDATED=" $DEFAULT_RC"
    fi

    ok "PATH atualizado em:$RC_UPDATED"
    warn "Feche e abra o terminal (ou rode: export PATH=\"\$HOME/.local/bin:\$PATH\")"
fi

# ─── Final ───────────────────────────────────────────────
cat << EOF

${C_GREEN}${C_BOLD}🎉 Instalação concluída!${C_RESET}

Próximos passos (só na primeira vez):

  ${C_BOLD}monitoria login${C_RESET}   — faz login com seu email do ClassContent
  ${C_BOLD}monitoria init${C_RESET}    — escolhe a turma

Durante cada aula:

  cd ~/caminho/do/projeto
  ${C_BOLD}monitoria watch .${C_RESET}

Dica: rode 'monitoria --help' pra ver todos os comandos.

EOF
