from abc import ABCMeta, abstractmethod
from tkinter import *
from tkinter import ttk

from .askdialogs import askinteger, ttkDialog
from ...receipts.nalog_api import auth_methods, authorization, SessionTokens
from ...receipts.utils import (get_phone_number,
                               get_inn,
                               get_password,
                               get_default_nalog_auth,
                               get_client_secret)

auth_frames = {}


def register(method: str):
    def reg_class(cls):
        cls.AUTH_METHOD = method
        auth_frames[method] = cls
        return cls

    return reg_class


class AuthFrame(ttk.Frame, metaclass=ABCMeta):
    AUTH_METHOD: str

    def __init__(self, master):
        super().__init__(master)

        self.error = StringVar()
        self.create_widgets()

        send_button = ttk.Button(self, text="Отправить", command=self.auth)
        send_button.grid(row=2, column=0, pady=5, columnspan=4)

        error_label = ttk.Label(self, textvariable=self.error, foreground='red')
        error_label.grid(row=3, column=0, columnspan=4, sticky='w')

    @abstractmethod
    def create_widgets(self):
        ...

    @abstractmethod
    def get_args(self):
        ...

    @abstractmethod
    def validate(self):
        ...

    def auth(self):
        if not self.validate():
            return
        args = self.get_args()
        self.auth_tokens = authorization(self.AUTH_METHOD,
                                         *args,
                                         client_secret=get_client_secret())
        if self.auth_tokens is not None:
            top = self.winfo_toplevel()
            if hasattr(top, 'ok'):
                top.ok()
        else:
            self.error.set("Ошибка авторизации. Попробуйте позже...")


@register('inn')
class InnAuthFrame(AuthFrame):
    def create_widgets(self):
        self.inn = StringVar()
        self.password = StringVar()
        self.inn.set(get_inn())
        self.password.set(get_password())

        ttk.Label(self, text="ИНН:").grid(row=0, column=0)
        ttk.Label(self, text="Пароль:").grid(row=1, column=0)
        ttk.Entry(self, width=20, textvariable=self.inn).grid(row=0, column=1, pady=5)
        ttk.Entry(self, width=20, textvariable=self.password, show='*').grid(row=1, column=1, pady=5)

    def get_args(self):
        return self.inn.get(), self.password.get()

    def validate(self):
        inn, password = self.get_args()
        if not inn:
            self.error.set("Необходимо указать ИНН")
            return False
        if not inn.isdigit():
            self.error.set("ИНН должен содержать только цифры")
            return False
        if len(inn) != 12:
            self.error.set("Необходимо ввести 12 цифр")
            return False
        if not password:
            self.error.set("Необходимо указать пароль")
        return True


@register('sms')
class SmsAuthFrame(AuthFrame):
    def create_widgets(self):
        self.phone = StringVar()
        self.phone.set(get_phone_number())

        ttk.Label(self, text="Введите телефон:").grid(row=0, column=0)
        ttk.Label(self, text="+7").grid(row=0, column=1, sticky='w')
        ttk.Entry(self, width=10, textvariable=self.phone).grid(row=0, column=2, sticky="ew")

    def get_args(self):
        return ('+7' + self.phone.get(),
                lambda prompt: str(askinteger('Налог', prompt)))

    def validate(self):
        phone = self.phone.get()
        if not phone:
            self.error.set("Необходимо указать \nномер телефона")
            return False
        if not phone.isdigit():
            self.error.set("Номер телефона должен \nсодержать только цифры")
            return False
        if len(phone) != 10:
            self.error.set("Необходимо ввести 10 цифр")
            return False
        return True


class AuthDialog(ttkDialog):
    current_frame: AuthFrame | None = None
    auth_frames: dict[str, AuthFrame] = {}
    auth_tokens: SessionTokens | None = None

    def body(self, master):
        self.auth_method = StringVar()

        master.columnconfigure(0, minsize=150)
        master.columnconfigure(2, minsize=350)
        master.rowconfigure(0, minsize=250)

        left = ttk.Frame(master)
        right = ttk.Frame(master)

        for i, method in enumerate(auth_methods):
            rb = ttk.Radiobutton(left, text=method, variable=self.auth_method, value=method)
            rb.grid(row=i)
            if method not in auth_frames:
                rb.state(['disabled'])
            else:
                rb.state(['!disabled'])
                auth_frame = auth_frames[method](right)
                self.auth_frames[method] = auth_frame
                self.current_frame = auth_frame

        self.auth_method.trace_add('write', self.show_auth_frame)
        self.auth_method.set(get_default_nalog_auth())

        left.grid(row=0, column=0)
        right.grid(row=0, column=2)
        ttk.Separator(master, orient=VERTICAL).grid(row=0, column=1, sticky='ns')

    def show_auth_frame(self, *args):
        self.current_frame.grid_remove()
        method = self.auth_method.get()
        self.current_frame = self.auth_frames[method]
        self.current_frame.grid(row=0, column=2)

    def apply(self):
        self.auth_tokens = getattr(self.current_frame, 'auth_tokens')
