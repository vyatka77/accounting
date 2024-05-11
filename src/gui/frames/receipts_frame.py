import logging
from tkinter import *
from tkinter import ttk, messagebox

from ..tools import win_icons as icon
from ..dialogs.auth_dialog import AuthDialog
from .qr_code_frame import QRCodeFrame
from .ticket_frame import TicketFrame
from ...receipts.utils import nalog_auth, get_ticket

logger = logging.getLogger(__name__)


class ReceiptFrame(ttk.Frame):

    def __init__(self, master):
        super().__init__(master, padding=5)
        self.current_ticket_frame = None
        self.ticket_frames = {}
        self.tickets = {}

        self.auth_status = BooleanVar()
        self.auth_status.trace_add('write', self.auth_status_handler)

        self.create_widgets()
        self.authorization()

    def authorization(self):
        root = self.winfo_toplevel()
        if nalog_auth(AuthDialog, root):
            self.auth_status.set(True)
        else:
            self.auth_status.set(False)

        root.attributes("-topmost", 1)
        root.attributes("-topmost", 0)

    def create_widgets(self):
        self.load_ico = icon.imageres_big.load
        self.key_ico = icon.imageres_big.key
        self.save_ico = icon.shell32_big.save

        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=0)

        self.qr_code = QRCodeFrame(self)
        self.qr_code.grid(row=0, column=0)

        manager_frame = ttk.Frame(self, border='1', relief='groove', padding=3)
        self.get_ticket_button = ttk.Button(manager_frame, image=self.load_ico, command=self.get_ticket_frame)
        self.auth_button = ttk.Button(manager_frame, image=self.key_ico, command=self.authorization)
        self.save_button = ttk.Button(manager_frame, image=self.save_ico, command=self.save)

        self.get_ticket_button.grid(row=0, column=0)

        status_frame = ttk.Frame(self)
        ttk.Label(status_frame, text="РККТ-Налог: ").grid(row=0, column=0)
        self.status_label = ttk.Label(status_frame)
        self.status_label.grid(row=0, column=1)

        status_frame.grid(row=1, column=0, sticky='ew')
        manager_frame.grid(row=0, column=1, rowspan=2, sticky='ns')

    def auth_status_handler(self, *args):
        if self.auth_status.get():
            self.status_label['text'] = "авторизованно"
            self.status_label['foreground'] = 'green'
            self.get_ticket_button.state(['!disabled'])
            self.auth_button.grid_remove()
        else:
            self.status_label['text'] = "неавторизованно"
            self.status_label['foreground'] = 'red'
            self.get_ticket_button.state(['disabled'])
            self.auth_button.grid(row=1, column=0, sticky='s')

    def get_ticket_frame(self):
        qr = self.qr_code.get()
        if qr is None:
            return

        ticket_json = self.tickets.get(qr) or self.tickets.setdefault(qr, get_ticket(qr))
        try:
            if self.current_ticket_frame:
                self.current_ticket_frame.grid_remove()
            self.current_ticket_frame = (self.ticket_frames.get(qr)
                                         or self.ticket_frames.setdefault(qr, TicketFrame(self, ticket_json)))
            self.current_ticket_frame.grid(row=0, column=2, rowspan=2, sticky="nsew")
            self.save_button.grid(row=1, column=0)
        except Exception:
            logger.warning(f"{ticket_json}")
            logger.exception('')
            messagebox.showinfo('Ошибка', "Не удалось получить информацию о чеке")
            self.authorization()

    def save(self):
        ticket_category = self.current_ticket_frame.ticket_category.get()
        for item in self.current_ticket_frame.items:
            if item.product.category_id is None:
                if ticket_category:
                    item.product.category_id = self.current_ticket_frame.categories[ticket_category].id
                else:
                    messagebox.showinfo(' ', 'Необходимо назначить категорию\nдля всех товаров')
                    return
        self.current_ticket_frame.ticket_orm.save()
        self.current_ticket_frame.destroy()
        self.save_button.grid_remove()
        self.qr_code.update_value()
