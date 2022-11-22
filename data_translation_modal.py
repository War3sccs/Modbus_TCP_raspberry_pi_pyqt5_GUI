# ！python3
# -*- coding: UTF-8 -*-

# @Time    :2020/5/8 21:30
# @Author  :Wu Yuming
# @Email   :61508712@qq.com
# @File    :
# @Software:PyCharm
# @Version :1.0


# TODO:1、数值转换
# 寄存器转二进制开关量,16位
def decimal_to_binary(Number):
    temp = int(Number)
    temp = bin(temp)[2:].rjust(16, '0')  # int转二进制
    return temp


# 二进制转字符
def binary_to_ascii_string(binary_string):
    return chr(int(binary_string, 2))


#  寄存器转字符
def register_binary(register_value):
    temp = int(register_value)
    temp = decimal_to_binary(temp)
    high = '0b' + temp[0:8]
    high = binary_to_ascii_string(high)
    low = '0b' + temp[8:16]
    low = binary_to_ascii_string(low)
    result = [high, low]
    return result


# 拼接字符串-读寄存器
def construct_string_from_data_read(register_data_list):
    string_data_raw = []
    for data in register_data_list:
        string = register_binary(data)
        string_data_raw.append(string)
    return string_data_raw


# 摘取拼接结果中有效的部分-根据字符串长度寄存器的反馈
def get_result_string(string_length, register_data_list):
    string_with_invalid_data = construct_string_from_data_read(register_data_list)
    if string_length > 0:
        count = string_length
        result_string = ''
        for item_high, item_low in string_with_invalid_data:
            result_string = result_string + item_high
            result_string = result_string + item_low
        # print(result_string)
        result_string = result_string[:count]
    else:
        result_string = 'No string read'
    return result_string


# 统计长度，拆成list
def string_dismantle(raw_string):
    string_length = len(raw_string)
    string_list_result = []
    for i in range(string_length):
        string_list_result.append(raw_string[i])
    return [string_length, string_list_result]


# 将字符串list转成ASCII码序列
def string_to_ascii(string_dismantle_result):
    result_list = []
    for i in range(len(string_dismantle_result[1])):
        temp = ord(string_dismantle_result[1][i])
        result_list.append(temp)
    return result_list


# ASCII码转二进制8位
def decimal_to_binary_8_bit(Number):
    temp = int(Number)
    temp = bin(temp)[2:].rjust(8, '0')  # int转二进制
    return temp


# 2个ASCII码转成16位二进制序列
def binary_list_16_bit_from_2_ascii(high, low):
    register_binary_data = ''
    temp = decimal_to_binary_8_bit(high)
    register_binary_data = register_binary_data + temp
    temp = decimal_to_binary_8_bit(low)
    register_binary_data = register_binary_data + temp
    # print(register_binary_data)  # 转为16位二进制序列
    return register_binary_data


# 由16位二进制序列转为寄存器整数
def register_data_from_binary_list_16_bit(register_binary_data_16_bit):
    string_list_register = '0b' + register_binary_data_16_bit
    register_data_write = int(string_list_register, 2)
    # print(register_data_write)
    return register_data_write


# 准备写入的寄存器数据序列/
# 除开机字符串外，通道1/通道2字符串修改也使用此函数
def meter_string_write(raw_string, string_length):
    temp_list_dismantle = string_dismantle(raw_string)
    result_list = [temp_list_dismantle[0]]  # 写入开机字符串长度
    ascii_sequence = string_to_ascii(temp_list_dismantle)  # 转成ascii序列
    for i in range(string_length):
        if 2 * i + 1 < len(ascii_sequence):
            binary_data_register = binary_list_16_bit_from_2_ascii(ascii_sequence[2 * i], ascii_sequence[2 * i+1])
        elif 2 * i + 1 == len(ascii_sequence):
            binary_data_register = binary_list_16_bit_from_2_ascii(ascii_sequence[2 * i], 0)
        else:
            binary_data_register = binary_list_16_bit_from_2_ascii(0, 0)
        register_data_write = register_data_from_binary_list_16_bit(binary_data_register)
        result_list.append(register_data_write)
    print(result_list)
    return result_list


# 测试函数
if __name__ == '__main__':
    test = decimal_to_binary(10)
    print(test)
    test = register_binary(27904)
    print(test)
    test = construct_string_from_data_read([28769,
                                            25700,
                                            27749,
                                            11622,
                                            27759,
                                            30510,
                                            25455,
                                            27904,
                                            0,
                                            0,
                                            ])
    print(test)
    test = get_result_string(15,
                             [28769,
                              25700,
                              27749,
                              11622,
                              27759,
                              30510,
                              25455,
                              27904,
                              0,
                              0,
                              ])
    print(test)
    test = get_result_string(0,
                             [28769,
                              25700,
                              27749,
                              11622,
                              27759,
                              30510,
                              25455,
                              27904,
                              0,
                              0,
                              ])
    print(test)
    string_test = string_dismantle('www.paddle-flow.com')
    print(string_test)
    string_ascii = string_to_ascii(string_test)
    print(string_ascii)
    test = binary_list_16_bit_from_2_ascii(119, 119)
    print(test)
    test = register_data_from_binary_list_16_bit(test)
    print(test)
    string_test = meter_string_write('www.paddle-flow.com', 10)
    print(string_test)
    string_test = meter_string_write('paddle-flow.com', 10)
    print(string_test)
    test = get_result_string(19, [30583, 30510, 28769, 25700, 27749, 11622, 27759, 30510, 25455, 27904])
    print(test)
