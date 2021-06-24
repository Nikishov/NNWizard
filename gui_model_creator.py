import tkinter as tkn

class ModelCreator(tkn.Frame):

    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.controller = master.master
        l = tkn.Label(self,text = 'Hello ModelCreator!')
        l.pack()