# ！python3
# -*- coding: UTF-8 -*-

# @Time    :2021/5/21 19:48
# @Author  :Wu Yuming
# @Email   :61508712@qq.com
# @File    :Modbus-TCP
# @Software:PyCharm
# @Version :1.0

import modbus_tk
import modbus_tk.defines as cst
import modbus_tk.modbus_tcp as modbus_tcp


def define_modbus_tcp_connection(ip_address):
    # PLC sever, PC　client
    try:
        # 连接MODBUS TCP从机
        master = modbus_tcp.TcpMaster(host=ip_address)
        master.set_timeout(5.0)
    except Exception as err:
        print(err)
        master = -1
    finally:
        return master


def read_modbus_tcp(modbust_tcp_connection, start_register, read_register_quantity):
    process_data = [-1]
    try:
        # 读保持寄存器
        data_read = modbust_tcp_connection.execute(1,
                                                   cst.READ_HOLDING_REGISTERS,
                                                   start_register,
                                                   read_register_quantity,
                                                   )
        process_data = list(data_read)
        # logger.info(data_read)
    except Exception as err:
        print(err)
        process_data.append(-1)
        process_data[0] = -1
    finally:
        return process_data


def write_modbus_tcp(modbust_tcp_connection, write_register, write_data):
    process_data = [-1]
    try:
        # 写寄存器地址为0的保持寄存器
        data_write = modbust_tcp_connection.execute(1,
                                                    cst.WRITE_SINGLE_REGISTER,
                                                    write_register,
                                                    output_value=write_data)
        process_data = list(data_write)
        # logger.info(data_write)
        # logger.info(master.execute(1, cst.READ_HOLDING_REGISTERS, 0, 1))
    except Exception as err:
        print(err)
        process_data.append(-1)
        process_data[0] = -1
    finally:
        return process_data


if __name__ == "__main__":
    connection = define_modbus_tcp_connection("10.100.0.10")
    print(connection)
    result_read = read_modbus_tcp(connection, 0, 42)
    print(result_read)
    result_read = read_modbus_tcp(connection, 0, 42)
    print(result_read)
    result_read = read_modbus_tcp(connection, 0, 42)
    print(result_read)
    del connection
    # result_write = write_modbus_tcp(connection, 33, 1)
    # print(result_write)


    # # 读输入寄存器
    # logger.info(master.execute(1, cst.READ_INPUT_REGISTERS, 0, 16))
    # # 读线圈寄存器
    # logger.info(master.execute(1, cst.READ_COILS, 0, 16))
    # # 读离散输入寄存器
    # logger.info(master.execute(1, cst.READ_DISCRETE_INPUTS, 0, 16))
    # 单个读写寄存器操作
    # # 写寄存器地址为0的线圈寄存器，写入内容为0（位操作）
    # logger.info(master.execute(1, cst.WRITE_SINGLE_COIL, 0, output_value=0))
    # logger.info(master.execute(1, cst.READ_COILS, 0, 1))
    # # 多个寄存器读写操作
    # # 写寄存器起始地址为0的保持寄存器，操作寄存器个数为4
    # logger.info(master.execute(1, cst.WRITE_MULTIPLE_REGISTERS, 0, output_value=[20,21,22,23]))
    # logger.info(master.execute(1, cst.READ_HOLDING_REGISTERS, 0, 4))
    # # 写寄存器起始地址为0的线圈寄存器
    # logger.info(master.execute(1, cst.WRITE_MULTIPLE_COILS, 0, output_value=[0,0,0,0]))
    # logger.info(master.execute(1, cst.READ_COILS, 0, 4))
