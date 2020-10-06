from typing import List, Dict, TypeVar, Callable, Type
from image_rename.template.exceptions import (
    HotkeyConflictWarning, PanelConflictWarning, ToolbarConflictWarning
)
import warnings
from enum import Enum
from image_rename.core import ImageRenameApp
from .library import Library
from .node import (
    NodeList, T_Node,
    HotkeyNode, PanelNode, ToolbarNode,
)
import inspect


class TokenType(Enum):
    __slots__ = ()
    Hotkey = 0
    Panel = 1
    Toolbar = 2


class Token:
    __slots__ = ('token_type',)

    def __init__(self, token_type):
        self.token_type: TokenType = token_type

    def __repr__(self):
        return f"<Token ({self.token_type.name}>"


class Template:
    __slots__ = ('app', 'engine', 'nodelist')

    def __init__(self, app: ImageRenameApp, engine=None):
        from .engine import Engine
        self.app: ImageRenameApp = app
        self.engine = Engine() if engine is None else engine
        self.nodelist: NodeList = self.compile_nodelist()

    def render(self, target_type: Type = None):
        self.nodelist.render(self.app, target_type)

    def compile_nodelist(self) -> NodeList:
        parser = Parser(self.engine.template_builtins)
        nodelist = parser.parse()
        return nodelist


class Parser:
    __slots__ = ('hotkeys', 'panels', 'toolbars')

    def __init__(self, builtins=None, ):
        self.hotkeys, self.panels, self.toolbars = self.init_library(builtins if builtins else [])  # type: Dict

    @staticmethod
    def check_conflict(lib: Library, lib_dict: Dict, target_dict: Dict, warning_class: Type[Warning]):
        for key, func, *_ in lib_dict.items():
            if key in target_dict:
                warnings.warn(f'{lib!r} {key}: {func.__name__} --> {target_dict[key][0].__name__}', warning_class, stacklevel=2)

    def init_library(self, lib_list: List[Library]) -> List[Dict]:
        dict_hotkeys = {}
        dict_panels = {}
        dict_toolbars = {}
        for lib in lib_list:
            self.check_conflict(lib, lib.hotkeys, dict_hotkeys, HotkeyConflictWarning)
            dict_hotkeys.update(lib.hotkeys)

            self.check_conflict(lib, lib.panels, dict_panels, PanelConflictWarning)
            dict_panels.update(lib.panels)

            self.check_conflict(lib, lib.toolbars, dict_toolbars, ToolbarConflictWarning)
            dict_toolbars.update(lib.toolbars)
        return [dict_hotkeys, dict_panels, dict_toolbars]

    def parse(self) -> NodeList:
        nodelist = NodeList()
        for name, (func, key_list) in self.hotkeys.items():
            args_list, *_others = inspect.getfullargspec(func)
            need_job_list = True if 'dict_job' in args_list else False
            self.extend_nodelist(nodelist, HotkeyNode(name, func, key_list, need_job_list), Token(TokenType.Hotkey))

        for window_name, (func, icon_path) in self.panels.items():
            self.extend_nodelist(nodelist, PanelNode(window_name, func, icon_path), Token(TokenType.Panel))

        for window_name, (func, btn_img_list, img_size, icon_path) in self.toolbars.items():
            self.extend_nodelist(nodelist, ToolbarNode(window_name, func, btn_img_list,
                                                       img_size, icon_path), Token(TokenType.Toolbar))
        return nodelist

    @staticmethod
    def extend_nodelist(nodelist: NodeList, node: T_Node, token: Token):
        # Set origin and token here since we can't modify the node __init__() method.
        node.token = token
        nodelist.append(node)
