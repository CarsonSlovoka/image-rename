import tkinter as tk
from typing import Union, List, Dict
from pathlib import Path
from grid_extractor import show_img
import cv2
import numpy as np
import asyncio


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


class EditBoxBase:
    __slots__ = ('root', 'canvas', 'entry')

    FONT_NAME = 'helvetica'

    def __init__(self, width=400, height=300, **options):
        self.root = root = tk.Tk()
        self.canvas = tk.Canvas(root, width=width, height=height, relief='raised')
        self.entry = self.init_ui()

    def put2canvas(self, widget: tk.Widget, x, y):
        self.canvas.create_window(x, y, window=widget)

    def init_ui(self) -> tk.Entry:
        raise NotImplementedError('init_ui')

    def on_click_entry(self, e: tk.Event):
        raise NotImplementedError('on_click_entry')


class RenameFactory(EditBoxBase):
    __slots__ = ('img_path_list', 'img_next', 'next_img_flag')

    ILLEGAL_CHARS = ('\\', '/', '?', '*', '<', '>', '|')  # These characters is not acceptable for the filename.
    FINISHED_MSG = 'FINISHED'

    def __init__(self, img_path_list: List[Path], **options):
        self.img_path_list = img_path_list
        self.img_next: Union[np.ndarray, None] = None
        self.next_img_flag = False
        super().__init__(**options)

    def init_ui(self):
        self.root.iconbitmap(Path(__file__).parent / Path('asset/icon/main.ico'))
        self.root.title('Rename Tool')

        self.canvas.pack()
        label_title = tk.Label(self.root, text='Rename Tool')
        label_title.config(font=(self.FONT_NAME, 24))
        self.put2canvas(label_title, 200, 25)

        label_input_info = tk.Label(self.root, text='New file name:')
        label_input_info.config(font=(self.FONT_NAME, 18))
        self.put2canvas(label_input_info, 200, 100)

        entry = tk.Entry(self.root)
        entry.config(font=(self.FONT_NAME, 18), fg='blue', width=10)
        entry.focus_set()
        self.put2canvas(entry, 200, 140)
        self.root.bind('<Return>', self.on_click_entry)

        btn_commit = tk.Button(text='Commit', command=lambda: self.on_click_entry(None), bg='brown', fg='white', font=(self.FONT_NAME, 12, 'bold'))
        self.put2canvas(btn_commit, 200, 180)
        return entry

    async def main(self, interval: float):
        if len(self.img_path_list) == 0:
            print('empty img_path_list')
            return
        for i in range(len(self.img_path_list) + 1):
            img_path = self.img_path_list[min(i, len(self.img_path_list) - 1)]
            if i == 0:
                show_img(imread(img_path), delay_time=1)
                continue
            self.next_img_flag = False
            while await asyncio.sleep(interval, True):
                self.img_next = imread(img_path)
                if self.next_img_flag:
                    break
        print('all done!')
        cv2.destroyAllWindows()
        return self.FINISHED_MSG

    def on_click_entry(self, e: Union[tk.Event, None]):
        new_file_name = self.entry.get()
        if new_file_name.strip() == '':
            return
        if new_file_name in self.ILLEGAL_CHARS:
            print(f'ILLEGAL_CHARS: {self.ILLEGAL_CHARS}')
            return
        print(new_file_name)
        self.entry.delete(0, len(new_file_name))
        show_img(self.img_next, delay_time=1)
        self.next_img_flag = True


class ImageRenameApp(RenameFactory):
    __slots__ = ('loop', 'dict_task', 'is_dead')

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
            if self.dict_task['main']._result == self.FINISHED_MSG:
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
