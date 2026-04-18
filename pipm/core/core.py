import json
from pathlib import Path
from typing import Any

import tomllib
from rich.tree import Tree

from ..env.manager import (  # noqa: TID252
    VenvName,
    get_env_python,
)
from ..exception import EnvIsCorruptedError, EnvNotExistsError  # noqa: TID252
from .config import (
    ENV_ROOT,
    METAFILE,
    PackageInfo,
    PipmData,
    PkgName,
    VenvMeta,
)
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
    then raise error. Else return name"""
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
    pth = path / ".pipm" if path.name != ".pipm" else path

    if not pth.exists():
        raise FileNotFoundError()

    try:
        with pth.open("rt") as f:
            data = json.load(f)
    except json.JSONDecodeError:
        raise ValueError("Invalid .pipm file (corrupted JSON)")  # noqa: B904, TRY003

    packages: dict[PkgName, PackageInfo] | None = None
    raw_packages: Any = data.get("packages")

    if isinstance(raw_packages, dict):
        packages = {}

        for name, info in raw_packages.items():
            if not isinstance(info, dict):
                continue  # skip bad entries

            version = info.get("version", "unknown")
            if not isinstance(version, str):
                version = "unknown"

            extras = info.get("extras", [])
            if not isinstance(extras, list):
                extras = []

            specifier = info.get("specifier", "")
            if not isinstance(specifier, str):
                specifier = ""

            packages[name] = PackageInfo(version=version, extras=extras, specifier=specifier)

    main_script_raw = data.get("main_script")
    main_script = Path(main_script_raw) if isinstance(main_script_raw, str) else None

    return PipmData(
        env=data.get("env"),
        main_script=main_script,
        packages=packages,
    )


def load_MetaEnv(name: VenvName) -> VenvMeta:  # noqa: N802
    meta_file = ENV_ROOT / name / METAFILE

    if not meta_file.exists():
        raise EnvIsCorruptedError()

    try:
        with meta_file.open() as f:
            data = json.load(f)
    except json.JSONDecodeError:
        raise EnvIsCorruptedError()  # noqa: B904

    packages: dict[PkgName, PackageInfo] = {}

    raw_packages = data.get("packages")
    if not isinstance(raw_packages, dict):
        raw_packages = {}

    for pkg, info in raw_packages.items():
        if not isinstance(info, dict):
            continue
        packages[pkg] = PackageInfo(
            version=info.get("version", "unknown"),
            extras=info.get("extras", []),
            specifier=info.get("specifier", ""),
        )

    main_script_raw = data.get("main_script")

    return VenvMeta(
        name=data.get("name", name),
        main_script=main_script_raw if isinstance(main_script_raw, str) else None,
        packages=packages,
        created_at=data.get("created_at", "unknown"),
    )


def read_toml(path: Path):
    _file = path
    if not _file.exists():
        return False

    with _file.open("rb") as f:
        _data = tomllib.load(f)
    return None
