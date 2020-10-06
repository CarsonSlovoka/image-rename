from typing import Callable, List, Union, Tuple
from pathlib import Path


class Library:
    __slots__ = ('lib_name', 'hotkeys', 'panels', 'toolbars')
    """
    A class for registering template **hotkeys**.
    """

    def __init__(self, lib_name):
        self.lib_name = lib_name
        self.hotkeys = {}
        self.panels = {}
        self.toolbars = {}

    def __repr__(self):
        return self.lib_name

    def hotkey(self, key_list: Union[str, List[str]], name: str = None):
        return lambda func: self.hotkey_function(func, key_list, name)

    def hotkey_function(self, func: Callable, key_list, name):
        self.hotkeys[name if name else func.__name__] = func, key_list
        return func

    def panel(self, window_name: str, icon_path: Path = None):
        return lambda func: self.panel_function(func, window_name, icon_path)

    def panel_function(self, func: Callable, window_name, icon_path: Path):
        self.panels[window_name if window_name else func.__name__] = func, icon_path
        return func

    def toolbar(self, window_name: str, btn_img_list: List[Path],
                img_size: Tuple[int, int] = None, icon_path: Path = None):
        return lambda func: self.toolbar_function(func, window_name, btn_img_list, img_size, icon_path)

    def toolbar_function(self, func: Callable, window_name,
                         btn_img_list: List[Path], img_size, icon_path: Path):
        self.toolbars[window_name if window_name else func.__name__] = func, btn_img_list, img_size, icon_path
