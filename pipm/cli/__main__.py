import platform
import time
from pathlib import Path

import typer
from rich.console import Console
from rich.tree import Tree

from ..core.config import ENV_ROOT  # noqa: TID252
from ..core.core import generate_tree, get_time, load_pipm, resolve_name, run_file  # noqa: TID252
from ..env import manager  # noqa: TID252
from ..exception import (  # noqa: TID252
    EnvNotExistsError,
    FailedToCreateError,
    PackageNotFoundError,
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

    return_list(manager.list_env())


@app.command()
def delete(name: str | None = typer.Argument(None, help="delete the given env")):
    if name is None:
        console.print("Please Enter the Env name")
        raise typer.Exit(1)

    try:
        manager.delete_env(name=name)
    except EnvNotExistsError:
        console.print(f"[red]❌ Env {name} does not exist[/red]")
        return_list(manager.list_env())
        raise typer.Exit(1)  # noqa: B904

    console.print(f"🗑️ Deleted env: {name}")

    Path(".pipm").unlink(missing_ok=True)


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

        activate_path, found = manager.get_activate_script(final_name)
        if found:
            console.print("\nTo activate this environment, run:", style="bold white")
            console.print(f"[dim]→ Run: source {activate_path}[/dim]")
        else:
            console.print("Not able to activate the venv", style="red")
    else:
        # This case is impossible for normal senarios
        console.print("WARNING! SOMETHING BAD HAD HAPPEND, NAME GOT BI-PASSED", style="bold red")
        raise RuntimeError("Unexpected state: resolved env is None")  # noqa: TRY003


@app.command()
def add(pkg: str | None = typer.Argument(None)):
    if pkg is None:
        raise typer.BadParameter("Package name required")  # noqa: TRY003

    pipm_data = load_pipm(path=Path.cwd())

    _venv = pipm_data.env
    if _venv is not None:
        try:
            console.print(f"Getting package '{pkg}' from pypi", style="dim white")
            manager.install_pkg(venv=_venv, pkg=pkg)
        except PackageNotFoundError:
            console.print("Invalid Package name!", style="bold red")
            return
        except RuntimeError as e:
            console.print(f"⚠ {e}", style="yellow")
            return

    else:
        console.print("Env is corrupted please recreate the env", style="bold red")
        return


@app.command()
def run(script: Path | None = typer.Argument(None)):  # noqa: B008
    project_path = Path.cwd() / ".pipm"

    # checks is the .pipm file exists or not
    if not project_path.exists():
        console.print("No `.pipm` file found please first create the file", style="bold red")
        console.print("→ pipm create <evn name>", style="bold white")
        return

    _data = load_pipm(project_path)

    env: str | None = _data.env
    scpt: Path | None = _data.main_script

    if script is None:
        if scpt is None:
            console.print(
                "Please initialize the main script first or give the path of script to run",
                style="bold red",
            )

            # Add the line after createing a pipm main-script command
            return
        fin_script: Path = scpt.absolute()
    else:
        fin_script: Path = script if script.is_absolute() else Path.cwd() / script

    if env is None:
        console.print(
            "Env is corrupted. please delete the `.pipm` file and recreate it", style="bold red"
        )
        return
    if env not in manager.list_env():
        console.print(f"Env {env} doesn't exist", style="bold red")
        return

    if not fin_script.exists():
        console.print(f"file [green]{fin_script}[/green] not found", style="bold red")
        tree = Tree(f"[bold white]{Path.cwd().name}[/bold white]")
        generate_tree(Path.cwd(), tree)
        return

    console.print(
        f"▶ Running [cyan]{fin_script}[/cyan] with env [green]'{env}'[/green]", end="\n\n"
    )
    time_start = time.perf_counter()
    return_code: int = run_file(env, fin_script)
    time_stop = time.perf_counter()

    if return_code == 0:
        console.print("\nThanks for using pipm", style="dim white")
        console.print(
            f"[yellow]⚡[/yellow][dim white]Completed in {get_time(time_start, time_stop)}[/]",
        )


@app.command()
def runx(script: Path | None = typer.Argument(None)):  # noqa: B008
    if script is None:
        pass


if __name__ == "__main__":
    app()
