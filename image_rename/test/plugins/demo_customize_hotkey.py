from image_rename import template
from image_rename.core import ImageRenameApp
from pathlib import Path

register = template.Library(__name__)


@register.hotkey(key_list=[']'])
def show_path(app: ImageRenameApp):
    print(app.widget_info.cur_img_path)
    print(app.widget_info.previous_img_path)


@register.hotkey(key_list=['<F7>'], name='insert_file_name')
def on_hotkey_insert_file_name(app: ImageRenameApp):
    """
    override config.py.insert_file_name
    Change the position of the cursor to the last.
    """
    img_path: Path = app.widget_info.cur_img_path
    entry = app.widget_info.entry
    entry.insert(0, img_path.stem)
    entry.icursor(len(entry.get()))
