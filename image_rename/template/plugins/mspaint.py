__all__ = ('PLUGIN_MS_PAINT',)

from image_rename import template
from image_rename.core import ImageRenameApp
from pathlib import Path
from subprocess import Popen, PIPE, DEVNULL

if '__file__' in globals():
    PLUGIN_MS_PAINT = Path(__file__)

register = template.Library(__name__)


@register.hotkey(key_list=['<Alt-P>', '<Alt-p>'])
def start_ms_paint(app: ImageRenameApp):
    Popen(['mspaint', str(app.widget_info.cur_img_path)], stdout=PIPE, stderr=PIPE, stdin=DEVNULL)
