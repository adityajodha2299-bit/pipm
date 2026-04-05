import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

from ..core.core import ENV_ROOT, METAFILE  # noqa: TID252
from ..core.runner import Cmd  # noqa: TID252
from ..exception import (  # noqa: TID252
    EnvNotExistsError,
    FailedToCreateError,
)

type VenvName = str
type PkgName = str
type PkgVersion = str


def create_env(name: VenvName):
    path = ENV_ROOT / name

    if path.exists():
        raise FileExistsError(path)

    result = (Cmd("python3") / "-m" / "venv" / path).run()

    if not result.ok:
        raise FailedToCreateError(name=name)

    meta_file = path / METAFILE

    data = {
        "name": name,
        "packages": {},
        "created_at": datetime.now(tz=timezone.utc).strftime("%B %d, %Y - %I:%M %p"),
    }

    with meta_file.open("w") as f:
        json.dump(data, f, indent=2)


def list_pkg(name: VenvName) -> dict[PkgName, PkgVersion]:
    path = ENV_ROOT / name
    with (path / METAFILE).open("r") as f:
        data = json.load(f)

    return data.get("packages", {})


def install_pkg(venv: VenvName, pkg: str):  # need to modify here
    python_path = get_env_python(venv)

    result = (Cmd(str(python_path)) / "-m" / "pip" / "install" / pkg).run()

    if not result.ok:
        print(f"❌ Failed to install '{pkg}'")
        print(f"→ {result.command_to_str}")
        return

    print(f"✔ Installed '{pkg}'")

    package: PkgName = pkg.split("==", maxsplit=1)[0]
    version: PkgVersion = get_pkg_version(python_path, package)

    add_meta_pkg(venv, package, version)


def get_pkg_version(python_path: Path, pkg: PkgName) -> str:
    result = (Cmd(str(python_path)) / "-m" / "pip" / "show" / pkg).run()

    if not result.ok:
        raise RuntimeError(f"Could not get version for {pkg}")  # noqa: TRY003

    for line in result.stdout.splitlines():
        if line.startswith("Version:"):
            return line.split(":")[1].strip()

    raise RuntimeError("Version not found")  # noqa: TRY003


def add_meta_pkg(venv: VenvName, pkg: PkgName, version: PkgVersion):
    meta_file = ENV_ROOT / venv / METAFILE

    with meta_file.open() as f:
        data = json.load(f)

    packages: dict[str, str] = data.get("packages", {})

    packages[pkg] = version  # overwrite if exists

    data["packages"] = packages

    with meta_file.open("w") as f:
        json.dump(data, f, indent=2)


def list_env() -> list[VenvName]:
    if not ENV_ROOT.exists():
        return []

    return [p.name for p in ENV_ROOT.iterdir() if p.is_dir()]


def get_env_python(venv: VenvName) -> Path:
    path = ENV_ROOT / venv / "bin" / "python"
    if not path.exists():
        raise FileNotFoundError()
    return path


def delete_env(name: VenvName):
    path = ENV_ROOT / name

    if not path.exists():
        raise EnvNotExistsError(name=name)

    shutil.rmtree(path)


def use_venv(name: VenvName, current_path: Path):
    path = current_path / ".pipm"

    _data = {"env": name}
    with path.open("w", encoding="utf-8") as f:
        json.dump(_data, f)
