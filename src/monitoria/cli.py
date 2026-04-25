"""CLI commands for MonitorIA."""

import click
from rich.console import Console

from monitoria import __version__

console = Console()


@click.group()
@click.version_option(version=__version__, prog_name="MonitorIA")
def main():
    """🤖 MonitorIA — Monitor de código em tempo real para ClassContent.digital"""
    pass


@main.command()
@click.option("--api-url", default=None, help="URL da API (default: produção)")
def login(api_url: str | None):
    """Faz login no ClassContent via email + código OTP."""
    from monitoria.auth import login as do_login
    from monitoria.config import MonitoriaConfig

    console.print(f"\n🤖 [bold]MonitorIA v{__version__}[/bold] — Login\n")

    config = MonitoriaConfig.load()
    if api_url:
        config.api_url = api_url

    if do_login(config, console):
        config.save()
        console.print("   💾 [green]Token salvo em ~/.monitoria/config.json[/green]")
        console.print("   Execute [bold]monitoria init[/bold] para escolher a turma.\n")
    else:
        raise SystemExit(1)


@main.command()
@click.option("--api-url", default=None, help="URL da API (default: produção)")
def init(api_url: str | None):
    """Login + seleção de turma. Tudo que precisa antes de 'watch'.

    Se já estiver logado, pula direto para a seleção de turma.
    """
    from monitoria.auth import login as do_login, fetch_my_classes, select_class
    from monitoria.config import MonitoriaConfig

    console.print(f"\n🤖 [bold]MonitorIA v{__version__}[/bold] — Configuração inicial\n")

    config = MonitoriaConfig.load()
    if api_url:
        config.api_url = api_url

    # ── Step 1: Login (skip if already has a valid token) ──────────
    if not config.token:
        console.print("   [dim]Nenhum token salvo — vamos fazer login primeiro.[/dim]\n")
        if not do_login(config, console):
            raise SystemExit(1)
        config.save()
    else:
        console.print("   ✅ Token encontrado — pulando login.\n")

    # ── Step 2: Fetch classes ──────────────────────────────────────
    console.print("   Buscando suas turmas...")
    classes = fetch_my_classes(config)

    if not classes:
        console.print("   [yellow]Nenhuma turma encontrada. Verifique se você está matriculado.[/yellow]\n")
        raise SystemExit(1)

    # ── Step 3: Select class ──────────────────────────────────────
    selected = select_class(classes, console)
    if not selected:
        raise SystemExit(1)

    config.class_id = selected["classId"]
    config.class_name = selected.get("className") or selected.get("classId")
    config.save()

    course = selected.get("courseName", "")
    label = f"{course} — {config.class_name}" if course else config.class_name
    console.print(f"\n   ✅ [green bold]Turma configurada![/green bold]")
    console.print(f"   📚 [cyan]{label}[/cyan]")
    console.print(f"   💾 Salvo em ~/.monitoria/config.json")
    console.print(f"\n   Agora execute [bold]monitoria watch ./seu-projeto[/bold] para iniciar.\n")


@main.command()
@click.argument("path", type=click.Path(exists=True, file_okay=False))
@click.option("--debounce", default=10, help="Segundos entre syncs (default: 10)")
@click.option("--offline", is_flag=True, default=False, help="Modo offline — só rastreia arquivos sem API")
@click.option("--skip-validation", is_flag=True, default=False,
              help="Pula a validação de diretório (use só se souber o que está fazendo)")
def watch(path: str, debounce: int, offline: bool, skip_validation: bool):
    """Observa uma pasta e envia código para análise da IA em tempo real.

    Uso: monitoria watch ./meu-projeto

    Antes de começar, valida se o diretório é seguro pra observar:
    - bloqueia pastas do sistema (HOME, Desktop, Downloads, ~/Library, etc.)
    - pergunta para a IA se o conteúdo bate com a aula em andamento

    No modo --offline, apenas rastreia arquivos localmente sem enviar para a API.
    O professor precisa ter uma aula ativa para que os syncs sejam aceitos.
    """
    from pathlib import Path
    from monitoria.config import MonitoriaConfig
    from monitoria.validate import (
        WatchDirBlocked,
        check_blocklist,
        validate_watch_dir,
    )
    from monitoria.watcher import start_watching

    config = MonitoriaConfig.load()

    if not offline and not config.token:
        console.print("❌ [red]Não autenticado. Execute 'monitoria login' ou use --offline[/red]")
        raise SystemExit(1)

    if not offline and not config.class_id:
        console.print("❌ [red]Turma não configurada. Execute 'monitoria init' primeiro.[/red]")
        raise SystemExit(1)

    project_path = Path(path).resolve()
    config.project_path = str(project_path)
    config.save()

    if not skip_validation:
        try:
            check_blocklist(project_path)
        except WatchDirBlocked as exc:
            console.print(f"\n🔴 [red bold]Diretório bloqueado[/red bold]")
            console.print(f"   [red]{exc}[/red]\n")
            raise SystemExit(1)

    if not offline and not skip_validation:
        with console.status("[cyan]Validando diretório com a IA...[/cyan]"):
            result = validate_watch_dir(config, project_path)

        if result is None:
            console.print("   [yellow]⚠ Não foi possível validar agora — seguindo mesmo assim.[/yellow]")
        elif not result.get("checked"):
            reason = result.get("reason", "")
            if reason:
                console.print(f"   [dim]ℹ {reason}[/dim]")
        else:
            decision = result.get("decision", "OK")
            reason = result.get("reason", "")
            session_title = result.get("sessionTitle", "")
            if decision == "OK":
                ctx_label = f" — {session_title}" if session_title else ""
                console.print(f"   🟢 [green]Diretório OK[/green]{ctx_label}")
            elif decision == "SUSPEITO":
                console.print(f"\n   🟡 [yellow bold]Diretório suspeito[/yellow bold]")
                console.print(f"   [yellow]{reason}[/yellow]\n")
                if not click.confirm("   Tem certeza que quer continuar?", default=False):
                    console.print("   [dim]Cancelado. Aponte para o projeto correto e tente de novo.[/dim]\n")
                    raise SystemExit(0)
            elif decision == "RECUSADO":
                console.print(f"\n   🔴 [red bold]Diretório recusado pela IA[/red bold]")
                console.print(f"   [red]{reason}[/red]")
                console.print(f"   [dim]O professor foi avisado. Aponte para o projeto correto da aula.[/dim]")
                console.print(f"   [dim]Se foi engano da IA, rode com --skip-validation.[/dim]\n")
                raise SystemExit(1)

    start_watching(str(project_path), config, debounce, console, offline=offline)


@main.command()
@click.argument("path", type=click.Path(exists=True, file_okay=False))
def scan(path: str):
    """Lista os arquivos rastreáveis de uma pasta (sem watch, sem IA).

    Uso: monitoria scan ./meu-projeto
    """
    from pathlib import Path
    from monitoria.config import MonitoriaConfig
    from monitoria.watcher import collect_all_files

    config = MonitoriaConfig.load()
    project_path = Path(path).resolve()
    config.merge_project_config(project_path)

    console.print(f"\n🤖 [bold]MonitorIA v{__version__}[/bold] — Scan\n")
    console.print(f"   Pasta: [cyan]{project_path}[/cyan]\n")

    with console.status("[bold cyan]Coletando arquivos...[/bold cyan]"):
        files = collect_all_files(project_path, config)

    console.print(f"   📄 {len(files)} arquivos encontrados\n")

    if not files:
        console.print("   [dim]Nenhum arquivo rastreável encontrado.[/dim]\n")
        return

    total_lines = sum(f.get("content", "").count("\n") + 1 for f in files)

    # Group by language
    lang_counts: dict[str, int] = {}
    for f in files:
        lang = f.get("language", "text")
        lang_counts[lang] = lang_counts.get(lang, 0) + 1

    console.print(f"   📝 {total_lines} linhas de código")
    for lang, count in sorted(lang_counts.items(), key=lambda x: -x[1]):
        console.print(f"      {lang}: {count} arquivo(s)")

    console.print()
    console.print("   [dim]💡 Use [bold]monitoria watch ./pasta[/bold] para análise da IA em tempo real.[/dim]\n")


@main.command()
def status():
    """Mostra o status da conexão e configuração."""
    from monitoria.config import MonitoriaConfig

    config = MonitoriaConfig.load()

    console.print(f"\n🤖 [bold]MonitorIA v{__version__}[/bold]\n")
    console.print(f"   Turma:       [cyan]{config.class_name or config.class_id or '(não configurado)'}[/cyan]")
    console.print(f"   Projeto:     [cyan]{config.project_path or '(não configurado)'}[/cyan]")
    console.print(f"   Token:       {'[green]✓ presente[/green]' if config.token else '[red]✗ ausente[/red]'}")
    console.print(f"   API:         [dim]{config.api_url}[/dim]")
    console.print(f"   Último sync: [dim]{config.last_sync_at or 'nunca'}[/dim]\n")

    if not config.token:
        console.print("   [dim]→ Execute [bold]monitoria login[/bold] para autenticar.[/dim]\n")
    elif not config.class_id:
        console.print("   [dim]→ Execute [bold]monitoria init[/bold] para escolher a turma.[/dim]\n")
    else:
        console.print("   [dim]→ Execute [bold]monitoria watch ./pasta[/bold] para iniciar.[/dim]\n")


@main.command()
def logout():
    """Remove token e configuração local."""
    from monitoria.config import MonitoriaConfig

    config = MonitoriaConfig.load()
    config.token = None
    config.refresh_token = None
    config.class_id = None
    config.class_name = None
    config.save()

    console.print("\n   ✅ [green]Logout realizado. Token removido.[/green]\n")
