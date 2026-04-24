# 🤖 MonitorIA — Coding Monitor em Tempo Real

> Monitor de código em tempo real para aulas práticas no ClassContent.digital

## O que é?

MonitorIA é um agente local que roda na máquina do aluno, observa os arquivos do projeto prático da disciplina, e analisa o código em tempo real. Exibe um dashboard TUI (Terminal UI) com score, erros de sintaxe, nomenclatura e padrões — tudo no terminal.

No **modo online**, envia snapshots para o ClassContent onde uma IA (Claude Haiku) faz análise avançada e o professor vê o dashboard de todos os alunos.

No **modo offline**, faz análise local via regex/heurísticas — perfeito para testar sem backend.

## Quick Start (Teste Local)

```bash
cd monitorIA

# Criar ambiente virtual e instalar
python3 -m venv .venv
source .venv/bin/activate   # macOS/Linux
pip install -e ".[dev]"

# Scan rápido (análise única)
monitoria scan ./test-project

# Watch ao vivo com TUI dashboard (modo offline)
monitoria watch ./test-project --offline --debounce 5

# Rodar testes
python -m pytest tests/ -v
```

## Comandos

| Comando | Descrição |
|---------|-----------|
| `monitoria scan <pasta>` | Analisa uma vez e mostra resultados |
| `monitoria watch <pasta> --offline` | Dashboard ao vivo (modo offline) |
| `monitoria watch <pasta>` | Dashboard ao vivo + sync com ClassContent |
| `monitoria init --class <id>` | Configura turma e autoriza via browser |
| `monitoria status` | Mostra configuração atual |

## TUI Dashboard

O comando `watch` abre um dashboard interativo no terminal:

```
┌───────────────────────────────────────────────────────┐
│ 🤖 MonitorIA v0.1.0  │  Turma: xxx  │  Modo: OFFLINE │
├──────────────────┬────────────────────────────────────┤
│ 📁 Arquivos (4)  │ 🔍 Problemas Encontrados (11)     │
│                  │                                    │
│ App.java     ✓   │ ❌ App.java:15 — ';' faltando     │
│ UserService  ✓   │ ⚠️ userService — PascalCase       │
│ Controller   ✓   │ 💡 System.out.println → Logger    │
│ pom.xml      ✓   │                                    │
├──────────────────┤                                    │
│ 📊 Score: 54/100 │                                    │
│ ❌ 3  ⚠️ 4  💡 4 │                                    │
├──────────────────┴────────────────────────────────────┤
│ 📋 Log                                               │
│ [21:30:03] Encontrados 4 arquivos                    │
│ [21:30:03] Análise: score 54/100 — 3 erros, 4 avisos │
│ [21:30:03] Observando mudanças (sync a cada 5s)...    │
└───────────────────────────────────────────────────────┘
```

O dashboard atualiza em tempo real quando você edita arquivos!

## O que ele detecta? (Análise Local)

### Java
- Chaves `{}` e parênteses `()` não fechados
- `;` faltando
- Nome de classe minúsculo (deve ser PascalCase)
- Variáveis com nomes de uma letra
- Blocos `catch` vazios
- `System.out.println` (sugestão de Logger)

### Python
- Indentação mista (tabs + espaços)
- `:` faltando em `def`, `class`, `if`, etc.
- Parênteses/colchetes não fechados
- camelCase em variáveis (deve ser snake_case)
- `except:` genérico (bare except)

### JavaScript/TypeScript
- Chaves/parênteses/colchetes não fechados
- `var` (sugestão de `const`/`let`)
- `==` em vez de `===`
- `console.log` esquecido

### Genérico (todas as linguagens)
- Linhas muito longas (>150 chars)
- TODOs/FIXMEs pendentes
- Trailing whitespace

## Estrutura

```
monitorIA/
├── README.md
├── pyproject.toml
├── .monitoria.example.yml     # Config exemplo por projeto
├── src/monitoria/
│   ├── __init__.py
│   ├── __main__.py            # python -m monitoria
│   ├── cli.py                 # Comandos CLI (click)
│   ├── analyzer.py            # Análise local (regex/heurísticas)
│   ├── tui.py                 # Dashboard TUI (rich)
│   ├── watcher.py             # File watcher (watchdog)
│   ├── sync.py                # Envio de snapshots para API
│   ├── auth.py                # Auth flow (browser + polling)
│   └── config.py              # Config local (~/.monitoria/)
├── tests/
│   └── test_watcher.py        # 14 testes unitários
└── test-project/              # Projeto Java com erros para teste
    ├── pom.xml
    └── src/main/java/com/example/
        ├── App.java
        ├── UserService.java
        └── HomeController.java
```

## Documentação Completa

Ver `docs/AGENT-MEMORY/MONITORIA.md` para arquitetura completa, decisões de design, rotas da API, tabelas DynamoDB e fases de implementação.
