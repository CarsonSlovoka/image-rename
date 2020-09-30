from image_rename import template
from image_rename.template.node import PanelBase
from image_rename.core import ImageRenameApp, Event
import tkinter as tk
from tkinter import ttk
from pathlib import Path
from typing import Callable, Tuple
import os

register = template.Library(__name__)


@register.panel(
    window_name='History',
    # icon_path=Path(r"...")
)
def my_panel(parent: tk.Toplevel, app: ImageRenameApp):
    return HistoryPanel(parent, app).build()  # Class must inherit PanelBase. Otherwise, update will not working.


class HistoryPanel(PanelBase, tk.Frame):
    __slots__ = ('tree', 'parent', 'app')

    def __init__(self, parent: tk.Toplevel, app: ImageRenameApp, top_n=5):
        super().__init__(parent)
        self.parent = parent
        self.app = app
        self.tree = ttk.Treeview(self.parent,
                                 show='headings',  # ignore the index column
                                 columns=('name', 'image_path'),
                                 height=top_n  # numbers of row
                                 )  # https://docs.python.org/3/library/tkinter.ttk.html
        # self.tree['columns'] = ('image_path',)

    def build(self):
        self.tree.column("name", width=30, anchor='e')
        self.tree.heading("name", text="File Name")

        self.tree.column("image_path", width=1000)
        self.tree.heading("image_path", text="image path")
        self.tree.bind('<Double-Button>', self.select_item)  # https://www.python-course.eu/tkinter_events_binds.php
        self.tree.grid()

    def update(self, event: Event, parent_update: Callable = None):
        # parent_update()

        if event != Event.IMG_CHANGE:
            return

        previous_info: Tuple[Path, Path] = self.app.widget_info.previous_info
        if previous_info:
            org_img_path, new_file_path = previous_info

            tuple_children: Tuple[str] = self.tree.get_children()
            item_id: str = tuple_children[0] if tuple_children else None
            if item_id:
                # dict_data: dict = self.tree.item(item_id)
                # values: list = self.tree.item(item_id, option='values')
                # https://blog.csdn.net/weixin_42272768/article/details/100915973
                self.tree.item(item_id, values=(new_file_path.name, new_file_path.absolute()))

        cur_img_path = self.app.widget_info.cur_img_path
        # self.tree.insert("", "end", text=cur_img_path.name, values=(cur_img_path.absolute(),))
        self.tree.insert("", 0, text=cur_img_path.name, values=(cur_img_path.name, cur_img_path.absolute()))

    def select_item(self, event):
        # cur_item: dict = self.tree.item(self.tree.focus())
        img_name, img_path = self.tree.item(self.tree.focus(), option='values')
        img_path = Path(img_path)
        os.startfile(img_path.parent)

        """
        col: str = self.tree.identify_column(event.x)    
        cell_value: str = cur_item['text'] if col == '#0' else \
            cur_item['values'][0] if col == '#1' else \
            cur_item['values'][1] if col == '#2' else ''        
        print('cell_value = ', cell_value)
        """

