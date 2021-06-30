#!/usr/bin/python3
#-*- coding: utf-8 -*-

'''
FPGA Client oblect.
'''

import sys
import time
import pickle
import socket
import threading

import app_logger
import tools

class FPGAClient():
    '''
    FPGA-клиент.
    '''

    _flag_server_connected = False # True - клиент подключен к серверу
    _flag_connection_process = False # True - идет процесс подключения к серверу
    _flag_sending_status = False # True - последняя отправка была успешной
    _flag_break_connection_process = False # True - прекратить попытку соединения

    _host = 'localhost' # хост по умолчанию
    _port = 49094 # порт по умолчанию

    #todo: какие константы можно вынести во внешний файл?
    _CONNECTION_ATTEMPT_NUM = 10 # число попыток подключения к серверу
    _TRANSMIT_CHUNK_SIZE = 2048 # размер передаваемого сообщения
    _TIME_TRY_TO_CONNECT = 1 # интервал попытки подключения к серверу
    _NAME_C_DRIVER = 'mem_access.so' # путь к драйверу управления ОЗУ

    def __init__(self):
        '''
        При инициализации создаем логгер по умолчанию (в консоль)
        Этот логгер будет использоваться если его не переопределили методом get_logger
        '''
        self.logger = app_logger.get_logger(__name__)
        self.logger.addHandler(app_logger.get_stream_handler())

    def get_logger(self, name):
        '''
        Получить логгер от основного приложения
        '''
        self.logger = app_logger.get_logger(name)

    def set_host_port(self, host, *port):
        '''
        Задание хоста и порта (по умолчанию localhost:49094)
        '''
        if type(host) == str:
            if tools.check_ip_adress(host):
                self._host = host
                self.logger.debug(f'Host has been changed to {self._host}!')
        if len(port) == 1:
            if type(port[0]) == int:
                self._port = port[0]
                self.logger.debug(f'Port has been changed to {self._port}!')

    def connect_to_server(self):
        '''
        Осуществить попытку подключения к серверу
        '''
        if not (self._flag_server_connected or self._flag_connection_process):
            self.logger.info(f'Connecting to the server {self._host}:{self._port}...')
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.thread_conn = threading.Thread(target=self._try_to_connect)
            self.thread_conn.start()
        else: self.logger.warning(f'Can\'t connect during other connection session!')

    def _try_to_connect(self):
        '''
        Ожидание запуска сервера, если он не запущен
        _CONNECTION_ATTEMPT_NUM раз через _TIME_TRY_TO_CONNECT секунд
        '''
        count = 1
        self._flag_connection_process = True
        start_time = time.time()
        while not self._flag_server_connected:
            if self._flag_break_connection_process:
                break
            if (self._CONNECTION_ATTEMPT_NUM-count<=0) or ((time.time()-start_time)>self._TIME_TRY_TO_CONNECT*self._CONNECTION_ATTEMPT_NUM):
                self.logger.warning(f'There are no more attempts or time!')
                self.close_connection() # закрываем клиентский сокет
                break # больше не пытаемся подключиться
            self.logger.debug(f'Attempt №{count}')
            try:
                self.sock.connect((self._host, self._port))
                self._flag_server_connected = True # успешное подключение
                self.logger.info(f'Connected successfully!')
                self.create_controller()
                break # больше не пытаемся подключиться
            except Exception:
                # неудачная попытка подключения, пытаемся по новой
                time.sleep(self._TIME_TRY_TO_CONNECT)
                count += 1
                self.logger.warning(f'Failed!')
        self._flag_connection_process = False

    def send(self, data):
        '''
        Отправка данных на сервер
        '''
        self._flag_sending_status = False
        self.data_from_server = []
        if self._flag_server_connected:
            try:
                request = pickle.dumps(data)
                data_size = sys.getsizeof(request)
                #todo: получение и передача всех данных???
                assert data_size <= self._TRANSMIT_CHUNK_SIZE
                self.sock.send(request)
                self.logger.debug(f'Data transmitted successfully!')
                data = self.sock.recv(self._TRANSMIT_CHUNK_SIZE)
                if not data:
                    raise BrokenPipeError
                self.data_from_server = pickle.loads(data)
                self.logger.debug(f'Data received successfully!')
                self._flag_sending_status = True
            except AssertionError:
                # размер данных слишком большой
                self.logger.warning(f'Can\'t transmit data, because it has big size!')
            except BrokenPipeError:
                # соединение отсутствует
                self.logger.info('Connection is lost!')
                self.close_connection()

    def close_connection(self):
        '''
        Закрываем сокет, отключаемся от сервера
        '''
        try:
            self.sock.close()
            del self.sock
            del self.thread_conn
            self._flag_server_connected = False
            self.logger.info(f'Connection closed!')
        except AttributeError:
            self.logger.info(f'FPGAClient has no attribute sock!')

    def stop_server(self):
        '''
        Остановка сервера посылкой команды 255.
        '''
        self.logger.info(f'Trying to shut down the server!')
        data = [255, ]
        self.send(data)
        if self._flag_sending_status: self.logger.info(f'The server is not running now!')
        self.close_connection()

    def create_controller(self):
        '''
        Создаем контроллер памяти на сервере
        '''
        self.logger.info(f'Trying to create memory controller on the server!')
        data = [252, self._NAME_C_DRIVER]
        self.send(data)
        if self._flag_sending_status: self.logger.info(f'Memory controller has been created!')

    def check_connection(self):
        '''
        Проверить соединение с сервером
        '''
        self.logger.info(f'Trying to check connection with the server!')
        data = [254, ]
        self.send(data)
        if self._flag_sending_status: self.logger.info(f'Server is already connected at {self._host}:{self._port}...')
        else: self.logger.warning(f'Server is not connected!')

if __name__ == '__main__':
    mine = FPGAClient()
    mine.check_connection()
    mine.set_host_port('127.0.0.1', 49094)
    mine.connect_to_server()
    mine.check_connection()
    mine.create_controller()
    mine.close_connection()
    mine.check_connection()
    mine.connect_to_server()
    mine.check_connection()
    mine.stop_server()
    mine.check_connection()