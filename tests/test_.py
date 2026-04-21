# ruff: noqa: S101
# ruff: noqa: ARG001

import json
from unittest.mock import patch

import pytest
from pipm.cli.__main__ import app
from pipm.core.config import PackageInfo, PipmData
from pipm.core.core import diff, get_time, load_pipm, resolve_name
from pipm.env.manager import delete_env, list_env, use_venv
from pipm.exception import EnvNotExistsError
from typer.testing import CliRunner

runner = CliRunner()

# ---------------------------
# 🧠 Helper
# ---------------------------


def pkg(version="", spec="*", extras=None):
    return PackageInfo(version=version, extras=extras or [], specifier=spec)


# ---------------------------
# 🧪 Diff Tests
# ---------------------------


class TestDiff:
    def test_perfect_match(self):
        desired = {"requests": pkg(spec=">=2.0")}
        actual = {"requests": pkg(version="2.31.0")}

        result = diff(desired, actual)

        assert "requests" in result.ok
        assert result.ok["requests"].version == "2.31.0"
        assert result.missing == {}
        assert result.extra == {}

    def test_missing_package(self):
        desired = {"numpy": pkg(spec="*")}
        actual = {}

        result = diff(desired, actual)

        assert "numpy" in result.missing
        assert result.ok == {}
        assert result.extra == {}

    def test_extra_package(self):
        desired = {}
        actual = {"flask": pkg(version="3.0.0")}

        result = diff(desired, actual)

        assert "flask" in result.extra
        assert result.ok == {}
        assert result.missing == {}

    def test_version_mismatch(self):
        desired = {"black": pkg(spec="==24.1.0")}
        actual = {"black": pkg(version="23.0.0")}

        result = diff(desired, actual)

        assert "black" in result.missing

    def test_canonicalization(self):
        desired = {"Requests": pkg(spec="*")}
        actual = {"requests": pkg(version="2.31.0")}

        result = diff(desired, actual)

        assert "requests" in result.ok

    def test_unknown_version_does_not_crash(self):
        desired = {"requests": pkg(spec=">=2.0")}
        actual = {"requests": pkg(version="unknown")}

        result = diff(desired, actual)

        # Just ensure no crash and classified somewhere
        assert "requests" in result.missing or "requests" in result.ok

    def test_diff_mixed_case(self):
        desired = {
            "requests": pkg(spec=">=2.0"),
            "numpy": pkg(spec="*"),
        }

        actual = {
            "requests": pkg(version="2.31.0"),
            "flask": pkg(version="3.0.0"),
        }

        result = diff(desired, actual)

        assert "requests" in result.ok
        assert "numpy" in result.missing
        assert "flask" in result.extra


# ---------------------------
# 🧪 Core Utility Tests
# ---------------------------


def test_resolve_name_valid():
    assert resolve_name("dev", ["dev", "prod"]) == "dev"


def test_resolve_name_none():
    assert resolve_name(None, ["dev"]) is None


def test_resolve_name_invalid():
    with pytest.raises(EnvNotExistsError):
        resolve_name("stage", ["dev", "prod"])


@pytest.mark.parametrize(
    "start, stop, expected",
    [
        (0, 0.5, "500ms"),
        (0, 10.5, "10.50sec"),
        (0, 65, "1min 5sec"),
    ],
)
def test_get_time(start, stop, expected):
    assert get_time(start, stop) == expected


# ---------------------------
# 🧪 load_pipm Tests
# ---------------------------


def test_load_pipm_valid(tmp_path):
    pipm_file = tmp_path / ".pipm"
    pipm_file.write_text(
        json.dumps({
            "env": "test-env",
            "packages": {"rich": {"version": "13.0.0", "specifier": ">=12.0.0"}},
        })
    )

    result = load_pipm(tmp_path)

    assert isinstance(result, PipmData)
    assert result.env == "test-env"
    assert "rich" in result.packages


def test_load_pipm_invalid(tmp_path):
    pipm_file = tmp_path / ".pipm"
    pipm_file.write_text("{ invalid json")

    with pytest.raises(ValueError):
        load_pipm(tmp_path)


def test_load_pipm_missing(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_pipm(tmp_path)


# ---------------------------
# 🧪 CLI Tests
# ---------------------------


@patch("pipm.env.manager.create_env")
@patch("pipm.env.manager.list_env")
def test_create_command(mock_list, mock_create):
    mock_list.return_value = ["test-env"]

    result = runner.invoke(app, ["create", "my-env"])

    assert result.exit_code == 0
    assert "Created env 'my-env'" in result.stdout
    mock_create.assert_called_once()


@patch("pipm.env.manager.delete_env")
def test_delete_command_not_found(mock_delete):
    mock_delete.side_effect = EnvNotExistsError(name="ghost")

    result = runner.invoke(app, ["delete", "ghost"])

    assert result.exit_code != 0
    assert "does not exist" in result.stdout


# ---------------------------
# 🧪 Env Tests
# ---------------------------


@pytest.fixture
def mock_env_root(tmp_path, monkeypatch):
    env_root = tmp_path / "envs"
    env_root.mkdir()
    monkeypatch.setattr("pipm.env.manager.ENV_ROOT", env_root)
    return env_root


def test_list_env_empty(mock_env_root):
    assert list_env() == []


def test_list_env_with_dirs(mock_env_root):
    (mock_env_root / "dev").mkdir()
    (mock_env_root / "prod").mkdir()

    envs = list_env()

    assert "dev" in envs
    assert "prod" in envs


def test_delete_env(mock_env_root):
    path = mock_env_root / "temp"
    path.mkdir()

    delete_env("temp")

    assert not path.exists()


def test_use_venv(tmp_path):
    use_venv("my-env", tmp_path)

    pipm_file = tmp_path / ".pipm"

    assert pipm_file.exists()

    with pipm_file.open() as f:
        data = json.load(f)
        assert data["env"] == "my-env"
