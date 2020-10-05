from tkinter import ttk
import tkinter as tk
from typing import Tuple, NamedTuple, Union
from tkinter.font import Font


class TkMixin:
    __slots__ = ()

    def get_widget(self, widget_name: str, ignore_err_msg=False) -> Union[tk.Widget, None]:
        root: tk.Tk = getattr(self, 'root')
        if root.children.get(widget_name):
            return root.children[widget_name]
        else:
            print(f'{KeyError(widget_name)}') if ignore_err_msg else None
            return None


class TreeMixin:
    __slots__ = ()

    header: NamedTuple
    tree: ttk.Treeview

    def build_scrollbar(self, parent):
        vsb = ttk.Scrollbar(parent, orient='vertical', command=self.tree.yview)
        hsb = ttk.Scrollbar(parent, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.configure(xscrollcommand=hsb.set)
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')

    def adjust_column(self, row_data: Tuple):
        """
        Decide the width of each column by the maximum string.
        """
        for idx, col_string in enumerate(row_data):
            col_width = Font().measure(col_string)
            if col_width > self.tree.column(self.header[idx], width=None):
                self.tree.column(self.header[idx], width=col_width)

    def sort_by(self, col_name: str, is_descending: bool):
        data_list = [(self.tree.set(child_id, col_name), child_id) for child_id in self.tree.get_children('')]
        data_list.sort(reverse=is_descending)
        for new_idx, (item_name, item_id) in enumerate(data_list):
            self.tree.move(item_id, '', new_idx)

        # switch the heading so it will sort in the opposite direction
        self.tree.heading(col_name, command=lambda col=col_name: self.sort_by(col, (not is_descending)))
