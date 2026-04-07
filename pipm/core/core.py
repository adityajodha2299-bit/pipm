import json
from pathlib import Path

from rich.tree import Tree

from ..env.manager import (  # noqa: TID252
    VenvName,
    get_env_python,
)
from ..exception import EnvNotExistsError  # noqa: TID252
from .config import PipmData, PipmJson
from .runner import Cmd


def generate_tree(path: Path, tree: Tree, find_file: str = ".py"):
    for entry in path.iterdir():
        full_path = Path(path) / entry
        if full_path.is_dir() and entry.name != ".venv" and not entry.name.startswith("."):
            # Add directory to tree
            branch = tree.add(f"[bold blue]{entry.name}[/bold blue]")
            generate_tree(full_path, branch)
        elif entry.name.endswith(find_file):
            # Add .py file to tree
            tree.add(f"[green]{entry.name}[/green]")


def resolve_name(name: VenvName | None, list_of_envs: list[str]) -> VenvName | None:
    """If name is none then return None. If name not in list
    then return None. Else return name"""
    if name is None:
        return None
    if name in list_of_envs:
        return name
    raise EnvNotExistsError(name=name)


def run_file(name: VenvName, script: Path):
    path = get_env_python(name)
    return (Cmd(str(path)) / str(script)).run_live()


def get_time(start: float, stop: float) -> str:
    t = stop - start

    if t < 1:
        return f"{t * 1000:.0f}ms"

    if t < 60:
        return f"{t:.2f}sec"

    minutes = t // 60
    seconds = t % 60
    return f"{minutes:.0f}min {seconds:.0f}sec"


def load_pipm(path: Path) -> PipmData:
    data: PipmJson = json.load(path.open())

    return PipmData(
        env=data["env"],
        main_script=Path(data["main_script"]) if data["main_script"] else None,
    )
