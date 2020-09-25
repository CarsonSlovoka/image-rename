from typing import Callable, List


class Library:
    __slots__ = ('lib_name', 'hotkeys',)
    """
    A class for registering template **hotkeys**.
    """

    def __init__(self, lib_name):
        self.lib_name = lib_name
        self.hotkeys = {}

    def __repr__(self):
        return self.lib_name

    def hotkey(self, key_list: List[str], name=None):
        return lambda func: self.hotkey_function(func, key_list, name)

    def hotkey_function(self, func: Callable, key_list, name):
        self.hotkeys[name if name else func.__name__] = func, key_list
        return func
