from typing import List, Dict, TypeVar, Callable
from image_rename.template.exceptions import HotkeyConflictWarning
import warnings
from enum import Enum
from image_rename.core import RenameFactory
from .library import Library
from .node import (
    NodeList, T_Node,
    HotkeyNode, PanelNode,
)
import inspect


class TokenType(Enum):
    HotKey = 0
    Panel = 1


class Token:
    __slots__ = ('token_type',)

    def __init__(self, token_type):
        self.token_type: TokenType = token_type

    def __repr__(self):
        return f"<Token ({self.token_type.name}>"


class Template:
    __slots__ = ('target', 'engine', 'nodelist')

    def __init__(self, target: RenameFactory, engine=None):
        from .engine import Engine
        self.target: RenameFactory = target
        self.engine = Engine() if engine is None else engine
        self.nodelist: NodeList = self.compile_nodelist()

    def render(self):
        self.nodelist.render(self.target)

    def compile_nodelist(self) -> NodeList:
        parser = Parser(self.engine.template_builtins)
        nodelist = parser.parse()
        return nodelist


class Parser:
    __slots__ = ('hotkeys', 'panels')

    def __init__(self, builtins=None, ):
        self.hotkeys, self.panels = self.init_library(builtins if builtins else [])

    @staticmethod
    def init_library(lib_list: List[Library]) -> List[Dict]:
        dict_hotkeys = {}
        dict_panels = {}
        for lib in lib_list:
            for cur_key, (func, key_list) in lib.hotkeys.items():
                if cur_key in dict_hotkeys:
                    warnings.warn(f'{lib!r} {cur_key}: {func.__name__} --> {dict_hotkeys[cur_key][0].__name__}', HotkeyConflictWarning, stacklevel=2)
            dict_hotkeys.update(lib.hotkeys)
            dict_panels.update(lib.panels)
        return [dict_hotkeys, dict_panels]

    def parse(self) -> NodeList:
        nodelist = NodeList()
        for name, (func, key_list) in self.hotkeys.items():
            args_list, *_others = inspect.getfullargspec(func)
            need_job_list = True if 'dict_job' in args_list else False
            self.extend_nodelist(nodelist, HotkeyNode(name, func, key_list, need_job_list), Token(TokenType.HotKey))

        for name, func in self.panels.items():
            self.extend_nodelist(nodelist, PanelNode(name, func), Token(TokenType.Panel))
        return nodelist

    @staticmethod
    def extend_nodelist(nodelist: NodeList, node: T_Node, token: Token):
        # Set origin and token here since we can't modify the node __init__() method.
        node.token = token
        nodelist.append(node)
