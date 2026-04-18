import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

from packaging.requirements import InvalidRequirement, Requirement
from packaging.utils import canonicalize_name

from ..core.config import (  # noqa: TID252
    ENV_ROOT,
    METAFILE,
    PkgName,
    PkgVersion,
    VenvName,
)
from ..core.runner import Cmd  # noqa: TID252
from ..exception import (  # noqa: TID252
    EnvNotExistsError,
    FailedToCreateError,
    PackageNotFoundError,
)


def create_env(name: VenvName):
    temp_sanitized_name = Path(name).name
    path = ENV_ROOT / temp_sanitized_name

    if path.exists():
        raise FileExistsError(path)

    result = (Cmd(sys.executable) / "-m" / "venv" / path).run()

    if not result.ok:
        raise FailedToCreateError(name=name)

    meta_file = path / METAFILE

    data = {
        "name": name,
        "main_script": None,
        "packages": {},
        "created_at": datetime.now(tz=timezone.utc).strftime("%B %d, %Y - %I:%M %p"),
    }

    with meta_file.open("w") as f:
        json.dump(data, f, indent=2)


def list_pkg(name: VenvName) -> dict[PkgName, dict[str, list[str] | str]]:
    path = ENV_ROOT / name
    with (path / METAFILE).open("r") as f:
        data = json.load(f)

    packages = data.get("packages")
    if not isinstance(packages, dict):
        packages = {}

    return packages


def install_pkg(venv: VenvName, pkg: str):
    python_path = get_env_python(venv)

    result = (Cmd(str(python_path)) / "-m" / "pip" / "install" / pkg).run()

    if not result.ok:
        print(f"❌ Failed to install '{pkg}'")
        print(f"→ {result.command_to_str}")
        print(result.stderr)
        raise PackageNotFoundError()

    print(f"✔ Installed '{pkg}'")

    try:
        req = Requirement(pkg)
        package = canonicalize_name(req.name)
        extras = list(req.extras)
        specifier = str(req.specifier)
    except InvalidRequirement:
        raise PackageNotFoundError(f"Failed to install '{pkg}'")  # noqa: B904, TRY003

    try:
        version = get_pkg_version(python_path, package)
    except Exception as e:  # noqa: BLE001
        version = f"unknown {e}"

    add_meta_pkg(venv, package, version, extras, specifier)


def get_pkg_version(python_path: Path, pkg: PkgName) -> str:
    code = f"import importlib.metadata as m;print(m.version('{pkg}'))"

    result = (Cmd(str(python_path)) / "-c" / code).run()

    if not result.ok:
        raise RuntimeError(f"Could not get version for {pkg}")  # noqa: TRY003

    return result.stdout.strip()


def add_meta_pkg(
    venv: VenvName,
    pkg: PkgName,
    version: PkgVersion,
    extras: list[str] | None = None,
    specifier: str = "",
):
    meta_file = ENV_ROOT / venv / METAFILE

    if not meta_file.exists():
        raise EnvNotExistsError(name=venv)

    with meta_file.open() as f:
        data = json.load(f)

    packages = data.get("packages")
    if not isinstance(packages, dict):
        packages = {}

    packages[pkg] = {
        "version": version,
        "extras": extras or [],
        "specifier": specifier,
    }

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

    _data = {
        "env": name,
        "main_script": None,
        "packages": None,
    }
    with path.open("w", encoding="utf-8") as f:
        json.dump(_data, f, indent=2)


def get_activate_script(name: VenvName) -> tuple[Path, bool]:
    activate_path = ENV_ROOT / name / "bin" / "activate"
    return activate_path, activate_path.exists()
