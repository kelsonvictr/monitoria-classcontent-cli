"""Auth flow — OTP passwordless via CLI (same flow as the web app).

Uses /auth/send-code + /auth/verify-code — zero new backend routes needed.
"""

from __future__ import annotations

import httpx
from rich.console import Console
from rich.prompt import Prompt

from monitoria.config import MonitoriaConfig


def login(config: MonitoriaConfig, console: Console) -> bool:
    """Authenticate via email + OTP code.

    Uses the same /auth/send-code + /auth/verify-code endpoints as the web app.
    Returns True if login was successful.
    """
    console.print()

    # ── Step 1: Collect email ──────────────────────────────────────
    email = Prompt.ask("📧 [bold]Seu email cadastrado no ClassContent[/bold]").strip().lower()
    if not email or "@" not in email:
        console.print("   [red]Email inválido.[/red]\n")
        return False

    # ── Step 2: Request OTP ────────────────────────────────────────
    console.print(f"\n   Enviando código para [cyan]{email}[/cyan]...")

    try:
        resp = httpx.post(
            f"{config.api_url}/auth/send-code",
            json={"email": email},
            timeout=15.0,
        )
    except httpx.HTTPError as exc:
        console.print(f"   [red]Erro de conexão: {exc}[/red]\n")
        return False

    if resp.status_code == 429:
        msg = resp.json().get("error", "Aguarde antes de tentar novamente.")
        console.print(f"   [yellow]⏳ {msg}[/yellow]\n")
        return False

    if resp.status_code == 403:
        msg = resp.json().get("error", "Email não autorizado.")
        console.print(f"   [red]🚫 {msg}[/red]\n")
        return False

    if resp.status_code != 200:
        msg = resp.json().get("error", "Erro ao enviar código.")
        console.print(f"   [red]❌ {msg}[/red]\n")
        return False

    console.print("   [green]✓ Código enviado![/green] Verifique seu email.\n")

    # ── Step 3: Collect OTP code (up to 3 attempts) ────────────────
    for attempt in range(1, 4):
        code = Prompt.ask("🔑 [bold]Digite o código de 6 dígitos[/bold]").strip()
        if not code:
            continue

        try:
            verify_resp = httpx.post(
                f"{config.api_url}/auth/verify-code",
                json={"email": email, "code": code},
                timeout=15.0,
            )
        except httpx.HTTPError as exc:
            console.print(f"   [red]Erro de conexão: {exc}[/red]\n")
            return False

        if verify_resp.status_code == 200:
            data = verify_resp.json()
            config.token = data["token"]
            config.refresh_token = data.get("refreshToken")

            user = data.get("user", {})
            user_name = user.get("name") or user.get("email", "")

            console.print(f"\n   ✅ [green bold]Login realizado com sucesso![/green bold]")
            console.print(f"   👤 [cyan]{user_name}[/cyan]\n")
            return True

        # Handle errors
        msg = verify_resp.json().get("error", "Código inválido.")

        if verify_resp.status_code == 429:
            console.print(f"   [yellow]⏳ {msg}[/yellow]\n")
            if "Solicite um novo código" in msg or "Muitas tentativas" in msg:
                return False
            continue

        if verify_resp.status_code == 400:
            console.print(f"   [red]❌ {msg}[/red]")
            if "expirado" in msg.lower() or "Máximo" in msg:
                return False
            if attempt < 3:
                console.print(f"   [dim]Tentativa {attempt}/3[/dim]\n")
            continue

        console.print(f"   [red]❌ {msg}[/red]\n")
        return False

    console.print("   [red]Máximo de tentativas atingido. Execute 'monitoria login' novamente.[/red]\n")
    return False


def fetch_my_classes(config: MonitoriaConfig) -> list[dict]:
    """Fetch the list of classes the authenticated user is enrolled in.

    Returns list of dicts with classId, className, courseName, role.
    """
    if not config.token:
        return []

    try:
        resp = httpx.get(
            f"{config.api_url}/me/classes",
            headers={"Authorization": f"Bearer {config.token}"},
            timeout=15.0,
        )
        if resp.status_code == 200:
            return resp.json().get("items", [])
    except httpx.HTTPError:
        pass

    return []


def select_class(
    classes: list[dict],
    console: Console,
) -> dict | None:
    """Let the user pick a class from the list.

    Returns the selected class dict or None if cancelled.
    """
    if not classes:
        console.print("   [yellow]Nenhuma turma encontrada para este usuário.[/yellow]\n")
        return None

    # Filter only active classes
    active = [c for c in classes if c.get("status", "active") == "active"]
    if not active:
        active = classes

    console.print("[bold]📚 Suas turmas:[/bold]\n")
    for i, c in enumerate(active, 1):
        course = c.get("courseName", "")
        name = c.get("className", c.get("classId", "?"))
        role_label = {"admin": "👨‍🏫", "teacher": "👨‍🏫", "student": "🎒"}.get(
            c.get("role", "student"), "🎒"
        )
        if course:
            console.print(f"   [bold]{i}.[/bold] {role_label} {course} — [cyan]{name}[/cyan]")
        else:
            console.print(f"   [bold]{i}.[/bold] {role_label} [cyan]{name}[/cyan]")

    console.print()
    choice = Prompt.ask(
        f"Escolha a turma [bold](1-{len(active)})[/bold]",
        default="1",
    ).strip()

    try:
        idx = int(choice) - 1
        if 0 <= idx < len(active):
            return active[idx]
    except ValueError:
        pass

    console.print("   [red]Opção inválida.[/red]\n")
    return None
