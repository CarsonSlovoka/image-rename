__version__ = '0.1.1'
__author__ = ['Carson', ]
__description__ = "Rename the picture by looking through the human eye and typing. (you don't need to open the file by yourself)"

from .core import (
    ImageRenameApp, APP_ICON_PATH,
    imread, Event
)

from .api.utils import work_dir
from .template.plugins import *
from .template.engine import Engine
from image_rename.template.node import PanelBase, HotkeyNode
