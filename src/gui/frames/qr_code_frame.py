import re
from pathlib import Path
from tkinter import *
from tkinter import ttk
from tkinter.filedialog import askopenfilename

from ..tools import win_icons as icon
from ...receipts.utils import get_qr_code, replace_file
from ...settings import settings
from ...storage.repository import QRCodeStorage

if settings.QR_IMAGES_DIR is not None:
    QR_IMAGES_DIR = settings.QR_IMAGES_DIR
else:
    QR_IMAGES_DIR = Path(__file__).resolve().parent


class QRCodeFrame(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)

        self.qr_code = StringVar()
        self.error = StringVar()
        self.tickets = StringVar()

        self.qr_code.trace_add('write', self.change_qr_code)

        self.update_value()

        self.create_widgets()

    def create_widgets(self):
        self.image_ico = icon.shell32_middle.image

        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=0)
        self.rowconfigure(2, weight=1)

        ttk.Label(self, text="QR Code", font=14).grid(row=0, column=0)
        ttk.Entry(self, width=60, textvariable=self.qr_code).grid(row=0, column=1, sticky='ns')
        ttk.Button(self, image=self.image_ico, command=self.get_from_img).grid(row=0, column=2)
        ttk.Label(self, textvariable=self.error, foreground="red").grid(row=1, column=1, sticky='w')

        self.unsaved_tickets = Listbox(self, listvariable=self.tickets)
        self.unsaved_tickets.grid(row=2, column=0, columnspan=3, sticky='nsew')

        self.unsaved_tickets.bind("<<ListboxSelect>>", self.unsaved_ticket_selection)

    def get_from_img(self):
        file = askopenfilename(title="Открыть файл",
                               initialdir=QR_IMAGES_DIR,
                               filetypes=(('', 'jpg'), ('', 'jpeg'),
                                          ('', 'png')))  # TODO нужно добавить все расширения изображений

        qr = get_qr_code(file)

        # TODO временный блок кода, который не должен войти в релиз
        if qr:
            replace_file(file, 'saved')
        elif file:
            self.error.set("QR код не распознан, попробуйте другой...")
            replace_file(file, 'failed')

        self.update_value(qr)

    def set(self, qr: str):
        self.qr_code.set(qr)

    def get(self) -> str | None:
        qr = self.qr_code.get()
        if not re.fullmatch(settings.TICKET_QR_FILTER, qr):
            self.error.set("Неправильный qr код")
            return None
        return qr

    def change_qr_code(self, *args):
        self.error.set('')

    def update_value(self, qr: str = None):
        tickets = [obj.qr for obj in QRCodeStorage.list(filter_by={'json_': None})]
        if qr is not None and qr in tickets:
            self.qr_code.set(qr)
        else:
            self.qr_code.set('')
        self.tickets.set(tickets)

    def unsaved_ticket_selection(self, e: Event):
        cur_idx = self.unsaved_tickets.curselection()
        if cur_idx:
            qr = self.unsaved_tickets.get(cur_idx)
            self.set(qr)
