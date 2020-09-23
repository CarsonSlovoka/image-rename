__version__ = '0.1.0'
__author__ = ['Carson', ]
__description__ = "Rename the picture by looking through the human eye and typing. (you don't need to open the file by yourself)"

from .core import (
    ImageRenameApp,
    imread,
)

from .api.utils import work_dir
