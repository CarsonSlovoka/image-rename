from typing import List, Dict, TypeVar, Callable
from image_rename.template.exceptions import HotkeyConflictWarning
import warnings
import abc
from enum import Enum
from image_rename.core import RenameFactory
import functools


class TokenType(Enum):
    HotKey = 0


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

    def compile_nodelist(self) -> 'NodeList':
        parser = Parser(self.engine.template_builtins)
        nodelist = parser.parse()
        return nodelist


class Parser:
    __slots__ = ('hotkeys',)

    def __init__(self, builtins=None, ):
        self.hotkeys = self.init_library(builtins if builtins else [])

    @staticmethod
    def init_library(lib_list: List) -> Dict:
        dict_hotkeys = {}
        for lib in lib_list:
            for cur_key, (func, key_list) in lib.hotkeys.items():
                if cur_key in dict_hotkeys:
                    warnings.warn(f'{lib!r} {cur_key}: {func.__name__} --> {dict_hotkeys[cur_key][0].__name__}', HotkeyConflictWarning, stacklevel=2)
            dict_hotkeys.update(lib.hotkeys)
        return dict_hotkeys

    def parse(self) -> "NodeList":
        nodelist = NodeList()
        for name, (func, key_list) in self.hotkeys.items():
            self.extend_nodelist(nodelist, HotkeyNode(name, func, key_list), Token(TokenType.HotKey))
        return nodelist

    @staticmethod
    def extend_nodelist(nodelist: "NodeList", node: "T_Node", token: Token):
        # Set origin and token here since we can't modify the node __init__() method.
        node.token = token
        nodelist.append(node)


class Node(abc.ABC):
    __slots__ = ()
    token = None

    @abc.abstractmethod
    def render(self, context):
        ...

    def __iter__(self):
        yield self


class HotkeyNode(Node):
    __slots__ = ('token',
                 'name', 'func', 'key_list')

    def __init__(self, name: str, func: Callable, key_list: List[str]):
        self.name = name
        self.func = func
        self.key_list = key_list

    def render(self, target: RenameFactory):
        for key_name in self.key_list:
            new_func = functools.wraps(self.func)(lambda tk_event: self.func(target))
            target.root.bind(key_name, new_func)


T_Node = TypeVar('T_Node', bound=Node)


class NodeList(list):
    def render(self, target: RenameFactory):
        for node in self:
            if isinstance(node, Node):
                node.render(target)
