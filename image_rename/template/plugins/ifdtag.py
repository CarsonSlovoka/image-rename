from pathlib import Path

if '__file__' in globals():
    PLUGIN_IFD_TAG = Path(__file__)  # https://www.awaresystems.be/imaging/tiff/tifftags/privateifd.html

try:
    import PIL.Image
    import PIL.ExifTags  # https://www.awaresystems.be/imaging/tiff/tifftags/privateifd/exif.html
except ImportError:
    raise ImportError('Please `pip install Pillow`')

import tkinter as tk
from tkinter import ttk
from tkinter.font import Font
from image_rename import ImageRenameApp, Event, template
from image_rename.template.node import PanelBase
import image_rename
from image_rename.api.tkmixins import TreeMixin
from typing import Callable, Tuple, NamedTuple, Union, List, Dict, Iterator
import os
import re

register = template.Library(__name__)


def get_exif(file_path: Union[Path, PIL.Image.Image],
             search_list: Union[int, str, List, Tuple] = None,
             ignore_error=True, fill_empty=None,
             ) -> Union[int, PIL.Image.Exif, List]:
    """
    :param file_path: image path
    :param search_list: if you want to get some property, then you can pass the id or name, it will return by order.
    :param ignore_error:
    :param fill_empty Fill the value with the flag if the value is empty.
    :return:
        int: -1 FileNotFoundError, or exif is None
        PIL.Image.Exif: when the `search_list` is None, return the whole Exif
    """
    try:
        if isinstance(file_path, PIL.Image.Image):
            im = file_path
        else:
            im: PIL.Image.Image = PIL.Image.open(str(file_path))
    except FileNotFoundError:
        if ignore_error:
            return -1
        else:
            raise FileNotFoundError(file_path)

    exif: PIL.Image.Exif = im.getexif()
    # print(im._getexif())
    if not exif:
        if ignore_error:
            return -1
        else:
            raise ValueError("exif is None")
    if search_list is None:
        return exif

    tag_by_id_exif: Dict[int, str] = PIL.ExifTags.TAGS
    tag_by_id_gps: [int, str] = PIL.ExifTags.GPSTAGS
    tag_by_name_exif = {tag_by_id_exif[dec_value]: exif[dec_value] for dec_value in exif if dec_value in tag_by_id_exif}
    gps: Dict = {key: val for key, val in exif.items() if key in PIL.ExifTags.GPSTAGS}
    gps.update(exif.get(0x8825, dict()))  # GPSTAGS is inside of the GPSInfo
    tag_by_name_gps = {tag_by_id_gps[dec_value]: gps[dec_value] for dec_value in gps if dec_value in tag_by_id_gps}
    if not isinstance(search_list, (list, tuple)):
        search_list = [search_list]

    result_list = []
    for key in search_list:
        if isinstance(key, int):
            result_list.append(exif.get(key, gps.get(key, fill_empty)))
            continue
        try:
            dec_value = int(key, 16)
            result_list.append(exif.get(dec_value, gps.get(dec_value, fill_empty)))
            continue
        except ValueError:
            ...
        result_list.append(tag_by_name_exif.get(key, tag_by_name_gps.get(key, fill_empty)))
    return result_list


@register.panel(window_name='IFD TAG', icon_path=Path(image_rename.__file__).parent / Path('asset/icon/exif.ico'))
def ifd_panel(parent: tk.Toplevel, app: ImageRenameApp):
    return IFDPanel(parent, app).build()  # Class must inherit PanelBase. Otherwise, update will not working.


class IFDPanel(PanelBase, TreeMixin):
    __slots__ = ('tree', 'parent', 'app',
                 'regex',)

    class Header(NamedTuple):
        property = 'property'
        value = 'value'

        def to_tuple(self) -> Tuple[str, str]:
            return self.property, self.value

        def __getitem__(self, item: int):
            return self.to_tuple()[item]

        def __iter__(self):
            for val in self.to_tuple():
                yield val

    class Property(NamedTuple):
        exif_version: str
        make: str
        file_name: str
        size: str
        date_time_original: str
        color_space: str

        contrast: str
        saturation: str
        sharpness: str

        latitude: str
        longitude: str
        altitude: str

        def to_list(self):
            return [(key, getattr(self, key))
                    for key in dir(self.__class__)
                    if not key.startswith('_') and key not in ('count', 'index') and not callable(getattr(self, key))]

        def __iter__(self) -> Iterator[Tuple[str, str]]:
            for val in self.to_list():
                yield val

    header = Header()
    prop = Property('Exif Version', 'Make by', 'File Name', 'Size (h, w)', 'DateTimeOriginal', 'ColorSpace',

                    'Contrast', 'Saturation', 'Sharpness',

                    'Latitude', 'Longitude', 'Altitude')

    def __init__(self, parent: tk.Toplevel, app: ImageRenameApp, top_n=20):
        super().__init__(parent)
        self.parent = parent
        self.app = app
        self.tree = ttk.Treeview(self.parent,
                                 show='headings',  # ignore the index column
                                 columns=self.header.to_tuple(),
                                 height=top_n  # numbers of row
                                 )  # https://docs.python.org/3/library/tkinter.ttk.html
        self.parent.protocol("WM_DELETE_WINDOW", lambda: self.parent.withdraw())  # hide window
        self.regex = re.compile(r"(?P<width>[0-9]+)x(?P<height>[0-9]+)\+(?P<xoffset>[0-9]+)\+(?P<offset_y>[0-9]+)")  # search 123*1+22+333

    def build(self):
        for col, width in zip(self.header, (None, 100)):
            text = col.replace('_', ' ').title()  # uppercase
            self.tree.heading(col, text=text, command=lambda col_name=col: self.sort_by(col_name, is_descending=False))
            # self.tree.column("name", width=150, anchor='e')
            if width is None:
                width = Font().measure(text)
            self.tree.column(col, width=width)

        self.tree.bind('<Double-Button>', self.select_item)  # https://www.python-course.eu/tkinter_events_binds.php
        self.tree.grid(sticky='news')
        self.build_scrollbar(self.parent)

    def update(self, event: Event, parent_update: Callable = None):
        # parent_update()

        if event != Event.IMG_CHANGE:
            return

        self.tree.delete(*self.tree.get_children())  # new empty tree, avoid write again.

        img_path = self.app.widget_info.cur_img_path
        im: PIL.Image.Image = PIL.Image.open(str(img_path))
        width, height, = im.size
        result = get_exif(im,
                          ('ExifVersion',
                           'Make',
                           'DateTimeOriginal',
                           'GPSInfo',
                           'GPSLatitudeRef', 'GPSLatitude', 'GPSLongitudeRef', 'GPSLongitude', 'GPSAltitudeRef', 'GPSAltitude',
                           'GPSDOP (data degree of precision)',
                           'ColorSpace',
                           'Contrast', 'Saturation', 'Sharpness',)
                          , ignore_error=True, fill_empty='')
        if result == -1:
            # EXIF does not support
            return

        (exif_version, make,
         data_time_original,
         gps_info,
         gps_latitude_ref, gps_latitude, gps_longitude_ref, gps_longitude, gps_altitude_ref, gps_altitude,
         gps_dop,
         color_space, contrast, saturation, sharpness) = result

        prop = IFDPanel.Property(exif_version.decode('utf-8'), make, img_path.name,
                                 f'{height}, {width}', data_time_original, color_space,

                                 contrast, saturation, sharpness,

                                 f'{gps_latitude_ref} {gps_latitude}',
                                 f'{gps_longitude_ref} {gps_longitude}',
                                 f'{gps_altitude_ref} {gps_altitude}')

        for key_row_data, row_data in zip(self.prop, prop):
            _, property_name = key_row_data
            _, value = row_data
            self.tree.insert("", "end", text=property_name, values=(property_name, value))
            self.adjust_column(row_data)

        cur_width = sum([self.tree.column(header_name)['width'] for header_name in self.header.to_tuple()])
        width, height, x_offset, y_offset = self.regex.match(self.parent.geometry()).groups()  # groupdict()
        self.parent.geometry(f'{cur_width}x{height}+{x_offset}+{y_offset}')

    def select_item(self, event):
        # cur_item: dict = self.tree.item(self.tree.focus())  # cur_item['text'] 'values'
        query_item: Union[Tuple, str] = self.tree.item(self.tree.focus(), option='values')
        if query_item == '':
            return
        col: str = self.tree.identify_column(event.x)
        prop, val = query_item
        if col == '#1':
            if prop == self.prop.file_name:
                os.startfile(self.app.widget_info.cur_img_path)
            return
        # '#2'
        if prop == self.prop.file_name:
            val = self.app.widget_info.cur_img_path.stem
        self.tree.clipboard_clear()
        self.tree.clipboard_append(val)
