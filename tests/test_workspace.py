import pytest

from pytuitor_web import workspace
from pytuitor_web.workspace import WorkspaceError, export_workspace, validate_files


@pytest.mark.parametrize(
    "name",
    [
        "/tmp/a.py",
        "../a.py",
        "a/../b.py",
        "a//b.py",
        "./a.py",
        "a\\b.py",
        "C:a.py",
        "a\x00.py",
        "a/",
        ".git/config",
        ".venv/a.py",
        "a./b.py",
    ],
)
def test_rejects_unsafe_project_names(name):
    with pytest.raises(WorkspaceError):
        validate_files({name: "print('hello')"})


@pytest.mark.parametrize(
    "files", [{"A.py": "", "a.py": ""}, {"a": "", "a/b.py": ""}, {"é.py": "", "e\u0301.py": ""}]
)
def test_rejects_cross_platform_path_collisions(files):
    with pytest.raises(WorkspaceError):
        validate_files(files)


def test_bounds_use_utf8_bytes_and_total_workspace_size():
    with pytest.raises(WorkspaceError, match="file limit"):
        validate_files({"large.py": "🐍" * (workspace.MAX_FILE_BYTES // 4 + 1)})
    with pytest.raises(WorkspaceError, match="total size"):
        validate_files({f"{index}.py": "a" * workspace.MAX_FILE_BYTES for index in range(5)})
    with pytest.raises(WorkspaceError, match="between"):
        validate_files({f"{index}.py": "" for index in range(workspace.MAX_FILES + 1)})


def test_exports_nested_files_without_replacing_existing_content(tmp_path):
    files = {"main.py": "from helpers.maths import double\n", "helpers/maths.py": "🐍\n"}
    destination = export_workspace(tmp_path / "project", files)
    assert (destination / "helpers/maths.py").read_text(encoding="utf-8") == "🐍\n"
    with pytest.raises(WorkspaceError, match="already exists"):
        export_workspace(destination, {"main.py": "overwritten"})
    assert (destination / "main.py").read_text(encoding="utf-8") == files["main.py"]
    assert sorted(path.name for path in tmp_path.iterdir()) == ["project"]


def test_rejects_symlink_parent_and_destination(tmp_path):
    original = tmp_path / "original"
    original.mkdir()
    alias = tmp_path / "alias"
    alias.symlink_to(original, target_is_directory=True)
    for destination in (alias, alias / "export"):
        with pytest.raises(WorkspaceError, match="symbolic"):
            export_workspace(destination, {"main.py": ""})
    assert not list(original.iterdir())
