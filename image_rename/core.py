import tkinter as tk
from typing import Union, List, Dict, Tuple
from pathlib import Path
from grid_extractor import show_img
import cv2
import numpy as np
import asyncio
import os


def on_click_enter(e: tk.Event):
    print(e)


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


class RenameFactory(EditBoxBase, TkMixin):
    __slots__ = ('img_path_list', 'next_img_flag',
                 'dict_hotkey', 'window_size')

    ILLEGAL_CHARS = ('\\', '/', '?', '*', '<', '>', '|')  # These characters is not acceptable for the filename.
    FINISHED_MSG = 'FINISHED'
    IMG_WINDOW_NAME = 'demo'

    def __init__(self, img_path_list: List[Path], **options):
        self.img_path_list = img_path_list

        self.dict_hotkey: Dict[str, List[str]] = options.get('dict_hotkey', dict(commit=['<Return>'], skip=[]))
        self.window_size: Union[Tuple[int, int], None] = options.get('window_size')
        self.next_img_flag = False
        EditBoxBase.__init__(self, **options)

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
        entry.config(font=(self.FONT_NAME, 18), fg='blue', width=10)
        entry.focus_set()
        self.put2canvas(entry, 200, 140)
        for key_name in self.dict_hotkey['commit']:
            # self.root.bind('<Return>', self.on_click_commit)
            self.root.bind(key_name, self.on_click_commit)
        for key_name in self.dict_hotkey['skip']:
            self.root.bind(key_name, self.on_click_skip)

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
        for img_path in self.img_path_list:
            img_cur = imread(img_path)
            show_flag = True
            self.next_img_flag = False
            while await asyncio.sleep(interval, True):
                if cv2.getWindowProperty('demo', cv2.WND_PROP_FULLSCREEN) == -1 or show_flag:
                    # If the user closed the window, then show it again.
                    show_img(img_cur, window_name=self.IMG_WINDOW_NAME,
                             window_size=self.window_size if self.window_size is not None else -1,
                             delay_time=1)
                    self.update_ui('label_abs_img_path', text=f'{str(img_path.resolve())[-50:]}').hide_msg = img_path
                    show_flag = False

                if self.next_img_flag:
                    self.update_ui('label_abs_img_path', text=f'{str(img_path.resolve())[-50:]}').hide_msg = img_path
                    break
        print('all done!')
        cv2.destroyAllWindows()
        return self.FINISHED_MSG

    def on_click_commit(self, _: Union[tk.Event, None]):
        new_file_name = self.entry.get()
        if new_file_name.strip() == '':
            self.update_ui('label_error_msg', text=f'name is empty!')
            return
        if [_ for _ in filter(lambda char: char in new_file_name, self.ILLEGAL_CHARS)]:
            self.update_ui('label_error_msg', text=f'ILLEGAL_CHARS: {" ".join(self.ILLEGAL_CHARS)}')
            return
        org_img_path = getattr(self.get_widget('label_abs_img_path'), 'hide_msg')
        new_file = org_img_path.parent / Path(new_file_name + org_img_path.suffix)
        # if new_file.exists():  # case insensitive
        if new_file.name in os.listdir(new_file.parent):
            self.update_ui('label_error_msg', text=f'FileExistsError: {org_img_path.name} -> {new_file.name}')
            return
        self.update_ui('label_error_msg', text=f'')
        org_img_path.rename(new_file)
        self.entry.delete(0, len(new_file_name))
        self.next_img_flag = True

    def on_click_open_source_dir(self, _: Union[tk.Event, None]):
        img_path = getattr(self.get_widget('label_abs_img_path'), 'hide_msg')
        os.startfile(img_path.parent)

    def on_click_skip(self, _: Union[tk.Event, None]):
        self.next_img_flag = True
        return "break"  # ignore tab  # https://stackoverflow.com/questions/62366097/python-tk-setting-widget-focus-when-using-tab-key


class ImageRenameApp(RenameFactory):
    __slots__ = ('loop', 'dict_task',
                 'is_dead',)

    def __init__(self, loop, img_path_list, **options):
        self.is_dead = False  # The app finished or not.
        self.loop = loop
        RenameFactory.__init__(self, img_path_list, **options)
        self.root.protocol("WM_DELETE_WINDOW", self.close)  # override original function
        interval = options.get('interval', 1 / 120)
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