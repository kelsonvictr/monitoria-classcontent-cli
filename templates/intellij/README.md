# Run Configuration do IntelliJ — MonitorIA

Como o professor usa este arquivo para distribuir um projeto-template com MonitorIA pré-configurado:

1. Crie ou prepare a pasta base do projeto que você vai compartilhar com os alunos.
2. Dentro dessa pasta, crie (se não existir) a subpasta `.idea/runConfigurations/`.
3. Copie `MonitorIA.xml` deste diretório para lá:

   ```bash
   mkdir -p /caminho/do/projeto/.idea/runConfigurations
   cp MonitorIA.xml /caminho/do/projeto/.idea/runConfigurations/
   ```

4. Compartilhe a pasta do projeto com os alunos (ZIP, Git, etc.).

Quando o aluno abrir a pasta no IntelliJ:

- Aparece uma configuração **🤖 MonitorIA** no seletor de Run (canto superior direito).
- Clicando no ▶ (Run), o IntelliJ abre o terminal integrado e dispara `monitoria watch .` na raiz do projeto.
- O aluno só precisa ter rodado o `install.sh` antes (e feito `monitoria login` + `monitoria init` na primeira vez).

Requisitos do aluno:

- Ter rodado o instalador do MonitorIA (o script garante que `monitoria` esteja em `~/.local/bin/`).
- `~/.local/bin` no PATH do shell dele (o instalador cuida disso).
- IntelliJ com o plugin **Shell Script** habilitado (já vem por padrão no IntelliJ IDEA recente).
