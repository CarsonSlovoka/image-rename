from typing import List, Dict, TypeVar, Callable, Type, Union, Tuple
from image_rename.core import ImageRenameApp, RenameFactory, Event
from image_rename import APP_ICON_PATH
from image_rename.api.tkmixins import TkMixin, TkImageMixin
import functools
import inspect
import tkinter as tk
from pathlib import Path
import cv2
from PIL import Image, ImageTk
import numpy as  np


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
    __slots__ = ('token',)

    def render(self, context):
        raise NotImplementedError

    def __iter__(self):
        yield self


T_Node = TypeVar('T_Node', bound=Node)


class HotkeyNode(Node):
    __slots__ = ('name', 'func', 'key_list',
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
                                                      self.func(app, getattr(RenameFactory.on_hotkey_event, 'dict_job',
                                                                             lambda: None)),
                                                      )
            else:
                new_func = functools.wraps(self.func)(lambda tk_event: self.func(app))
            app.root.bind(key_name, new_func)


class TopWindow(TkMixin):
    __slots__ = ('window', 'is_exists')

    def __init__(self, parent: tk.Tk, window_name: str, name: str, icon_path: Path = None):
        window: Union[tk.Toplevel, None] = self.get_widget(name, ignore_err_msg=True, root=parent)
        if window:
            if window.wm_state() == 'withdrawn':  # If the window is hidden, then show it again.
                window.deiconify()
            self.window = window
            self.is_exists = True
            return  # window already exists!

        window = tk.Toplevel(parent, name=name)
        window.title(window_name)

        # We let the first widget can expand and fill. If you have many widgets, you can build a Frame and contains all the widgets.
        window.grid_columnconfigure(0, weight=1)  # expand and fill ({n e w s}) the first widget.
        window.grid_rowconfigure(0, weight=1)
        if icon_path and icon_path.exists():
            window.iconbitmap(icon_path)
        else:
            window.iconbitmap(APP_ICON_PATH)
        self.window = window
        self.is_exists = False


class PanelNode(Node):
    __slots__ = ('window_name', 'func', 'icon_path')

    def __init__(self, window_name: str, func: Callable, icon_path: Path = None):
        self.window_name = window_name
        self.func = func
        self.icon_path = icon_path

    def render(self, app: ImageRenameApp):
        win = TopWindow(app.root, self.window_name, f'!panel_{self.window_name}', self.icon_path)
        if win.is_exists:
            return
        window: tk.Toplevel = win.window
        args_list, *_others = inspect.getfullargspec(self.func)
        self.func(window, app) if 'app' in args_list else self.func(window)


class PanelBase:
    __slots__ = ('parent',)

    def __init__(self, parent):
        self.parent: tk.Toplevel = parent
        org_parent_update: Callable = self.parent.update
        self.parent.update = lambda event: self.update(event, org_parent_update)

    def update(self, event: Event, parent_update=None):
        parent_update()


class ToolbarNode(Node, TkImageMixin):
    __slots__ = ('window_name', 'func', 'btn_img_list', 'img_size', 'icon_path')

    def __init__(self, window_name: str, func: Callable, btn_img_list: List[Path],
                 img_size: Tuple[int, int], icon_path: Path):
        self.window_name = window_name
        self.func = func
        self.btn_img_list = btn_img_list
        self.img_size = img_size
        self.icon_path = icon_path

    def render(self, app: ImageRenameApp):
        win = TopWindow(app.root, self.window_name, f'!toolbar_{self.window_name}', self.icon_path)
        if win.is_exists:
            return
        window: tk.Toplevel = win.window
        photo_list: List[tk.PhotoImage] = []
        for img_path in self.btn_img_list:
            if not img_path.exists() or not img_path.is_file():
                FileNotFoundError(img_path)

            if self.img_size is not None:
                photo: ImageTk.PhotoImage = self.resize(img_path, self.img_size, name=f'PhotoImage-{img_path.stem}')
                photo.name = f'PhotoImage-{img_path.stem}'
            else:
                photo = tk.PhotoImage(name=f'PhotoImage-{img_path.stem}', file=img_path)
            photo_list.append(photo)

        cmd_list = [lambda: None for _ in range(len(photo_list))]
        self.func(app, window, photo_list, cmd_list)


class ToolbarBase:
    __slots__ = ('app', 'parent', 'photo_list', 'cmd_list')

    IMG_PER_ROW: int = 1
    BTN_SIZE = 50, 20

    def __init__(self, app, parent, photo_list, cmd_list):
        self.app: ImageRenameApp = app
        self.parent: tk.Toplevel = parent
        self.photo_list: List[tk.PhotoImage] = photo_list
        self.cmd_list: List[Callable] = cmd_list

    def init_buttons(self):
        btn_w, btn_h = self.BTN_SIZE
        row, col = 0, 0
        for idx, (photo, cmd) in enumerate(zip(self.photo_list, self.cmd_list)):
            idx += 1
            # photo.name, photo.width(), photo.height()
            # http://effbot.org/pyfaq/why-do-my-tkinter-images-not-appear.htm
            # tk.Button(parent, text='condition', image=photo, compound=tk.LEFT).pack()
            btn = tk.Button(self.parent, text='condition', image=photo, command=cmd, width=btn_w, height=btn_h)
            btn.image = photo  # keep a reference!
            btn.grid(row=row, column=col, sticky=tk.NSEW)
            if idx % (self.IMG_PER_ROW + 1) == 0:
                row += 1
                col = 0
            else:
                col += 1
