"""
Show the information of IFD {EXIF, GPS}. According to its type and put it to different TreeView.
"""

from pathlib import Path

if '__file__' in globals():
    PLUGIN_IFD_TAG_V2 = Path(__file__)  # https://www.awaresystems.be/imaging/tiff/tifftags/privateifd.html

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
from image_rename.api.utils import init_namedtuple
from typing import Callable, Tuple, NamedTuple, Union, List, Dict
import os
import re

register = template.Library(__name__)


@init_namedtuple('init_style')
class TTKStyle(NamedTuple):
    LF_NORMAL = f'{__name__.split(".")[-1]}-Normal.TLabelframe'

    def init_style(self):
        style = ttk.Style()
        style.configure(self.LF_NORMAL, background='black')
        style.configure(f'{self.LF_NORMAL}.Label', foreground='#99FF00', background='blue', font=('courier', 15, 'bold'))


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


@register.panel(window_name='IFD TAG2', icon_path=Path(image_rename.__file__).parent / Path('asset/icon/exif.ico'))
def ifd_panel(parent: tk.Toplevel, app: ImageRenameApp):
    return IFDPanel(parent, app).build()  # Class must inherit PanelBase. Otherwise, update will not working.


class IFDPanel(PanelBase, TreeMixin):
    __slots__ = ('exif_tree', 'gps_tree',
                 'parent', 'app',
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

    class EXIFProperty(NamedTuple):
        exif_version: str
        make: str
        file_name: str
        size: str
        date_time_original: str
        color_space: str

        contrast: str
        saturation: str
        sharpness: str

    class GPSProperty(NamedTuple):
        latitude: str
        longitude: str
        altitude: str

    header = Header()
    prop_exif = EXIFProperty('Exif Version', 'Make by', 'File Name', 'Size (h, w)', 'DateTimeOriginal', 'ColorSpace',
                             'Contrast', 'Saturation', 'Sharpness',
                             )

    prop_gps = GPSProperty('Latitude', 'Longitude', 'Altitude', )

    def __init__(self, parent: tk.Toplevel, app: ImageRenameApp):
        super().__init__(parent)
        self.app = app

        ttk_style = TTKStyle()

        frame = ttk.Frame(self.parent)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(0, weight=1)
        frame.grid(sticky='news')

        lf_exif = ttk.Labelframe(frame, text='EXIF Tag', style=ttk_style.LF_NORMAL)
        lf_gps = ttk.Labelframe(frame, text='GPS Tag', style=ttk_style.LF_NORMAL)
        for lf in (lf_exif, lf_gps):
            lf.grid_columnconfigure(0, weight=1)
            lf.grid_rowconfigure(0, weight=1)
            lf.grid(sticky='news')
        self.exif_tree = ttk.Treeview(lf_exif, show='headings', columns=self.header.to_tuple(), height=10)
        self.gps_tree = ttk.Treeview(lf_gps, show='headings', columns=self.header.to_tuple(), height=10)
        self.parent.protocol("WM_DELETE_WINDOW", lambda: self.parent.withdraw())  # hide window
        self.regex = re.compile(r"(?P<width>[0-9]+)x(?P<height>[0-9]+)\+(?P<xoffset>[0-9]+)\+(?P<offset_y>[0-9]+)")  # search 123*1+22+333

    def build(self):
        for tree, prop in zip([self.exif_tree, self.gps_tree], [self.prop_exif, self.prop_gps]):
            for col, width in zip(self.header, (None, 100)):
                text = col.replace('_', ' ').title()  # uppercase
                tree.heading(col, text=text, command=lambda col_name=col: self.sort_by(col_name, is_descending=False, tree=tree))
                # self.tree.column("name", width=150, anchor='e')
                if width is None:
                    width = Font().measure(text)
                tree.column(col, width=width)

            tree.bind('<ButtonRelease-1>',  # https://www.python-course.eu/tkinter_events_binds.php
                      lambda event, pro=prop, tree_view=tree: self.select_item(event, pro, tree_view))  # https://www.python-course.eu/tkinter_events_binds.php
            tree.grid(sticky='news')
            self.build_scrollbar(self.parent, tree)

        offset_x, offset_y = [int(_) for _ in self.app.root.geometry().split('+')[1:]]
        offset_x -= self.parent.winfo_width()
        self.parent.geometry(f'+{offset_x}+{offset_y}')

    def update(self, event: Event, parent_update: Callable = None):
        if event != Event.IMG_CHANGE:
            return

        for tree in (self.exif_tree, self.gps_tree):
            tree.delete(*tree.get_children())  # new empty tree, avoid write again.

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
                           'Contrast', 'Saturation', 'Sharpness',),
                          ignore_error=True, fill_empty='')
        if result == -1:
            # EXIF does not support
            return

        (exif_version, make,
         data_time_original,
         gps_info,
         gps_latitude_ref, gps_latitude, gps_longitude_ref, gps_longitude, gps_altitude_ref, gps_altitude,
         gps_dop,
         color_space, contrast, saturation, sharpness) = result

        prop_gps = IFDPanel.GPSProperty(f'{gps_latitude_ref} {gps_latitude}',
                                        f'{gps_longitude_ref} {gps_longitude}',
                                        f'{gps_altitude_ref} {gps_altitude}')

        prop_exif = IFDPanel.EXIFProperty(
            exif_version.decode('utf-8'), make, img_path.name,
            f'{height}, {width}', data_time_original, color_space,
            contrast, saturation, sharpness,
        )
        for tree, prop_key, prop in ((self.exif_tree, self.prop_exif, prop_exif),
                                     (self.gps_tree, self.prop_gps, prop_gps)):
            for property_name, val in zip(prop_key, prop):
                row_data = property_name, val
                tree.insert("", "end", text=property_name, values=row_data)
                self.adjust_column(row_data, tree)

        cur_width = max([sum([tree.column(header_name)['width'] for header_name in self.header.to_tuple()])
                         for tree in (self.exif_tree, self.gps_tree)
                         ])
        width, height, offset_x, offset_y = self.regex.match(self.parent.geometry()).groups()  # groupdict()

        offset_x, offset_y = [int(_) for _ in self.app.root.geometry().split('+')[1:]]
        offset_x -= cur_width
        self.parent.geometry(f'{cur_width}x{height}+{offset_x}+{offset_y}')

    def select_item(self, event: tk.Event,
                    prop_class: Union[EXIFProperty, GPSProperty], tree: ttk.Treeview):
        query_item: Union[Tuple, str] = tree.item(tree.focus(), option='values')
        if query_item == '':
            return
        col: str = tree.identify_column(getattr(event, 'x'))
        prop, val = query_item
        if col == '#1':
            if isinstance(prop_class, IFDPanel.EXIFProperty) and prop == prop_class.file_name:
                os.startfile(self.app.widget_info.cur_img_path)
            return
        # '#2'
        if isinstance(prop_class, IFDPanel.EXIFProperty) and prop == prop_class.file_name:
            val = self.app.widget_info.cur_img_path.stem
        tree.clipboard_clear()
        tree.clipboard_append(val)
