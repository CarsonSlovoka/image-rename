from typing import Tuple
from pathlib import Path

DEBUG = True
dict_hotkey = dict(
    commit=['<Return>',  # Enter
            '<space>'],
    skip=['<Tab>'],
    insert_file_name=['<F7>'],
)
window_size = None  # (300, 400)
default_name_flag = False  # If the flag is True, then it will show the name in the widget of entry.
img_path_list = [f for f in Path('./test/image').glob('*') if f.suffix[1:].lower() in ('png', 'bmp', 'jpg')]
# img_path_list = [f for f in Path('./test').glob('**/*') if f.suffix[1:].lower() in ('png', 'bmp', 'jpg')]  # It's able to look the nest directory.

if DEBUG:
    print('use default config')
