class FailedToCreateError(Exception):
    def __init__(self, name: str, *args: object) -> None:
        super().__init__(f"❌ Failed to create env '{name}'", *args)


class EnvIsCorruptedError(Exception):
    def __init__(self, *args: object):
        super().__init__(*args)


class EnvNotExistsError(Exception):
    def __init__(self, name: str, *args: object) -> None:
        super().__init__(f"❌ Env {name} does not exist", *args)


class FailedToActivateError(Exception):
    def __init__(self, name: str, *args: object) -> None:
        super().__init__(f"Failed to activate {name} venv", *args)


class PackageNotFoundError(Exception):
    def __init__(self, *args: object):
        super().__init__(*args)
