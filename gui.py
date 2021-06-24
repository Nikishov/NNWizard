#!/usr/bin/python3
#-*- coding: utf-8 -*-

'''
Main GUI structure
'''

import os
import tkinter as tkn
import tkinter.ttk as ttk
import gui_elements

# импорт интерфейсов для отдельных менеджеров
from gui_data_manager import DataManager
from gui_model_creator import ModelCreator
from gui_visualisation import Visualisation

class GUI():

    def __init__(self, main_window, data, *args, **kwargs):
        self.main_window = main_window
        self.data = data
        self.show_main_frame()
        self.show_toolbar()
        self.show_tools_frame()

    def show_main_frame(self):
        '''
        Main frame
        '''
        self.main_frame = tkn.Frame(self.main_window)
        self.main_frame.pack(fill=tkn.BOTH, expand=True)

    def show_toolbar(self):
        '''
        Toolbar
        '''
        toolbar = tkn.Frame(self.main_frame, bd=1, relief=tkn.RAISED)
        toolbar.pack(side=tkn.TOP, fill=tkn.X)

        # buttons launch modules
        self.img_data = tkn.PhotoImage(file=os.path.join(os.getcwd(),'icons','data.png'))
        button_data = ttk.Button(toolbar, image=self.img_data, command=lambda: self.show_tool(DataManager))
        button_data.grid(row=0, column=0)
        gui_elements.create_alt_window(button_data,'Data Manager')

        self.img_model = tkn.PhotoImage(file=os.path.join(os.getcwd(),'icons','model.png'))
        button_model = ttk.Button(toolbar, image=self.img_model, command=lambda: self.show_tool(ModelCreator))
        button_model.grid(row=0, column=1)
        gui_elements.create_alt_window(button_model,'Model Manager')

        #button_vis = ttk.Button(toolbar, text='Visualisation', command=lambda: self.show_tool(Visualisation))
        #button_vis.grid(row=0, column=2)

    def show_tools_frame(self):
        '''
        Frame for each tool
        '''
        self.tools_frame = tkn.Frame(self.main_frame)
        self.tools_frame.pack(side=tkn.BOTTOM, fill=tkn.BOTH, expand=True)
        self.tools_frame.columnconfigure(0, weight=1)
        self.tools_frame.rowconfigure(0, weight=1)

        self.tools_frames = {}
        for F in (PromptWindow, DataManager, ModelCreator, Visualisation): #todo: добавить ссылки на классы всех менеджеров
            frame = F(self.tools_frame)
            frame.data_storage = self.data
            self.tools_frames[F] = frame
            frame.grid(row=0, column=0, sticky=tkn.NSEW)

        # указываем страницу, загружаемую по умолчанию
        self.show_tool(PromptWindow)

    def show_tool(self, tool_class_name):
        '''
        Show the frame of current tool
        '''
        self.current_frame = self.tools_frames[tool_class_name]
        self.current_frame.tkraise()

class PromptWindow(tkn.Frame):

    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.controller = master.master

        frame_prompt = tkn.Frame(self)
        frame_prompt.place(relx=0.5, rely=0.5, anchor=tkn.CENTER)

        self.img_brain = tkn.PhotoImage(file=os.path.join(os.getcwd(),'icons','brain.png'))
        label_brain = tkn.Label(frame_prompt, image=self.img_brain)
        label_brain.pack(side=tkn.LEFT)

        self.img_prompt = tkn.PhotoImage(file=os.path.join(os.getcwd(),'icons','prompt.png'))
        label_prompt = tkn.Label(frame_prompt, image=self.img_prompt)
        label_prompt.pack(side=tkn.LEFT)
