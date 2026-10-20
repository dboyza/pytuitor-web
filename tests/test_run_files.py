from dataclasses import replace

from pytuitor_web.curriculum import LESSONS
from pytuitor_web.models import Check
from pytuitor_web.runner import RunResult, execute
from pytuitor_web.workspace import MAX_FILE_BYTES, MAX_FILES, MAX_WORKSPACE_BYTES, validate_files


async def test_run_returns_generated_utf8_data_and_changed_source_without_changing_input():
    source = (
        "from pathlib import Path\n"
        "Path('reports').mkdir()\n"
        "Path('reports/résumé.txt').write_text('Hello, 🐍!\\n', encoding='utf-8')\n"
        "Path('lesson.py').write_text('# replaced by the running program\\n', encoding='utf-8')\n"
        "print('finished')\n"
    )
    original = {"lesson.py": source, "notes.txt": "Keep my notes"}
    result = await execute(LESSONS[0], source, files=original, check=False)
    assert not result.error
    assert result.output.strip() == "finished"
    assert result.files == {
        "lesson.py": "# replaced by the running program\n",
        "notes.txt": "Keep my notes",
        "reports/résumé.txt": "Hello, 🐍!\n",
    }
    assert original["lesson.py"] == source
    assert not result.files_notice


async def test_check_never_returns_its_fixtures():
    lesson = replace(
        LESSONS[0],
        checks=(Check("Works", "answer", 42, "Return 42."),),
        build_stage=None,
        repair_stage=None,
    )
    result = await execute(
        lesson,
        "from pathlib import Path\n"
        "Path('check-fixture.txt').write_text('temporary')\nanswer = 42\n",
    )
    assert result.passed
    assert result.files == {}
    assert result.files_notice == ""


async def test_run_ignores_symlink_files_and_directories(tmp_path):
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "private.txt").write_text("Do not include this file")
    source = (
        "from pathlib import Path\n"
        f"Path('linked-directory').symlink_to({str(outside)!r}, target_is_directory=True)\n"
        f"Path('linked-file.txt').symlink_to({str(outside / 'private.txt')!r})\n"
        "Path('report.txt').write_text('Safe result')\n"
    )
    result = await execute(LESSONS[0], source, check=False)
    assert not result.error
    assert result.files == {"lesson.py": source, "report.txt": "Safe result"}
    assert "symbolic links" in result.files_notice


async def test_run_omits_binary_oversized_and_special_files():
    source = (
        "from pathlib import Path\nimport os\n"
        "Path('binary.dat').write_bytes(b'\\xff\\x00\\x01')\n"
        f"Path('large.txt').write_text('x' * {MAX_FILE_BYTES + 1})\n"
        "if hasattr(os, 'mkfifo'): os.mkfifo('pipe')\n"
        "Path('report.txt').write_text('This file remains available')\n"
    )
    result = await execute(LESSONS[0], source, check=False)
    assert not result.error
    assert set(result.files) == {"lesson.py", "report.txt"}
    assert "binary files" in result.files_notice
    assert "oversized files" in result.files_notice
    import os

    if hasattr(os, "mkfifo"):
        assert "non-text file types" in result.files_notice


async def test_run_snapshot_obeys_file_count_and_total_bytes():
    source = (
        "from pathlib import Path\n"
        f"for index in range({MAX_FILES + 4}):\n"
        "    Path(f'file-{index}.txt').write_text('small')\n"
    )
    result = await execute(LESSONS[0], source, check=False)
    assert not result.error
    assert len(result.files) == MAX_FILES
    assert "file-count limit" in result.files_notice
    validate_files(result.files)

    source = (
        "from pathlib import Path\n"
        "for index in range(5):\n"
        f"    Path(f'large-{{index}}.txt').write_text('x' * {MAX_FILE_BYTES})\n"
    )
    result = await execute(LESSONS[0], source, check=False)
    assert not result.error
    assert sum(len(text.encode("utf-8")) for text in result.files.values()) <= MAX_WORKSPACE_BYTES
    assert "workspace limits" in result.files_notice
    validate_files(result.files)


async def test_generated_files_are_available_even_when_program_reports_an_error():
    source = (
        "from pathlib import Path\n"
        "Path('partial.txt').write_text('Useful partial result')\n"
        "raise ValueError('try again')\n"
    )
    result = await execute(LESSONS[0], source, check=False)
    assert "ValueError" in result.error
    assert result.files["partial.txt"] == "Useful partial result"


async def test_replaced_workspace_symlink_is_not_followed(tmp_path):
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "private.txt").write_text("Do not include this file")
    source = (
        "from pathlib import Path\nimport os, shutil\n"
        "os.chdir('..')\nshutil.rmtree('workspace')\n"
        f"Path('workspace').symlink_to({str(outside)!r}, target_is_directory=True)\n"
    )
    result = await execute(LESSONS[0], source, check=False)
    assert not result.error
    assert result.files == {}
    assert "symbolic link" in result.files_notice


def test_run_result_keeps_positional_compatibility_and_independent_defaults():
    result = RunResult("output", "error", [{"passed": False}])
    assert result.files == {}
    result.files["file.txt"] = "data"
    assert RunResult().files == {}
    assert result.files_notice == ""
