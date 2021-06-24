#!/usr/bin/python3
#-*- coding: utf-8 -*-

'''
Neural Network Wizard.
This software is aimed to help people create neural networks.

'''

#import toolbar_list
import os
import io
import importlib
import pandas as pd

WINDOW_NAME = 'Neural Network Wizard'
MAXIMIZE_WINDOW = True
ABOUT_INFORMATION = '''Neural Network Wizard. 2021'''
RESIZEABLE_FLAG = True
#TOOLBARS_PATH = 'tools'
TOP_MENU = {'file_menu': ['File','Exit'],
            'help_menu': ['Help','About']}

'''
toolbars = os.listdir(TOOLBARS_PATH)
for toolbar in toolbars:
    if toolbar.split('_')[-1] == 'gui.py':
        print('_'.join(toolbar.split('_')[:-1])+'_back.py')
        if os.path.exists(os.path.join(TOOLBARS_PATH,'_'.join(toolbar.split('_')[:-1])+'_back.py')):
            print(os.path.join(TOOLBARS_PATH,toolbar))
            importlib.import_module(TOOLBARS_PATH,toolbar)
'''

class DataStorage():

    file_path = ''

    def load_csv_pandas(self):
        self.csv_data = pd.read_csv(self.file_path)

    def set_csv_data(self, new_csv_data):
        self.csv_data = new_csv_data.copy()

    def get_csv_info(self):
        buffer = io.StringIO()
        self.csv_data.info(buf=buffer)
        return buffer.getvalue()

    def head_csv(self):
        result = self.csv_data.head()
        return result

    def check_dataset(self, dataset):
        '''
        '''
        pass

if __name__ == '__main__':
    pass