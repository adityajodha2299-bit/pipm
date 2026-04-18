from dataclasses import dataclass
from pathlib import Path
from typing import TypedDict

type EnvPath = Path
type MetaPath = Path


type VenvName = str

type PkgName = str
type PkgVersion = str
type PkgExtra = list[str]


class PackageJson(TypedDict):
    version: str
    extras: list[str]


@dataclass
class PackageInfo:
    version: str
    extras: list[str]
    specifier: str


class PipmJson(TypedDict):
    """The pipm file data in the form of JSON
    wil look like this."""

    env: str | None
    main_script: str | None
    packages: dict[PkgName, PackageJson] | None


@dataclass
class VenvMeta:
    """The Meta data of vevn will look like this"""

    name: str
    main_script: str | None
    packages: dict[PkgName, PackageInfo]
    created_at: str


@dataclass
class PipmData:
    """The pipm file data will look like this when
    it is converted into dict to object"""

    env: str | None
    main_script: Path | None
    packages: dict[PkgName, PackageInfo] | None


ENV_ROOT: EnvPath = Path.home() / ".pipm" / "envs"
METAFILE: MetaPath = Path("metadata.json")
