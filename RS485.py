# ！python3
# -*- coding: UTF-8 -*-

# @Time    :2021/2/7 19:48
# @Author  :Wu Yuming
# @Email   :61508712@qq.com
# @File    :RS-485
# @Software:PyCharm
# @Version :1.2


import serial  # 导入串口驱动程序模块
import serial.tools.list_ports  # 导入串口搜索模块
import modbus_tk  # 导入modbus RTU模块
import modbus_tk.defines as cst  # 导入modbus RTU模块
from modbus_tk import modbus_rtu  # 导入modbus RTU模块


# TODO: 1、建立modbus连接和PLC通信。
# TODO:(1)建立串口连接。
# TODO:  1）搜索可用串口
def Search_Serial():
    Serial_ports = []
    Result = serial.tools.list_ports.comports()
    if len(Result) == 0:
        print('搜索不到串口!')
        Serial_ports.append('无串口!')
    else:
        for i in range(0, len(Result)):
            Serial_ports.append(str(Result[i]))
            print(Serial_ports[i])
    return Serial_ports


# TODO: 2)建立RS-485连接
def define_rs_485_connection(COM, baudrate, bytesize, parity, stopbits, address):
    PORT = COM
    try:
        master = modbus_rtu.RtuMaster(serial.Serial(port=PORT,
                                                    baudrate=baudrate,  # 9600 波特率
                                                    bytesize=bytesize,  # 8  数据位
                                                    parity=parity,  # 'N'  校验位
                                                    stopbits=stopbits,  # 1   停止位
                                                    xonxoff=0))
        master.set_timeout(5)
        master.set_verbose(False)
    except modbus_tk.modbus_rtu.ModbusInvalidResponseError as err:
        print(err)
        master = -1
    finally:
        return master


# TODO:(2)通过RS-485从仪表读取寄存器数据
def modbus_read(rs485connection, address, startRegister, quantityRegister):
    process_data = []  # 读取的寄存器数据
    logger = modbus_tk.utils.create_logger("console")
    try:
        # logger.info('connected')
        register_data_read = master.execute(address,  # PLC站号 1
                                            cst.READ_HOLDING_REGISTERS,  # 读寄存器操作
                                            startRegister,  # 起始寄存器,2代默认值0
                                            quantityRegister,  # 读寄存器的个数，2代默认值65
                                            )  # 读寄存器
        process_data = list(register_data_read)
        # logger.info(register_data_read)
        # logger.info('register_data_read\' type:' + str(type(register_data_read)))
        # logger.info('master\' type' + str(type(master)))
        # logger.info('process_data\' type' + str(type(process_data)))
        # logger.info('process_data:' + str(process_data))
    except modbus_tk.modbus_rtu.ModbusInvalidResponseError as err:
        print(err)
        process_data.append(-1)
        process_data[0] = -1
    finally:
        return process_data


# TODO:(3)通过RS-485向仪表写入单个寄存器数据
def modbus_write(COM, baudrate, bytesize, parity, stopbits, address, register, data_write):
    PORT = COM
    # logger = modbus_tk.utils.create_logger("console")
    try:
        master = modbus_rtu.RtuMaster(serial.Serial(port=PORT,
                                                    baudrate=baudrate,  # 9600 波特率
                                                    bytesize=bytesize,  # 8  数据位
                                                    parity=parity,  # 'N'  校验位
                                                    stopbits=stopbits,  # 1   停止位
                                                    xonxoff=0))
        master.set_timeout(5)
        master.set_verbose(False)
        # logger.info('connected')
        register_data_write = master.execute(address,  # PLC站号1
                                             cst.WRITE_SINGLE_REGISTER,  # 写寄存器操作
                                             register,  # 写入的寄存器
                                             output_value=data_write  # 写入的数值
                                             )  # 写单个寄存器
        # logger.info(register_data_write)  # 显示写入纪录
    except modbus_tk.modbus_rtu.ModbusInvalidResponseError as err:
        print(err)
        register_data_write = -1
    finally:
        return register_data_write


# TODO:(4)通过RS-485向仪表写入多个寄存器数据
# 一次写入寄存器数量过多的时候会失败，试过超过20个，就会失败。
def modbus_write_multiple(COM, baudrate, bytesize, parity, stopbits, address, register, data_write):
    PORT = COM
    # logger = modbus_tk.utils.create_logger("console")
    try:
        master = modbus_rtu.RtuMaster(serial.Serial(port=PORT,
                                                    baudrate=baudrate,  # 9600 波特率
                                                    bytesize=bytesize,  # 8  数据位
                                                    parity=parity,  # 'N'  校验位
                                                    stopbits=stopbits,  # 1   停止位
                                                    xonxoff=0))
        master.set_timeout(5)
        master.set_verbose(False)
        # logger.info('connected')
        register_data_write = master.execute(address,  # PLC站号1
                                             cst.WRITE_MULTIPLE_REGISTERS,  # 写多个寄存器操作
                                             register,  # 起始写入的寄存器地址
                                             output_value=data_write  # 写入的数据
                                             )  # 写多个寄存器
        # logger.info(register_data_write)  # 显示写入纪录
    except modbus_tk.modbus_rtu.ModbusInvalidResponseError as err:
        print(err)
        register_data_write = -1
    finally:
        return register_data_write


# TODO:(2)通过RS-485读取开关量数据
def modbus_read_boolean_data(COM, baudrate, bytesize, parity, stopbits, address, startRegister, quantityRegister):
    PORT = COM
    process_data = []  # 读取的寄存器数据
    # logger = modbus_tk.utils.create_logger("console")
    try:
        master = modbus_rtu.RtuMaster(serial.Serial(port=PORT,
                                                    baudrate=baudrate,  # 9600 波特率
                                                    bytesize=bytesize,  # 8  数据位
                                                    parity=parity,  # 'N'  校验位
                                                    stopbits=stopbits,  # 1   停止位
                                                    xonxoff=0))
        master.set_timeout(5)
        master.set_verbose(False)
        # logger.info('connected')

        register_data_read = master.execute(address,  # PLC站号 1
                                            cst.READ_DISCRETE_INPUTS,  # 读单个线圈
                                            startRegister,  # 起始寄存器,2代默认值0
                                            quantityRegister,  # 读寄存器的个数，2代默认值65
                                            )  # 读寄存器
        process_data = list(register_data_read)
        # logger.info(register_data_read)
        # logger.info('register_data_read\' type:' + str(type(register_data_read)))
        # logger.info('master\' type' + str(type(master)))
        # logger.info('process_data\' type' + str(type(process_data)))
        # logger.info('process_data:' + str(process_data))
    except modbus_tk.modbus_rtu.ModbusInvalidResponseError as err:
        print(err)
        process_data.append(-1)
        process_data[0] = -1
    finally:
        return process_data

# TODO:2、连接Modbus RS-485错误返回值列表：
# 2.1 搜索不到串口、没有连接到485转USB转换器：返回get_data=[]
# 2.2 搜索到串口，连接到485转USB转换器，但连不到仪表，返回get_data=[-1]

# TODO:3、实际测试中遇到的问题级解决
# 杜工仪表部分参数，需要同时操作2个或多个寄存器才能修改时，只写入单个寄存器，可能有回应，也可能没有回应。
# FS编号的参数，只写入1个寄存器，会有回应，但不成功。SDTU参数的寄存器，没有回应且不成功。
# SDTU要同时操作41038和41039这2个寄存器，不能和之后的网址混合。


# 测试函数
if __name__ == '__main__':
    # Serial_ports=Search_Serial()
    # print(Serial_ports)
    connect = define_rs_485_connection('/dev/ttyUSB0', 9600, 8,'N', 1, 1 )
    get_data = modbus_read(connect, 1,  1, 1)
    print('get_data=' + str(get_data))
    # write_data = modbus_write('COM15', 9600, 8, 'N', 1, 1, 1, 1)  # 1002为modbus地址，寄存器地址41003
    # print(write_data)
    # multiple_write_data = modbus_write_multiple('COM15', 9600, 8, 'N', 1, 1, 1032,
    #                                             [0, 71])
    # print(multiple_write_data)
    # multiple_write_data = modbus_write_multiple('COM15', 9600, 8, 'N', 1, 1, 1013,
    #                                             [1, 235])
    # print(multiple_write_data)
    # get_boolean_data = modbus_read_boolean_data('COM5', 9600, 8, 'N', 1, 2, 0, 16)
    # print('get_data=' + str(get_boolean_data))
