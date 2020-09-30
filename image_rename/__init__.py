__version__ = '0.1.1'
__author__ = ['Carson', ]
__description__ = "Rename the picture by looking through the human eye and typing. (you don't need to open the file by yourself)"

from .core import (
    ImageRenameApp, APP_ICON_PATH,
    imread,
)

from .api.utils import work_dir
from .template.plugins.mspaint import PLUGIN_MS_PAINT
from .template.engine import Engine

