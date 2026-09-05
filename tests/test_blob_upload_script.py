import subprocess
import sys
from pathlib import Path


def test_blob_upload_script_runs_directly_from_script_directory():
    repo_root = Path(__file__).resolve().parents[1]
    script_path = repo_root / "backend" / "scripts" / "test_blob_upload.py"
    cwd = script_path.parent

    result = subprocess.run(
        [sys.executable, str(script_path)],
        cwd=str(cwd),
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr or result.stdout
