# Sources:
# https://stackoverflow.com/questions/19760913/how-to-extract-32x32-icon-bitmap-data-from-exe-and-convert-it-into-a-pil-image-o
# https://stackoverflow.com/questions/23263599/how-to-extract-128x128-icon-bitmap-data-from-exe-in-python/28102999#28102999
# https://stackoverflow.com/questions/32341661/getting-a-windows-program-icon-and-saving-it-as-a-png-python?rq=3

import win32api
import win32con
import win32gui
import win32ui
from PIL import Image, ImageTk

ico_x = win32api.GetSystemMetrics(win32con.SM_CXICON)
ico_y = win32api.GetSystemMetrics(win32con.SM_CYICON)


class Icon:
    resource: str

    def __init__(self, srf: float = 1.0):
        self.srf = srf

    def __getattr__(self, item: str):
        _item = '_' + item.upper()
        if not hasattr(self.__class__, _item):
            raise AttributeError(f"{self.__class__.__name__} object has no attribute {item!r}")
        descriptor = getattr(self, _item)
        return self.get_icon(descriptor)

    def get_icon(self, descriptor: int) -> ImageTk.PhotoImage:
        large, small = win32gui.ExtractIconEx(self.resource, descriptor)
        win32gui.DestroyIcon(small[0])

        hdc = win32ui.CreateDCFromHandle(win32gui.GetDC(0))
        hbmp = win32ui.CreateBitmap()
        hbmp.CreateCompatibleBitmap(hdc, ico_x, ico_y)
        hdc = hdc.CreateCompatibleDC()

        hdc.SelectObject(hbmp)
        hdc.DrawIcon((0, 0), large[0])
        bmpstr = hbmp.GetBitmapBits(True)
        img = Image.frombuffer('RGBA',
                               (ico_x, ico_y),
                               bmpstr,
                               'raw',
                               'BGRA', 0, 1)
        img.thumbnail((int(self.srf * ico_x), int(self.srf * ico_y)))
        return ImageTk.PhotoImage(img)


class ImageresIcon(Icon):
    resource = r"C:\Windows\System32\imageres.dll"
    _KEY = 77
    _RECYCLE_BIN = 49
    _CHECK = 232
    _LOAD = 334
    _ADD = 279


class Shell32Icon(Icon):
    resource = r"C:\Windows\System32\shell32.dll"
    _SEARCH = 268
    _IMAGE = 327
    _SAVE = 258
    _INFO = 221
    _SCANNER = 201
    _PHOTO = 195
    _PRINTER = 105


imageres_big = ImageresIcon()
imageres_middle = ImageresIcon(0.75)
imageres_small = ImageresIcon(0.5)

shell32_big = Shell32Icon()
shell32_middle = Shell32Icon(0.75)
shell32_small = Shell32Icon(0.5)
