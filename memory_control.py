#!/usr/bin/python3
#-*- coding: utf-8 -*-

import ctypes
import time
import logging
import os

class MemoryController():

    def __init__(self, library_path):
        '''
        При инициализации указываем путь до библиотеки
        и устанавливаем настройки по умолчанию
        '''
        self.library_path = os.path.join(os.getcwd(), library_path) # путь до библиотеки
        self.driver = ctypes.CDLL(self.library_path) # подключение библиотеки на C
        self.driver.read_data.restype = ctypes.c_int
        self.driver.read_data.argtypes = [ctypes.c_int]
        self.driver.write_data.argtypes = [ctypes.c_int, ctypes.c_int]
        self.logger = logging.getLogger(__name__)
        self.logger.info('MemoryController has been created!')

    def read_word(self, address):
        '''
        Прочитать слово из памяти по заданному адресу
        Принимает:
            address (int) - адрес памяти для чтения
        Возвращает:
            word (int) - слово данных
        '''
        word = self.driver.read_data(address)
        self.logger.info('Reading ' + hex(word) + ' from ' + hex(address))
        return word

    def write_word(self, address, word):
        '''
        Записать слово в память по заданному адресу
        Принимает:
            address (int) - адрес памяти для записи
            word (int) - слово данных
        '''
        self.driver.write_data(address, word)
        self.logger.info('Writing ' + hex(word) + ' to ' + hex(address))

    def read_data(self, address, num_elements, shift):
        '''
        Прочитать блок данных из памяти начиная с заданного адреса
        Принимает:
            num_elements (int) - число читаемых слов из памяти
            address (int) - адрес памяти для начала чтения
            shift (int) - шаг чтения
        Возвращает:
            data (list) - данные из памяти
        '''
        data = []
        for i in range(num_elements):
            data.append(self.read_word(address + i*shift))
        return data

    def write_data(self, address, data, shift):
        '''
        Записать блок данных в память по заданному адресу
        Принимает:
            data (list) - список, содержащий данные для записи
            address (int) - адрес памяти для начала записи
            shift (int) - шаг записи
        '''
        for i,datum in enumerate(data):
            self.write_word(address + i*shift, datum)

    def wait_flag(self, address, value, timing):
        '''
        Ожидать появления значения в памяти заданное время
        Принимает:
            address (int) - адрес памяти для чтения
            value (int) - значение
            timing (int) - время (секунды)
        Возвращает:
            ready (bool) - готовность
        '''
        self.logger.info('Waiting ' + hex(value) + ' in ' + hex(address) + ' for ' + str(timing) + 's')
        ready = False
        for i in range(timing):
            if self.read_word(address) == value:
                ready = True
                break
            time.sleep(1)
        self.logger.info('The value has been obtained!')
        return ready

    def request(self, request):
        '''
        Обработать запрос от сервера
        Принимает:
            request (list) - запрос от сервера
        Возвращает:
            answer (list) - ответ серверу
        '''
        try:
            if request[0] == 1:
                address = request[1]
                answer = [self.read_word(address)]
            elif request[0] == 2:
                '''
                Запись одного слова данных (32 bit) (word) в ОЗУ по адресу (address)
                '''
                address = request[1]
                word = request[2]
                self.write_word(address, word)
                answer = [self.read_word(address)]
            elif request[0] == 3:
                '''
                Чтение пакета данных из ОЗУ начиная с адреса (address) с шагом (shift)
                в количестве (num_elements) слов
                '''
                address = request[1]
                num_elements = request[2]
                shift = request[3]
                answer = self.read_data(address, num_elements, shift)
            elif request[0] == 4:
                address = request[1]
                data = request[2]
                shift = request[3]
                self.write_data(address, data, shift)
                answer = self.read_data(address, len(data), shift)
            elif request[0] == 5:
                '''
                Запрос ожидания заданного значения (value) в ОЗУ по адресу (address)
                в течении заданного времени (timing)
                '''
                address = request[1]
                value = request[2]
                timing = request[3]
                answer = [self.wait_flag(address, value, timing)]
            else:
                answer = ['there is no such request']
        except Exception:
            answer = ['Error in MemoryController']
        return answer

    def __repr__(self):
        description = '''Класс работы с памятью. Использует бибилотеку на C.

Атрибуты:
    driver - библиотека работы с памятью на C
    library_path - путь до библиотеки

Методы:
    read_word(address)
    write_word(address, word)
    read_data(num_elements, address, shift)
    write_data(data, address, shift)
    wait_flag(address, value, timing)
        '''
        return description
