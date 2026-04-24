# 🤖 MonitorIA — Coding Monitor em Tempo Real

> CLI que roda na máquina do aluno e sincroniza o estado do projeto com o ClassContent.digital durante aulas práticas. O backend invoca o **Claude Haiku** a cada sync e devolve score, resumo e issues — que aparecem no TUI do aluno **e** no dashboard do professor.

## Como funciona (v3 — sempre online, Haiku por sync)

```
┌────────────────────────┐          ┌──────────────────────────┐
│  IntelliJ do aluno     │          │   ClassContent.digital    │
│  (edita Tarefa.java)   │          │                          │
│                        │          │   POST /monitor/sync     │
│  monitoria watch ./    │ ───────▶ │     ↓                    │
│  (terminal embaixo)    │  snapshot│   valida sessão ativa    │
│                        │  + token │     ↓                    │
│  TUI: score, issues,   │ ◀─────── │   Claude Haiku analisa   │
│  currentStep           │aiAnalysis│     ↓                    │
└────────────────────────┘          │   grava snapshot +       │
                                    │   mostra no MonitorTab    │
                                    └──────────────────────────┘
```

1. Professor cria uma **sessão** na aba Monitor da turma (`POST /monitor/sessions`).
2. Aluno roda `monitoria watch ./projeto` no terminal do IntelliJ.
3. A cada salvamento (debounce configurável), o CLI envia o snapshot completo via `POST /monitor/sync`.
4. O backend verifica se há sessão ativa; se sim, chama o Haiku e retorna `aiAnalysis` (score, summary, issues).
5. CLI atualiza o TUI no terminal do aluno; `MonitorTab` atualiza no frontend do professor.
6. Professor pausa/encerra a sessão → CLI recebe `423 Locked` (pausada) ou `410 Gone` (encerrada).

> **Não existe modo offline.** A CLI **sempre** exige `login`, turma configurada e sessão ativa do professor. Toda análise é feita pelo Haiku no backend — não há fallback local.

## Instalação

Pré-requisito: **Python 3.10+**.

```bash
git clone https://github.com/kelsonvictr/monitoria-classcontent-cli.git
cd monitoria-classcontent-cli

python3 -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -e .
```

## Uso típico (aluno em aula)

```bash
# 1. Autenticar (login OTP — mesmo código por email do site)
monitoria login

# 2. Escolher turma
monitoria init

# 3. Iniciar watch apontando para o projeto (ex: projeto Spring no IntelliJ)
monitoria watch ~/IdeaProjects/tarefas --debounce 5
```

A partir daí, basta codar no IntelliJ — o CLI detecta cada salvamento e o TUI abaixo mostra score, issues e a etapa atual da aula em tempo real.

### Como funciona o `monitoria login` (passo a passo)

O CLI usa **exatamente o mesmo OTP passwordless do site** (rotas `/auth/send-code` e `/auth/verify-code`) — **tudo no terminal, sem browser**.

```
$ monitoria login

🤖 MonitorIA v0.1.0 — Login

📧 Seu email cadastrado no ClassContent: aluno@programaai.dev

   Enviando código para aluno@programaai.dev...
   ✓ Código enviado! Verifique seu email.

🔑 Digite o código de 6 dígitos: 483921

   ✅ Login realizado com sucesso!
   👤 João da Silva

   💾 Token salvo em ~/.monitoria/config.json
   Execute monitoria init para escolher a turma.
```

**Fluxo:**
1. CLI pergunta o email **no próprio terminal** (sem abrir browser).
2. `POST /auth/send-code` — mesma rota do site → backend manda o email OTP via SES.
3. Aluno abre o email (mesmo template que chegaria logando pelo site) e pega o código de 6 dígitos.
4. CLI pergunta o código no terminal. Até **3 tentativas** antes de cair.
5. `POST /auth/verify-code` — retorna `token` + `refreshToken` + `user`.
6. Tokens salvos em `~/.monitoria/config.json` (permissão 0600).

**Erros que o CLI trata no login:**

| Status | Situação | Mensagem |
|--------|----------|----------|
| `429` em `send-code` | Throttle (muitos pedidos em pouco tempo) | ⏳ mensagem do backend |
| `403` em `send-code` | Email não autorizado / pendente de aprovação | 🚫 mensagem do backend |
| `400` em `verify-code` | Código errado ou expirado | ❌ incrementa tentativa |
| `429` em `verify-code` | Excedeu tentativas → pedir novo código | Encerra o fluxo |

Depois do login, `monitoria init` reusa o token pra chamar `GET /me/classes` e listar as turmas do aluno. Se o token expirar durante o `watch`, o CLI tenta `POST /auth/refresh` automaticamente antes de pedir login de novo.

## Comandos

| Comando | Descrição |
|---------|-----------|
| `monitoria login` | Login OTP (email + código de 6 dígitos) no terminal |
| `monitoria init` | Lista suas turmas e escolhe em qual rastrear |
| `monitoria watch <pasta> [--debounce N]` | Sincroniza snapshots com o backend e exibe TUI |
| `monitoria scan <pasta>` | Lista arquivos rastreáveis (sanity check, sem sync) |
| `monitoria status` | Mostra token, turma e último sync |
| `monitoria logout` | Remove token e limpa config local |

## Config

Fica em `~/.monitoria/config.json`. Gerenciada pelo CLI — **não edite à mão**. Contém: `token`, `refresh_token`, `api_url`, `class_id`, `class_name`, `project_path`, `last_sync_at`.

Opcionalmente, por projeto, você pode criar um `.monitoria.yml` (ver `.monitoria.example.yml`) para ajustar `debounce_seconds`, padrões de `include`/`exclude`, etc.

## Respostas da API que o CLI trata

| Status | Significado | O que o CLI faz |
|--------|-------------|-----------------|
| `200 OK` | Sessão ativa, snapshot aceito | Renderiza `aiAnalysis` no TUI |
| `401` | Token expirado | Tenta refresh; se falhar, encerra pedindo `monitoria login` |
| `403` | Aluno não matriculado na turma | Encerra com mensagem |
| `410 Gone` | Professor encerrou a sessão | Encerra o watch |
| `423 Locked` | Sessão pausada | Avisa no TUI e segue tentando |
| `428` | Nenhuma sessão ativa | Avisa no TUI e aguarda |

## Estrutura

```
monitoria-classcontent-cli/
├── README.md
├── pyproject.toml
├── .monitoria.example.yml
├── src/monitoria/
│   ├── cli.py       # Comandos (click)
│   ├── auth.py      # OTP no terminal (/auth/send-code + /auth/verify-code) + refresh
│   ├── config.py    # Config local (~/.monitoria/config.json)
│   ├── watcher.py   # File watcher (watchdog) + debounce
│   ├── sync.py      # POST /monitor/sync
│   ├── tui.py       # Dashboard TUI (rich)
│   └── analyzer.py  # (legacy — mantido só para os testes; v3 não usa em runtime)
├── tests/
│   └── test_watcher.py
├── test-project/         # Projeto Java mínimo para smoke test
└── teste-aluno-monitoria/ # Projeto React mínimo para smoke test
```

## Desenvolvimento

```bash
pip install -e ".[dev]"
python -m pytest tests/ -v
```
