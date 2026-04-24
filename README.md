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
- [Dicas para usar no IntelliJ](#-dicas-para-usar-no-intellij)
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
   Se aparecer algo como `Python 3.10.x` ou superior, está tudo certo. Caso contrário, baixe em [python.org/downloads](https://www.python.org/downloads/).

2. **Git** instalado (para baixar o MonitorIA).
   Confirme com:
   ```bash
   git --version
   ```

3. **Uma conta no ClassContent.digital** (o mesmo email que você usa para acessar o site).

4. **Estar matriculado na turma** em que vai acontecer a aula. Se tiver dúvida, fale com o professor.

5. Um **terminal** onde rodar os comandos. Recomendamos usar o **terminal integrado do IntelliJ** (`Alt + F12`), mas qualquer terminal funciona.

---

## 📥 Instalação (só na primeira vez)

Abra o terminal, escolha uma pasta onde quiser guardar o MonitorIA (ex: sua pasta de documentos) e rode:

```bash
# 1. Baixa o MonitorIA
git clone https://github.com/kelsonvictr/monitoria-classcontent-cli.git
cd monitoria-classcontent-cli

# 2. Cria um ambiente virtual isolado (boa prática do Python)
python3 -m venv .venv

# 3. Ativa o ambiente virtual
source .venv/bin/activate          # macOS / Linux
# .venv\Scripts\activate           # Windows (PowerShell)

# 4. Instala o MonitorIA
pip install -e .
```

Se tudo deu certo, rode:

```bash
monitoria --help
```

e você verá a lista de comandos disponíveis.

> 💡 **Importante:** sempre que abrir um terminal novo para usar o MonitorIA, você precisa **reativar o ambiente virtual** com `source .venv/bin/activate` (ou `.venv\Scripts\activate` no Windows) antes de rodar `monitoria`.

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

Exemplo: abra sua pasta `tarefas/` no IntelliJ.

### Passo 2 — Abra o terminal integrado

No IntelliJ, pressione **`Alt + F12`** (no macOS: `Option + F12`).

### Passo 3 — Ative o ambiente virtual do MonitorIA

```bash
cd ~/monitoria-classcontent-cli    # ajuste para o caminho onde você clonou
source .venv/bin/activate          # Windows: .venv\Scripts\activate
```

### Passo 4 — Inicie o `watch` apontando para a pasta do seu projeto

```bash
monitoria watch ~/IdeaProjects/tarefas
```

> Substitua `~/IdeaProjects/tarefas` pelo caminho real da pasta do seu projeto.

A partir desse momento, o painel do MonitorIA aparece **no próprio terminal**, e cada vez que você salvar um arquivo no editor, ele envia o código atualizado para o ClassContent e mostra o feedback na tela.

### Passo 5 — Codifique normalmente no editor!

Só isso. Volte para o editor e continue a aula. Pode deixar o terminal com o MonitorIA visível (split embaixo do editor) para acompanhar o feedback.

### Passo 6 — Ao final da aula

Para encerrar o MonitorIA, basta apertar **`Ctrl + C`** no terminal. Os dados já foram enviados; pode fechar tudo tranquilo.

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

## 💡 Dicas para usar no IntelliJ

- **Atalho do terminal integrado**: `Alt + F12` (Windows/Linux) ou `Option + F12` (macOS).
- **Divida a tela**: clique com o botão direito na aba do terminal → "Split Right" — assim você mantém o painel do MonitorIA visível ao lado do código.
- **Auto-save do IntelliJ**: já basta. O IntelliJ salva sozinho quando você perde o foco (troca de aba, clica em outro lugar). Não precisa ficar apertando `Ctrl + S`.
- **Vários terminais**: você pode ter um terminal rodando o MonitorIA e outro rodando `mvn spring-boot:run` (ou o comando do seu projeto) em paralelo — basta clicar no `+` na aba do terminal.

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

### `pip install -e .` deu erro

Confira se o ambiente virtual está ativado — no início da linha do terminal deve aparecer `(.venv)`. Se não aparecer, rode `source .venv/bin/activate` (ou `.venv\Scripts\activate` no Windows).

### O painel está todo bagunçado / aparecendo caracteres estranhos

Seu terminal pode não estar renderizando bem. Teste:
- **No IntelliJ**: `Settings → Tools → Terminal` → escolha "Shell path" como `bash` ou `zsh` (macOS/Linux) / `cmd.exe` (Windows).
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

# 3. Saia do ambiente virtual
deactivate

# 4. Apague a pasta inteira
cd ..
rm -rf monitoria-classcontent-cli

# 5. (Opcional) Apague a configuração local
rm -rf ~/.monitoria
```

Pronto — nada mais do MonitorIA ficará no seu computador.

---

## 📬 Dúvidas ou problemas?

- **Com o uso do MonitorIA em sala**: fale com seu professor.
- **Com sua conta / matrícula**: fale com o professor ou responda o email de convite do ClassContent.
- **Bugs técnicos** que não estão nesse README: abra uma *issue* [neste repositório](https://github.com/kelsonvictr/monitoria-classcontent-cli/issues).
