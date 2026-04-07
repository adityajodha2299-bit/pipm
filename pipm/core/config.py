from dataclasses import dataclass
from pathlib import Path
from typing import TypedDict

type EnvPath = Path
type MetaPath = Path


class PipmJson(TypedDict):
    env: str | None  # for most unexcepted case
    main_script: str | None


@dataclass
class PipmData:
    env: str | None
    main_script: Path | None


ENV_ROOT: EnvPath = Path.home() / ".pipm" / "envs"
METAFILE: MetaPath = Path("metadata.json")
