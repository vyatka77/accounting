from tkinter import *
from tkinter import _get_temp_root, _destroy_temp_root  # type: ignore[attr-defined]
from tkinter import ttk
from tkinter.simpledialog import _place_window, _setup_dialog  # type: ignore[attr-defined]


class ttkDialog(Toplevel):
    '''Class to open dialogs.

    This class is intended as a base class for custom dialogs
    '''

    def __init__(self, parent, title=None):
        '''Initialize a dialog.

        Arguments:

            parent -- a parent window (the application window)

            title -- the dialog title
        '''
        master = parent
        if master is None:
            master = _get_temp_root()

        Toplevel.__init__(self, master)

        self.withdraw()  # remain invisible for now
        # If the parent is not viewable, don't
        # make the child transient, or else it
        # would be opened withdrawn
        if parent is not None and parent.winfo_viewable():
            self.transient(parent)

        if title:
            self.title(title)

        _setup_dialog(self)

        self.parent = parent

        self.result = None

        body = ttk.Frame(self)
        self.initial_focus = self.body(body)
        body.grid(row=0, column=0, sticky='nswe')

        self.buttonbox()

        if self.initial_focus is None:
            self.initial_focus = self

        self.protocol("WM_DELETE_WINDOW", self.cancel)

        _place_window(self, parent)

        self.initial_focus.focus_set()

        # wait for window to appear on screen before calling grab_set
        self.wait_visibility()
        self.grab_set()
        self.wait_window(self)

    def destroy(self):
        '''Destroy the window'''
        self.initial_focus = None
        Toplevel.destroy(self)
        _destroy_temp_root(self.master)

    #
    # construction hooks

    def body(self, master):
        '''create dialog body.

        return widget that should have initial focus.
        This method should be overridden, and is called
        by the __init__ method.
        '''
        pass

    def buttonbox(self):
        '''add standard button box.

        override if you do not want the standard buttons
        '''

        box = ttk.Frame(self)

        w = ttk.Button(box, text="OK", width=10, command=self.ok, default=ACTIVE)
        w.pack(side=LEFT, padx=5, pady=5, expand=True, anchor='e')
        w = ttk.Button(box, text="Cancel", width=10, command=self.cancel)
        w.pack(side=LEFT, padx=5, pady=5, expand=True, anchor='w')

        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)

        box.grid(row=1, column=0, sticky='we')

    #
    # standard button semantics

    def ok(self, event=None):

        if not self.validate():
            self.initial_focus.focus_set()  # put focus back
            return

        self.withdraw()
        self.update_idletasks()

        try:
            self.apply()
        finally:
            self.cancel()

    def cancel(self, event=None):

        # put focus back to the parent window
        if self.parent is not None:
            self.parent.focus_set()
        self.destroy()

    #
    # command hooks

    def validate(self):
        '''validate the data

        This method is called automatically to validate the data before the
        dialog is destroyed. By default, it always validates OK.
        '''

        return 1  # override

    def apply(self):
        '''process the data

        This method is called automatically to process the data, *after*
        the dialog is destroyed. By default, it does nothing.
        '''

        pass  # override
