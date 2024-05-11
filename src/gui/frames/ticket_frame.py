from tkinter import *
from tkinter import ttk

from ..tools import win_icons as icon
from ..dialogs.askdialogs import askstring
from ...receipts.json_parse import TicketParser
from ...storage.models import TicketORM
from ...storage.repository import ProductStorage, CategoryStorage


class TicketFrame(ttk.Frame):
    def __init__(self, master, ticket_json: str):
        super().__init__(master, padding=5)

        self.init_data(ticket_json)
        self.combo_list: list[ttk.Combobox] = []
        self.ticket_category = StringVar()
        self.create_widgets()

        self.set_categories()

    def create_widgets(self):
        self.add_ico = icon.imageres_small.add

        common_category = ttk.Frame(self)
        ttk.Label(common_category, text='Категория покупки').grid(row=0, column=0)
        combo = ttk.Combobox(common_category, textvariable=self.ticket_category)
        combo.state(['readonly'])
        combo.grid(row=0, column=1, padx=5)
        self.combo_list.append(combo)
        ttk.Button(common_category, image=self.add_ico, command=self.add_category).grid(row=0, column=2)
        common_category.grid(sticky='w')

        ttk.Separator(self, orient=HORIZONTAL).grid(row=1, sticky='we', pady=5)

        common_items = ttk.Frame(self, width=150, height=250)
        common_items.grid(row=2)

        for i, item in enumerate(self.items):
            product = item.product

            item_frame = ttk.Frame(common_items)
            item_frame.grid(row=i, sticky='we')

            ttk.Label(item_frame, text=product.name, wraplength=200).grid(row=0, sticky='w')
            category_frame = ttk.Frame(item_frame)
            category_frame.grid(row=1, sticky='we')
            ttk.Label(category_frame, text='Категория ').grid(row=0, column=0)
            if product.category:
                ttk.Label(category_frame, text=product.category.name).grid(row=0, column=1)
            else:
                category = ttk.Combobox(category_frame)
                category.state(['readonly'])
                category.product = product
                category.grid(row=0, column=1, padx=5)
                category.bind('<<ComboboxSelected>>', self.select_category)
                self.combo_list.append(category)

    def select_category(self, e: Event):
        category = e.widget.get()
        product = e.widget.product
        product.category = self.categories[category]

    def set_categories(self):
        self.categories = {category.name: category for category in CategoryStorage.list()}
        self.values = list(self.categories.keys())
        for combo in self.combo_list:
            combo['values'] = self.values

    def add_category(self):
        category = askstring(' ', 'Введите категорию')
        if category:
            data = {'name': self.format(category)}
            CategoryStorage.add(data)
            self.set_categories()

    def init_data(self, ticket_json: str):
        ticket_parser = TicketParser.model_validate_json(ticket_json)
        self.ticket_orm = TicketORM.from_pydantic(ticket_parser)
        self.items = self.ticket_orm.purchases
        for item in self.items:
            filter = {
                'name': item.product.name
            }
            product = ProductStorage.list(filter_by=filter)
            if product:
                item.product = product[0]

    @staticmethod
    def format(s: str) -> str:
        s = s.strip()
        return s[0].upper() + s[1:].lower()
