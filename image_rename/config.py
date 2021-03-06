from typing import Tuple
from pathlib import Path
from image_rename import (
    Engine,
    PLUGIN_MS_PAINT, PLUGIN_IFD_TAG, PLUGIN_IFD_TAG_V2,
)

dict_hotkey = dict(
    commit=['<Return>',  # Enter
            '<space>'],
    skip=['<Tab>'],
    insert_file_name=['<F7>'],
    insert_previous=['<F4>'],
)

if not 'ignore default_builtins':
    Engine.default_builtins += [
        # Path(r"X:\...\customize_hotkey.py")
    ]
else:
    engine = Engine([
        # Path(r"X:\...\customize_hotkey.py")
        PLUGIN_MS_PAINT,
        # PLUGIN_IFD_TAG,
        PLUGIN_IFD_TAG_V2,
        ])

window_size = None  # (300, 400)
clear_window = True if window_size is None else False  # If True, it will fill the canvas with the white color every time, avoid the last remaining.
display_n_img = 3  # Display how many images in once.
if display_n_img > 1:
    highlight_color = (0, 0, 255)  # BGR  # fill the border with the red on the current image.
    border_thickness = 10
default_name_flag = True  # If the flag is True, then it will show the name in the widget of entry in each image.
img_path_list = [f for f in Path('./test/image').glob('*') if f.suffix[1:].lower() in ('png', 'bmp', 'jpg')]
# img_path_list = [f for f in Path('./test').glob('**/*') if f.suffix[1:].lower() in ('png', 'bmp', 'jpg')]  # It's able to look the nest directory.

if 'The area record the variable used for the plugin':
    output_history_log_path = Path('./my_history_log.txt')
    output_change_log_path = Path('./my_change_log.txt')

DEBUG = True
if DEBUG:
    print('use default config')
