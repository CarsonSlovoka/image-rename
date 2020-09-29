import tkinter as tk
from typing import Union, List, Dict, Tuple, Callable, Any
from pathlib import Path
from grid_extractor import show_img
from .api.imagehelper import append_image_to_news
import cv2
import numpy as np
import asyncio
import os
import types
from dataclasses import dataclass, field
from enum import Enum


def imread(file, flag=cv2.IMREAD_UNCHANGED):
    """
    To fix the problem of the path contains Chinese.
    :param file: Path or str
    :param flag:
    """
    if not Path(file).exists():
        raise FileNotFoundError(f"{file}")
    if isinstance(file, Path):
        file = str(file)
    np_img = cv2.imdecode(np.fromfile(file, dtype=np.uint8), flag)
    return np_img


class TkMixin:
    __slots__ = ()

    def get_widget(self, widget_name: str) -> Union[tk.Widget, None]:
        root: tk.Tk = getattr(self, 'root')
        if root.children.get(widget_name):
            return root.children[widget_name]
        else:
            print(f'{KeyError(widget_name)}')
            return None


class EditBoxBase:
    __slots__ = ('root', 'canvas', 'entry')

    FONT_NAME = 'helvetica'

    def __init__(self, width=400, height=500, **options):
        self.root = root = tk.Tk()
        self.canvas = tk.Canvas(root, width=width, height=height, relief='raised')
        self.entry = self.init_ui()

    def put2canvas(self, widget: tk.Widget, x, y):
        self.canvas.create_window(x, y, window=widget)

    def init_ui(self) -> tk.Entry:
        raise NotImplementedError('init_ui')

    def on_click_commit(self, e: tk.Event):
        raise NotImplementedError('on_click_commit')


class Event(Enum):
    NONE = -1
    IMG_CHANGE = 0


class JobState(Enum):
    ONCE = 0
    FOREVER = 1


class RenameFactory(EditBoxBase, TkMixin):
    __slots__ = ('img_path_list', '_next_img_flag',
                 'config', 'widget_info')

    ILLEGAL_CHARS = ('\\', '/', '?', '*', '<', '>', '|')  # These characters is not acceptable for the filename.
    FINISHED_MSG = 'FINISHED'
    IMG_WINDOW_NAME = 'demo'

    @dataclass(repr=False, eq=False)
    class WidgetInfo:
        cur_img_path: Path = field(init=False, default=None)
        previous_img_path: Path = field(init=False, default=None)
        previous_info: Path = field(init=False, default=None)
        entry: tk.Entry = field(init=False, default=None)

    def __init__(self, img_path_list: List[Path], config: types.SimpleNamespace, **options):
        self.img_path_list = img_path_list

        self.config = config
        self.widget_info = self.WidgetInfo()
        self._next_img_flag = False
        EditBoxBase.__init__(self, **options)
        self.__class__.on_hotkey_event.dict_job = dict()

    def init_ui(self):
        self.root.iconbitmap(Path(__file__).parent / Path('asset/icon/main.ico'))
        self.root.title('Rename Tool')

        self.canvas.pack()
        label_title = tk.Label(self.root, text='Rename Tool',
                               font=(self.FONT_NAME, 48), bg='black', fg='white')
        self.put2canvas(label_title, 200, 25)

        label_input_info = tk.Label(self.root, text='New file name:')
        label_input_info.config(font=(self.FONT_NAME, 18))
        self.put2canvas(label_input_info, 200, 100)

        entry = tk.Entry(self.root, name='entry_new_name')
        entry.config(font=(self.FONT_NAME, 18), fg='blue', width=16)
        entry.focus_set()
        self.widget_info.entry = entry
        self.put2canvas(entry, 200, 140)
        if hasattr(self.config, 'dict_hotkey') and isinstance(self.config.dict_hotkey, dict):
            dict_hotkey: Dict = self.config.dict_hotkey
            for key_name in dict_hotkey.get('commit', []):
                # self.root.bind('<Return>', self.on_click_commit)
                self.root.bind(key_name, self.on_click_commit)
            for key_name in dict_hotkey.get('skip', []):
                self.root.bind(key_name, self.on_click_skip)

            for hotkey_name in ('insert_file_name', 'insert_previous'):
                for key_name in dict_hotkey.get(hotkey_name):
                    event_func: Callable[[RenameFactory], Tuple] = getattr(self, f'on_hotkey_{hotkey_name}', None)
                    if event_func:
                        self.root.bind(key_name, event_func)

        self.put2canvas(tk.Button(text='Commit', command=lambda: self.on_click_commit(None),
                                  width=20,
                                  bg='brown', fg='white', font=(self.FONT_NAME, 12, 'bold')),
                        200, 180)
        self.put2canvas(tk.Button(text='Skip', command=lambda: self.on_click_skip(None),
                                  bg='brown', fg='white', font=(self.FONT_NAME, 12, 'bold')),
                        310, 180)
        self.put2canvas(tk.Label(self.root, name='label_error_msg', text='', font=(self.FONT_NAME, 12, 'italic'), fg='red'),
                        200, 220)

        self.put2canvas(tk.Label(self.root, name='label_abs_img_path', text='', font=(self.FONT_NAME, 12)),
                        40, 300)
        self.put2canvas(
            tk.Button(text='Open Source Folder', name='btn_open_source_dir',
                      bg='brown', fg='white', font=(self.FONT_NAME, 12, 'bold'),
                      command=lambda: self.on_click_open_source_dir(None)),
            200, 350)
        return entry

    def update_ui(self, widget_name, **options) -> tk.Widget:
        """

        :param widget_name::
                - label_abs_img_path
                - label_error_msg
        :param options:: dict(text='...')
        """
        widget = self.get_widget(widget_name)
        if widget:
            widget.config(**options)
            return widget

    async def main(self, interval: float):
        if len(self.img_path_list) == 0:
            print('empty img_path_list')
            return
        window_size: Tuple[int, int] = getattr(self.config, 'window_size', None)
        display_n_img = getattr(self.config, 'display_n_img', 1)
        highlight_color: Tuple[int, int, int] = getattr(self.config, 'highlight_color', None)
        border_thickness: int = getattr(self.config, 'border_thickness', 1)
        n_total_img = len(self.img_path_list)
        for idx, img_path in enumerate(self.img_path_list):
            img_display = imread(img_path)
            show_flag = True
            self._next_img_flag = False
            is_first_show = True
            while await asyncio.sleep(interval, True):
                if (cv2.getWindowProperty(self.IMG_WINDOW_NAME, cv2.WND_PROP_FULLSCREEN) == -1  # If the user closed the window, then show it again.
                        or show_flag):
                    img_cur = imread(img_path)
                    if display_n_img > 1:
                        if img_cur.ndim == 2 or img_cur.shape[-1] == 1:
                            img_cur = cv2.cvtColor(img_cur, cv2.COLOR_GRAY2RGBA)
                        if highlight_color is not None:
                            img_cur = cv2.copyMakeBorder(img_cur,
                                                         border_thickness, border_thickness, border_thickness, border_thickness,
                                                         cv2.BORDER_CONSTANT, value=highlight_color)
                    img_display: np.ndarray = img_cur if display_n_img == 1 else \
                        append_image_to_news(img_cur,
                                             [imread(_) for _ in
                                              self.img_path_list[idx + 1:min(idx + display_n_img, n_total_img)] if idx + 1 < n_total_img],
                                             direction='r')
                    show_img(img_display, window_name=self.IMG_WINDOW_NAME,
                             window_size=window_size if window_size is not None else -1,
                             delay_time=1)

                    if is_first_show:
                        self.update_ui('label_abs_img_path', text=f'{str(img_path.resolve())[-50:]}')
                        self.widget_info.cur_img_path = img_path
                        if hasattr(self.config, 'default_name_flag') and self.config.default_name_flag:
                            self.on_hotkey_insert_file_name(None)
                        self.on_hotkey_event(Event.IMG_CHANGE)
                        is_first_show = False
                    show_flag = False

                self.on_hotkey_event(Event.NONE)

                if self._next_img_flag:
                    if self.config.clear_window:
                        show_img((np.ones(img_display.shape) * 255).astype(np.uint8), window_name=self.IMG_WINDOW_NAME,
                                 window_size=window_size if window_size is not None else -1,
                                 delay_time=1)  # Avoid previous images remaining. use destroyWindow is not a good idea, it's too slow.
                    break
        print('all done!')
        cv2.destroyAllWindows()
        return self.FINISHED_MSG

    def refresh_window(self):
        cv2.destroyWindow(self.IMG_WINDOW_NAME)

    def on_hotkey_event(self, cur_event: Event):
        dict_job = getattr(self.on_hotkey_event, 'dict_job', dict)
        if not dict_job:
            return

        dict_job = {k: v for k, v in [(k, v) for k, v in
                                      sorted(dict_job.items(), key=lambda item: item[1][0])][::-1]  # sorted by priority: ascending
                    }
        self.__class__.on_hotkey_event.dict_job = dict_job

        for name, (n_priority, job, event, state) in dict_job.items():
            job: Callable
            if event == cur_event:
                job()
                if state == JobState.ONCE:
                    del dict_job[name]

    def on_click_commit(self, _: Union[tk.Event, None]):
        new_file_name = self.entry.get()
        if new_file_name.strip() == '':
            self.update_ui('label_error_msg', text=f'name is empty!')
            return
        if [_ for _ in filter(lambda char: char in new_file_name, self.ILLEGAL_CHARS)]:
            self.update_ui('label_error_msg', text=f'ILLEGAL_CHARS: {" ".join(self.ILLEGAL_CHARS)}')
            return
        org_img_path = self.widget_info.cur_img_path
        new_file: Path = org_img_path.parent / Path(new_file_name + org_img_path.suffix)
        # if new_file.exists():  # case insensitive
        if new_file.name in os.listdir(new_file.parent):
            self.update_ui('label_error_msg', text=f'FileExistsError: {org_img_path.name} -> {new_file.name}')
            return
        self.update_ui('label_error_msg', text=f'')
        self.widget_info.previous_img_path = new_file
        self.widget_info.previous_info = org_img_path, new_file
        org_img_path.rename(new_file)
        self.entry.delete(0, len(new_file_name))
        self._next_img_flag = True

    def on_click_open_source_dir(self, _: Union[tk.Event, None]):
        img_path = self.widget_info.cur_img_path
        os.startfile(img_path.parent)

    def on_click_skip(self, _: Union[tk.Event, None]):
        self._next_img_flag = True
        self.entry.delete(0, len(self.widget_info.cur_img_path.name))
        self.widget_info.previous_info = None
        return "break"  # ignore tab  # https://stackoverflow.com/questions/62366097/python-tk-setting-widget-focus-when-using-tab-key

    def on_hotkey_insert_file_name(self, _: Union[tk.Event, None]):
        img_path: Path = self.widget_info.cur_img_path
        self.entry.insert(0, img_path.stem)
        self.entry.icursor(0)

    def on_hotkey_insert_previous(self, _: Union[tk.Event, None]):
        if not self.widget_info.previous_img_path:
            return
        previous_img_path: Path = self.widget_info.previous_img_path
        self.entry.insert(0, previous_img_path.stem)
        self.entry.icursor(0)


class ImageRenameApp(RenameFactory):
    __slots__ = ('loop', 'dict_task',
                 'interval',
                 'is_dead',)

    def __init__(self, loop, img_path_list, **options):
        self.is_dead = False  # The app finished or not.
        self.loop = loop
        RenameFactory.__init__(self, img_path_list, **options)
        config = self.config

        from .template.base import Template
        Template(self, engine=getattr(config, 'engine', None)).render()  # load Template

        self.root.protocol("WM_DELETE_WINDOW", self.close)  # override original function
        self.interval = interval = getattr(config, 'interval', 1 / 40)
        self.dict_task: Dict[str, asyncio.Task] = dict(
            main=loop.create_task(self.main(interval)),
            updater=loop.create_task(self.updater(interval)),
        )

    def run(self):
        self.loop.run_forever()  # Run the event loop until stop() is called.
        if not self.is_dead:
            self.loop.close()

    async def updater(self, interval):
        while True:
            self.root.update()
            await asyncio.sleep(interval)
            if getattr(self.dict_task['main'], '_result') == self.FINISHED_MSG:
                break
        print('close updater')
        self.loop.stop()

    def close(self):
        for task_name, task in self.dict_task.items():
            task.cancel()
        cv2.destroyAllWindows()
        self.root.destroy()
        self.loop.stop()
        self.is_dead = True
