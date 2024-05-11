from abc import abstractmethod
from tkinter import *
from tkinter import messagebox
from tkinter import ttk

from .dialog import ttkDialog


class _QueryDialog(ttkDialog):
    errormessage = ''

    def __init__(self, title, prompt,
                 initialvalue=None,
                 minvalue=None, maxvalue=None,
                 parent=None):

        self.prompt = prompt
        self.minvalue = minvalue
        self.maxvalue = maxvalue

        self.initialvalue = initialvalue

        super().__init__(parent, title)

    def destroy(self):
        self.entry = None
        super().destroy()

    def body(self, master):

        w = ttk.Label(master, text=self.prompt)
        w.grid(row=0, column=0, padx=5, pady=5)

        self.entry = ttk.Entry(master, name="entry")
        self.entry.grid(row=1, column=0, padx=5, pady=(0, 5))

        if self.initialvalue is not None:
            self.entry.insert(0, self.initialvalue)
            self.entry.select_range(0, END)

        return self.entry

    @abstractmethod
    def getresult(self):
        ...

    def validate(self):
        try:
            result = self.getresult()
        except ValueError:
            messagebox.showwarning(
                "Illegal value",
                self.errormessage + "\nPlease try again",
                parent=self
            )
            return 0

        if self.minvalue is not None and result < self.minvalue:
            messagebox.showwarning(
                "Too small",
                "The allowed minimum value is %s. "
                "Please try again." % self.minvalue,
                parent=self
            )
            return 0

        if self.maxvalue is not None and result > self.maxvalue:
            messagebox.showwarning(
                "Too large",
                "The allowed maximum value is %s. "
                "Please try again." % self.maxvalue,
                parent=self
            )
            return 0

        self.result = result

        return 1


class _QueryString(_QueryDialog):
    def __init__(self, *args, **kw):
        if "show" in kw:
            self.__show = kw["show"]
            del kw["show"]
        else:
            self.__show = None
        _QueryDialog.__init__(self, *args, **kw)

    def body(self, master):
        entry = _QueryDialog.body(self, master)
        if self.__show is not None:
            entry.configure(show=self.__show)
        return entry

    def getresult(self):
        return self.entry.get()


class _QueryInteger(_QueryDialog):
    errormessage = "Not an integer."

    def getresult(self):
        return self.getint(self.entry.get())


def askinteger(title, prompt, **kw):
    '''get an integer from the user

    Arguments:

        title -- the dialog title
        prompt -- the label text
        **kw -- see SimpleDialog class

    Return value is an integer
    '''
    d = _QueryInteger(title, prompt, **kw)
    return d.result


def askstring(title, prompt, **kw):
    '''get a string from the user

    Arguments:

        title -- the dialog title
        prompt -- the label text
        **kw -- see SimpleDialog class

    Return value is a string
    '''
    d = _QueryString(title, prompt, **kw)
    return d.result
