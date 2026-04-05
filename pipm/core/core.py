from pathlib import Path

from ..env.manager import VenvName  # noqa: TID252
from ..exception import EnvNotExistsError  # noqa: TID252

type EnvPath = Path
type MetaPath = Path


ENV_ROOT: EnvPath = Path.home() / ".pipm" / "envs"
METAFILE: MetaPath = Path("metadata.json")


def resolve_name(name: VenvName | None, list_of_envs: list[str]) -> VenvName | None:
    """If name is none then return None. If name not in list
    then return None. Else return name"""
    if name is None:
        return None
    if name in list_of_envs:
        return name
    raise EnvNotExistsError(name=name)
