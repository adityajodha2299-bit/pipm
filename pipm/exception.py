class FailedToCreateError(Exception):
    def __init__(self, name: str, *args: object) -> None:
        super().__init__(f"❌ Failed to create env '{name}'", *args)


class EnvNotExistsError(Exception):
    def __init__(self, name: str, *args: object) -> None:
        super().__init__(f"❌ Env {name} does not exist", *args)
