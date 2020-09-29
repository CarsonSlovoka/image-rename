from image_rename import template
from image_rename.core import ImageRenameApp, Event, JobState
import tkinter.messagebox
import os
from pathlib import Path
import functools
from typing import List, Tuple, Callable, Dict

register = template.Library(__name__)  # You can assign any str as a parameter. It can make the programmer easy to understand where the path of the module is.


@register.hotkey(key_list=['<Alt-D>', '<Alt-d>'])
def delete_file(app: ImageRenameApp):
    img_path = app.widget_info.cur_img_path
    if tkinter.messagebox.askokcancel('Delete', f'Do you want to delete the file?\n{img_path}'):
        os.remove(img_path)
        app.on_click_skip(None)  # next image


@register.hotkey(key_list='<F12>')
def change_log(app: ImageRenameApp, dict_job: Dict[str, Tuple[int, Callable, Event, JobState]]):
    """
    Save the information to the log file (the name before rename and after)
    You can click again to suspend or reopen it.
    """
    def main(run: bool):
        if not run:
            return

        if app.widget_info.previous_info is None:
            return

        output_path: Path = app.config.output_change_log_path
        mode = 'a'
        if not getattr(change_log, 'init_done', False):
            change_log.init_done = True
            mode = 'w'

        sep = '\t'
        with open(output_path, mode, encoding='utf-8') as f:
            # rename before, after
            before_path, after_path = app.widget_info.previous_info  # type: Path
            f.write(sep.join([str(before_path.absolute()), str(after_path.absolute())]) + '\n')

    # suspend when clicking hotkey again
    change_log.is_run = not change_log.is_run if getattr(change_log, 'is_run', False) else True

    new_func = functools.wraps(change_log)(lambda: main(change_log.is_run))
    priority = 1
    dict_job[change_log.__name__] = (
        priority,
        new_func,
        Event.IMG_CHANGE, JobState.FOREVER
    )


@register.hotkey(key_list='<F1>')
def history_log(app: ImageRenameApp, dict_job: Dict[str, Tuple[int, Callable, Event, JobState]]):
    """
    Save the history which data is the Path of your first sees the image.
    You can click again to suspend or reopen it.
    """
    def main(run: bool):
        if not run:
            return

        output_path = app.config.output_history_log_path
        mode = 'a'
        if not getattr(history_log, 'init_done', False):
            history_log.init_done = True
            mode = 'w'

        sep = '\t'
        with open(output_path, mode, encoding='utf-8') as f:
            f.write(sep.join([str(app.widget_info.cur_img_path.absolute())]) + '\n')

    # suspend when clicking hotkey again
    history_log.is_run = not history_log.is_run if getattr(history_log, 'is_run', False) else True

    new_func = functools.wraps(history_log)(lambda: main(history_log.is_run))
    priority = 1
    dict_job[history_log.__name__] = (
        priority,
        new_func,
        Event.IMG_CHANGE, JobState.FOREVER
    )
    new_func()
