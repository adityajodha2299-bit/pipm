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
    PackageInfo,
    PipmData,
    PkgName,
    VenvName,
)
from ..core.runner import Cmd  # noqa: TID252
from ..exception import (  # noqa: TID252
    EnvNotExistsError,
    FailedToCreateError,
    PackageNotFoundError,
    PipmFileNotExistsError,
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

    _data = {
        "name": name,
        "main_script": None,
        "packages": {},
        "created_at": datetime.now(tz=timezone.utc).strftime("%B %d, %Y - %I:%M %p"),
    }

    with meta_file.open("w") as f:
        json.dump(_data, f, indent=2)


def list_pkg(name: VenvName) -> dict[PkgName, dict[str, list[str] | str]]:
    path = ENV_ROOT / name
    with (path / METAFILE).open("r") as f:
        data = json.load(f)

    packages = data.get("packages")
    if not isinstance(packages, dict):
        packages = {}

    return packages


def install_pkg(venv: VenvName, pkg: str, user_dir: Path, _data: PipmData):
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
        specifier = str(req.specifier) or "*"
    except InvalidRequirement:
        raise PackageNotFoundError(f"Failed to install '{pkg}'")  # noqa: B904, TRY003

    update_meta_pkg(
        venv_name=venv, python_path=python_path, package=package, extras=extras, specifier=specifier
    )
    add_pipm_pkg(venv, package, user_dir, _data, extras, specifier)


def get_pkg_version(python_path: Path, pkg: PkgName) -> str:
    code = f"import importlib.metadata as m;print(m.version('{pkg}'))"

    result = (Cmd(str(python_path)) / "-c" / code).run()

    if not result.ok:
        raise RuntimeError(f"Could not get version for {pkg}")  # noqa: TRY003

    return result.stdout.strip()


def update_meta_pkg(
    venv_name: VenvName, python_path: Path, package: PkgName, extras: list[str], specifier: str
):  # Here i not used load_meta coz i am lazy but in future i will use it.

    meta_pth = ENV_ROOT / venv_name / METAFILE

    if not meta_pth.exists():
        raise FileNotFoundError(venv_name)

    with meta_pth.open("rt") as f:
        _data = json.load(f)

    packages = _data.get("packages", {})
    package = canonicalize_name(package)

    try:
        version = get_pkg_version(python_path, package)
    except Exception as e:  # noqa: BLE001
        version = f"unknown {e}"

    packages[package] = {
        "version": version,
        "extras": extras,
        "specifier": specifier or "*",
    }

    _data["packages"] = packages

    with meta_pth.open("w") as f:
        json.dump(_data, f, indent=2)


def add_pipm_pkg(
    venv: VenvName,
    pkg: PkgName,
    user_dir: Path,
    _data: PipmData,
    extras: list[str] | None = None,
    specifier: str = "*",
):
    pipm_file = user_dir / ".pipm" if user_dir.name != ".pipm" else user_dir

    if not pipm_file.exists():
        raise PipmFileNotExistsError(name=venv)

    pkg = canonicalize_name(pkg)

    packages = _data.packages
    if packages is None:
        packages = {}

    pkg_info = PackageInfo(
        version="",
        extras=extras or [],
        specifier=specifier,
    )

    packages[pkg] = pkg_info

    _data.packages = packages

    with pipm_file.open("w") as f:
        json.dump(
            {
                "env": _data.env,
                "main_script": str(_data.main_script) if _data.main_script else None,
                "packages": {
                    name: {"specifier": pkg.specifier, "extras": pkg.extras}
                    for name, pkg in _data.packages.items()
                },
            },
            f,
            indent=2,
        )


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
