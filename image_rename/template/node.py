from typing import List, Dict, TypeVar, Callable, Type, Union
from image_rename.core import ImageRenameApp, RenameFactory, Event
from image_rename import APP_ICON_PATH
import functools
import inspect
import tkinter as tk
from pathlib import Path


class NodeList(list):
    def render(self, app: ImageRenameApp, target_type: Type):
        for node in self:
            if isinstance(node, Node):
                if target_type is None:
                    node.render(app)
                    continue
                if target_type.__name__ == node.__class__.__name__:
                    node.render(app)


class Node:
    __slots__ = ()
    token = None

    def render(self, context):
        raise NotImplementedError

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

    def render(self, app: ImageRenameApp):
        if not isinstance(self.key_list, list):
            self.key_list = [self.key_list]
        for key_name in self.key_list:
            if self.need_job_list:
                new_func = functools.wraps(self.func)(lambda tk_event:
                                                      self.func(app, getattr(RenameFactory.on_hotkey_event, 'dict_job', lambda: None)),
                                                      )
            else:
                new_func = functools.wraps(self.func)(lambda tk_event: self.func(app))
            app.root.bind(key_name, new_func)


class PanelNode(Node):
    __slots__ = ('token',
                 'window_name', 'func', 'icon_path')

    def __init__(self, window_name: str, func: Callable, icon_path: Path = None):
        self.window_name = window_name
        self.func = func
        self.icon_path = icon_path

    def render(self, app: RenameFactory):
        widget_name = '!toplevel_' + self.window_name
        window: Union[tk.Toplevel, None] = app.get_widget(widget_name, ignore_err_msg=True)
        if window:
            if window.wm_state() == 'withdrawn':  # If the window is hidden, then show it again.
                window.deiconify()
            return  # window already exists!

        parent = tk.Toplevel(app.root, name=widget_name)
        parent.title(self.window_name)
        parent.grid_columnconfigure(0, weight=1)  # expand and fill ({n e w s}) the first widget.
        parent.grid_rowconfigure(0, weight=1)
        if self.icon_path and self.icon_path.exists():
            parent.iconbitmap(self.icon_path)
        else:
            parent.iconbitmap(APP_ICON_PATH)
        args_list, *_others = inspect.getfullargspec(self.func)
        self.func(parent, app) if 'app' in args_list else self.func(parent)


class PanelBase:
    __slots__ = ('parent',)

    def __init__(self, parent):
        self.parent: tk.Toplevel = parent
        org_parent_update: Callable = self.parent.update
        self.parent.update = lambda event: self.update(event, org_parent_update)

    def update(self, event: Event, parent_update=None):
        parent_update()
