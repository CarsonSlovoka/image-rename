import image_rename
from image_rename import template
from image_rename.template.node import PanelBase
from image_rename.core import ImageRenameApp, Event
from image_rename.api.tkmixins import TreeMixin
import tkinter as tk
from tkinter.font import Font
from tkinter import ttk
from pathlib import Path
from typing import Callable, Tuple, NamedTuple, Union
import os
import re

register = template.Library(__name__)


@register.panel(
    window_name='History',
    icon_path=Path(image_rename.__file__).parent / Path('asset/icon/history.ico')  # if icon_path is None, then its icon is from the parent.
)
def history_panel(parent: tk.Toplevel, app: ImageRenameApp):
    return HistoryPanel(parent, app).build()  # Class must inherit PanelBase. Otherwise, update will not working.


class HistoryPanel(PanelBase, TreeMixin):
    __slots__ = ('tree', 'parent', 'app',
                 'regex',)

    class Header(NamedTuple):
        name = 'file_name'
        image_path = 'image_path'

        def to_tuple(self) -> Tuple[str, str]:
            return self.name, self.image_path

        def __getitem__(self, item: int):
            return self.to_tuple()[item]

        def __iter__(self):
            for val in self.to_tuple():
                yield val

    header = Header()

    def __init__(self, parent: tk.Toplevel, app: ImageRenameApp, top_n=None):
        super().__init__(parent)
        # self.header = self.Header()
        self.parent = parent
        self.app = app
        self.tree = ttk.Treeview(self.parent,
                                 show='headings',  # ignore the index column
                                 columns=self.header.to_tuple(),
                                 height=top_n  # numbers of row
                                 )  # https://docs.python.org/3/library/tkinter.ttk.html
        # self.tree['columns'] = ('image_path',)
        self.parent.protocol("WM_DELETE_WINDOW", lambda: self.parent.withdraw())  # hide window
        self.regex = re.compile(r"(?P<width>[0-9]+)x(?P<height>[0-9]+)\+(?P<xoffset>[0-9]+)\+(?P<offset_y>[0-9]+)")  # search 123*1+22+333

    def build(self):
        for col in self.header:
            text = col.replace('_', ' ').title()  # uppercase
            self.tree.heading(col, text=text, command=lambda col_name=col: self.sort_by(col_name, is_descending=False))
            # self.tree.column("name", width=150, anchor='e')
            self.tree.column(col, width=Font().measure(text))

        self.tree.bind('<Double-Button>', self.select_item)  # https://www.python-course.eu/tkinter_events_binds.php
        self.tree.grid(sticky='news')
        self.build_scrollbar(self.parent)

        offset_x, offset_y = [int(_) for _ in self.app.root.geometry().split('+')[1:]]
        offset_y += self.parent.winfo_height() + 300
        self.parent.geometry(f'+{offset_x}+{offset_y}')

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
                for row_data in [(new_file_path.name, new_file_path.absolute())]:
                    self.tree.item(item_id, values=row_data)
                    self.adjust_column(row_data)

        cur_img_path = self.app.widget_info.cur_img_path
        # self.tree.insert("", "end", text=cur_img_path.name, values=(cur_img_path.absolute(),))
        for row_data in [(cur_img_path.name, cur_img_path.absolute())]:
            self.tree.insert("", 0, text=cur_img_path.name, values=row_data)
            self.adjust_column(row_data)

        cur_width = sum([self.tree.column(header_name)['width'] for header_name in self.header.to_tuple()])
        width, height, x_offset, y_offset = self.regex.match(self.parent.geometry()).groups()  # groupdict()
        self.parent.geometry(f'{cur_width}x{height}+{x_offset}+{y_offset}')

    def select_item(self, event):
        # cur_item: dict = self.tree.item(self.tree.focus())  # cur_item['text'] 'values'
        query_item: Union[Tuple, str] = self.tree.item(self.tree.focus(), option='values')
        if query_item == '':
            return
        img_name, img_path = query_item
        img_path = Path(img_path)
        col: str = self.tree.identify_column(event.x)

        os.startfile(img_path.parent) if col == '#1' else \
            os.startfile(img_path) if col == '#2' else ''
