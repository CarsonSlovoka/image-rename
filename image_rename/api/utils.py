from contextlib import contextmanager
from pathlib import Path
import os
from typing import Callable


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


@contextmanager
def after_end(cb_fun: Callable):
    """
    with after_end(cb_fun) as cb_fun:
        ...

    with after_end(cb_fun=lambda: shutil.rmtree(temp_dir)) as _:  # make sure the temp_dir will remove after finished.
        ...

    with after_end(cb_fun=lambda: [os.remove(file) for file in [_ for _ in work_dir.glob('*.*') if _.suffix[1:] in ('html',)]]) as _
        ...
    """
    try:
        yield cb_fun
    finally:
        cb_fun()
