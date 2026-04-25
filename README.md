# 🤖 MonitorIA

> Seu monitor pessoal de programação durante as aulas práticas no **ClassContent.digital**.

MonitorIA é um pequeno programa que roda no **seu computador**, acompanha o projeto que você está desenvolvendo durante a aula e te dá feedback em tempo real no terminal: o que já está bom, o que pode melhorar, quais erros apareceram e qual a etapa atual que o professor está conduzindo.

Enquanto você codifica no seu editor preferido (IntelliJ, VS Code, Cursor, etc.), o MonitorIA fica "de olho" nos arquivos do projeto. A cada salvamento ele atualiza o painel na sua tela — e, ao mesmo tempo, o **professor** consegue ver seu progresso no painel dele. Assim, se você travar em algum ponto, ele consegue enxergar exatamente onde e te ajudar mais rápido.

---

## 📋 Sumário

- [O que você precisa ter antes](#-o-que-você-precisa-ter-antes)
- [Instalação (só na primeira vez)](#-instalação-só-na-primeira-vez)
- [Primeiro uso: fazer login e escolher a turma](#-primeiro-uso-fazer-login-e-escolher-a-turma)
- [Usando durante a aula](#-usando-durante-a-aula)
- [Entendendo o painel na sua tela](#-entendendo-o-painel-na-sua-tela)
- [Dicas para usar no seu editor](#-dicas-para-usar-no-seu-editor)
- [Todos os comandos](#-todos-os-comandos)
- [Perguntas frequentes](#-perguntas-frequentes)
- [Problemas comuns](#-problemas-comuns)
- [Privacidade e segurança](#-privacidade-e-segurança)
- [Desinstalando](#-desinstalando)

---

## ✅ O que você precisa ter antes

1. **Python 3.10 ou superior** instalado no seu computador.
   Para conferir, abra um terminal e rode:
   ```bash
   python3 --version
   ```
   (No Windows, pode ser `python --version` ou `py --version`.) Se aparecer `Python 3.10.x` ou superior, está tudo certo. Caso contrário, baixe em [python.org/downloads](https://www.python.org/downloads/) (no Windows, marque "Add Python to PATH" durante a instalação).

2. **Uma conta no ClassContent.digital** (o mesmo email que você usa para acessar o site).

3. **Estar matriculado na turma** em que vai acontecer a aula. Se tiver dúvida, fale com o professor.

4. Um **terminal** onde rodar os comandos. Recomendamos usar o **terminal integrado do seu editor** — assim ele já abre na raiz do projeto:
   - **IntelliJ / Android Studio / PyCharm**: `Alt + F12` (macOS: `Option + F12`)
   - **VS Code / Cursor**: `` Ctrl + ` `` (macOS: `` Cmd + ` ``) — também em `View → Terminal`
   - **Sublime Text**: instale o plugin "Terminus" ou use um terminal externo

   Mas qualquer terminal do sistema funciona — Terminal/iTerm2 (macOS), GNOME Terminal/Konsole (Linux), Git Bash/Windows Terminal/PowerShell (Windows).

---

## 📥 Instalação (só na primeira vez)

O MonitorIA está publicado no [PyPI](https://pypi.org/project/monitoria-classcontent/) — então a instalação é **um único comando**, igual qualquer pacote Python.

A forma recomendada é com [`pipx`](https://pipx.pypa.io/), que instala o MonitorIA isolado num ambiente próprio (sem misturar com seus outros projetos). Abra um terminal (qualquer um — do IntelliJ, do VS Code, do Cursor, ou um terminal do sistema) e rode:

```bash
# 1. Instala o pipx (só na primeira vez na sua máquina)
python3 -m pip install --user pipx
python3 -m pipx ensurepath

# 2. Feche e reabra o terminal (importante!)

# 3. Instala o MonitorIA
pipx install monitoria-classcontent
```

> 💡 **Windows**: troque `python3` por `py` (ou `python`) nos comandos acima.

Confirma que deu certo:

```bash
monitoria --help
```

Se aparecer a lista de comandos, **pronto**. Você nunca mais vai precisar ativar venv nenhum — o comando `monitoria` funciona direto em qualquer terminal, em qualquer pasta.

### Alternativa sem pipx

Se preferir não usar pipx, dá pra instalar direto com `pip`:

```bash
python3 -m pip install --user monitoria-classcontent
```

Funciona igual, mas o pacote fica junto com outros instalados no seu usuário. Se você só usa Python pra estudar, sem problema.

### Atualizando o MonitorIA

Quando o professor avisar que tem versão nova:

```bash
pipx upgrade monitoria-classcontent
# ou, se você instalou com pip:
python3 -m pip install --user --upgrade monitoria-classcontent
```

---

## 🔑 Primeiro uso: fazer login e escolher a turma

Depois de instalar, faça isso **uma única vez** (ficará salvo para as próximas aulas):

### 1. Login

```bash
monitoria login
```

O MonitorIA vai pedir seu **email** cadastrado no ClassContent. Depois de digitar, ele envia um **código de 6 dígitos** para esse email — o mesmo código que você receberia se estivesse entrando no site.

```
🤖 MonitorIA — Login

📧 Seu email cadastrado no ClassContent: aluno@exemplo.com

   Enviando código para aluno@exemplo.com...
   ✓ Código enviado! Verifique seu email.

🔑 Digite o código de 6 dígitos: 483921

   ✅ Login realizado com sucesso!
   👤 João da Silva
```

Abra seu email (cheque também a caixa de spam), pegue o código e cole no terminal. Pronto — você está logado.

### 2. Escolher a turma

```bash
monitoria init
```

O MonitorIA lista todas as turmas em que você está matriculado. Digite o número da que vai ter aula agora:

```
📚 Suas turmas:

   1. 🎒 Programação Backend — Turma 2026.1
   2. 🎒 Desenvolvimento Web — Turma 2026.1

Escolha a turma (1-2): 1

   ✅ Turma configurada!
   📚 Programação Backend — Turma 2026.1
```

Pronto. Login e turma ficam salvos. Nas próximas aulas você vai direto para o passo seguinte.

---

## 🎓 Usando durante a aula

O momento que você realmente vai usar o MonitorIA é **durante a aula**, com seu projeto aberto no IntelliJ (ou outro editor). O fluxo é:

### Passo 1 — Abra o projeto no seu editor

Exemplo: abra sua pasta `tarefas/` no editor que você usa (IntelliJ, VS Code, Cursor, PyCharm, etc.).

### Passo 2 — Abra o terminal integrado do editor

| Editor | Atalho |
|--------|--------|
| IntelliJ / PyCharm / Android Studio | `Alt + F12` (macOS: `Option + F12`) |
| VS Code / Cursor | `` Ctrl + ` `` (macOS: `` Cmd + ` ``) |
| Outros | menu **View / Terminal** ou abra um terminal externo na pasta do projeto |

O bom de usar o terminal integrado é que ele abre já na raiz do projeto — sem precisar de `cd`.

### Passo 3 — Inicie o watch

```bash
monitoria watch .
```

O **ponto final** (`.`) significa "pasta atual" — como o terminal integrado já abre na raiz do projeto, é só rodar assim. Não precisa ativar ambiente virtual nenhum.

A partir desse momento, o painel do MonitorIA aparece no próprio terminal, e cada vez que você salvar um arquivo no editor, ele envia o código atualizado para o ClassContent e mostra o feedback na tela.

### Passo 4 — Codifique normalmente no editor!

Só isso. Volte para o editor e continue a aula. Pode deixar o terminal com o MonitorIA visível (split embaixo do editor) para acompanhar o feedback.

### Passo 5 — Ao final da aula

Para encerrar o MonitorIA, aperte **`Ctrl + C`** no terminal. Os dados já foram enviados; pode fechar tudo tranquilo.

### 🎯 Atalho: botão "MonitorIA" no IntelliJ

Se o professor distribuir o projeto já com um arquivo `.idea/runConfigurations/MonitorIA.xml`, aparece uma configuração **🤖 MonitorIA** no topo do IntelliJ. Basta clicar no ▶ (Run) e o terminal integrado abre rodando `monitoria watch .` automaticamente — sem digitar comando. Pergunta ao professor.

---

## 📺 Entendendo o painel na sua tela

Quando o `monitoria watch` está rodando, você verá algo parecido com isso no terminal:

```
┌─────────────────────────────────────────────────────────────┐
│ 🤖 MonitorIA  │  Turma: Programação Backend — 2026.1       │
│               │  Etapa atual: Criar o endpoint POST         │
├──────────────────────┬──────────────────────────────────────┤
│ 📁 Arquivos (4)       │ 🔍 Feedback                          │
│                      │                                      │
│ TarefaController ✓   │ ✅ Boa separação de responsabilidades│
│ Tarefa.java      ✓   │ ⚠️  Falta validar título vazio       │
│ Application.java ✓   │ 💡 Considere retornar 201 no POST    │
│ pom.xml          ✓   │                                      │
├──────────────────────┤                                      │
│ 📊 Score: 78/100      │                                      │
├──────────────────────┴──────────────────────────────────────┤
│ 📋 Últimas atividades                                        │
│ [14:32:10] Você salvou TarefaController.java                │
│ [14:32:11] Análise recebida                                  │
│ [14:32:40] Aguardando próxima mudança...                     │
└─────────────────────────────────────────────────────────────┘
```

O que cada parte significa:

| Parte | Descrição |
|-------|-----------|
| **Turma** | Nome da turma em que você está sincronizando |
| **Etapa atual** | O que o professor pediu para ser feito agora. Atualiza em tempo real quando ele muda a etapa |
| **Arquivos** | Lista dos arquivos do seu projeto que o MonitorIA está acompanhando |
| **Feedback** | Observações sobre seu código: ✅ pontos positivos, ⚠️ avisos, 💡 sugestões de melhoria |
| **Score** | Uma nota de 0 a 100 para o estado atual do projeto (ajuda a ver se você está progredindo) |
| **Últimas atividades** | Um log do que aconteceu (quando você salvou, quando chegou análise nova, etc.) |

O painel **se atualiza sozinho** a cada salvamento. Você não precisa apertar nada — só continuar codando.

---

## 💡 Dicas para usar no seu editor

### IntelliJ / PyCharm / Android Studio

- **Atalho do terminal integrado**: `Alt + F12` (Windows/Linux) ou `Option + F12` (macOS).
- **Divida a tela**: clique com o botão direito na aba do terminal → "Split Right" — assim você mantém o painel do MonitorIA visível ao lado do código.
- **Auto-save**: já basta. O IntelliJ salva sozinho quando você perde o foco (troca de aba, clica em outro lugar). Não precisa ficar apertando `Ctrl + S`.
- **Vários terminais**: clique no `+` na aba do terminal pra abrir mais um (ex: um rodando o MonitorIA e outro rodando `mvn spring-boot:run` em paralelo).

### VS Code / Cursor

- **Atalho do terminal integrado**: `` Ctrl + ` `` (Windows/Linux) ou `` Cmd + ` `` (macOS) — também em `View → Terminal`.
- **Divida a tela**: no painel do terminal, clique no ícone "Split Terminal" (ou `Ctrl + Shift + 5`) pra ter terminais lado a lado.
- **Auto-save**: ative em `File → Auto Save` (ou `"files.autoSave": "onFocusChange"` em settings.json) — assim seus arquivos vão pro MonitorIA sem precisar `Ctrl + S`.
- **Vários terminais**: clique no `+` no canto do terminal, ou use o dropdown pra alternar entre eles.

### Outros editores (Sublime, Vim/Neovim, Emacs, ...)

Sem terminal integrado nativo? Sem problema — abra qualquer terminal externo, navegue até a raiz do projeto e rode `monitoria watch .`. Funciona igual.

---

## 📖 Todos os comandos

| Comando | O que faz | Quando usar |
|---------|-----------|-------------|
| `monitoria --help` | Mostra a lista de comandos | Esqueceu algum comando |
| `monitoria login` | Faz login por email + código | Primeira vez, ou depois de `logout` |
| `monitoria init` | Escolhe qual turma monitorar | Primeira vez, ou se mudar de turma |
| `monitoria watch <pasta>` | Começa a acompanhar o projeto e exibir o painel | Toda vez que for ter aula |
| `monitoria scan <pasta>` | Lista quais arquivos seriam enviados (sem enviar) | Conferir se tudo certo antes da aula |
| `monitoria status` | Mostra se você está logado, turma atual, etc. | Conferir estado |
| `monitoria logout` | Remove seu login do computador | Se for usar o computador de outra pessoa |

Exemplos:

```bash
# Ver se está tudo configurado
monitoria status

# Conferir quais arquivos serão enviados antes da aula
monitoria scan ~/IdeaProjects/tarefas

# Ajustar o intervalo entre envios (padrão é 10 segundos)
monitoria watch ~/IdeaProjects/tarefas --debounce 5
```

---

## ❓ Perguntas frequentes

### O MonitorIA envia meu código para algum lugar?

Sim. Enquanto o `monitoria watch` está rodando, os arquivos de código do projeto que você apontou são enviados para o **ClassContent.digital**, dentro da turma em que você está matriculado. É o mesmo lugar onde você assiste aulas e posta na comunidade.

Nada é enviado quando o `watch` **não** está rodando.

### Quem vê meu código?

- **Você** (no seu próprio painel, no terminal)
- **O professor / monitor da turma** (no painel deles, para poderem te ajudar)
- **Colegas da turma: NÃO**. O código de cada aluno é individual.

### Por quanto tempo meu código fica guardado?

Curto prazo. Os envios têm validade temporária e são usados só para o feedback em tempo real. O objetivo é acompanhar a aula, não armazenar soluções indefinidamente.

### Preciso instalar alguma coisa no meu projeto (pom.xml, package.json...)?

**Não.** O MonitorIA é completamente externo ao seu projeto. Ele só lê os arquivos — não modifica nada e não adiciona dependências.

### Funciona com qualquer linguagem?

Sim. O MonitorIA analisa o texto dos arquivos independentemente da linguagem. Funciona bem com Java, Python, JavaScript/TypeScript, Kotlin, Go e outros.

### Posso usar em casa, fora da aula?

Pode — mas o feedback mais rico só aparece quando **o professor abriu uma sessão ativa** para a turma. Fora de aula, o MonitorIA avisa que não há sessão no momento.

### Preciso ficar com o terminal aberto o tempo todo?

Sim, **enquanto quiser o feedback em tempo real**. Se fechar o terminal ou apertar `Ctrl + C`, a sincronização para. É só reabrir e rodar `monitoria watch ...` de novo.

### O MonitorIA usa internet?

Sim. Ele precisa de internet para conversar com o ClassContent. Em conexões lentas pode demorar um pouco mais para aparecer o feedback, mas normalmente funciona bem em qualquer wifi de sala de aula.

---

## 🛠️ Problemas comuns

### "Não recebi o código por email"

- Confira a caixa de **spam / lixo eletrônico**.
- Aguarde até **1 minuto** — pode demorar um pouco para chegar.
- Confirme que digitou o email certo (o mesmo cadastrado no ClassContent).
- Tente de novo com `monitoria login` — ele reenvia o código.

### "Código inválido ou expirado"

- O código expira depois de alguns minutos. Se demorou muito, solicite outro com `monitoria login`.
- Você tem **3 tentativas** por código. Depois disso, peça um novo.

### "Você não está matriculado nesta turma"

Fale com o professor para conferir sua matrícula no ClassContent. Depois, rode `monitoria init` novamente para atualizar.

### "Nenhuma sessão ativa no momento"

Significa que o professor ainda não abriu a sessão da aula no painel dele. **Aguarde o início oficial da aula** — o MonitorIA detecta automaticamente quando a sessão abre.

### "A sessão foi encerrada pelo professor"

A aula acabou (ou foi pausada). Aperte `Ctrl + C` para encerrar o `watch`. Da próxima aula, é só rodar `monitoria watch ...` de novo.

### `python3: command not found`

No Windows, tente `python` em vez de `python3`. Se nenhum funcionar, instale do site oficial: [python.org/downloads](https://www.python.org/downloads/).

### `monitoria: command not found` depois de instalar

Feche e reabra o terminal — o `pipx` ajusta o PATH mas o terminal atual não enxerga a mudança. Se persistir, rode:

```bash
python3 -m pipx ensurepath
```

Feche e abra de novo. Confirme que o pacote está instalado:

```bash
pipx list
```

Se `monitoria-classcontent` não aparecer, reinstale:

```bash
pipx install monitoria-classcontent
```

### `error: externally-managed-environment` (em distros Linux modernas)

Algumas versões novas do Linux/macOS não deixam usar `pip install` direto. Use o `pipx` (recomendado neste README) — ele resolve isso automaticamente.

### O painel está todo bagunçado / aparecendo caracteres estranhos

Seu terminal pode não estar renderizando bem. Teste:
- **No IntelliJ / PyCharm**: `Settings → Tools → Terminal` → "Shell path" = `bash` ou `zsh` (macOS/Linux) / `cmd.exe` ou Git Bash (Windows).
- **No VS Code / Cursor**: `Settings → Terminal › Integrated › Default Profile` — escolha `bash`, `zsh` ou Git Bash conforme seu sistema.
- Aumente a largura da janela do terminal (mínimo ~100 colunas).
- Em último caso, feche e reabra o terminal.

### Os arquivos que eu salvo não aparecem no painel

- Confirme que está editando arquivos **dentro da pasta** que você passou para o `monitoria watch`.
- Pastas como `.venv`, `node_modules`, `target`, `.git`, arquivos binários e imagens são ignorados de propósito.
- Experimente rodar `monitoria scan <pasta>` para conferir quais arquivos estão sendo vistos.

---

## 🔒 Privacidade e segurança

- O MonitorIA **só envia os arquivos de código** do projeto que você apontou no `watch`. Fora isso, nada sai do seu computador.
- **Arquivos ignorados automaticamente**: `.git/`, `.venv/`, `node_modules/`, `target/`, `build/`, `dist/`, `__pycache__/`, arquivos binários, imagens, vídeos, PDFs, pacotes (`.jar`, `.zip`), etc.
- **Nenhuma informação pessoal do seu computador** é coletada (senhas salvas, histórico de navegador, outros projetos, emails, nada).
- Seu **token de login** fica salvo localmente em `~/.monitoria/config.json` com permissão restrita (somente o seu usuário do sistema consegue ler). Esse arquivo **não** deve ser compartilhado.
- Se usar um computador compartilhado, sempre rode `monitoria logout` ao terminar.

---

## 🗑️ Desinstalando

Se quiser remover o MonitorIA:

```bash
# 1. Encerre qualquer watch em execução (Ctrl + C no terminal)

# 2. Remova seu login local
monitoria logout

# 3. Desinstala o pacote
pipx uninstall monitoria-classcontent
# ou, se você instalou com pip:
python3 -m pip uninstall monitoria-classcontent

# 4. (Opcional) remove a configuração local
rm -rf ~/.monitoria
```

Pronto — nada mais do MonitorIA fica no seu computador.

---

## 📬 Dúvidas ou problemas?

- **Com o uso do MonitorIA em sala**: fale com seu professor.
- **Com sua conta / matrícula**: fale com o professor ou responda o email de convite do ClassContent.
- **Bugs técnicos** que não estão nesse README: abra uma *issue* [neste repositório](https://github.com/kelsonvictr/monitoria-classcontent-cli/issues).
