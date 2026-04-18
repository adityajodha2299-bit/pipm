
## Data Conversion Mental Model
```PYTHON
┌──────────────────────────────┐
│        JSON FILE (.pipm)     │   ← stored on disk (untrusted)
└──────────────┬───────────────┘
               │
               │ json.load()
               ▼
┌──────────────────────────────┐
│   PipmJson (TypedDict)       │   ← raw structure (dict, loosely safe)
└──────────────┬───────────────┘
               │    _data = load_pipm(pipm_file) or load_pipm(CWD)
               │
               ▼
┌──────────────────────────────┐
│   PipmData (dataclass)       │   ← clean, structured, safe
└──────────────┬───────────────┘
               │
               │ used everywhere in code
               ▼
        APPLICATION LOGIC
```


 - ### 1. JSON FILE (disk layer)
    ```JSON
        {
            "env": "myenv",
            "main_script": "main.py",
            "packages": {
                "requests": {
                "version": "2.31.0",
                "extras": ["security"]
                }
            }
        }
    ```


 - ### 2. PipmJson (TypedDict layer)
    ```python
    class PipmJson(TypedDict):
        env: str | None
        main_script: str | None
        packages: dict[PkgName, PackageJson] | None
    ```


    #### After Loading:
    ```python
    _data = load_pipm(pipm_file) or load_pipm(CWD)
    ```


    #### Now:
    ```python
    data["packages"]["requests"]
    ```

    #### Is still:
    ```python
    {"version": "2.31.0", "extras": ["security"]}
    ```

    #### Caution:-
    TypedDict(PipmJson) is NOT your runtime model
    **It is only a shape description of `JSON`**


- ### PipmData (dataclass)
    ```python
    @dataclass
    class PipmData:
        env: str | None
        main_script: Path | None
        packages: dict[PkgName, PackageInfo] | None
    ```

## Main Conversion Function (present in core.py)
   ```python
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

                packages[name] = PackageInfo(
                    version=version,
                    extras=extras,
                )

        main_script_raw = data.get("main_script")
        main_script = Path(main_script_raw) if isinstance(main_script_raw, str) else None

        return PipmData(
            env=data.get("env"),
            main_script=main_script,
            packages=packages,
        )
   ```
    
### ***Clean, structured, safe and can used everywhere in code***