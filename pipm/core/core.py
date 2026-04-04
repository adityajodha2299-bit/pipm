from pathlib import Path

type EnvPath = Path
type MetaPath = Path


ENV_ROOT: EnvPath = Path.home() / ".pipm" / "envs"
METAFILE: MetaPath = Path("metadata.json")
