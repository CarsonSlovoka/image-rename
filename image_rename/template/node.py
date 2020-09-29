from typing import List, Dict, TypeVar, Callable
from image_rename.core import RenameFactory
import functools
import abc


class NodeList(list):
    def render(self, target: RenameFactory):
        for node in self:
            if isinstance(node, Node):
                node.render(target)


class Node(abc.ABC):
    __slots__ = ()
    token = None

    @abc.abstractmethod
    def render(self, context):
        ...

    def __iter__(self):
        yield self


T_Node = TypeVar('T_Node', bound=Node)


class HotkeyNode(Node):
    __slots__ = ('token',
                 'name', 'func', 'key_list',
                 'need_job_list')

    def __init__(self, name: str, func: Callable, key_list: List[str], need_job_list: bool):
        self.name = name
        self.func = func
        self.key_list = key_list
        self.need_job_list = need_job_list

    def render(self, target: RenameFactory):
        if not isinstance(self.key_list, list):
            self.key_list = [self.key_list]
        for key_name in self.key_list:
            if self.need_job_list:
                new_func = functools.wraps(self.func)(lambda tk_event:
                                                      self.func(target, getattr(RenameFactory.on_hotkey_event, 'dict_job', lambda: None)),
                                                      )
            else:
                new_func = functools.wraps(self.func)(lambda tk_event: self.func(target))
            target.root.bind(key_name, new_func)


class PanelNode(Node):
    def __init__(self, name: str, func: Callable):
        self.name = name
        self.func = func

    def render(self, target: RenameFactory):
        ...
