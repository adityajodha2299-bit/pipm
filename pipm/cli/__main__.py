import platform
from pathlib import Path

import typer
from rich.console import Console

from ..core.core import ENV_ROOT, resolve_name  # noqa: TID252
from ..env import manager  # noqa: TID252
from ..exception import (  # noqa: TID252
    EnvNotExistsError,
    FailedToCreateError,
)

app = typer.Typer()

console = Console()


def return_list(items: list[str] | dict[str, str], show_version: bool = True):
    if isinstance(items, dict):
        if not items:
            console.print("(No packages installed)", style="bold white")
            return
        for pkg, ver in items.items():
            if show_version:
                console.print(
                    f" [green]+[/green] [bold white]{pkg}[/bold white][dim white]=={ver}[/dim white]"  # noqa: E501
                )
            else:
                console.print(f" [green]+[/green] [bold white]{pkg}[/bold white]")
    elif isinstance(items, list):  # type: ignore
        if not items:
            console.print("(No environments found)", style="bold white")
            return
        for item in items:
            console.print(f" [green]+[/green] [bold white]{item}[/bold white]")
    else:
        raise TypeError("items must be dict or list")  # noqa: TRY003


@app.command()
def create(name: str | None = typer.Argument(None, help="name of env")):
    if name is None:
        name = Path.cwd().name

    console.print(
        f"[bold white]Using {platform.python_version()} interpreter at:[/bold white] "
        + f"[cyan]{ENV_ROOT / name}[/cyan]"
    )

    try:
        manager.create_env(name=name)
    except FileExistsError:
        console.print(f"[red]Env {name} is already created[/red]")
        return
    except FailedToCreateError:
        console.print(f"[red]❌ Failed to create env '{name}'[/red]")
        return

    console.print(f"✔ Created env '{name}'")

    return_list(manager.list_pkg(name=name))


@app.command()
def delete(name: str | None = typer.Argument(None, help="delete the given env")):
    if name is None:
        console.print("Please Enter the Env name")
        raise typer.Exit(1)

    try:
        manager.delete_env(name=name)
    except EnvNotExistsError:
        console.print(f"[red]❌ Env {name} does not exist[/red]")
        raise typer.Exit(1)  # noqa: B904

    console.print(f"🗑️ Deleted env: {name}")


@app.command()
def use(name: str | None = typer.Argument(None, help="use a venv")):
    envs = manager.list_env()
    if name is None:
        name_env: str = Path.cwd().name
        console.print(f"⚠ No env specified → using [white]'{name_env}'[/white]", style="dim white")
    else:
        name_env = name

    try:
        final_name = resolve_name(name_env, envs)
    except EnvNotExistsError:
        console.print(f"❌ Env [green]'{name_env}'[/green] not found", style="red")
        console.print("→ pipm use <env>", style="red")

        return_list(items=envs)
        raise typer.Exit(1)  # noqa: B904

    if final_name:
        manager.use_venv(name=final_name, current_path=Path.cwd())
        console.print(f"✔ Using env [green]'{final_name}'[/green]", style="bold white")
    else:
        # This case is impossible for normal senarios
        console.print("WARNING! SOMETHING BAD HAD HAPPEND, NAME GOT BI-PASSED", style="bold red")
        typer.Exit(1)


if __name__ == "__main__":
    app()
