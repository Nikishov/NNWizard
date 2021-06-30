#!/usr/bin/python3
#-*- coding: utf-8 -*-

import time
import random
import threading, queue

class FPGA():
    '''
    FPGA
    '''

    def __init__(self):
        pass

    def ready(self):
        '''
        Готова работать
        '''
        RAM[0xC0000000] = 0x1
        print('    FPGA: пишу в адрес 0xC0000000 - %s, жду...' % (hex(0x1)))

    def busy(self):
        '''
        Занята работой
        '''
        RAM[0xC0000000] = 0x0
        print('    FPGA: пишу в адрес 0xC0000000 - %s, занята...' % (hex(0x0)))

    def run(self):
        '''
        Работа ПЛИС
        '''
        self.ready()
        while True:
            mode = RAM[0xC0000010].get() # это дыра
            print('    FPGA: читаю адрес 0xC0000010 - %s' % (hex(mode)))
            if mode == 777:  break
            self.work(mode)
        print('    FPGA: Эмулятор корректно завершил работу!')

    def set_result_id(self, result_id):
        '''
        Изменение флага результата
        '''
        RAM[0xC0000004] = result_id
        print('    FPGA: пишу в адрес 0xC0000004 - %s' % (hex(result_id)))

    def write_word(self, addr, word):
        '''
        Изменение флага результата
        '''
        RAM[addr] = word
        print('    FPGA: пишу в адрес %s - %s' % (hex(addr), hex(word)))

    def work(self, mode):
        '''
        Работа ПЛИС в отдельном потоке
        '''
        if mode == 0xA1:
            '''
            Работа в режиме тестирования
            '''
            self.busy() # ПЛИС не готова выполнять другие команды
            self.set_result_id(0x0) # Результата работы нет
            print('    FPGA: работаю в режиме тестирования')
            # пишем в память результаты тестирования 40, 44, 48, 4C... 7C 4 байта (32 бит шина)
            addrs = [0xC0000040+i*4 for i in range(16)]
            for addr in addrs:
                value = random.randint(0, 4095)
                print('    FPGA: пишу в адрес %s - %s' % (hex(addr), hex(value)))
                RAM[addr] = value
            self.set_result_id(0x1)
            self.ready()

        elif mode == 0xB2:
            '''
            Работа в режиме программирования
            '''
            self.busy() # ПЛИС не готова выполнять другие команды
            self.set_result_id(0x0) # Результата работы нет
            print('    FPGA: работаю в режиме программирования')
            print('    FPGA: жду слово данных...')
            data = RAM[0xC0000010].get()
            print('    FPGA: слово данных получено!')
            '''

            '0b00000000000000000000000000000000'
            '0b 0000 0 000 000000000000 000000000000'
            data = int('0b11111101000000100001001100001001', 2)
            11..0 - целевое значение сопротивления, переведенное в значение АЦП;
            23..12 - допустимое отклонение от целевого значения;
            26..24 - максимальное количество попыток программирования;
            27 - режим измерения “гребенки” (1 - включено, 0 - выключено);
            31..28 - номер программируемого элемента (от 0 до 15).
            '''

            mask = int('0b00000000000000000000111111111111', 2)
            target_R = data & mask
            print('    FPGA: целевое значение сопротивления %d' % (target_R))

            mask = int('0b00000000111111111111000000000000', 2)
            tolerance_R = (data & mask) >> 12
            print('    FPGA: допустимое отклонение сопротивления %d' % (tolerance_R))

            mask = int('0b00000111000000000000000000000000', 2)
            number_prog = (data & mask) >> 24
            print('    FPGA: количество попыток %d' % (number_prog))

            mask = int('0b00001000000000000000000000000000', 2)
            mode_prog = (data & mask) >> 27
            print('    FPGA: режим программирования %d' % (mode_prog))

            mask = int('0b11110000000000000000000000000000', 2)
            number_elem = (data & mask) >> 28
            print('    FPGA: номер программируемого элемента %d' % (number_elem))


            step = 4095 / 461
            num = int((target_R*461) / 4095)
            resistance = 0
            for i in range(num):
                resistance = resistance + step
                if mode_prog == 1: # сохранять историю
                    self.write_word(0xC0004000 + i*4, int(resistance))

            self.write_word(0xC0000080, int(resistance))
            self.set_result_id(0x2)
            self.ready()

class read_data():
    '''
    обработка функции чтения данных по адресу в памяти
    '''
    def __call__(self, addr):
        print('    ДРАЙВЕР: читаю адрес %s' % (hex(addr)))
        if addr == 0xC0000010:
            data = 0
            print('    ДРАЙВЕР: прочитал %s' % (hex(0x0)))
        else:
            print('    ДРАЙВЕР: прочитал %s' % (hex(RAM[addr])))
            data = RAM[addr]
        return data

class write_data():
    '''
    обработка функции записи данных
    '''
    def __call__(self, addr, data):
        if addr == 0xC0000010:
            RAM[addr].put(data)
        else:
            RAM[addr] = data
        print('    ДРАЙВЕР: Запись по адресу %s данных %s' % (hex(addr),hex(data)))

class CDLL():
    '''
    Класс эмулятор работы ctypes
    '''
    def __init__(self, path):
        self.path = path
        self.read_data = read_data()
        self.write_data = write_data()

c_int = None
RAM = {0xC0000000+i: 0 for i in range(30000)}
RAM[0xC0000010] = queue.Queue()
fpga = FPGA()
thread_fpga = threading.Thread(target=fpga.run)
thread_fpga.start()