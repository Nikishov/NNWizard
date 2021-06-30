#!/usr/bin/python3
#-*- coding: utf-8 -*-

'''
Main window of FPGA control software
Icons from https://icon-icons.com/ru/pack/Freebie-Flat-Icons-Vol5/2313

'''

import os
import copy
import tkinter as tkn
import tkinter.ttk as ttk
from tkinter import messagebox

import gui_settings
import gui_elements

class MainWindow(tkn.Tk):

    WINDOW_TITLE = 'FPGAClient'
    WINDOW_GEOMETRY = '800x480'
    WIDTH_FRAME_MAIN = 0.70

    def __init__(self, main_app, *args, **kwargs):
        #todo: сделать через super()
        tkn.Tk.__init__(self, *args, **kwargs)
        tkn.Tk.wm_title(self, self.WINDOW_TITLE)
        tkn.Tk.wm_resizable(self, width=False, height=False)
        #self.geometry(self.WINDOW_GEOMETRY)
        self.screen_height = self.winfo_screenheight()
        self.screen_width = self.winfo_screenwidth()
        self.main_app = main_app # по этой ссылке доступны все методы из main
        self.create_menu()
        self.create_main_window()
        self.create_binders()

    def create_menu(self):
        '''
        Create menu bar
        '''
        menu = tkn.Menu(self)
        self.config(menu=menu)
        menu_file = tkn.Menu(menu, tearoff=0)
        menu.add_cascade(label='File', menu=menu_file)
        menu_file.add_command(label='Exit', command=self.exit_click)
        menu_help = tkn.Menu(menu, tearoff=0)
        menu.add_cascade(label='Help', menu=menu_help)
        menu_help.add_command(label='About', command=self.about_click)

    def exit_click(self, *args):
        '''
        Exit from the app
        '''
        self.main_app.on_quitting()

    def about_click(self):
        '''
        About the app
        '''
        messagebox.showinfo('About', f'{self.WINDOW_TITLE}, 2021')

    def create_binders(self):
        '''
        Binders
        '''
        self.bind('<Escape>', self.exit_click)
        self.bind('<t>', lambda event: self.main_app.test_matrix()) #загрузка модели клавишой space

    def create_main_window(self):
        '''
        Create main GUI of the app
        '''

        ## ----- Toolbar
        frame_toolbar = tkn.Frame(self, relief=tkn.RAISED, borderwidth=2)
        frame_toolbar.pack(fill=tkn.X, anchor=tkn.N)

        self.img_connect = tkn.PhotoImage(file=os.path.join(os.getcwd(),'icons','connect.png'))
        self.img_settings = tkn.PhotoImage(file=os.path.join(os.getcwd(),'icons','settings.png'))

        button_connect = ttk.Button(frame_toolbar, image=self.img_connect, command=self.main_app.connect)
        button_connect.grid(row=0, column=0)

        button_settings = ttk.Button(frame_toolbar, image=self.img_settings, command=lambda: gui_settings.SettingsWindow(self))
        button_settings.grid(row=0, column=1)

        gui_elements.create_alt_window(button_connect,'Connect to the server')
        gui_elements.create_alt_window(button_settings,'App settings')

        ## ----- Main

        frame_main_functions = ttk.Notebook(self)
        frame_main_functions.pack(fill=tkn.X, expand=True, anchor=tkn.N)

        # ----- Test tab
        tab_test = ttk.Frame(frame_main_functions)
        frame_main_functions.add(tab_test, text ='Matrix') # добавляем новую вкладку

        tab_test_frame_button = tkn.Frame(tab_test)
        tab_test_frame_button.grid(row=0, column=0, padx=5, pady=5, sticky=tkn.NS)

        self.img_test = tkn.PhotoImage(file=os.path.join(os.getcwd(),'icons','test.png'))
        tab_test_frame_button_test = ttk.Button(tab_test_frame_button, image=self.img_test, command=self.test_matrix)
        tab_test_frame_button_test.grid(row=0, column=0, sticky=tkn.NW)
        gui_elements.create_alt_window(tab_test_frame_button_test,'Test matrix')

        # ----- Matrix frame
        self.frame_matrix = tkn.LabelFrame(tab_test, text='Matrix map')
        self.frame_matrix.grid(row=0, column=1, padx=5, pady=5, sticky=tkn.NS)
        self.show_matrix()

        # ----- Programming frame
        frame_program = tkn.LabelFrame(tab_test, text='Programming')
        frame_program.grid(row=0, column=2, padx=5, pady=5, ipadx=5, ipady=5, sticky=tkn.NSEW)

        label_target = ttk.Label(frame_program, text='Target')
        label_target.grid(row=0, column=0, sticky=tkn.E)
        self.entry_target = ttk.Entry(frame_program, width=7)
        self.entry_target.grid(row=0, column=1, sticky=tkn.W)
        #self.target = entry_target.get()

        label_tolerance = ttk.Label(frame_program, text='Tolerance')
        label_tolerance.grid(row=1, column=0, sticky=tkn.E)
        self.entry_tolerance = ttk.Entry(frame_program, width=7)
        self.entry_tolerance.grid(row=1, column=1, sticky=tkn.W)
        #self.tolerance = entry_tolerance.get()

        label_attempt = ttk.Label(frame_program, text='Attempt')
        label_attempt.grid(row=2, column=0, sticky=tkn.E)
        self.combobox_attempt = ttk.Combobox(frame_program, values=[1,2,3,4,5,6,7], width=2)
        self.combobox_attempt.grid(row=2, column=1, sticky=tkn.W)
        self.combobox_attempt.current(0)

        label_history = ttk.Label(frame_program, text='History')
        label_history.grid(row=3, column=0, sticky=tkn.E)
        self.check_val = tkn.IntVar()
        self.checkbutton_history = tkn.Checkbutton(frame_program, variable=self.check_val)
        self.checkbutton_history.grid(row=3, column=1, sticky=tkn.W)



        self.button_show_history = ttk.Button(frame_program, text='Show history', command=self.click_button_show_history)
        self.button_show_history.grid(row=4, column=0, columnspan=3)
        self.button_show_history['state'] = 'disabled'

        # ----- Log
        frame_bottom = tkn.Frame(self, bg='red')
        frame_bottom.pack(fill=tkn.X, anchor=tkn.N)

        frame_for_text = ttk.Frame(frame_bottom)
        frame_for_text.grid(row=0, column=0, sticky='news')

        self.text = tkn.Text(frame_for_text, width=75, height=10, wrap=tkn.WORD)
        scy = ttk.Scrollbar(frame_for_text, command=self.text.yview)
        self.text.configure(yscrollcommand=scy.set)
        self.text.grid(row=0, column=0, sticky='news')
        scy.grid(row=0, column=1, sticky='ns')

        # ----- Фрейм для кнопок лога
        frame_for_log_button = ttk.Frame(frame_bottom)
        frame_for_log_button.grid(row=1, column=0, sticky=tkn.W)

        # ----- Кнопка Очистить лог
        button_clearlog = ttk.Button(frame_for_log_button, text='Clear log', command=self.clear_log)
        button_clearlog.grid(row=0, column=0, sticky=tkn.W)

    def click_button_show_history(self):
        '''
        Визуализация истории
        '''
        print(self.main_app.program_result_history)
        self.main_app.plot_program_result_history()

    def show_matrix(self):
        '''
        Визуализация матрицы из кнопок
        '''
        k = 1
        self.matrix = []
        for i in range(4):
            self.matrix.append([])
            for j in range(4):
                b = tkn.Button(self.frame_matrix, text=f'{k}', width=2, height=1)
                b.memristor_number = k
                b.bind('<Button-1>', self.program_mem)
                b.grid(row=i, column=j)
                self.matrix[-1].append(b)
                k += 1

    def program_mem(self, event):
        '''
        '''
        #1. Получить 5 параметров
        try:
            target_resistance = int(self.entry_target.get()) #прочитать из поля Entry
            tolerance_resistance = int(self.entry_tolerance.get()) #прочитать из поля Entry
            flag_save_history = int(self.check_val.get()) #прочитать флаг
            number_attempts = int(self.combobox_attempt.get()) #прочитать значение из выпадающего списка
            element_number = event.widget.memristor_number
        #2. Передать их в main_app
        except:
            print('Неверные входные данные')
            return
        self.main_app.program_element(target_resistance, tolerance_resistance, flag_save_history, number_attempts,
                                      element_number)
        #3. Обновить подпись кнопки
        # self.main_app.program_result
        event.widget.configure(text=int(self.main_app.program_result))

        #4. Разлочить кнопку истории если стоял флаг истории
        self.button_show_history['state'] = 'normal'


    def test_matrix(self):
        '''
        '''
        self.main_app.test_matrix()
        self.write_test_results_to_buttons()

    def write_test_results_to_buttons(self):
        k = 0
        for i in range(4):
            for j in range(4):
                self.matrix[i][j].configure(text=int(self.main_app.test_data[k]))
                k+=1

    def temp_test(self):
        pass

    def kill_server(self):
        pass

    def clear_log(self):
        self.text.config(state='normal')
        self.text.delete('1.0', tkn.END)
        self.text.config(state='disabled')