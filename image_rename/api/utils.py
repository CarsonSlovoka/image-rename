from contextlib import contextmanager
from pathlib import Path
import os


@contextmanager
def work_dir(dir_path: Path):
    """
    Path('.') will change.
    """
    org_dir_path = Path(os.getcwd())
    os.chdir(dir_path)
    try:
        yield
    finally:
        os.chdir(org_dir_path)
