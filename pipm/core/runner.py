from __future__ import annotations

import subprocess
from typing import TYPE_CHECKING, Any, Literal

if TYPE_CHECKING:
    from collections.abc import Mapping
    from pathlib import Path

Tool = Literal["showmydir", "git", "ls", "grep", "uv"] | str
Arguments = list[str]
Flags = dict[str, str | bool]


class Cmd:
    def __init__(
        self,
        tool: Tool,
        args: Arguments | None = None,
        fl: Flags | None = None,
    ) -> None:
        self.base: Tool = tool
        self.args = args or []
        self.flags = fl or {}

    def __call__(self) -> Any:
        return self.run()

    def __str__(self) -> str:
        return " ".join(self._token_create())

    def __truediv__(self, other: str | Path) -> Cmd:
        new_flags = dict(self.flags)
        new_args = list(self.args)
        new_args.append(str(other))
        return Cmd(tool=self.base, args=new_args, fl=new_flags)

    def __add__(self, other: Mapping[str, str | bool]):
        new_flags = dict(self.flags)
        new_flags.update(other)
        new_args = list(self.args)
        return Cmd(tool=self.base, args=new_args, fl=new_flags)

    def _token_create(self):
        tokens: list[str] = []
        tokens.append(self.base)
        tokens.extend(self.args)

        for key, value in self.flags.items():
            if isinstance(value, bool):
                if value is True:
                    tokens.append(key)
                else:
                    # if false skip completely
                    pass
            else:
                tokens.append(key)
                tokens.append(value)

        return tokens

    def debug(self):
        print(self._token_create())
        return self.run()

    def run(self) -> CmdResult:
        user_command = self._token_create()
        result = subprocess.run(user_command, text=True, capture_output=True)  # noqa: S603
        return CmdResult(result.returncode, result.stderr, result.stdout, user_command)


class CmdResult:
    def __init__(self, code: int, stderr: str, stdout: str, command: list[str]) -> None:
        self._code: int = code
        self._command = command
        self._stderr = stderr
        self._stdout = stdout

    def __str__(self) -> str:
        return f"commadn: {self.command_to_str}" + "\n" + f"code: {self._code}"

    @property
    def command(self) -> list[str]:
        return self._command

    @property
    def command_to_str(self) -> str:
        return " ".join(self._command)

    @property
    def stderr(self) -> str:
        return self._stderr

    @property
    def stdout(self) -> str:
        return self._stdout

    @property
    def code(self) -> int:
        return self._code

    @property
    def ok(self):
        return self._code == 0
