from image_rename import template
from image_rename.core import ImageRenameApp
import tkinter.messagebox
import os

register = template.Library(__name__)  # You can assign any str as a parameter. It can make the programmer easy to understand where the path of the module is.


@register.hotkey(key_list=['<Alt-D>', '<Alt-d>'])
def delete_file(app: ImageRenameApp):
    img_path = app.widget_info.cur_img_path
    if tkinter.messagebox.askokcancel('Delete', f'Do you want to delete the file?\n{img_path}'):
        os.remove(img_path)
        app.next_img_flag = True
