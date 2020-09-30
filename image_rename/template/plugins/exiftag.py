try:
    import PIL.Image
    import PIL.ExifTags  # https://www.awaresystems.be/imaging/tiff/tifftags/privateifd/exif.html
except ImportError:
    raise ImportError('Please `pip install Pillow`')
from pathlib import Path

if '__file__' in globals():
    PLUGIN_EXIF_TAG = Path(__file__)
