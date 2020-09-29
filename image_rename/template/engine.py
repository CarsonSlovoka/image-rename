import importlib
from .exceptions import (
    InvalidTemplateLibrary,
)
from typing import List
from types import ModuleType
from pathlib import Path
import importlib.machinery
from image_rename.api.utils import work_dir


class Engine:
    __slots__ = ('dirs', 'template_builtins', 'file_charset')

    default_builtins = [
        Path(__file__).parent.parent / Path('template/plugins/default_hotkeys.py'),
    ]

    def __init__(self, builtins: List[Path] = None,):
        builtins = (builtins if builtins else []) + self.default_builtins
        self.template_builtins: List[ModuleType] = self.get_template_builtins(builtins)

    @staticmethod
    def get_template_builtins(builtin_list):
        rtn_list: List[ModuleType] = []
        for module_path in builtin_list:
            try:
                with work_dir(module_path.parent):
                    loader = importlib.machinery.SourceFileLoader(f'module:{module_path.absolute()}', module_path.name)
                    plugin_module = ModuleType(loader.name)  # type: Any
                    loader.exec_module(plugin_module)
            except ImportError as e:
                raise InvalidTemplateLibrary(f'Invalid template library specified. ImportError raised when'
                                             f'trying to load {module_path}: {e}')
            if not hasattr(plugin_module, 'register'):
                raise InvalidTemplateLibrary(f'There is no attribute `register` on your module: {plugin_module}')
            rtn_list.append(getattr(plugin_module, 'register'))
        return rtn_list
