import logging
from tkinter import *
from tkinter import ttk, messagebox

from ..settings import settings
from .frames.receipts_frame import ReceiptFrame

logger = logging.getLogger(__name__)


def run(root: Tk | None = None):
    try:
        if root is None:
            root = Tk()
            root.tk.call('lappend', 'auto_path', settings.GUI_THEME_PATH)
            root.tk.call('package', 'require', settings.NAME_THEME)

        root.title("Бухучёт")
        root.geometry("+300+200")
        root.resizable(False, False)

        style = ttk.Style()
        style.theme_use(settings.NAME_THEME)
        frame = ReceiptFrame(root)
        frame.grid(row=0, column=0)
        root.mainloop()
    except Exception:
        logger.critical('', exc_info=True)
        messagebox.showinfo("Ошибка", "Ошибка приложения")
