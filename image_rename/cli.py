import asyncio
import importlib
import importlib.machinery
from pathlib import Path

from .core import ImageRenameApp
from .api.utils import work_dir

from typing import Any
import types


def main(input_setting_path=None):
    import inspect
    from argparse import ArgumentParser
    if input_setting_path is None:
        arg_parser = ArgumentParser()
        arg_parser.add_argument("--setting", '-config', dest='setting', type=Path, help="path of setting.py", default=Path(__file__).parent / Path('config.py'))
        args = arg_parser.parse_args()
    else:
        args = types.SimpleNamespace(**dict(setting=input_setting_path))
        if not isinstance(args.setting, Path):
            raise RuntimeError

    with work_dir(args.setting.parent):
        loader = importlib.machinery.SourceFileLoader('setting', args.setting.name)
        config = setting_module = types.ModuleType(loader.name)  # type: Any
        loader.exec_module(setting_module)

        # Solve the problem of the relative path.
        [setattr(setting_module, member_name, str(member.resolve())) for member_name, member in inspect.getmembers(setting_module) if not member_name.startswith('_') and isinstance(member, Path)]

        loop = asyncio.get_event_loop()
        app = ImageRenameApp(loop, config.img_path_list)
        app.run()


if __name__ == '__main__':
    main()
