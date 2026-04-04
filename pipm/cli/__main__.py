import platform
from pathlib import Path

import typer
from rich.console import Console

from ..core.core import ENV_ROOT  # noqa: TID252
from ..env import manager  # noqa: TID252
from ..exception import EnvNotExistsError, FailedToCreateError  # noqa: TID252

app = typer.Typer()

console = Console()


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

    for pckge, version in manager.list_pkg(name=name).items():
        console.print(
            f" [green]+[/green] [bold white]{pckge}[/bold white][dim white]=={version}[/dim white]"
        )


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


if __name__ == "__main__":
    app()
