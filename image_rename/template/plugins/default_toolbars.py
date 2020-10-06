from image_rename import template
from image_rename import (
    ImageRenameApp,
    ToolbarBase, PanelNode,
    __version__,
)
import tkinter as tk
from pathlib import Path
from typing import Callable, Tuple, NamedTuple, Union, List
import image_rename
from subprocess import Popen, PIPE, DEVNULL
from tkinter.messagebox import showinfo

register = template.Library(__name__)


@register.toolbar(
    'My Toolbar',
    btn_img_list=[Path(image_rename.__file__).parent / Path('asset/icon/paint.png'),
                  Path(image_rename.__file__).parent / Path('asset/icon/panel.png'),
                  Path(image_rename.__file__).parent / Path('asset/icon/info.png'),
                  ],
    img_size=(48, 48),  # If assigned, then all the photo has the same size. Otherwise, it will not change the size.
    icon_path=Path(image_rename.__file__).parent / Path('asset/icon/toolbar.ico'))  # if icon_path is None, then its icon is from the parent.
def my_toolbar(app: ImageRenameApp,
               parent: tk.Toplevel, photo_list: List[tk.PhotoImage], cmd_list: List[Callable]):
    return MainToolBar(app, parent, photo_list, cmd_list).build()


class MainToolBar(ToolbarBase):
    __slots__ = ()
    IMG_PER_ROW: int = 2
    BTN_SIZE = (100, 50)

    def open_ms_paint(self):
        job = Popen(['mspaint', str(self.app.widget_info.cur_img_path)], stdout=PIPE, stderr=PIPE, stdin=DEVNULL)
        job.communicate()  # waiting for the job done.
        self.app.refresh_window()
        # app.next_img_flag = True

    def render_all_panel(self):
        self.app.template.render(target_type=PanelNode)

    def build(self):
        self.cmd_list[0] = self.open_ms_paint
        self.cmd_list[1] = self.render_all_panel
        self.cmd_list[2] = lambda: showinfo('App Version', __version__)
        self.init_buttons()
