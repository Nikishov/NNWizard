#!/usr/bin/python3
#-*- coding: utf-8 -*-

'''
Main app of FPGA control software.
Use --mode='c' to launch in console mode.
'''

import os
import sys
import time
import argparse
import threading
import matplotlib.pyplot as plt
import numpy as np

import tools
import app_logger
import fpga_client
from gui_main import MainWindow

# настройка парсера аргументов вызова из терминала (уточнить как вызывать)
parser = argparse.ArgumentParser()
parser.add_argument('--mode', type=str, default='g', help='Launch Mode')
args = parser.parse_args()

class MainApp():

    _flag_server_works_local = False  # True - сервер запущен локально

    #todo: какие константы можно вынести во внешний файл
    LOGGER_NAME = 'MainApp' # имя логгера
    TIME_CHECK_LOCAL_SERVER = 0.5 # интервал проверки запуска сервера на локалхосте
    PATH_FPGA_CLIENT = os.path.dirname(os.path.realpath(__file__))
    PATH_SETTINGS_DIRECTORY = os.path.join(PATH_FPGA_CLIENT, 'settings')
    PATH_SETTINGS_IP_FILE = os.path.join(PATH_SETTINGS_DIRECTORY, 'ip_list.conf')
    PATH_LOGS_DIRECTORY = os.path.join(PATH_FPGA_CLIENT, 'logs')
    PATH_LOG_FILE = app_logger.get_log_file_path(PATH_LOGS_DIRECTORY)

    def plot_program_result_history(self):
        plt.stem(np.delete(np.array(self.program_result_history), np.where(np.array(self.program_result_history) < 2.5)))
        plt.show()

    def test_matrix(self):
        '''
        Тестирование матрицы
        '''
        try:
            self.logger.info('Trying to test the matrix!')
            # 1. проверить готовность ПЛИС (это значит ожидание флага готовности)
            fpga_state_reg_addr = 0xC0000000
            data = [5, fpga_state_reg_addr, 0x1, 10] # ждем появления в ОЗУ 0x1 в течении 10 секунд
            self.fpga_client.send(data)
            assert self.fpga_client.data_from_server[0]

            # 2. отправить команду на проведение тестирования (это значит записать данные по адресу)
            fifo_addr = 0xC0000010
            data = [2, fifo_addr, 0xA1]
            self.fpga_client.send(data)

            # 3. отправить запрос на ожидание
            flags_reg_addr = 0xC0000004
            data = [5, flags_reg_addr, 0x1, 10]
            self.fpga_client.send(data)
            assert self.fpga_client.data_from_server[0]

            # 4. отправить запрос на чтение результата
            test_data_reg_addr = 0xC0000040
            data = [3, test_data_reg_addr, 16, 4]
            self.fpga_client.send(data)

            # 5. переводим напряжения в сопротивления
            try:
                assert len(self.fpga_client.data_from_server) == 16
                self.test_data = list(map(tools.conv_to_resistance, self.fpga_client.data_from_server))
                # один канал с погрешностями, поэтому его корректируем отдельно
                for x in range(4, 8):
                    self.test_data[x] = tools.conv_to_resistance_second(self.fpga_client.data_from_server[x])
                for i,item in enumerate(self.test_data):
                    self.logger.info(f"Memristor №{i+1}: {round(item,2)} kOhm")
            except AssertionError:
                self.test_data = [0 for i in range(16)]
                self.logger.warning(f'Data size is not correct!')

        except AssertionError:
            self.test_data = [0 for i in range(16)]
            self.logger.warning(f'Something wrong!')

    def program_element(self,target_resistance,tolerance_resistance,flag_save_history,number_attempts,element_number):

        print(target_resistance)
        print(tolerance_resistance)
        print(flag_save_history)
        print(number_attempts)
        print(element_number)
        pass

        #подготовка слова
        '''
        11..0 - целевое значение сопротивления, переведенное в значение АЦП;
        23..12 - допустимое отклонение от целевого значения;
        26..24 - максимальное количество попыток программирования;
        27 - режим измерения “гребенки” (1 - включено, 0 - выключено);
        31..28 - номер программируемого элемента (от 0 до 15).
        '0b 0000 0 000 000000000000 000000000000'
        '''
        word = (element_number - 1) << 1
        word = (word + flag_save_history) << 3
        word = (word + number_attempts) << 12
        word = (word + (tools.conv_to_voltage(target_resistance * (1 + tolerance_resistance / 100)) - tools.conv_to_voltage(target_resistance))) << 12
        word = (word + tools.conv_to_voltage(target_resistance))

        print(bin(word))
        #1.

        self.logger.info('Trying to test the matrix!')
        # 1. проверить готовность ПЛИС (это значит ожидание флага готовности)
        fpga_state_reg_addr = 0xC0000000
        data = [5, fpga_state_reg_addr, 0x1, 10] # ждем появления в ОЗУ 0x1 в течении 10 секунд
        self.fpga_client.send(data)
        assert self.fpga_client.data_from_server[0]

        #2. Мы отправляем 2 слова: идентификатор и слово данных вот так - request(4, [0xb2, data], 0xC0000010, 0)
        fifo_addr = 0xC0000010
        data = [4, fifo_addr, [0xb2, word], 0]
        self.fpga_client.send(data)

        #3.
        flags_reg_addr = 0xC0000004
        data = [5, flags_reg_addr, 0x2, 20]
        self.fpga_client.send(data)
        assert self.fpga_client.data_from_server[0]

        #4.
        # value finish
        self.program_result = 0
        prog_data_reg_addr = 0xC0000080
        data = [1, prog_data_reg_addr]
        self.fpga_client.send(data)
        self.program_result = self.fpga_client.data_from_server[0]

        # all history
        if flag_save_history == 1:
            buff_addr = 0xC0004000
            data_history = [3, buff_addr, 461, 4]
            self.fpga_client.send(data_history)
            print(self.fpga_client.data_from_server)

        #5.
        if element_number in [5, 6, 7, 8]:
            self.program_result = tools.conv_to_resistance_second(self.program_result)
        else:
            self.program_result = tools.conv_to_resistance(self.program_result)

        if flag_save_history == 1:
            try:
                assert len(self.fpga_client.data_from_server) == 461
                if element_number in [5,6,7,8]:
                    # один канал с погрешностями, поэтому его корректируем отдельно
                    self.program_result_history = list(map(tools.conv_to_resistance_second, self.fpga_client.data_from_server))
                else:
                    self.program_result_history = list(map(tools.conv_to_resistance, self.fpga_client.data_from_server))
            except AssertionError:
                self.program_result_history = [0 for i in range(461)]
                self.logger.warning(f'Data size is not correct!')

    ## ОТЛАЖЕННЫЕ
    def __init__(self):
        '''
        Инициализация программы
        '''
        self.create_logger()
        self.check_settings_files()
        self.fpga_client = fpga_client.FPGAClient()
        self.fpga_client.get_logger(self.LOGGER_NAME)
        self.start_local_for_debug()

    def run(self, run_mode):
        '''
        Запуск приложения в заданном режиме
        '''
        if run_mode == 'c':
            '''
            Консольный режим
            '''
            # connect logger
            self.logger.addHandler(app_logger.get_stream_handler())
            # show prompt in console
            self.logger.info('Console mode not implemented!')
        elif run_mode == 'g':
            '''
            Режим графического интерфейса
            '''
            # create main window object
            self.gui = MainWindow(self)
            # connect logger
            self.logger.addHandler(app_logger.get_text_handler(self.gui.text))
            # bind closing event
            self.gui.protocol('WM_DELETE_WINDOW', self.on_quitting)
            # show main window
            self.gui.mainloop()

    def start_local_for_debug(self):
        '''
        Если указан localhost то запускаем ещё и сервер в отдельном потоке
        '''
        self.set_host_from_file()
        if self.fpga_client._host in ['localhost', '127.0.0.1', '']:
            self._flag_server_works_local = True
            self.start_local_server()
            #todo: проверить успех старта?
            self.fpga_client.connect_to_server()

    def start_local_server(self):
        '''
        Запуск сервера локально в отдельном потоке
        '''
        self.logger.info(f'Trying to start the server on the localhost...')
        self.thread_ls = threading.Thread(target=self.launch_server)
        self.thread_ls.start()
        time.sleep(self.TIME_CHECK_LOCAL_SERVER)
        if self.thread_ls.is_alive():
            self.logger.info(f'The server is running on the localhost!')
        else:
            self.logger.info(f'Can\'t start the server on the localhost!')

    def launch_server(self):
        if sys.platform == "linux" or sys.platform == "linux2":
            os.system('python3 ' + os.path.join('server','server.py'))
        elif sys.platform == "win32":
            os.system('py ' + os.path.join('server','server.py'))

    def on_quitting(self):
        '''
        Метод вызывается при закрытии графического окна
        '''
        #todo: закрытие программы в момент подключения

        #if self.fpga_client._flag_connection_process:
        #    self.fpga_client._flag_break_connection_process = True
        #    print('!!!!')
        #while self.fpga_client._flag_connection_process:
        #    print(self.fpga_client._flag_break_connection_process)
        #    pass

        if self._flag_server_works_local:
            self.fpga_client.stop_server()
        self.fpga_client.close_connection()
        self.gui.destroy()

    def create_logger(self):
        '''
        Создание журнала
        '''
        # получение логгера
        self.logger = app_logger.get_logger(self.LOGGER_NAME)
        # установка файла для ведения журнала
        self.logger.addHandler(app_logger.get_file_handler(self.PATH_LOG_FILE))

    def check_settings_files(self):
        '''
        Проверка наличия файлов настройки
        '''
        # директория настроек
        if not os.path.exists(self.PATH_SETTINGS_DIRECTORY):
            os.mkdir(self.PATH_SETTINGS_DIRECTORY)
            self.logger.debug(f'{self.PATH_SETTINGS_DIRECTORY} has been created!')
        # файл настроек IP адресов
        if not os.path.exists(self.PATH_SETTINGS_IP_FILE):
            with open(self.PATH_SETTINGS_IP_FILE, 'w') as ip_list_file:
                self.ip_list = []
            self.logger.debug(f'{self.PATH_SETTINGS_IP_FILE} has been created!')

    def delete_logs(self):
        '''
        Очистка директории с лог-файлами кроме текущего лога.
        '''
        flag_error = False
        if os.path.exists(self.PATH_LOGS_DIRECTORY):
            for log_file in os.listdir(self.PATH_LOGS_DIRECTORY):
                log_path = os.path.join(self.PATH_LOGS_DIRECTORY, log_file)
                if log_path != self.PATH_LOG_FILE:
                    try:
                        os.remove(log_path)
                    except Exception:
                        flag_error = True
        # проверка возникновения ошибок
        if not flag_error:
            self.logger.debug(f'The directory for logs is clear!')
        else:
            self.logger.warning(f'There are some erros during clearing the logs directory!')

    def read_host_list_from_file(self):
        '''
        Чтение истории хостов
        '''
        self.logger.debug(f'Trying to read IP config file!')
        host_list = []
        try:
            # читаем историю хостов в файле PATH_SETTINGS_IP_FILE
            with open(self.PATH_SETTINGS_IP_FILE, 'r') as ip_list_file:
                for ip_adress in ip_list_file:
                    host_list.append(ip_adress[:-1])
            self.logger.debug(f'IP config file found!')
        except FileNotFoundError:
            # если файла PATH_SETTINGS_IP_FILE не существует (вероятность -> 0)
            self.logger.debug(f'IP config file not found!')
        return host_list

    def write_host_list_to_file(self, host_list):
        '''
        Запись списка хостов в файл
        '''
        # запишем в файл
        with open(self.PATH_SETTINGS_IP_FILE, 'w') as ip_list_file:
            ip_list_file.write("\n".join(host_list)+"\n")
        self.logger.debug(f'Rewriting IP config file!')

    def add_host_to_history(self, ip_adress):
        '''
        Добавление IP адреса в историю адресов
        '''
        host_list = self.read_host_list_from_file()
        if ip_adress in host_list:
            # если есть, то удалим, чтобы он был на первом месте потом
            host_list.remove(ip_adress)
        # вставляем на первое место
        host_list.insert(0, ip_adress)
        # записать
        self.write_host_list_to_file(host_list)

    def set_host_from_file(self):
        '''
        Получение ip адреса из файла PATH_SETTINGS_IP_FILE
        '''
        host_list = self.read_host_list_from_file()
        if host_list:
            self.fpga_client.set_host_port(host_list[0])
            self.logger.debug(f'{self.fpga_client._host} now is the host!')

    def connect(self, *args):
        '''
        Подключение к серверу
        '''
        #1. считать настройки
        self.set_host_from_file()
        #2. подключиться
        self.fpga_client.connect_to_server()

    def CheckConnection(self):
        self.fpga_client.check_connection()

    def CloseConnection(self):
        self.fpga_client.close_connection()

    def StopServer(self):
        self.fpga_client.stop_server()

main = MainApp()
main.run(args.mode)