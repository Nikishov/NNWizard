#!/usr/bin/python3
#-*- coding: utf-8 -*-

'''
Tkinter GUI for Neural Network Wizard.
Main Window.
'''

import tkinter as tkn
import tkinter.ttk as ttk
from tkinter import messagebox
import main_back as main_back
import gui

class MainWindow(tkn.Tk):
    def __init__(self):
        # general settings
        super().__init__()
        tkn.Tk.wm_title(self, main_back.WINDOW_NAME)
        tkn.Tk.wm_resizable(self, width=main_back.RESIZEABLE_FLAG, height=main_back.RESIZEABLE_FLAG)
        if main_back.MAXIMIZE_WINDOW:
            screen_height = self.winfo_screenheight()
            screen_width = self.winfo_screenwidth()
            tkn.Tk.wm_geometry(self, str(int(screen_width))+'x'+str(screen_height))
        self.set_defaults() # setting up default values
        self.show_GUI() # showing main parts of GUI

        # topbar menu
        top_menu = tkn.Menu(self)
        self.config(menu=top_menu)
        file_menu = tkn.Menu(top_menu, tearoff=0)
        top_menu.add_cascade(label=main_back.TOP_MENU['file_menu'][0], menu=file_menu)
        file_menu.add_command(label=main_back.TOP_MENU['file_menu'][1], command=self.exit_click)
        help_menu = tkn.Menu(top_menu, tearoff=0)
        top_menu.add_cascade(label=main_back.TOP_MENU['help_menu'][0], menu=help_menu)
        help_menu.add_command(label=main_back.TOP_MENU['help_menu'][1], command=self.about_click)

        # events handlers
        self.bind('<Escape>', self.exit_click) # closing the main window

    def show_GUI(self):
        '''
        Here we provide visualization of GUI
        '''
        self.data = main_back.DataStorage()
        self.gui = gui.GUI(self, self.data)

    def set_defaults(self):
        '''
        Here we provide resetting settings to default values
        '''
        pass

    def exit_click(self, *args):
        '''
        Quit the GUI
        '''
        self.destroy()

    def about_click(self):
        '''
        About the GUI
        '''
        messagebox.showinfo(main_back.TOP_MENU['help_menu'][1], main_back.ABOUT_INFORMATION)

if __name__ == '__main__':
    root = MainWindow()
    root.mainloop()
