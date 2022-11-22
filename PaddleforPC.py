# ！python3
# -*- coding: UTF-8 -*-

# @Time    :2019/12/30 20:17
# @Author  :Wu Yuming
# @Email   :61508712@qq.com
# @File    :Paddle for PC
# @Software:PyCharm
# @Version :1.0.003

import os

from PyQt5.QtGui import *
import PyQt5.sip
import webbrowser  # 导入网页模块
import sys
from PyQt5.QtWidgets import *  # 导入ＰｙＱｔ５库，绘制ＧＵＩ界面
from PyQt5 import QtCore, QtGui, QtWidgets  # 导入ＰｙＱｔ５库，绘制ＧＵＩ界面
from PyQt5.QtCore import QTimer  # 导入Qt库定时器
import GUI  # 导入主窗口界面
import datetime  # 导入日期时间模块
import connect_dialog  # 导入通信设置子窗体
import search_dialog  # 导入搜索仪表子窗体
import Modbus_adress_modify  # 导入设置Modbus地址子窗体
import period_modify  # 导入修改采集周期子窗体
import parameter_modify  # 导入修改仪表参数子窗体
import RS485  # 导入ＲＳ－４８５连接模块
import messagebox_in_Chinese  # 导入提示信息框
import save_search_meter_result  # 导入搜索仪表结果保存模块
import numpy as np  # 导入numpy模块
import pandas as pd  # 导入pandas模块
import import_setting_prepare  # 导入仪表配置文件数据准备
from decimal import Decimal  # 导入浮点运算整数模块
from decimal import getcontext  # 导入浮点运算整数模块
import data_translation_modal  # 导入数据转换模块

if hasattr(sys, 'frozen'):
    os.environ['PATH'] = sys._MEIPASS + ";" + os.environ['PATH']  # 导入Qt5Core库
sys.setrecursionlimit(4000)  # set the maximum depth as 4000  修改最大归递次数

# TODO:全局变量
Serial_ports = []  # 可用串口列表
Connect_status_meter = 0  # 仪表连接状态，0：断开;1：连接2代仪表;2：连接2代plus仪表;3：连接3代仪表
Modbus_parameter = {'PORT': '无串口!',  # 串口号
                    'baudrate': 9600,  # 9600 波特率
                    'bytesize': 8,  # 8 数据位
                    'parity': 'N',  # 'N'  校验位
                    'stopbits': 1,  # 1   停止位
                    'address': 1,  # PLC站号
                    }  # Modbus连接参数
Time_count = 0  # 定时器始值

# 搜索结果：可用仪表列表
available_meter = [[],  # 储存站号
                   [],  # 储存编号FS
                   [],  # 储存硬件版本:1:2代标准版本仪表;2:2代plus仪表;3:3代仪表
                   ]
# TODO:数据结构
# 仪表485传输数据结构

# 2代仪表的数据结构
# 读
Meter_data_column = ['DateTime',  # 当前时间
                     '40001',  # 'R', '产品型号', '6', '无', '', '=6，利亨昌双通道流量计；'],
                     '40002',  # 'R', '产品版本号', '36001', '无', '', '=36001，版本号为V3.6.001；'],
                     '40003',  # 'R', '流量计编号', '0-999999999', '无', '', ''],
                     '40004',  # 'R', None, None, None, None, None],
                     '40005',  # 'R', '第一路瞬时流量', '0-9999', 'L/H', '', '整数部分'],
                     '40006',  # None, None, '0-9999', None, None, '小数部分'],
                     '40007',  # 'R', '第二路瞬时流量', '0-9999', 'L/H', '', '整数部分'],
                     '40008',  # None, None, '0-9999', None, None, '小数部分'],
                     '40009',  # 'R', '第一路累计容量', '0-999999999', 'L', '', '整数部分'],
                     '40010',  # None, None, None, None, None, None],
                     '40011',  # None, None, '0-9', None, None, '小数部分'],
                     '40012',  # 'R', '第二路累计容量', '0-999999999', 'L', '', '整数部分'],
                     '40013',  # None, None, None, None, None, None],
                     '40014',  # None, None, '0-9', None, None, '小数部分'],
                     '40015',  # None, None, None, '探头数量标志位', '', '位0', '=1，双探头；=0，单探头'],
                     # None, None, None, '双探头偏差报警标志位', '', '位1', '=1，报警；=0，正常'],
                     # [None, None, None, '第一路上限报警标志位', '', '位2', '=1，报警；=0，正常'],
                     # [None, None, None, '第一路下限报警标志位', '', '位3', '=1，报警；=0，正常'],
                     # [None, None, None, '第二路上限报警标志位', '', '位4', '=1，报警；=0，正常'],
                     # [None, None, None, '第二路下限报警标志位', '', '位5', '=1，报警；=0，正常'],
                     # [None, None, None, '流量校正方式', '', '位6', '00,单点校正；01,两点校正；         \\n10,三点校正'],
                     # [None, None, None, None, '', '位7', None],
                     # [None, None, None, '脉冲统计方式', '', '位8', '=1，脉冲时间间隔；             \\n=0，统计单位时间脉冲数'],
                     # [None, None, None, '偏差报警使能状态', '', '位9', '=1，开启；=0，关闭'],
                     # ['第一路上限报警使能状态', '', '位10', '=1，开启；=0，关闭'],
                     # ['第一路下限报警使能状态', '', '位11', '=1，开启；=0，关闭'],
                     # ['第二路上限报警使能状态', '', '位12', '=1，开启；=0，关闭'],
                     # ['第二路下限报警使能状态', '', '位13', '=1，开启；=0，关闭'],
                     # ['数据读更新标志位', '', '位14', '=1，更新；=0，无 （来自远传）'],
                     # ['编号写更新标志位', '', '位15', '=1，更新；=0，无 （来自表头）'],
                     '40016',  # ['域名写更新标志位', '', '位0', '=1，更新；=0，无 （来自表头）'],
                     # ['偏差报警屏蔽状态', '', '位1', '=1，屏蔽；=0，无屏蔽'],
                     # ['第一路上限报警屏蔽状态', '', '位2', '=1，屏蔽；=0，无屏蔽'],
                     # ['第一路下限报警屏蔽状态', '', '位3', '=1，屏蔽；=0，无屏蔽'],
                     # ['第二路上限报警屏蔽状态', '', '位4', '=1，屏蔽；=0，无屏蔽'],
                     # ['第二路下限报警屏蔽状态', '', '位5', '=1，屏蔽；=0，无屏蔽'],
                     '40017',  # 'R', '单位统计时间', '1-120秒或8-1000个脉冲', '', '',
                     # '如果“脉冲统计方式”选择“统计单位\\n时间脉冲数”，则该参数为“统计脉冲\\n数的单位时间长度”，范围是1-120秒\\n。
                     # 如果“脉冲统计方式”选择“脉冲时\\n间间隔”，则该参数为“多少个脉冲的\\n平均值”，范围是8-1000个。'],
                     '40018',  # 'R', '偏差报警修正', '0-200(20.0)', '', '', '第一路探头倍差强制修正值'],
                     '40019',  # 'R', '偏差报警比例', '0-100', '%', '', '偏差报警比例值,为0即禁止报警'],
                     '40020',  # 'R', '第一路上限报警值', '0-999', 'L/H', '', '整数部分'],
                     '40021',  # None, None, '0-999', None, None, '小数部分'],
                     '40022',  # 'R', '第一路下限报警值', '0-999', 'L/H', '', '整数部分'],
                     '40023',  # None, None, '0-999', None, None, '小数部分'],
                     '40024',  # 'R', '第二路上限报警值', '0-999', 'L/H', '', '整数部分'],
                     '40025',  # None, None, '0-999', None, None, '小数部分'],
                     '40026',  # 'R', '第二路下限报警值', '0-999', 'L/H', '', '整数部分'],
                     '40027',  # None, None, '0-999', None, None, '小数部分'],
                     '40028',  # 'R', '第一路满刻度设定值', '0-999', 'L/H', '', '整数部分'],
                     '40029',  # None, None, '0-999', None, None, '小数部分'],
                     '40030',  # 'R', '第二路满刻度设定值', '0-999', 'L/H', '', '整数部分'],
                     '40031',  # None, None, '0-999', None, None, '小数部分'],
                     '40032',  # 'R', '第一路单位时间脉冲数', '', '', '', ''],
                     '40033',  # 'R', '第二路单位时间脉冲数', '', '', '', ''],
                     '40034',  # 'R', '第一路SPM', '', '', '', ''],
                     '40035',  # 'R', '第二路SPM', '', '', '', ''],
                     '40036',  # 'R', '第一路A点校正脉冲数', '0-60000', 'P', '', ''],
                     '40037',  # 'R', '第一路A点校正容积数', '0-60000', 'ML', '', ''],
                     '40038',  # 'R', '第一路B点校正脉冲数', '0-60000', 'P', '', ''],
                     '40039',  # 'R', '第一路B点校正容积数', '0-60000', 'ML', '', ''],
                     '40040',  # 'R', '第一路C点校正脉冲数', '0-60000', 'P', '', ''],
                     '40041',  # 'R', '第一路C点校正容积数', '0-60000', 'ML', '', ''],
                     '40042',  # 'R', '第二路A点校正脉冲数', '0-60000', 'P', '', ''],
                     '40043',  # 'R', '第二路A点校正容积数', '0-60000', 'ML', '', ''],
                     '40044',  # 'R', '第二路B点校正脉冲数', '0-60000', 'P', '', ''],
                     '40045',  # 'R', '第二路B点校正容积数', '0-60000', 'ML', '', ''],
                     '40046',  # 'R', '第二路C点校正脉冲数', '0-60000', 'P', '', ''],
                     '40047',  # 'R', '第二路C点校正容积数', '0-60000', 'ML', '', ''],
                     '40048',  # 'R', '远传编号', '0-999999999', '无', '', ''],
                     '40049',  # 'R', None, None, None, None, None],
                     '40050',  # 'R', '域名长度', '0-30', '', '', ''],
                     '40051',  # 'R', '平台域名', '第1个字符', '', '', ''], [None, None, None, '第2个字符', '', '', ''],
                     '40052',  # 'R', None, '第3个字符', '', '', ''], [None, None, None, '第4个字符', '', '', ''],
                     '40053',  # 'R', None, '第5个字符', '', '', ''], [None, None, None, '第6个字符', '', '', ''],
                     '40054',  # 'R', None, '第7个字符', '', '', ''], [None, None, None, '第8个字符', '', '', ''],
                     '40055',  # 'R', None, '第9个字符', '', '', ''], ['第10个字符', '', '', ''],
                     '40056',  # 'R'],['第11个字符', '', '', ''], ['第12个字符', '', '', ''],
                     '40057',  # 'R'],['第13个字符', '', '', ''],['第14个字符', '', '', ''],
                     '40058',  # 'R'],['第15个字符', '', '', ''],['第16个字符', '', '', ''],
                     '40059',  # 'R'],  ['第17个字符', '', '', ''],  ['第18个字符', '', '', ''],
                     '40060',  # 'R'],  ['第19个字符', '', '', ''], ['第20个字符', '', '', ''],
                     '40061',  # 'R'],  ['第21个字符', '', '', ''],[ ['第22个字符', '', '', ''],
                     '40062',  # 'R'],  ['第23个字符', '', '', ''], ['第24个字符', '', '', ''],
                     '40063',  # 'R'],  ['第25个字符', '', '', ''], ['第26个字符', '', '', ''],
                     '40064',  # 'R', None, '第27个字符', '', '', ''], [None, None, None, '第28个字符', '', '', ''],
                     '40065',  # 'R', None, '第29个字符', '', '', ''], [None, None, None, '第30个字符', '', '', ''],
                     '40066',  # 'R', 'Solenoid_Charge_Time', '1-499', '', '', '泵1'],
                     '40067',  # 'R', 'Max_SPM', '0-999', '', '', '泵2'],
                     '40068',  # 'R', 'Solenoid_Charge_Time', '1-499', '', '', '泵1'],
                     '40069',  # 'R', 'Max_SPM', '0-999', '', '', '泵2'],
                     'ModbusAddress',  # 当前设置modbus地址
                     ]
Meter_data = list(np.zeros(71).astype(int))
Meter_data[0] = datetime.datetime.now()  # 获取当前时间
# 写
Meter_data_write_index = list(np.arange(60) + 41001)
for i in range(len(Meter_data_write_index)):
    Meter_data_write_index[i] = str(Meter_data_write_index[i])
Meter_data_write_value = list(np.arange(60) + 1000)
Meter_data_write = pd.Series(Meter_data_write_value, index=Meter_data_write_index)

# 2代plus仪表数据结构
# 读
Meter_data_column_2_plus = list(np.arange(109) + 40001)
for i in range(len(Meter_data_column_2_plus)):
    Meter_data_column_2_plus[i] = str(Meter_data_column_2_plus[i])
Meter_data_column_2_plus.insert(0, 'DateTime')
Meter_data_column_2_plus.append('ModbusAddress')
Meter_data_2_plus = list(np.zeros(111).astype(int))
Meter_data_2_plus[0] = datetime.datetime.now()  # 获取当前时间
# 写
Meter_data_2_plus_write_index = list(np.arange(181) + 41001)
for i in range(len(Meter_data_2_plus_write_index)):
    Meter_data_2_plus_write_index[i] = str(Meter_data_2_plus_write_index[i])
Meter_data_2_plus_write_value = list(np.arange(181) + 1000)
Meter_data_2_plus_write = pd.Series(Meter_data_2_plus_write_value, index=Meter_data_2_plus_write_index)


# TODO:1.打开Paddle-flow网页
# 模块Open_website.py

# TODO:2.RS-485连接
# 模块RS485

# 搜索可用串口
def search_serial():
    global Serial_ports
    Serial_ports = []
    Serial_ports = RS485.Search_Serial()
    Connect.comboBox.clear()
    Connect.comboBox.addItems(Serial_ports)
    Search.comboBox.clear()
    Search.comboBox.addItems(Serial_ports)


# modbus参数复位
def modbus_parameter_reset():
    Modbus_parameter['PORT'] = "无串口!"  # 串口号
    Modbus_parameter['baudrate'] = 9600  # 波特率
    Modbus_parameter['bytesize'] = 8  # 数据位
    Modbus_parameter['parity'] = 'N'  # 校验位
    Modbus_parameter['stopbits'] = 1  # 停止位
    Modbus_parameter['address'] = 1  # 仪表从站站号


# TODO:3.GUI界面运行
app = QApplication(sys.argv)

# TODO:3.1主界面运行方法设计
MainWindow = GUI.Ui_MainWindow()  # 主界面定义


# TODO:3.1.1定时刷新主界面参数
# 获取当前时间
def date_time_now_text(date_time_now):
    date_time_now_text = str(date_time_now.year) + '年' + \
                         str(date_time_now.month) + '月' + \
                         str(date_time_now.day) + '日' + \
                         str(date_time_now.hour) + ':' + \
                         str(date_time_now.minute) + ':' + \
                         str(date_time_now.second)
    return date_time_now_text


# 刷新函数
def refresh_parameter():
    global Connect_status_meter
    # print(Connect_status_meter)
    # 刷新仪表数据结构中的数据
    if Connect_status_meter == 1:
        Meter_data[0] = datetime.datetime.now()
    elif Connect_status_meter == 2:
        Meter_data_2_plus[0] = datetime.datetime.now()
    # 更新时间显示
    date_time = date_time_now_text(datetime.datetime.now())
    MainWindow.label_28.setText(date_time)

    # 读取仪表信息
    get_meter_data = RS485.modbus_read(Modbus_parameter['PORT'],  # 串口号
                                       Modbus_parameter['baudrate'],  # 波特率
                                       Modbus_parameter['bytesize'],  # 数据位
                                       Modbus_parameter['parity'],  # 校验位
                                       Modbus_parameter['stopbits'],  # 停止位
                                       Modbus_parameter['address'],  # 仪表从站站号
                                       0,  # 起始寄存器
                                       1,  # 读寄存器的数量
                                       )
    if (get_meter_data == []) or (get_meter_data[0] == -1):
        Connect_status_meter = 0  # 连接modbus错误
        modbus_parameter_reset()  # 复位modbus参数
    else:
        if get_meter_data[0] == 6:
            Connect_status_meter = 1
        elif get_meter_data[0] == 7:
            Connect_status_meter = 2
    if Connect_status_meter == 1:
        get_meter_data = RS485.modbus_read(Modbus_parameter['PORT'],  # 串口号
                                           Modbus_parameter['baudrate'],  # 波特率
                                           Modbus_parameter['bytesize'],  # 数据位
                                           Modbus_parameter['parity'],  # 校验位
                                           Modbus_parameter['stopbits'],  # 停止位
                                           Modbus_parameter['address'],  # 仪表从站站号
                                           0,  # 起始寄存器
                                           65,  # 读寄存器的数量
                                           )
    elif Connect_status_meter == 2:
        get_meter_data = RS485.modbus_read(Modbus_parameter['PORT'],  # 串口号
                                           Modbus_parameter['baudrate'],  # 波特率
                                           Modbus_parameter['bytesize'],  # 数据位
                                           Modbus_parameter['parity'],  # 校验位
                                           Modbus_parameter['stopbits'],  # 停止位
                                           Modbus_parameter['address'],  # 仪表从站站号
                                           0,  # 起始寄存器
                                           109,  # 读寄存器的数量
                                           )
    # 刷新仪表数据结构中的数据
    if Connect_status_meter == 1:
        for item in range(65):
            Meter_data[item + 1] = get_meter_data[item]
    elif Connect_status_meter == 2:
        for item in range(109):
            Meter_data_2_plus[item + 1] = get_meter_data[item]

    # 刷新硬件版本
    if Connect_status_meter == 0:
        MainWindow.label_32.setText('未连接')
        MainWindow.label_32.setStyleSheet("background-color: rgb(255, 255, 0);\n")
    else:
        if Connect_status_meter == 1:
            MainWindow.label_32.setText('标准2代')
            MainWindow.label_32.setStyleSheet("background-color: rgb(255, 255, 255);\n")
        elif Connect_status_meter == 2:
            MainWindow.label_32.setText('2代plus')
            MainWindow.label_32.setStyleSheet("background-color: rgb(255, 255, 255);\n")

    # 更新当前modbus地址
    if Connect_status_meter == 1:
        Meter_data[70] = Modbus_parameter['address']
    elif Connect_status_meter == 2:
        Meter_data_2_plus[110] = Modbus_parameter['address']

    # 刷新仪表连接状态
    if Connect_status_meter == 0:
        MainWindow.label_5.setText('未连接')
        MainWindow.label_5.setStyleSheet("background-color: rgb(255, 0, 0);\n")
    else:
        MainWindow.label_5.setText("已连接")
        MainWindow.label_5.setStyleSheet("background-color: rgb(0, 255, 0);\n")

    # 刷新仪表编号
    if Connect_status_meter == 1:
        FS = Meter_data[3] * 65536 + Meter_data[4]
    elif Connect_status_meter == 2:
        FS = Meter_data_2_plus[3] * 65536 + Meter_data_2_plus[4]
    else:
        FS = 0
    FS = str(FS)
    FS_text = 'FS' + FS.rjust(9, '0')
    MainWindow.label_25.setText(FS_text)

    # 刷新仪表Modbus地址
    if Connect_status_meter == 0:
        MainWindow.label_26.setText('未连接')
        MainWindow.label_26.setStyleSheet("background-color: rgb(255, 255, 0);\n")
    else:
        MainWindow.label_26.setText(str(Modbus_parameter['address']))
        MainWindow.label_26.setStyleSheet("background-color: rgb(255, 255, 255);\n")

    # 刷新脉冲数
    # 通道1
    if Connect_status_meter == 0:
        MainWindow.lcdNumber_3.display(0)
    elif Connect_status_meter == 1:
        MainWindow.lcdNumber_3.display(Meter_data[32])
    elif Connect_status_meter == 2:
        MainWindow.lcdNumber_3.display(Meter_data_2_plus[44])
    # 通道2
    if Connect_status_meter == 0:
        MainWindow.lcdNumber_8.display(0)
    elif Connect_status_meter == 1:
        MainWindow.lcdNumber_8.display(Meter_data[33])
    elif Connect_status_meter == 2:
        MainWindow.lcdNumber_8.display(Meter_data_2_plus[45])

    # 刷新流量
    if Connect_status_meter == 0:
        flow_1 = 0
        flow_2 = 0
    elif Connect_status_meter == 1:
        # 通道1
        flow_1 = float(Meter_data[5]) + float(Meter_data[6] / 1000)  # 40005为通道1流量整数，40006为通道1流量小数
        # 通道2
        flow_2 = float(Meter_data[7]) + float(Meter_data[8] / 1000)  # 40007为通道1流量整数，40008为通道1流量小数
    elif Connect_status_meter == 2:
        # 通道1
        flow_1 = float(32768 * Meter_data_2_plus[5]) + float(Meter_data_2_plus[6] + float(Meter_data_2_plus[7]) / 1000)
        # 40005为通道1流量整数高位，40006为通道1流量整数,40007为通道1流量小数
        # 通道2
        flow_2 = float(32768 * Meter_data_2_plus[8]) + float(Meter_data_2_plus[9] + float(Meter_data_2_plus[10]) / 1000)
        # 40008为通道1流量整数高位，40009为通道1流量整数,40010为通道1流量小数
    # 在界面显示
    MainWindow.lcdNumber_2.display(flow_1)
    MainWindow.lcdNumber_6.display(flow_2)

    # 刷新累积容积
    if Connect_status_meter == 0:
        total_1 = 0
        total_2 = 0
    elif Connect_status_meter == 1:
        # 通道1
        total_1 = float(Meter_data[9]) * 65536 + float(Meter_data[10]) + float(
            Meter_data[11]) / 10  # 40009整数高位，40010整数低位，40011小数
        # print(total_1)
        # 通道2
        total_2 = float(Meter_data[12]) * 65536 + float(Meter_data[13]) + float(
            Meter_data[14]) / 10  # 40010整数高位，40011整数低位，40012小数
        # print(total_2)
    elif Connect_status_meter == 2:
        # 通道1
        total_1 = float(Meter_data_2_plus[11]) * 32768 * 32768 * 32768 + \
                  float(Meter_data_2_plus[12]) * 32768 * 32768 + \
                  float(Meter_data_2_plus[13]) * 32768 + \
                  float(Meter_data_2_plus[14]) + float(Meter_data_2_plus[15]) / 1000
        # print(total_1)
        # 通道2
        total_2 = float(Meter_data_2_plus[16]) * 32768 * 32768 * 32768 + \
                  float(Meter_data_2_plus[17]) * 32768 * 32768 + \
                  float(Meter_data_2_plus[18]) * 32768 + \
                  float(Meter_data_2_plus[19]) + float(Meter_data_2_plus[20]) / 1000
        # print(total_2)
    # 在界面显示
    MainWindow.lcdNumber.display(total_1)
    MainWindow.lcdNumber_7.display(total_2)

    # 刷新报警
    if Connect_status_meter == 0:
        # 偏流报警
        MainWindow.label_21.setText("未连接")
        MainWindow.label_21.setStyleSheet("background-color: rgb(255, 255, 0);\n")
        # 通道1流量报警
        # 过高
        MainWindow.label_20.setText("未连接")
        MainWindow.label_20.setStyleSheet("background-color: rgb(255, 255, 0);\n")
        # 过低
        MainWindow.label_19.setText("未连接")
        MainWindow.label_19.setStyleSheet("background-color: rgb(255, 255, 0);\n")
        # 通道2流量报警
        # 过高
        MainWindow.label_22.setText("未连接")
        MainWindow.label_22.setStyleSheet("background-color: rgb(255, 255, 0);\n")
        # 过低
        MainWindow.label_23.setText("未连接")
        MainWindow.label_23.setStyleSheet("background-color: rgb(255, 255, 0);\n")
    else:
        if Connect_status_meter == 1:
            flow_alarm = data_translation_modal.decimal_to_binary(Meter_data[15])  # 40015 标志状态寄存器
        elif Connect_status_meter == 2:
            flow_alarm = data_translation_modal.decimal_to_binary(Meter_data_2_plus[21])  # 40021 标志状态寄存器
        # 偏流报警
        deviation_flow = int(flow_alarm[-2])
        if deviation_flow == 1:
            MainWindow.label_21.setText("报警")
            MainWindow.label_21.setStyleSheet("background-color: rgb(255, 0, 0);\n")
        else:
            MainWindow.label_21.setText("正常")
            MainWindow.label_21.setStyleSheet("background-color: rgb(0, 255, 0);\n")
        # # 通道1流量报警
        # # 过高
        high_flow_1 = int(flow_alarm[-3])
        # print(type(high_flow_1))
        # print(high_flow_1)
        if high_flow_1 == 1:
            MainWindow.label_20.setText("报警")
            MainWindow.label_20.setStyleSheet("background-color: rgb(255, 0, 0);\n")
        else:
            MainWindow.label_20.setText("正常")
            MainWindow.label_20.setStyleSheet("background-color: rgb(0, 255, 0);\n")
        # 过低
        low_flow_1 = int(flow_alarm[-4])
        if low_flow_1 == 1:
            MainWindow.label_19.setText("报警")
            MainWindow.label_19.setStyleSheet("background-color: rgb(255, 0, 0);\n")
        else:
            MainWindow.label_19.setText("正常")
            MainWindow.label_19.setStyleSheet("background-color: rgb(0, 255, 0);\n")
        # 通道2流量报警
        # # 过高
        high_flow_2 = int(flow_alarm[-5])
        # print(type(high_flow_2))
        # print(high_flow_2)
        if high_flow_2 == 1:
            MainWindow.label_22.setText("报警")
            MainWindow.label_22.setStyleSheet("background-color: rgb(255, 0, 0);\n")
        else:
            MainWindow.label_22.setText("正常")
            MainWindow.label_22.setStyleSheet("background-color: rgb(0, 255, 0);\n")
        # 过低
        low_flow_2 = int(flow_alarm[-6])
        if low_flow_2 == 1:
            MainWindow.label_23.setText("报警")
            MainWindow.label_23.setStyleSheet("background-color: rgb(255, 0, 0);\n")
        else:
            MainWindow.label_23.setText("正常")
            MainWindow.label_23.setStyleSheet("background-color: rgb(0, 255, 0);\n")

    # 刷新采集周期
    if Connect_status_meter == 0:
        MainWindow.label_30.setText('未连接')
        MainWindow.label_30.setStyleSheet("background-color: rgb(255, 255, 0);\n")
    else:
        if Connect_status_meter == 1:
            MainWindow.label_30.setText(str(Meter_data[17]))
            MainWindow.label_30.setStyleSheet("background-color: rgb(255, 255, 255);\n")
        elif Connect_status_meter == 2:
            MainWindow.label_30.setText(str(Meter_data_2_plus[23]))
            MainWindow.label_30.setStyleSheet("background-color: rgb(255, 255, 255);\n")

    # 删除已创建对象
    del get_meter_data


MainWindow.timer = QTimer()  # 初始化定时器
MainWindow.timer.timeout.connect(refresh_parameter)  # 定时操作
MainWindow.timer.start(1000)  # 每秒刷新1次


# TODO:3.1.2 打开各个子窗体的方法
# 定义打开“通信设置”子窗体方法
def show_connect():
    Connect.show()  # 显示"通信设置"子窗体
    connect_config_modbus_option()  # 初始化modbus参数选项
    Connect.pushButton.clicked.connect(search_serial)  # 初始化搜索串口按钮动作
    Connect.pushButton_2.clicked.connect(try_connect_meter)  # 初始化仪表连接按钮动作


# 定义打开“搜索仪表”子窗体的方法
def search_meter():
    Search.show()  # 显示“搜索仪表”子窗体
    search_config_modbus_option()  # 初始化modbus参数选项
    Search.pushButton.clicked.connect(search_serial)  # 初始化搜索串口按钮动作
    Search.pushButton_2.clicked.connect(search_try_connect_meter)  # 初始化仪表连接按钮动作
    Search.pushButton_3.clicked.connect(search_meter_try_conect)  # 初始化搜索仪表按钮动作
    Search.pushButton_4.clicked.connect(search_meter_result_save)  # 保存搜索结果
    # search_result_table.show()#显示搜索结果表格


# 定义打开“设置Modbus地址”子窗体的方法
def modify_modbus_address():
    Modify_modbus_address.show()  # 显示“设置Modbus地址子窗体
    initial_modify_modbus()  # 初始化窗体显示
    modify_modbus_reflash_parameter()  # 初始化窗体显示-连接状态和modbus地址
    Modify_modbus_address.pushButton_1.clicked.connect(modify_modbus_address_pushbutton)  # 设置Modbus地址按钮


# 定义打开“设置采集周期”子窗体的方法
def modify_period():
    period_modify.show()  # 显示“设置采集周期”子窗体
    change_period_initial()  # 初始化窗体显示
    change_period_reflash_parameter()  # 初始化窗体显示-连接状态和当前采集周期
    period_modify.pushButton_1.clicked.connect(change_period_pushbutton_modify)  # 修改采集周期按钮


# 定义打开“修改仪表参数”子窗体的方法
def meter_parameter_setting():
    parameter_setting.show()  # 显示“修改仪表参数”子窗体
    parameter_modify_reflash_parameter()  # 初始化窗体显示-连接状态和当前仪表参数
    parameter_setting.pushButton_4.clicked.connect(import_meter_setting)  # 导入配置文件
    parameter_setting.pushButton_11.clicked.connect(export_meter_setting)  # 导出配置文件
    parameter_setting.pushButton_1.clicked.connect(modify_FS_number)  # 设置FS编号
    parameter_setting.pushButton_2.clicked.connect(change_modbus_address)  # 设置modbus地址
    parameter_setting.pushButton_3.clicked.connect(change_calibration_method)  # 设置modbus地址
    parameter_setting.pushButton_5.clicked.connect(change_pulse_calculation_method)  # 设置脉冲统计方式
    parameter_setting.pushButton_6.clicked.connect(change_pulse_period)  # 设置采集周期
    parameter_setting.pushButton_7.clicked.connect(change_SDTU_number)  # 设置SDTU编号
    parameter_setting.pushButton_10.clicked.connect(change_flow_deviation)  # 设置偏差报警系数
    parameter_setting.pushButton_9.clicked.connect(change_flow_deviation_ratio)  # 设置偏差报警比例
    parameter_setting.pushButton_8.clicked.connect(change_1_high_flow_alarm)  # 设置1路流量上限报警
    parameter_setting.pushButton_13.clicked.connect(change_1_low_flow_alarm)  # 设置1路流量下限报警
    parameter_setting.pushButton_14.clicked.connect(change_2_high_flow_alarm)  # 设置2路流量上限报警
    parameter_setting.pushButton_15.clicked.connect(change_2_low_flow_alarm)  # 设置2路流量下限报警
    parameter_setting.pushButton_30.clicked.connect(enable_flow_deviation_alarm)  # 偏差报警使能
    parameter_setting.pushButton_31.clicked.connect(enable_1_flow_high_alarm)  # 1路流量上限报警使能
    parameter_setting.pushButton_33.clicked.connect(enable_1_flow_low_alarm)  # 1路流量下限报警使能
    parameter_setting.pushButton_32.clicked.connect(enable_2_flow_high_alarm)  # 2路流量上限报警使能
    parameter_setting.pushButton_34.clicked.connect(enable_2_flow_low_alarm)  # 2路流量下限报警使能
    parameter_setting.pushButton_18.clicked.connect(change_1_a_pulse)  # 1路A点脉冲
    parameter_setting.pushButton_19.clicked.connect(change_1_a_volumn)  # 1路A点容积
    parameter_setting.pushButton_20.clicked.connect(change_1_b_pulse)  # 1路B点脉冲
    parameter_setting.pushButton_21.clicked.connect(change_1_b_volumn)  # 1路B点容积
    parameter_setting.pushButton_22.clicked.connect(change_1_c_pulse)  # 1路C点脉冲
    parameter_setting.pushButton_23.clicked.connect(change_1_c_volumn)  # 1路C点容积
    parameter_setting.pushButton_27.clicked.connect(change_2_a_pulse)  # 2路A点脉冲
    parameter_setting.pushButton_29.clicked.connect(change_2_a_volumn)  # 2路A点容积
    parameter_setting.pushButton_25.clicked.connect(change_2_b_pulse)  # 2路B点脉冲
    parameter_setting.pushButton_28.clicked.connect(change_2_b_volumn)  # 2路B点容积
    parameter_setting.pushButton_26.clicked.connect(change_2_c_pulse)  # 2路C点脉冲
    parameter_setting.pushButton_24.clicked.connect(change_2_c_volumn)  # 2路C点容积
    parameter_setting.pushButton_35.clicked.connect(change_1_full_scale)  # 1路4-20mA满刻度
    parameter_setting.pushButton_36.clicked.connect(change_2_full_scale)  # 2路4-20mA满刻度
    parameter_setting.pushButton_38.clicked.connect(change_meter_start_string)  # 修改开机字符串
    parameter_setting.pushButton_37.clicked.connect(extension_parameter_upload_enable)  # 扩展参数上传使能
    parameter_setting.pushButton_39.clicked.connect(change_meter_ch1_string)  # 修改通道1字符串
    parameter_setting.pushButton_40.clicked.connect(change_meter_ch2_string)  # 修改通道2字符串
    parameter_setting.pushButton_41.clicked.connect(change_web_address)  # 修改平台域名
    parameter_setting.pushButton_42.clicked.connect(change_port_number)  # 修改端口号
    parameter_setting.pushButton_43.clicked.connect(change_ch1_display_unit)  # 修改通道1显示单位
    parameter_setting.pushButton_44.clicked.connect(change_ch2_display_unit)  # 修改通道2显示单位


# 定义打开Paddle网页的方法
def Open_website():
    webbrowser.open('http://www.paddle-flow.com')


MainWindow.actionwww_paddle_flow_com.triggered.connect(Open_website)  # 设置打开Paddle网页方法

# TODO:3.2 连接仪表
Connect = connect_dialog.Ui_Dialog()  # 通信设置子窗口
Search = search_dialog.Ui_Dialog()  # 搜索仪表子窗口


# TODO:3.2.1 设置modbus参数选项
# 连接仪表-通信设置菜单设置Modbus参数
def connect_config_modbus_option():
    Connect.comboBox.addItems(['无串口!'])  # 可用串口
    Connect.comboBox_2.addItems(
        ['9600', '4800', '2400', '19200', '38400', '43000', '56000', '57600', '115200', '128000'])  # 波特率
    Connect.comboBox_3.addItems(['8', '5', '6', '7'])  # 数据位
    Connect.comboBox_4.addItems(['N', 'O', 'E', 'M', 'S'])  # 校验位
    Connect.comboBox_5.addItems(['1', '1.5', '2'])  # 停止位
    Connect.comboBox_6.addItems(['1', '2', '3', '4', '5', '6', '7', '8', '9', '10'])  # 仪表从站站号


# 连接仪表-搜索仪表菜单设置modbus参数
def search_config_modbus_option():
    Search.comboBox.addItems(['无串口!'])  # 可用串口
    Search.comboBox_2.addItems(
        ['9600', '4800', '2400', '19200', '38400', '43000', '56000', '57600', '115200', '128000'])  # 波特率
    Search.comboBox_3.addItems(['8', '5', '6', '7'])  # 数据位
    Search.comboBox_4.addItems(['N', 'O', 'E', 'M', 'S'])  # 校验位
    Search.comboBox_5.addItems(['1', '1.5', '2'])  # 停止位
    Search.comboBox_6.addItems(['1'])  # 搜索起始从站站号
    Search.comboBox_7.addItems(['20'])  # 搜索结束从站站号
    Search.comboBox_8.addItems(['未搜索'])  # 可用从站站号


# TODO:3.2.2 通信设置
# 通信设置菜单连接仪表
def try_connect_meter():
    global Connect_status_meter
    Connect_status_meter = 1
    port_current = Connect.comboBox.currentText().split()
    Modbus_parameter['PORT'] = port_current[0]  # 串口号
    Modbus_parameter['baudrate'] = int(Connect.comboBox_2.currentText())  # 波特率
    Modbus_parameter['bytesize'] = int(Connect.comboBox_3.currentText())  # 数据位
    Modbus_parameter['parity'] = Connect.comboBox_4.currentText()  # 校验位
    Modbus_parameter['stopbits'] = float(Connect.comboBox_5.currentText())  # 停止位
    Modbus_parameter['address'] = int(Connect.comboBox_6.currentText())  # 仪表从站站号
    # modbus连接有可能有2种错误：一是连接过程中就出错，没有返回，通过except中的程序处理；二是返回-1，通过if data_get[0]==-1处理。
    data_get = RS485.modbus_read(Modbus_parameter['PORT'],  # 串口号
                                 Modbus_parameter['baudrate'],  # 波特率
                                 Modbus_parameter['bytesize'],  # 数据位
                                 Modbus_parameter['parity'],  # 校验位
                                 Modbus_parameter['stopbits'],  # 停止位
                                 Modbus_parameter['address'],  # 仪表从站站号
                                 0,  # 起始寄存器
                                 1,  # 读寄存器的数量
                                 )
    # 处理连接过程中出错
    if (data_get == []) or (data_get[0] == -1):
        Connect_status_meter = 0  # 连接modbus错误
        # print('Connect_status_meter='+str(Connect_status_meter))
        modbus_parameter_reset()  # 复位modbus参数
        result_retry = messagebox_in_Chinese.retry_messagebox('连接仪表', '连接仪表失败，是否重试？')
        if result_retry == 1:
            print('retry')
        else:
            Connect.close()
            print('cancel')
        #  删除已创建对象
        del data_get
        return -1  # 返回连接失败
    else:
        if data_get[0] == 6:
            Connect_status_meter = 1
        elif data_get[0] == 7:
            Connect_status_meter = 2
        Connect.close()
        #  删除已创建对象
        del data_get
        print('Connect_status_meter=' + str(Connect_status_meter))
        messagebox_in_Chinese.information_messagebox('连接仪表', '成功连接仪表！')
        return 0  # 返回连接成功


# TODO:3.2.3 搜索仪表
# 搜索仪表中连接仪表按钮
def search_try_connect_meter():
    address_get = Search.comboBox_8.currentText()
    if (address_get == '未搜索') or (address_get == '无可用仪表'):
        messagebox_in_Chinese.information_messagebox('未搜索或无可用仪表', '搜索仪表，或者连接仪表后重新搜索！')
    else:
        port_current = Search.comboBox.currentText().split()
        Modbus_parameter['PORT'] = port_current[0]  # 串口号
        Modbus_parameter['baudrate'] = int(Search.comboBox_2.currentText())  # 波特率
        Modbus_parameter['bytesize'] = int(Search.comboBox_3.currentText())  # 数据位
        Modbus_parameter['parity'] = Search.comboBox_4.currentText()  # 校验位
        Modbus_parameter['stopbits'] = float(Search.comboBox_5.currentText())  # 停止位
        Modbus_parameter['address'] = int(Search.comboBox_8.currentText())  # 仪表从站站号
        # modbus连接有可能有2种错误：一是连接过程中就出错，没有返回，通过except中的程序处理；二是返回-1，通过if data_get[0]==-1处理。
        data_get = RS485.modbus_read(Modbus_parameter['PORT'],  # 串口号
                                     Modbus_parameter['baudrate'],  # 波特率
                                     Modbus_parameter['bytesize'],  # 数据位
                                     Modbus_parameter['parity'],  # 校验位
                                     Modbus_parameter['stopbits'],  # 停止位
                                     Modbus_parameter['address'],  # 仪表从站站号
                                     0,  # 起始寄存器
                                     1,  # 读寄存器的数量
                                     )
        # 处理连接过程中出错
        if (data_get == []) or (data_get[0] == -1):
            global Connect_status_meter
            Connect_status_meter = 0  # 连接modbus错误
            # print('Connect_status_meter='+str(Connect_status_meter))
            modbus_parameter_reset()  # 复位modbus参数
            result_retry = messagebox_in_Chinese.retry_messagebox('连接仪表', '连接仪表失败，是否重试？')
            if result_retry == 1:
                print('retry')
            else:
                Search.close()
                print('cancel')
            #  删除已创建对象
            del data_get
            return -1  # 返回连接失败
        else:
            messagebox_in_Chinese.information_messagebox('连接仪表', '成功连接仪表！')
            if data_get[0] == 6:
                Connect_status_meter = 1
            elif data_get[0] == 7:
                Connect_status_meter = 2
            Search.close()  # 关闭子窗口
            #  删除已创建对象
            del data_get
            return 0  # 返回连接成功
        print('Connect_status_meter=' + str(Connect_status_meter))


# 搜索仪表：搜索仪表中搜索结果表格
class SearchResultTable(QWidget):
    def __init__(self, parent=Search.groupBox):
        super(SearchResultTable, self).__init__(parent)
        # 设置标题与初始大小
        self.setWindowTitle('QTableView表格视图的例子')
        self.setGeometry(QtCore.QRect(5, 10, 430, 110))

        # 设置数据层次结构，2行2列
        self.model = QStandardItemModel(3, 2)
        # 设置水平方向四个头标签文本内容
        self.model.setVerticalHeaderLabels(['仪表站号', '流量计编号', '硬件版本'])

        item_address = '未搜索'
        item_FS = '未搜索'
        item_version = '未搜索'
        # 设置每个位置的文本值
        self.model.setItem(0, 0, QStandardItem(item_address))
        self.model.setItem(1, 0, QStandardItem(item_FS))
        self.model.setItem(2, 0, QStandardItem(item_version))

        # 实例化表格视图，设置模型为自定义的模型
        self.tableView = QTableView()
        self.tableView.setModel(self.model)
        #  优化1 表格填满窗口
        # 水平方向标签拓展剩下的窗口部分，填满表格
        self.tableView.verticalHeader().setStretchLastSection(True)
        # 水平方向，表格大小拓展到适当的尺寸
        self.tableView.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # 设置布局
        layout = QVBoxLayout()
        layout.addWidget(self.tableView)
        self.setLayout(layout)


search_result_table = SearchResultTable()  # 配置搜索结果表格


# 搜索仪表：搜索仪表按钮函数
def search_meter_try_conect():
    available_meter_count = 0  # 可用仪表数为0
    if Search.comboBox_6.currentText().isdecimal() == False:
        messagebox_in_Chinese.information_messagebox('参数错误', '起始搜索从站站号必须为整数！')
    elif Search.comboBox_7.currentText().isdecimal() == False:
        messagebox_in_Chinese.information_messagebox('参数错误', '结束搜索从站站号必须为整数！')
    else:
        start_search_address = int(Search.comboBox_6.currentText())
        end_search_address = int(Search.comboBox_7.currentText())
        if start_search_address > end_search_address:
            messagebox_in_Chinese.information_messagebox('参数错误', '结束搜索从站站号必须大于或等于开始搜索从站站号！')
        else:
            # 可用仪表记录复位
            global available_meter
            available_meter = [[],  # 站号
                               [],  # 编号FS
                               [],  # 硬件版本:1:2代标准版本仪表;2:2代plus仪表;3:3代仪表
                               ]

            Search.comboBox_8.clear()  # 清除搜索框内"未搜索"显示
            port_current = Search.comboBox.currentText().split()
            Modbus_parameter['PORT'] = port_current[0]  # 串口号
            Modbus_parameter['baudrate'] = int(Search.comboBox_2.currentText())  # 波特率
            Modbus_parameter['bytesize'] = int(Search.comboBox_3.currentText())  # 数据位
            Modbus_parameter['parity'] = Search.comboBox_4.currentText()  # 校验位
            Modbus_parameter['stopbits'] = float(Search.comboBox_5.currentText())  # 停止位
            for i in range(start_search_address, end_search_address + 1):
                Search.label_12.setText('正在尝试连接站号为' + str(i) + '的仪表。')
                print('正在尝试连接站号为' + str(i) + '的仪表。')
                # modbus连接有可能有2种错误：一是连接过程中就出错，没有返回，通过except中的程序处理；二是返回-1，通过if data_get[0]==-1处理。
                data_get = RS485.modbus_read(Modbus_parameter['PORT'],  # 串口号
                                             Modbus_parameter['baudrate'],  # 波特率
                                             Modbus_parameter['bytesize'],  # 数据位
                                             Modbus_parameter['parity'],  # 校验位
                                             Modbus_parameter['stopbits'],  # 停止位
                                             i,  # 当前从站站号
                                             0,  # 起始寄存器
                                             4,  # 读寄存器数量,至少要读到FS编号
                                             )
                # 处理连接过程中出错
                if (data_get == []) or (data_get[0] == -1):
                    Search.label_12.setText('连接站号为' + str(i) + '的仪表失败！')
                    print('连接站号为' + str(i) + '的仪表失败！')
                else:
                    Search.label_12.setText('连接站号为' + str(i) + '的仪表成功！')
                    print('连接站号为' + str(i) + '的仪表成功！')
                    # 更新可用仪表列表
                    available_meter[0].append(i)  # 存入站号
                    print(available_meter[0])
                    # 读取仪表编号
                    FS = data_get[2] * 65536 + data_get[3]
                    FS = str(FS)
                    FS_text = 'FS' + FS.rjust(9, '0')
                    available_meter[1].append(FS_text)  # 存入仪表编号
                    print(available_meter[1])
                    # 存入硬件版本
                    if data_get[0] == 6:
                        available_meter[2].append('2代')  # 标准2代
                    elif data_get[0] == 7:
                        available_meter[2].append('2代plus')  # 2代plus
                    else:
                        available_meter[2].append(-1)  # 错误
                    print(available_meter[2])
                    Search.comboBox_8.addItem(str(i))  # 加入可用站号
                    available_meter_count = available_meter_count + 1  # 更新可用仪表计数
            if available_meter_count == 0:
                modbus_parameter_reset()  # 复位modbus参数
                Search.comboBox_8.addItem('未搜索')
            Search.label_12.setText('共搜索到' + str(available_meter_count) + '个可用仪表')
            print('共搜索到' + str(available_meter_count) + '个可用仪表')
            modbus_parameter_reset()  # 复位modbus参数
    if available_meter_count == 0:
        search_result_table.model.setItem(0, 0, QStandardItem('未搜索到仪表！'))
        search_result_table.model.setItem(1, 0, QStandardItem('未搜索到仪表！'))
        search_result_table.model.setItem(2, 0, QStandardItem('未搜索到仪表！'))
    else:
        for i in range(len(available_meter[0])):
            address = available_meter[0][i]
            FS = available_meter[1][i]
            meter_version = available_meter[2][i]
            # print(address)
            # print(FS)
            search_result_table.model.setItem(0, i, QStandardItem(str(address)))
            search_result_table.model.setItem(1, i, QStandardItem(FS))
            search_result_table.model.setItem(2, i, QStandardItem(meter_version))
    search_result_table.show()  # 显示搜索结果表格


# 搜索仪表：保存搜索仪表结果按钮函数
def search_meter_result_save():
    print(available_meter[0][0])
    print(available_meter[1][0])
    print(available_meter[2][0])
    save_search_meter_result.MeterSearchResult(available_meter)
    dir_now = os.getcwd()  # 获取当前工作目录
    messagebox_in_Chinese.information_messagebox('保存仪表搜索结果', '仪表搜索结果已保存至"' + dir_now + '"目录下的"搜索仪表结果.xlsx"！')


# TODO:3.3 设置仪表
Modify_modbus_address = Modbus_adress_modify.Ui_Dialog()  # 设置Modbus地址子窗体
period_modify = period_modify.Ui_Dialog()  # 设置修改采集周期子窗体
parameter_setting = parameter_modify.Ui_Dialog()  # 设置修改参数设置子窗体


# TODO:3.3.1 设置仪表公共方法
# 将Meter_data转换为导出配置记录的格式
def translate_meter_data_to_save_parlance(meter_data, meter_data_column):
    meter_setting = pd.DataFrame(meter_data, index=meter_data_column)
    meter_setting = meter_setting.T
    print(meter_setting)
    return meter_setting


# 设置仪表参数记录log
def save_log_data(log_data):
    dir_now = os.getcwd()  # 获取当前工作目录
    print(dir_now)
    export_file_name = dir_now + '\\' + 'meter_config.paddlelog'
    print(export_file_name)
    log_data.to_csv(export_file_name, index=False, mode='a')


def save_meter_config_log():
    refresh_parameter()  # 更新参数
    if Connect_status_meter == 1:
        log_data = translate_meter_data_to_save_parlance(Meter_data, Meter_data_column)
        save_log_data(log_data)
    elif Connect_status_meter == 2:
        log_data = translate_meter_data_to_save_parlance(Meter_data_2_plus, Meter_data_column_2_plus)
        save_log_data(log_data)
    else:
        messagebox_in_Chinese.information_messagebox('保存参数设置记录', '仪表未连接，无法保存参数设置记录！')


# 写多个寄存器
class WriteMultipleRegister:
    def __init__(self,
                 message_title,  # 消息标题
                 message_disconnect,  # 消息未连接
                 register_write_start,  # 写入的起始寄存器
                 data_wrote,  # 写入的数据
                 message_write_error,  # 消息写入错误
                 message_write_success,  # 消息写入成功
                 ):
        self.message_title = message_title
        self.message_disconnect = message_disconnect
        self.register_write_start = register_write_start
        self.data_wrote = data_wrote
        self.message_write_error = message_write_error
        self.message_write_success = message_write_success
        # self.write_data_to_meter_register_multiple(self)

    def write_data_to_meter_register_multiple(self):
        global Connect_status_meter
        if Connect_status_meter == 0:
            messagebox_in_Chinese.information_messagebox(self.message_title, self.message_disconnect)
            Connect.show()  # 打开连接仪表子窗体
        else:
            # 通过RS-485将数据写入仪表
            data_write = RS485.modbus_write_multiple(Modbus_parameter['PORT'],  # 端口号
                                                     Modbus_parameter['baudrate'],  # 波特率
                                                     Modbus_parameter['bytesize'],  # 数据位
                                                     Modbus_parameter['parity'],  # 校验位
                                                     Modbus_parameter['stopbits'],  # 停止位
                                                     Modbus_parameter['address'],  # 从站地址
                                                     self.register_write_start,  # Modbus地址寄存器起始地址
                                                     self.data_wrote,  # 写入的寄存器序列
                                                     )
            print(data_write)
            if (data_write == []) or (data_write == -1):
                messagebox_in_Chinese.information_messagebox(self.message_title, self.message_write_error)
                #  删除已创建对象
                del data_write
                return -1  # 返回连接失败
            else:
                messagebox_in_Chinese.information_messagebox(self.message_title, self.message_write_success)
                save_meter_config_log()  # 保存操作记录
                #  删除已创建对象
                del data_write
                return 0  # 返回修改参数成功


# 写单个寄存器
class WriteSingleRegister:
    def __init__(self,
                 message_title,  # 消息标题
                 message_disconnect,  # 消息未连接
                 register_write_start,  # 写入的起始寄存器
                 data_wrote,  # 写入的数据
                 message_write_error,  # 消息写入错误
                 message_write_success,  # 消息写入成功
                 ):
        self.message_title = message_title
        self.message_disconnect = message_disconnect
        self.register_write_start = register_write_start
        self.data_wrote = data_wrote
        self.message_write_error = message_write_error
        self.message_write_success = message_write_success

    def write_data_to_meter_register_single(self):
        global Connect_status_meter
        if Connect_status_meter == 0:
            messagebox_in_Chinese.information_messagebox(self.message_title, self.message_disconnect)
            Connect.show()  # 打开连接仪表子窗体
        else:
            # 通过RS-485将数据写入仪表
            data_write = RS485.modbus_write(Modbus_parameter['PORT'],  # 端口号
                                            Modbus_parameter['baudrate'],  # 波特率
                                            Modbus_parameter['bytesize'],  # 数据位
                                            Modbus_parameter['parity'],  # 校验位
                                            Modbus_parameter['stopbits'],  # 停止位
                                            Modbus_parameter['address'],  # 从站地址
                                            self.register_write_start,  # Modbus地址寄存器起始地址
                                            self.data_wrote,  # 写入的寄存器序列
                                            )
            print(data_write)
            if (data_write == []) or (data_write == -1):
                messagebox_in_Chinese.information_messagebox(self.message_title, self.message_write_error)
                #  删除已创建对象
                del data_write
                return -1  # 返回连接失败
            else:
                messagebox_in_Chinese.information_messagebox(self.message_title, self.message_write_success)
                save_meter_config_log()  # 保存操作记录
                #  删除已创建对象
                del data_write
                return 0  # 返回修改参数成功


# TODO:3.3.2 修改Modbus地址
# 初始化界面显示
def initial_modify_modbus():
    Modify_modbus_address.comboBox_1.addItems(['1', '2', '3', '4', '5', '6', '7', '8', '9', '10'])  # 仪表从站站号


# 刷新界面数据
def modify_modbus_reflash_parameter():
    global Connect_status_meter
    # 刷新连接状态
    if Connect_status_meter == 0:
        Modify_modbus_address.label_4.setText('未连接')
        Modify_modbus_address.label_4.setStyleSheet("background-color: rgb(255, 0, 0);\n")
    else:
        Modify_modbus_address.label_4.setText("已连接")
        Modify_modbus_address.label_4.setStyleSheet("background-color: rgb(0, 255, 0);\n")
    # 刷新仪表Modbus地址
    if Connect_status_meter == 0:
        Modify_modbus_address.label_5.setText('未连接')
        Modify_modbus_address.label_5.setStyleSheet("background-color: rgb(255, 255, 0);\n")
    else:
        Modify_modbus_address.label_5.setText(str(Modbus_parameter['address']))
        Modify_modbus_address.label_5.setStyleSheet("background-color: rgb(255, 255, 255);\n")
    # 定时刷新显示界面数据
    Modify_modbus_address.timer = QTimer()  # 初始化定时器
    Modify_modbus_address.timer.timeout.connect(modify_modbus_reflash_parameter)  # 定时操作
    Modify_modbus_address.timer.start(1000)  # 每秒刷新1次


# 设置Modbus地址按钮
def modify_modbus_address_pushbutton():
    # 改写Modbus从站地址
    global Connect_status_meter
    if Connect_status_meter == 0:
        messagebox_in_Chinese.information_messagebox('Modbus从站地址设置', '未连接仪表！')
        Modify_modbus_address.close()  # 关闭子窗口
        Connect.show()  # 打开连接仪表子窗体
    else:
        data_write = RS485.modbus_write(Modbus_parameter['PORT'],  # 端口号
                                        Modbus_parameter['baudrate'],  # 波特率
                                        Modbus_parameter['bytesize'],  # 数据位
                                        Modbus_parameter['parity'],  # 校验位
                                        Modbus_parameter['stopbits'],  # 停止位
                                        Modbus_parameter['address'],  # 从站地址
                                        Meter_data_write['41003'],  # Modbus地址寄存器地址
                                        int(Modify_modbus_address.comboBox_1.currentText()),  # 新的Modbus地址
                                        )

        # 更新当前modbus地址
        Modbus_parameter['address'] = int(Modify_modbus_address.comboBox_1.currentText())
        Meter_data[70] = Modbus_parameter['address']

        if (data_write == []) or (data_write == -1):
            result_retry = messagebox_in_Chinese.retry_messagebox('Modbus从站地址设置', '设置Modbus从站地址失败，是否重试？')
            if result_retry == 1:
                Modify_modbus_address.close()  # 关闭子窗体
                show_connect()  # 打开连接仪表子窗体
                print('retry')
            else:
                Modify_modbus_address.close()
                print('cancel')
            #  删除已创建对象
            del data_write
            return -1  # 返回连接失败
        else:
            save_meter_config_log()  # 将配置参数导出至配置记录
            messagebox_in_Chinese.information_messagebox('Modbus从站地址设置', '成功设置Modbus从站地址！')
            Modify_modbus_address.close()  # 关闭modbus设置子窗体
            #  删除已创建对象
            del data_write
            return 0  # 返回连接成功
        # print('Connect_status_meter=' + str(Connect_status_meter))


# TODO:3.3.3 修改采集周期
# 初始化界面显示
def change_period_initial():
    periods = list(np.arange(30) + 1)
    for item in range(len(periods)):
        periods[item] = str(periods[item])
    print(periods)
    period_modify.comboBox_1.addItems(periods)  # 可用采集周期


# 刷新界面数据
def change_period_reflash_parameter():
    global Connect_status_meter
    # 刷新连接状态
    if Connect_status_meter == 0:
        period_modify.label_4.setText('未连接')
        period_modify.label_4.setStyleSheet("background-color: rgb(255, 0, 0);\n")
    else:
        period_modify.label_4.setText("已连接")
        period_modify.label_4.setStyleSheet("background-color: rgb(0, 255, 0);\n")
    # 刷新采集周期
    if Connect_status_meter == 1:
        period_modify.label_5.setText(str(Meter_data[17]))
        period_modify.label_5.setStyleSheet("background-color: rgb(255, 255, 255);\n")
    elif Connect_status_meter == 2:
        period_modify.label_5.setText(str(Meter_data_2_plus[23]))
        period_modify.label_5.setStyleSheet("background-color: rgb(255, 255, 255);\n")
    else:
        period_modify.label_5.setText('未连接')
        period_modify.label_5.setStyleSheet("background-color: rgb(255, 255, 0);\n")
    # 定时刷新显示界面数据
    period_modify.timer = QTimer()  # 初始化定时器
    period_modify.timer.timeout.connect(change_period_reflash_parameter)  # 定时操作
    period_modify.timer.start(1000)  # 每秒刷新1次


# 修改采集周期按钮
def change_period_pushbutton_modify():
    # 修改采集周期
    global Connect_status_meter
    if Connect_status_meter == 0:
        messagebox_in_Chinese.information_messagebox('修改采集周期', '未连接仪表！')
        period_modify.close()  # 关闭子窗口
        Connect.show()  # 打开连接仪表子窗体
    else:
        data_write = RS485.modbus_write(Modbus_parameter['PORT'],  # 端口号
                                        Modbus_parameter['baudrate'],  # 波特率
                                        Modbus_parameter['bytesize'],  # 数据位
                                        Modbus_parameter['parity'],  # 校验位
                                        Modbus_parameter['stopbits'],  # 停止位
                                        Modbus_parameter['address'],  # 从站地址
                                        Meter_data_write['41006'],  # Modbus地址寄存器地址
                                        int(period_modify.comboBox_1.currentText()),  # 新的采集周期
                                        )
        if (data_write == []) or (data_write == -1):
            result_retry = messagebox_in_Chinese.retry_messagebox('修改采集周期', '修改采集周期失败，是否重试？')
            if result_retry == 1:
                period_modify.close()  # 关闭子窗体
                show_connect()  # 打开连接仪表子窗体
                print('retry')
            else:
                period_modify.close()
                print('cancel')
            #  删除已创建对象
            del data_write
            return -1  # 返回连接失败
        else:
            save_meter_config_log()  # 保存设置记录
            messagebox_in_Chinese.information_messagebox('修改采集周期', '成功修改采集周期！')
            period_modify.close()  # 关闭修改采集周期子窗体
            #  删除已创建对象
            del data_write
            return 0  # 返回连接成功


# TODO:3.3.4 导出仪表配置参数
# 导出仪表配置参数
def export_meter_setting():
    if Connect_status_meter == 1:
        dir_now = os.getcwd()  # 获取当前工作目录
        print(Meter_data)
        print(len(Meter_data))
        print(Meter_data_column)
        print(len(Meter_data_column))
        meter_setting = translate_meter_data_to_save_parlance(Meter_data, Meter_data_column)  # 将Meter_data格式转换为保存格式
        FS = str(Meter_data[3] * 65536 + Meter_data[4])  # 获取仪表编号
        FS_text = 'FS' + FS.rjust(9, '0')
        date_time_now = datetime.datetime.now()  # 获取当前时间
        export_file_name = dir_now + '\\' + str(date_time_now.year) + str(date_time_now.month).rjust(2, '0') + str(
            date_time_now.day).rjust(2, '0') + FS_text + '仪表配置type2.paddle'
        print(export_file_name)
        meter_setting.to_csv(export_file_name, index=False, mode='w')
        messagebox_in_Chinese.information_messagebox('保存仪表搜索结果', '仪表搜索结果已保存至"' + export_file_name)
    elif Connect_status_meter == 2:
        dir_now = os.getcwd()  # 获取当前工作目录
        print(Meter_data_2_plus)
        print(len(Meter_data_2_plus))
        print(Meter_data_column_2_plus)
        print(len(Meter_data_column_2_plus))
        meter_setting = translate_meter_data_to_save_parlance(Meter_data_2_plus,
                                                              Meter_data_column_2_plus)  # 将Meter_data格式转换为保存格式
        FS = str(Meter_data_2_plus[3] * 65536 + Meter_data_2_plus[4])  # 获取仪表编号
        FS_text = 'FS' + FS.rjust(9, '0')
        date_time_now = datetime.datetime.now()  # 获取当前时间
        export_file_name = dir_now + '\\' + str(date_time_now.year) + str(date_time_now.month).rjust(2, '0') + str(
            date_time_now.day).rjust(2, '0') + FS_text + '仪表配置type2plus.paddle'
        print(export_file_name)
        meter_setting.to_csv(export_file_name, index=False, mode='w')
        messagebox_in_Chinese.information_messagebox('保存仪表搜索结果', '仪表搜索结果已保存至"' + export_file_name)
    else:
        messagebox_in_Chinese.information_messagebox('Modbus从站地址设置', '未连接仪表！')
        show_connect()  # 打开连接仪表子窗体


# TODO:3.3.5 导入仪表配置参数
# 打开文件对话框
def open_file_dialog():
    # 选择的文件名
    import_file_name = QFileDialog.getOpenFileName(MainWindow, '选择文件', './', 'Paddle Files (*.paddle);;All Files (*)')
    print(import_file_name)
    print(import_file_name[0])
    return import_file_name[0]


# 导入数据总体过程
def import_meter_setting():
    global Connect_status_meter
    import_file_path = open_file_dialog()
    meter_data_import = pd.read_csv(import_file_path)  # 从配置文件中读出仪表设置
    print(type(meter_data_import))
    print(meter_data_import)
    if Connect_status_meter == 1:
        if meter_data_import.loc[0, '40001'] == 6:
            setting_write_to_meter = import_setting_prepare.data_translate(meter_data_import)  # 准备要导入的数据
            print(setting_write_to_meter)
            print(len(setting_write_to_meter))
            print(setting_write_to_meter[37])
            # 通过RS-485将数据写入仪表
            data_write = RS485.modbus_write_multiple(Modbus_parameter['PORT'],  # 端口号
                                                     Modbus_parameter['baudrate'],  # 波特率
                                                     Modbus_parameter['bytesize'],  # 数据位
                                                     Modbus_parameter['parity'],  # 校验位
                                                     Modbus_parameter['stopbits'],  # 停止位
                                                     Modbus_parameter['address'],  # 从站地址
                                                     Meter_data_write['41001'],  # Modbus地址寄存器地址
                                                     setting_write_to_meter[0:18],  # 写入的寄存器序列
                                                     )
            print(data_write)
            if (data_write == []) or (data_write == -1):
                messagebox_in_Chinese.information_messagebox('导入仪表配置', '导入仪表配置失败！')
                return -1  # 返回连接失败
            else:
                Modbus_parameter['address'] = int(meter_data_import.loc[0, 'ModbusAddress'])  # 更新Modbus地址
                data_write = RS485.modbus_write_multiple(Modbus_parameter['PORT'],  # 端口号
                                                         Modbus_parameter['baudrate'],  # 波特率
                                                         Modbus_parameter['bytesize'],  # 数据位
                                                         Modbus_parameter['parity'],  # 校验位
                                                         Modbus_parameter['stopbits'],  # 停止位
                                                         Modbus_parameter['address'],  # 从站地址
                                                         Meter_data_write['41019'],  # Modbus地址寄存器地址
                                                         setting_write_to_meter[18:37],  # 写入的寄存器序列
                                                         )
                print(data_write)
                if (data_write == []) or (data_write == -1):
                    messagebox_in_Chinese.information_messagebox('导入仪表配置', '导入仪表配置失败！')
                    return -1  # 返回连接失败
                else:
                    print(Meter_data_write['41038'])
                    data_write = RS485.modbus_write_multiple(Modbus_parameter['PORT'],  # 端口号
                                                             Modbus_parameter['baudrate'],  # 波特率
                                                             Modbus_parameter['bytesize'],  # 数据位
                                                             Modbus_parameter['parity'],  # 校验位
                                                             Modbus_parameter['stopbits'],  # 停止位
                                                             Modbus_parameter['address'],  # 从站地址
                                                             Meter_data_write['41038'],  # Modbus地址寄存器地址
                                                             setting_write_to_meter[37:39],  # 写入的寄存器序列
                                                             )
                    print(data_write)
                    if (data_write == []) or (data_write == -1):
                        messagebox_in_Chinese.information_messagebox('导入仪表配置', '导入仪表配置失败！')
                        return -1  # 返回连接失败
                    else:
                        data_write = RS485.modbus_write_multiple(Modbus_parameter['PORT'],  # 端口号
                                                                 Modbus_parameter['baudrate'],  # 波特率
                                                                 Modbus_parameter['bytesize'],  # 数据位
                                                                 Modbus_parameter['parity'],  # 校验位
                                                                 Modbus_parameter['stopbits'],  # 停止位
                                                                 Modbus_parameter['address'],  # 从站地址
                                                                 Meter_data_write['41040'],  # Modbus地址寄存器地址
                                                                 setting_write_to_meter[39:55],  # 写入的寄存器序列
                                                                 )
                        print(data_write)
                        if (data_write == []) or (data_write == -1):
                            messagebox_in_Chinese.information_messagebox('导入仪表配置', '导入仪表配置失败！')
                            return -1  # 返回连接失败
                        else:
                            save_meter_config_log()  # 保存操作记录
                            messagebox_in_Chinese.information_messagebox('导入仪表配置', '导入仪表配置成功！')
                            return 0  # 返回导入设置成功
            #  删除已创建对象
            del data_write
        else:
            messagebox_in_Chinese.information_messagebox('导入仪表配置', '请导入2代仪表配置文件！')
            return -1  # 返回连接失败
    elif Connect_status_meter == 2:
        if meter_data_import.loc[0, '40001'] == 7:
            # 解锁仪表
            unlock_meter_setting = WriteMultipleRegister('解锁仪表',
                                                         '未连接仪表！',
                                                         Meter_data_2_plus_write['41180'],  # 开始地址
                                                         [43690, 21845],  # 写入数据
                                                         '解锁仪表失败！',
                                                         '解锁仪表成功！')  # 初始化类
            unlock_meter_setting.write_data_to_meter_register_multiple()
            #  删除已创建对象
            del unlock_meter_setting
            setting_write_to_meter = import_setting_prepare.data_translate_2_plus(meter_data_import)  # 准备要导入的数据
            print(setting_write_to_meter)
            print(len(setting_write_to_meter))
            connection_error_counts = 0
            data_write = RS485.modbus_write_multiple(Modbus_parameter['PORT'],  # 端口号
                                                     Modbus_parameter['baudrate'],  # 波特率
                                                     Modbus_parameter['bytesize'],  # 数据位
                                                     Modbus_parameter['parity'],  # 校验位
                                                     Modbus_parameter['stopbits'],  # 停止位
                                                     Modbus_parameter['address'],  # 从站地址
                                                     Meter_data_2_plus_write['41001'],  # Modbus地址寄存器地址
                                                     setting_write_to_meter[0:18],  # 写入的寄存器序列
                                                     )
            print(data_write)
            if (data_write == []) or (data_write == -1):
                messagebox_in_Chinese.information_messagebox('导入仪表配置', '导入仪表配置失败！')
                return -1  # 返回连接失败
            else:
                Modbus_parameter['address'] = int(meter_data_import.loc[0, 'ModbusAddress'])  # 更新Modbus地址
                data_write = RS485.modbus_write_multiple(Modbus_parameter['PORT'],  # 端口号
                                                         Modbus_parameter['baudrate'],  # 波特率
                                                         Modbus_parameter['bytesize'],  # 数据位
                                                         Modbus_parameter['parity'],  # 校验位
                                                         Modbus_parameter['stopbits'],  # 停止位
                                                         Modbus_parameter['address'],  # 从站地址
                                                         Meter_data_2_plus_write['41019'],  # Modbus地址寄存器地址
                                                         setting_write_to_meter[18:37],  # 写入的寄存器序列
                                                         )
                print(data_write)
                if (data_write == []) or (data_write == -1):
                    connection_error_counts += 1
                data_write = RS485.modbus_write_multiple(Modbus_parameter['PORT'],  # 端口号
                                                         Modbus_parameter['baudrate'],  # 波特率
                                                         Modbus_parameter['bytesize'],  # 数据位
                                                         Modbus_parameter['parity'],  # 校验位
                                                         Modbus_parameter['stopbits'],  # 停止位
                                                         Modbus_parameter['address'],  # 从站地址
                                                         Meter_data_2_plus_write['41038'],  # Modbus地址寄存器地址
                                                         setting_write_to_meter[37:51],  # 写入的寄存器序列
                                                         )
                print(data_write)
                if (data_write == []) or (data_write == -1):
                    connection_error_counts += 1
                data_write = RS485.modbus_write_multiple(Modbus_parameter['PORT'],  # 端口号
                                                         Modbus_parameter['baudrate'],  # 波特率
                                                         Modbus_parameter['bytesize'],  # 数据位
                                                         Modbus_parameter['parity'],  # 校验位
                                                         Modbus_parameter['stopbits'],  # 停止位
                                                         Modbus_parameter['address'],  # 从站地址
                                                         Meter_data_2_plus_write['41052'],  # Modbus地址寄存器地址
                                                         setting_write_to_meter[51:67],  # 写入的寄存器序列
                                                         )
                print(data_write)
                if (data_write == []) or (data_write == -1):
                    connection_error_counts += 1
                print(Modbus_parameter['PORT'])
                print(Modbus_parameter['baudrate'])
                print(Modbus_parameter['bytesize'])
                print(Modbus_parameter['parity'])
                print(Modbus_parameter['stopbits'])
                print(Modbus_parameter['address'])
                print(Meter_data_2_plus_write['41069'])
                print(setting_write_to_meter[68:78])
                data_write = RS485.modbus_write_multiple(Modbus_parameter['PORT'],  # 端口号
                                                         Modbus_parameter['baudrate'],  # 波特率
                                                         Modbus_parameter['bytesize'],  # 数据位
                                                         Modbus_parameter['parity'],  # 校验位
                                                         Modbus_parameter['stopbits'],  # 停止位
                                                         Modbus_parameter['address'],  # 从站地址
                                                         Meter_data_2_plus_write['41069'],  # Modbus地址寄存器地址
                                                         setting_write_to_meter[68:78],  # 写入的寄存器序列
                                                         )
                print(data_write)
                if (data_write == []) or (data_write == -1):
                    connection_error_counts += 1
                data_write = RS485.modbus_write_multiple(Modbus_parameter['PORT'],  # 端口号
                                                         Modbus_parameter['baudrate'],  # 波特率
                                                         Modbus_parameter['bytesize'],  # 数据位
                                                         Modbus_parameter['parity'],  # 校验位
                                                         Modbus_parameter['stopbits'],  # 停止位
                                                         Modbus_parameter['address'],  # 从站地址
                                                         Meter_data_2_plus_write['41089'],  # Modbus地址寄存器地址
                                                         setting_write_to_meter[88:95],  # 写入的寄存器序列
                                                         )
                print(data_write)
                if (data_write == []) or (data_write == -1):
                    connection_error_counts += 1
                print(setting_write_to_meter[95])
                data_write = RS485.modbus_write(Modbus_parameter['PORT'],  # 端口号
                                                Modbus_parameter['baudrate'],  # 波特率
                                                Modbus_parameter['bytesize'],  # 数据位
                                                Modbus_parameter['parity'],  # 校验位
                                                Modbus_parameter['stopbits'],  # 停止位
                                                Modbus_parameter['address'],  # 从站地址
                                                Meter_data_2_plus_write['41099'],  # Modbus地址寄存器地址
                                                setting_write_to_meter[95],  # 写入的寄存器
                                                )
                print(data_write)
                if (data_write == []) or (data_write == -1):
                    connection_error_counts += 1
                if connection_error_counts > 0:
                    messagebox_in_Chinese.information_messagebox('导入仪表配置', '导入仪表配置失败！')
                    #  删除已创建对象
                    del data_write
                    return -1  # 返回连接失败
                else:
                    save_meter_config_log()  # 保存操作记录
                    messagebox_in_Chinese.information_messagebox('导入仪表配置', '导入仪表配置成功！')
                    #  删除已创建对象
                    del data_write
                    return 0  # 返回导入设置成功
        else:
            messagebox_in_Chinese.information_messagebox('导入仪表配置', '文件格式错误，请导入2代plus仪表配置文件！')
            return -1  # 返回连接失败
    else:
        messagebox_in_Chinese.information_messagebox('导入仪表配置', '未连接仪表！')
        Connect.show()  # 打开连接仪表子窗体
        return -1  # 返回连接失败


# TODO:3.3.6 修改仪表参数
# 刷新界面参数及初始化comboBox显示
def parameter_modify_reflash_parameter():
    global Connect_status_meter
    # 刷新连接状态
    if Connect_status_meter == 0:
        parameter_setting.label_4.setText('未连接')
        parameter_setting.label_4.setStyleSheet("background-color: rgb(255, 0, 0);\n")  # 红色
    else:
        parameter_setting.label_4.setText("已连接")
        parameter_setting.label_4.setStyleSheet("background-color: rgb(0, 255, 0);\n")  # 绿色

    # 刷新仪表编号
    if Connect_status_meter == 1:
        FS = Meter_data[3] * 65536 + Meter_data[4]
        FS = str(FS)
        FS_text = 'FS' + FS.rjust(9, '0')
        parameter_setting.label_5.setText(FS_text)
        parameter_setting.label_5.setStyleSheet("background-color: rgb(255, 255, 255);\n")
        parameter_setting.comboBox_1.addItems([FS_text])  # 更新combox选项
    elif Connect_status_meter == 2:
        FS = Meter_data_2_plus[3] * 65536 + Meter_data_2_plus[4]
        FS = str(FS)
        FS_text = 'FS' + FS.rjust(9, '0')
        parameter_setting.label_5.setText(FS_text)
        parameter_setting.label_5.setStyleSheet("background-color: rgb(255, 255, 255);\n")
        parameter_setting.comboBox_1.addItems([FS_text])  # 更新combox选项
    else:
        parameter_setting.label_5.setText("未连接")
        parameter_setting.label_5.setStyleSheet("background-color: rgb(255, 255, 0);\n")

    # 刷新仪表Modbus地址
    if Connect_status_meter == 1:
        parameter_setting.label_10.setText(str(Meter_data[70]))
        parameter_setting.label_10.setStyleSheet("background-color: rgb(255, 255, 255);\n")
        parameter_setting.comboBox_2.addItems([str(Meter_data[70])])  # 更新combox选项
    elif Connect_status_meter == 2:
        parameter_setting.label_10.setText(str(Meter_data_2_plus[110]))
        parameter_setting.label_10.setStyleSheet("background-color: rgb(255, 255, 255);\n")
        parameter_setting.comboBox_2.addItems([str(Meter_data_2_plus[110])])  # 更新combox选项
    else:
        parameter_setting.label_10.setText('未连接')
        parameter_setting.label_10.setStyleSheet("background-color: rgb(255, 255, 0);\n")

    # 刷新寄存器'40015'-- 2代仪表
    register_40015 = data_translation_modal.decimal_to_binary(Meter_data[15])  # 40015 标志状态寄存器

    # 刷新寄存器'40021'-- 2代plus仪表
    register_40021 = data_translation_modal.decimal_to_binary(Meter_data_2_plus[21])  # 40021 标志状态寄存器

    # 刷新寄存器'40022'-- 2代plus仪表
    register_40022 = data_translation_modal.decimal_to_binary(Meter_data_2_plus[22])  # 40021 标志状态寄存器

    # 刷新流量校正方式
    if Connect_status_meter == 1:
        # 流量校正方式
        calibration_method = int(register_40015[-7]) + int(register_40015[-8]) * 2
        parameter_setting.label_14.setText(str(calibration_method))
        parameter_setting.label_14.setStyleSheet("background-color: rgb(255, 255, 255);\n")
        parameter_setting.comboBox_3.addItems([str(calibration_method)])  # 更新combox选项
    elif Connect_status_meter == 2:
        # 流量校正方式
        calibration_method = int(register_40021[-7]) + int(register_40021[-8]) * 2
        parameter_setting.label_14.setText(str(calibration_method))
        parameter_setting.label_14.setStyleSheet("background-color: rgb(255, 255, 255);\n")
        parameter_setting.comboBox_3.addItems([str(calibration_method)])  # 更新combox选项
    else:
        parameter_setting.label_14.setText('未连接')
        parameter_setting.label_14.setStyleSheet("background-color: rgb(255, 255, 0);\n")

    # 刷新脉冲统计方式
    if Connect_status_meter == 1:
        # 脉冲统计方式
        pulse_calculation_method = int(register_40015[-9])
        parameter_setting.label_22.setText(str(pulse_calculation_method))
        parameter_setting.label_22.setStyleSheet("background-color: rgb(255, 255, 255);\n")
        parameter_setting.comboBox_5.addItems([str(pulse_calculation_method)])  # 更新combox选项
    elif Connect_status_meter == 2:
        # 脉冲统计方式
        pulse_calculation_method = int(register_40021[-9])
        parameter_setting.label_22.setText(str(pulse_calculation_method))
        parameter_setting.label_22.setStyleSheet("background-color: rgb(255, 255, 255);\n")
        parameter_setting.comboBox_5.addItems([str(pulse_calculation_method)])  # 更新combox选项
    else:
        parameter_setting.label_22.setText('未连接')
        parameter_setting.label_22.setStyleSheet("background-color: rgb(255, 255, 0);\n")

    # 刷新采集周期
    if Connect_status_meter == 1:
        parameter_setting.label_26.setText(str(Meter_data[17]))
        parameter_setting.label_26.setStyleSheet("background-color: rgb(255, 255, 255);\n")
        parameter_setting.comboBox_6.addItems([str(Meter_data[17])])  # 更新combox选项
    elif Connect_status_meter == 2:
        parameter_setting.label_26.setText(str(Meter_data_2_plus[23]))
        parameter_setting.label_26.setStyleSheet("background-color: rgb(255, 255, 255);\n")
        parameter_setting.comboBox_6.addItems([str(Meter_data_2_plus[23])])  # 更新combox选项
    else:
        parameter_setting.label_26.setText('未连接')
        parameter_setting.label_26.setStyleSheet("background-color: rgb(255, 255, 0);\n")

    # 刷新SDTU编号
    if Connect_status_meter == 1:
        SDTU = Meter_data[48] * 65536 + Meter_data[49]
        SDTU = str(SDTU)
        SDTU_text = 'SDTU' + SDTU.rjust(9, '0')
        parameter_setting.label_18.setText(SDTU_text)
        parameter_setting.comboBox_4.addItems([SDTU_text])  # 更新combox选项
    elif Connect_status_meter == 2:
        SDTU = Meter_data_2_plus[66] * 65536 + Meter_data_2_plus[67]
        SDTU = str(SDTU)
        SDTU_text = 'SDTU' + SDTU.rjust(9, '0')
        parameter_setting.label_18.setText(SDTU_text)
        parameter_setting.comboBox_4.addItems([SDTU_text])  # 更新combox选项
    else:
        parameter_setting.label_18.setText("未连接")
        parameter_setting.label_18.setStyleSheet("background-color: rgb(255, 255, 0);\n")

    # 偏差报警使能
    if Connect_status_meter == 1:
        # 偏差报警使能
        pulse_calculation_method = int(register_40015[-10])
        parameter_setting.label_107.setText(str(pulse_calculation_method))
        parameter_setting.label_107.setStyleSheet("background-color: rgb(255, 255, 255);\n")
        parameter_setting.comboBox_25.addItems([str(pulse_calculation_method)])  # 更新combox选项
    elif Connect_status_meter == 2:
        # 偏差报警使能
        pulse_calculation_method = int(register_40021[-10])
        parameter_setting.label_107.setText(str(pulse_calculation_method))
        parameter_setting.label_107.setStyleSheet("background-color: rgb(255, 255, 255);\n")
        parameter_setting.comboBox_25.addItems([str(pulse_calculation_method)])  # 更新combox选项
    else:
        parameter_setting.label_107.setText('未连接')
        parameter_setting.label_107.setStyleSheet("background-color: rgb(255, 255, 0);\n")

    # 第1路流量报警上限使能
    if Connect_status_meter == 1:
        # 第1路流量报警上限使能
        high_alarm_1_enable = int(register_40015[-11])
        parameter_setting.label_111.setText(str(high_alarm_1_enable))
        parameter_setting.label_111.setStyleSheet("background-color: rgb(255, 255, 255);\n")
        parameter_setting.comboBox_26.addItems([str(high_alarm_1_enable)])  # 更新combox选项
    elif Connect_status_meter == 2:
        # 第1路流量报警上限使能
        high_alarm_1_enable = int(register_40021[-11])
        parameter_setting.label_111.setText(str(high_alarm_1_enable))
        parameter_setting.label_111.setStyleSheet("background-color: rgb(255, 255, 255);\n")
        parameter_setting.comboBox_26.addItems([str(high_alarm_1_enable)])  # 更新combox选项
    else:
        parameter_setting.label_111.setText('未连接')
        parameter_setting.label_111.setStyleSheet("background-color: rgb(255, 255, 0);\n")

    # 第1路流量报警下限使能
    if Connect_status_meter == 1:
        # 第1路流量报警下限使能
        low_alarm_1_enable = int(register_40015[-12])
        parameter_setting.label_119.setText(str(low_alarm_1_enable))
        parameter_setting.label_119.setStyleSheet("background-color: rgb(255, 255, 255);\n")
        parameter_setting.comboBox_28.addItems([str(low_alarm_1_enable)])  # 更新combox选项
    elif Connect_status_meter == 2:
        # 第1路流量报警下限使能
        low_alarm_1_enable = int(register_40021[-12])
        parameter_setting.label_119.setText(str(low_alarm_1_enable))
        parameter_setting.label_119.setStyleSheet("background-color: rgb(255, 255, 255);\n")
        parameter_setting.comboBox_28.addItems([str(low_alarm_1_enable)])  # 更新combox选项
    else:
        parameter_setting.label_119.setText('未连接')
        parameter_setting.label_119.setStyleSheet("background-color: rgb(255, 255, 0);\n")

    # 第2路流量报警上限使能
    if Connect_status_meter == 1:
        # 第2路流量报警上限使能
        high_alarm_2_enable = int(register_40015[-13])
        parameter_setting.label_115.setText(str(high_alarm_2_enable))
        parameter_setting.label_115.setStyleSheet("background-color: rgb(255, 255, 255);\n")
        parameter_setting.comboBox_27.addItems([str(high_alarm_2_enable)])  # 更新combox选项
    elif Connect_status_meter == 2:
        # 第2路流量报警上限使能
        high_alarm_2_enable = int(register_40021[-13])
        parameter_setting.label_115.setText(str(high_alarm_2_enable))
        parameter_setting.label_115.setStyleSheet("background-color: rgb(255, 255, 255);\n")
        parameter_setting.comboBox_27.addItems([str(high_alarm_2_enable)])  # 更新combox选项
    else:
        parameter_setting.label_115.setText('未连接')
        parameter_setting.label_115.setStyleSheet("background-color: rgb(255, 255, 0);\n")

    # 第2路流量报警下限使能
    if Connect_status_meter == 1:
        # 第2路流量报警下限使能
        low_alarm_2_enable = int(register_40015[-14])
        parameter_setting.label_123.setText(str(low_alarm_2_enable))
        parameter_setting.label_123.setStyleSheet("background-color: rgb(255, 255, 255);\n")
        parameter_setting.comboBox_29.addItems([str(low_alarm_2_enable)])  # 更新combox选项
    elif Connect_status_meter == 2:
        # 第2路流量报警下限使能
        low_alarm_2_enable = int(register_40021[-14])
        parameter_setting.label_123.setText(str(low_alarm_2_enable))
        parameter_setting.label_123.setStyleSheet("background-color: rgb(255, 255, 255);\n")
        parameter_setting.comboBox_29.addItems([str(low_alarm_2_enable)])  # 更新combox选项
    else:
        parameter_setting.label_123.setText('未连接')
        parameter_setting.label_123.setStyleSheet("background-color: rgb(255, 255, 0);\n")

    # 扩展参数上传使能
    if Connect_status_meter == 1:
        parameter_setting.label_130.setText('不可用')
        parameter_setting.label_130.setStyleSheet("background-color: rgb(255, 255, 0);\n")
    elif Connect_status_meter == 2:
        # 扩展参数上传使能
        extension_parameter_enable = int(register_40021[-15]) + int(register_40021[-16]) * 2
        parameter_setting.label_130.setText(str(extension_parameter_enable))
        parameter_setting.label_130.setStyleSheet("background-color: rgb(255, 255, 255);\n")
        parameter_setting.comboBox_32.addItems([str(extension_parameter_enable)])  # 更新combox选项
    else:
        parameter_setting.label_130.setText('未连接')
        parameter_setting.label_130.setStyleSheet("background-color: rgb(255, 255, 0);\n")

    # 设置通道1流量显示单位
    if Connect_status_meter == 1:
        parameter_setting.label_149.setText('不可用')
        parameter_setting.label_149.setStyleSheet("background-color: rgb(255, 255, 0);\n")
    elif Connect_status_meter == 2:
        # 设置通道1流量显示单位
        flow_unit = int(register_40022[-12]) + int(register_40022[-13]) * 2
        if flow_unit == 0:
            flow_unit_display = '0-L/min'
        elif flow_unit == 1:
            flow_unit_display = '1-ml/min'
        elif flow_unit == 2:
            flow_unit_display = '2-L/h'
        elif flow_unit == 3:
            flow_unit_display = '3-ml/h'
        parameter_setting.label_149.setText(flow_unit_display)
        parameter_setting.label_149.setStyleSheet("background-color: rgb(255, 255, 255);\n")
        parameter_setting.comboBox_38.addItems([str(extension_parameter_enable)])  # 更新combox选项
    else:
        parameter_setting.label_149.setText('未连接')
        parameter_setting.label_149.setStyleSheet("background-color: rgb(255, 255, 0);\n")

    # 设置通道2流量显示单位
    if Connect_status_meter == 1:
        parameter_setting.label_152.setText('不可用')
        parameter_setting.label_152.setStyleSheet("background-color: rgb(255, 255, 0);\n")
    elif Connect_status_meter == 2:
        # 设置通道2流量显示单位
        flow_unit = int(register_40022[-14]) + int(register_40022[-15]) * 2
        if flow_unit == 0:
            flow_unit_display = '0-L/min'
        elif flow_unit == 1:
            flow_unit_display = '1-ml/min'
        elif flow_unit == 2:
            flow_unit_display = '2-L/h'
        elif flow_unit == 3:
            flow_unit_display = '3-ml/h'
        parameter_setting.label_152.setText(flow_unit_display)
        parameter_setting.label_152.setStyleSheet("background-color: rgb(255, 255, 255);\n")
        parameter_setting.comboBox_39.addItems([str(flow_unit)])  # 更新combox选项
    else:
        parameter_setting.label_152.setText('未连接')
        parameter_setting.label_152.setStyleSheet("background-color: rgb(255, 255, 0);\n")

    # 偏差报警系数
    if Connect_status_meter == 1:
        parameter_setting.label_41.setText(str(Meter_data[18]))
        parameter_setting.label_41.setStyleSheet("background-color: rgb(255, 255, 255);\n")
        parameter_setting.comboBox_10.addItems([str(Meter_data[18])])  # 更新combox选项
    elif Connect_status_meter == 2:
        parameter_setting.label_41.setText(str(Meter_data_2_plus[24]))
        parameter_setting.label_41.setStyleSheet("background-color: rgb(255, 255, 255);\n")
        parameter_setting.comboBox_10.addItems([str(Meter_data_2_plus[24])])  # 更新combox选项
    else:
        parameter_setting.label_41.setText('未连接')
        parameter_setting.label_41.setStyleSheet("background-color: rgb(255, 255, 0);\n")

    # 偏差报警比例
    if Connect_status_meter == 1:
        parameter_setting.label_37.setText(str(Meter_data[19]))
        parameter_setting.label_37.setStyleSheet("background-color: rgb(255, 255, 255);\n")
        parameter_setting.comboBox_9.addItems([str(Meter_data[19])])  # 更新combox选项
    elif Connect_status_meter == 2:
        parameter_setting.label_37.setText(str(Meter_data_2_plus[25]))
        parameter_setting.label_37.setStyleSheet("background-color: rgb(255, 255, 255);\n")
        parameter_setting.comboBox_9.addItems([str(Meter_data_2_plus[25])])  # 更新combox选项
    else:
        parameter_setting.label_37.setText('未连接')
        parameter_setting.label_37.setStyleSheet("background-color: rgb(255, 255, 0);\n")

    # 第1路上限报警
    if Connect_status_meter == 1:
        high_alarm_1 = Decimal(str(Meter_data[20])) + Decimal(str(Meter_data[21] / 1000))
    elif Connect_status_meter == 2:
        high_alarm_1 = Decimal(str(Meter_data_2_plus[26] * 65536)) + \
                       Decimal(str(Meter_data_2_plus[27])) + \
                       Decimal(str(Meter_data_2_plus[28] / 1000))
    if Connect_status_meter == 0:
        parameter_setting.label_33.setText('未连接')
        parameter_setting.label_33.setStyleSheet("background-color: rgb(255, 255, 0);\n")
    else:
        parameter_setting.label_33.setText(str(high_alarm_1))
        parameter_setting.label_33.setStyleSheet("background-color: rgb(255, 255, 255);\n")
        parameter_setting.comboBox_8.addItems([str(high_alarm_1)])  # 更新combox选项

    # 第1路下限报警
    if Connect_status_meter == 1:
        low_alarm_1 = Decimal(str(Meter_data[22])) + Decimal(str(Meter_data[23] / 1000))
    elif Connect_status_meter == 2:
        low_alarm_1 = Decimal(str(Meter_data_2_plus[29] * 65536)) + \
                      Decimal(str(Meter_data_2_plus[30])) + \
                      Decimal(str(Meter_data_2_plus[31] / 1000))
    if Connect_status_meter == 0:
        parameter_setting.label_46.setText('未连接')
        parameter_setting.label_46.setStyleSheet("background-color: rgb(255, 255, 0);\n")
    else:
        parameter_setting.label_46.setText(str(low_alarm_1))
        parameter_setting.label_46.setStyleSheet("background-color: rgb(255, 255, 255);\n")
        parameter_setting.comboBox_11.addItems([str(low_alarm_1)])  # 更新combox选项

    # 第2路上限报警
    if Connect_status_meter == 1:
        high_alarm_2 = Decimal(str(Meter_data[24])) + Decimal(str(Meter_data[25] / 1000))
    elif Connect_status_meter == 2:
        high_alarm_2 = Decimal(str(Meter_data_2_plus[32] * 65536)) + \
                       Decimal(str(Meter_data_2_plus[33])) + \
                       Decimal(str(Meter_data_2_plus[34] / 1000))
    if Connect_status_meter == 0:
        parameter_setting.label_50.setText('未连接')
        parameter_setting.label_50.setStyleSheet("background-color: rgb(255, 255, 0);\n")
    else:
        parameter_setting.label_50.setText(str(high_alarm_2))
        parameter_setting.label_50.setStyleSheet("background-color: rgb(255, 255, 255);\n")
        parameter_setting.comboBox_12.addItems([str(high_alarm_2)])  # 更新combox选项

    # 第2路下限报警
    if Connect_status_meter == 1:
        low_alarm_2 = Decimal(str(Meter_data[26])) + Decimal(str(Meter_data[27] / 1000))
    elif Connect_status_meter == 2:
        low_alarm_2 = Decimal(str(Meter_data_2_plus[35] * 65536)) + \
                      Decimal(str(Meter_data_2_plus[36])) + \
                      Decimal(str(Meter_data_2_plus[37] / 1000))

    if Connect_status_meter == 0:
        parameter_setting.label_56.setText('未连接')
        parameter_setting.label_56.setStyleSheet("background-color: rgb(255, 255, 0);\n")
    else:
        parameter_setting.label_56.setText(str(low_alarm_2))
        parameter_setting.label_56.setStyleSheet("background-color: rgb(255, 255, 255);\n")
        parameter_setting.comboBox_13.addItems([str(low_alarm_2)])  # 更新combox选项

    # 第1路满刻度
    if Connect_status_meter == 1:
        full_scale_1 = Decimal(str(Meter_data[28])) + Decimal(str(Meter_data[29] / 1000))
    elif Connect_status_meter == 2:
        full_scale_1 = Decimal(str(Meter_data_2_plus[38] * 65536)) + \
                       Decimal(str(Meter_data_2_plus[39])) + \
                       Decimal(str(Meter_data_2_plus[40] / 1000))
    if Connect_status_meter == 0:
        parameter_setting.label_124.setText('未连接')
        parameter_setting.label_124.setStyleSheet("background-color: rgb(255, 255, 0);\n")
    else:
        parameter_setting.label_124.setText(str(full_scale_1))
        parameter_setting.label_124.setStyleSheet("background-color: rgb(255, 255, 255);\n")
        parameter_setting.comboBox_30.addItems([str(full_scale_1)])  # 更新combox选项

    # 第2路满刻度
    if Connect_status_meter == 1:
        full_scale_2 = Decimal(str(Meter_data[30])) + Decimal(str(Meter_data[31] / 1000))
    elif Connect_status_meter == 2:
        full_scale_2 = Decimal(str(Meter_data_2_plus[41] * 65536)) + \
                       Decimal(str(Meter_data_2_plus[42])) + \
                       Decimal(str(Meter_data_2_plus[43] / 1000))

    if Connect_status_meter == 0:
        parameter_setting.label_128.setText('未连接')
        parameter_setting.label_128.setStyleSheet("background-color: rgb(255, 255, 0);\n")
    else:
        parameter_setting.label_128.setText(str(full_scale_2))
        parameter_setting.label_128.setStyleSheet("background-color: rgb(255, 255, 255);\n")
        parameter_setting.comboBox_31.addItems([str(full_scale_2)])  # 更新combox选项

    # 第1路A点校正脉冲数
    if Connect_status_meter == 1:
        calibration_pulse_1_a = Meter_data[36]
    elif Connect_status_meter == 2:
        calibration_pulse_1_a = Meter_data_2_plus[48]
    if Connect_status_meter == 0:
        parameter_setting.label_59.setText('未连接')
        parameter_setting.label_59.setStyleSheet("background-color: rgb(255, 255, 0);\n")
    else:
        parameter_setting.label_59.setText(str(calibration_pulse_1_a))
        parameter_setting.label_59.setStyleSheet("background-color: rgb(255, 255, 255);\n")
        parameter_setting.comboBox_7.addItems([str(calibration_pulse_1_a)])  # 更新combox选项

    # 第1路A点校正容积数
    if Connect_status_meter == 1:
        calibration_volume_1_a = Meter_data[37]
    elif Connect_status_meter == 2:
        calibration_volume_1_a = Meter_data_2_plus[49] * 65536 + Meter_data_2_plus[50]
    if Connect_status_meter == 0:
        parameter_setting.label_63.setText('未连接')
        parameter_setting.label_63.setStyleSheet("background-color: rgb(255, 255, 0);\n")
    else:
        parameter_setting.label_63.setText(str(calibration_volume_1_a))
        parameter_setting.label_63.setStyleSheet("background-color: rgb(255, 255, 255);\n")
        parameter_setting.comboBox_14.addItems([str(calibration_volume_1_a)])  # 更新combox选项

    # 第1路B点校正脉冲数
    if Connect_status_meter == 1:
        calibration_pulse_1_b = Meter_data[38]
    elif Connect_status_meter == 2:
        calibration_pulse_1_b = Meter_data_2_plus[51]
    if Connect_status_meter == 0:
        parameter_setting.label_67.setText('未连接')
        parameter_setting.label_67.setStyleSheet("background-color: rgb(255, 255, 0);\n")
    else:
        parameter_setting.label_67.setText(str(calibration_pulse_1_b))
        parameter_setting.label_67.setStyleSheet("background-color: rgb(255, 255, 255);\n")
        parameter_setting.comboBox_15.addItems([str(calibration_pulse_1_b)])  # 更新combox选项

    # 第1路B点校正容积数
    if Connect_status_meter == 1:
        calibration_volume_1_b = Meter_data[39]
    elif Connect_status_meter == 2:
        calibration_volume_1_b = Meter_data_2_plus[52] * 65536 + Meter_data_2_plus[53]
    if Connect_status_meter == 0:
        parameter_setting.label_71.setText('未连接')
        parameter_setting.label_71.setStyleSheet("background-color: rgb(255, 255, 0);\n")
    else:
        parameter_setting.label_71.setText(str(calibration_volume_1_b))
        parameter_setting.label_71.setStyleSheet("background-color: rgb(255, 255, 255);\n")
        parameter_setting.comboBox_16.addItems([str(calibration_volume_1_b)])  # 更新combox选项

    # 第1路C点校正脉冲数
    if Connect_status_meter == 1:
        calibration_pulse_1_c = Meter_data[40]
    elif Connect_status_meter == 2:
        calibration_pulse_1_c = Meter_data_2_plus[54]
    if Connect_status_meter == 0:
        parameter_setting.label_75.setText('未连接')
        parameter_setting.label_75.setStyleSheet("background-color: rgb(255, 255, 0);\n")
    else:
        parameter_setting.label_75.setText(str(calibration_pulse_1_c))
        parameter_setting.label_75.setStyleSheet("background-color: rgb(255, 255, 255);\n")
        parameter_setting.comboBox_17.addItems([str(calibration_pulse_1_c)])  # 更新combox选项

    # 第1路C点校正容积数
    if Connect_status_meter == 1:
        calibration_volume_1_c = Meter_data[41]
    elif Connect_status_meter == 2:
        calibration_volume_1_c = Meter_data_2_plus[55] * 65536 + Meter_data_2_plus[56]
    if Connect_status_meter == 0:
        parameter_setting.label_79.setText('未连接')
        parameter_setting.label_79.setStyleSheet("background-color: rgb(255, 255, 0);\n")
    else:
        parameter_setting.label_79.setText(str(calibration_volume_1_c))
        parameter_setting.label_79.setStyleSheet("background-color: rgb(255, 255, 255);\n")
        parameter_setting.comboBox_18.addItems([str(calibration_volume_1_c)])  # 更新combox选项

    # 第2路A点校正脉冲数
    if Connect_status_meter == 1:
        calibration_pulse_2_a = Meter_data[42]
    elif Connect_status_meter == 2:
        calibration_pulse_2_a = Meter_data_2_plus[57]
    if Connect_status_meter == 0:
        parameter_setting.label_92.setText('未连接')
        parameter_setting.label_92.setStyleSheet("background-color: rgb(255, 255, 0);\n")
    else:
        parameter_setting.label_92.setText(str(calibration_pulse_2_a))
        parameter_setting.label_92.setStyleSheet("background-color: rgb(255, 255, 255);\n")
        parameter_setting.comboBox_22.addItems([str(calibration_pulse_2_a)])  # 更新combox选项

    # 第2路A点校正容积数
    if Connect_status_meter == 1:
        calibration_volume_2_a = Meter_data[43]
    elif Connect_status_meter == 2:
        calibration_volume_2_a = Meter_data_2_plus[58] * 65536 + Meter_data_2_plus[59]
    if Connect_status_meter == 0:
        parameter_setting.label_103.setText('未连接')
        parameter_setting.label_103.setStyleSheet("background-color: rgb(255, 255, 0);\n")
    else:
        parameter_setting.label_103.setText(str(calibration_volume_2_a))
        parameter_setting.label_103.setStyleSheet("background-color: rgb(255, 255, 255);\n")
        parameter_setting.comboBox_24.addItems([str(calibration_volume_2_a)])  # 更新combox选项

    # 第2路B点校正脉冲数
    if Connect_status_meter == 1:
        calibration_pulse_2_b = Meter_data[44]
    elif Connect_status_meter == 2:
        calibration_pulse_2_b = Meter_data_2_plus[60]
    if Connect_status_meter == 0:
        parameter_setting.label_87.setText('未连接')
        parameter_setting.label_87.setStyleSheet("background-color: rgb(255, 255, 0);\n")
    else:
        parameter_setting.label_87.setText(str(calibration_pulse_2_b))
        parameter_setting.label_87.setStyleSheet("background-color: rgb(255, 255, 255);\n")
        parameter_setting.comboBox_20.addItems([str(calibration_pulse_2_b)])  # 更新combox选项

    # 第2路B点校正容积数
    if Connect_status_meter == 1:
        calibration_volume_2_b = Meter_data[45]
    elif Connect_status_meter == 2:
        calibration_volume_2_b = Meter_data_2_plus[61] * 65536 + Meter_data_2_plus[62]
    if Connect_status_meter == 0:
        parameter_setting.label_99.setText('未连接')
        parameter_setting.label_99.setStyleSheet("background-color: rgb(255, 255, 0);\n")
    else:
        parameter_setting.label_99.setText(str(calibration_volume_2_b))
        parameter_setting.label_99.setStyleSheet("background-color: rgb(255, 255, 255);\n")
        parameter_setting.comboBox_23.addItems([str(calibration_volume_2_b)])  # 更新combox选项

    # 第2路C点校正脉冲数
    if Connect_status_meter == 1:
        calibration_pulse_2_c = Meter_data[46]
    elif Connect_status_meter == 2:
        calibration_pulse_2_c = Meter_data_2_plus[63]
    if Connect_status_meter == 0:
        parameter_setting.label_91.setText('未连接')
        parameter_setting.label_91.setStyleSheet("background-color: rgb(255, 255, 0);\n")
    else:
        parameter_setting.label_91.setText(str(calibration_pulse_2_c))
        parameter_setting.label_91.setStyleSheet("background-color: rgb(255, 255, 255);\n")
        parameter_setting.comboBox_21.addItems([str(calibration_pulse_2_c)])  # 更新combox选项

    # 第2路C点校正容积数
    if Connect_status_meter == 1:
        calibration_volume_2_c = Meter_data[47]
    elif Connect_status_meter == 2:
        calibration_volume_2_c = Meter_data_2_plus[64] * 65536 + Meter_data_2_plus[65]
    if Connect_status_meter == 0:
        parameter_setting.label_83.setText('未连接')
        parameter_setting.label_83.setStyleSheet("background-color: rgb(255, 255, 0);\n")
    else:
        parameter_setting.label_83.setText(str(calibration_volume_2_c))
        parameter_setting.label_83.setStyleSheet("background-color: rgb(255, 255, 255);\n")
        parameter_setting.comboBox_19.addItems([str(calibration_volume_2_c)])  # 更新combox选项

    # 显示开机字符串
    if Connect_status_meter == 0:
        parameter_setting.label_134.setText('未连接')
        parameter_setting.label_134.setStyleSheet("background-color: rgb(255, 255, 0);\n")
    elif Connect_status_meter == 1:
        parameter_setting.label_134.setText('2代仪表不可设置')
        parameter_setting.label_134.setStyleSheet("background-color: rgb(255, 255, 0);\n")
    elif Connect_status_meter == 2:
        meter_start_string_length = Meter_data_2_plus[89]
        # print(meter_start_string_length)
        meter_start_string = Meter_data_2_plus[90:100]
        # print(meter_start_string)
        meter_start_string_display = data_translation_modal.get_result_string(meter_start_string_length,
                                                                              meter_start_string)
        parameter_setting.label_134.setText(str(meter_start_string_display))
        parameter_setting.label_134.setStyleSheet("background-color: rgb(255, 255, 255);\n")
        parameter_setting.comboBox_33.addItems([str(meter_start_string_display)])  # 更新combox选项

    # 显示通道1字符串
    if Connect_status_meter == 0:
        parameter_setting.label_137.setText('未连接')
        parameter_setting.label_137.setStyleSheet("background-color: rgb(255, 255, 0);\n")
    elif Connect_status_meter == 1:
        parameter_setting.label_137.setText('2代仪表不可设置')
        parameter_setting.label_137.setStyleSheet("background-color: rgb(255, 255, 0);\n")
    elif Connect_status_meter == 2:
        meter_ch1_string_length = Meter_data_2_plus[100]
        # print(meter_ch1_string_length)
        meter_ch1_string = Meter_data_2_plus[101:105]
        print(meter_ch1_string)
        meter_ch1_string_display = data_translation_modal.get_result_string(meter_ch1_string_length,
                                                                            meter_ch1_string)
        parameter_setting.label_137.setText(str(meter_ch1_string_display))
        parameter_setting.label_137.setStyleSheet("background-color: rgb(255, 255, 255);\n")
        parameter_setting.comboBox_34.addItems([str(meter_ch1_string_display)])  # 更新combox选项

    # 显示通道2字符串
    if Connect_status_meter == 0:
        parameter_setting.label_140.setText('未连接')
        parameter_setting.label_140.setStyleSheet("background-color: rgb(255, 255, 0);\n")
    elif Connect_status_meter == 1:
        parameter_setting.label_140.setText('2代仪表不可设置')
        parameter_setting.label_140.setStyleSheet("background-color: rgb(255, 255, 0);\n")
    elif Connect_status_meter == 2:
        meter_ch2_string_length = Meter_data_2_plus[105]
        # print(meter_ch2_string_length)
        meter_ch2_string = Meter_data_2_plus[106:110]
        # print(meter_ch2_string)
        meter_ch2_string_display = data_translation_modal.get_result_string(meter_ch2_string_length,
                                                                            meter_ch2_string)
        parameter_setting.label_140.setText(str(meter_ch2_string_display))
        parameter_setting.label_140.setStyleSheet("background-color: rgb(255, 255, 255);\n")
        parameter_setting.comboBox_35.addItems([str(meter_ch2_string_display)])  # 更新combox选项

    # 显示平台域名
    if Connect_status_meter == 0:
        parameter_setting.label_143.setText('未连接')
        parameter_setting.label_143.setStyleSheet("background-color: rgb(255, 255, 0);\n")
    elif Connect_status_meter == 1:
        web_address_string_length = Meter_data[50]
        # print(web_address_string_length)
        web_address_string = Meter_data[51:65]
        # print(web_address_string)
        web_address_string_display = data_translation_modal.get_result_string(web_address_string_length,
                                                                              web_address_string)
        parameter_setting.label_143.setText(str(web_address_string_display))
        parameter_setting.label_143.setStyleSheet("background-color: rgb(255, 255, 255);\n")
        parameter_setting.comboBox_36.addItems([str(web_address_string_display)])  # 更新combox选项
    elif Connect_status_meter == 2:
        web_address_string_length = Meter_data_2_plus[68]
        # print(web_address_string_length)
        web_address_string = Meter_data_2_plus[69:84]
        # print(web_address_string)
        web_address_string_display = data_translation_modal.get_result_string(web_address_string_length,
                                                                              web_address_string)
        parameter_setting.label_143.setText(str(web_address_string_display))
        parameter_setting.label_143.setStyleSheet("background-color: rgb(255, 255, 255);\n")
        parameter_setting.comboBox_36.addItems([str(web_address_string_display)])  # 更新combox选项

    # 显示端口号
    if Connect_status_meter == 0:
        parameter_setting.label_146.setText('未连接')
        parameter_setting.label_146.setStyleSheet("background-color: rgb(255, 255, 0);\n")
    elif Connect_status_meter == 1:
        parameter_setting.label_146.setText('2代仪表不可设置')
        parameter_setting.label_146.setStyleSheet("background-color: rgb(255, 255, 0);\n")
    elif Connect_status_meter == 2:
        web_port_number = Meter_data_2_plus[84]
        parameter_setting.label_146.setText(str(web_port_number))
        parameter_setting.label_146.setStyleSheet("background-color: rgb(255, 255, 255);\n")
        parameter_setting.comboBox_37.addItems([str(web_port_number)])  # 更新combox选项

    # 定时刷新显示界面数据
    parameter_setting.timer = QTimer()  # 初始化定时器
    parameter_setting.timer.timeout.connect(parameter_modify_reflash_parameter)  # 定时操作
    parameter_setting.timer.start(1000)  # 每秒刷新1次


# 设置FS编号
def modify_FS_number():
    # FS = Meter_data[3] * 65536 + Meter_data[4]
    # Modbus_parameter['address'] = int(Connect.comboBox_6.currentText())  # 仪表从站站号
    FS_number = parameter_setting.comboBox_1.currentText()
    print(FS_number)
    FS_number = int(FS_number[2:])
    print(FS_number)
    register_write_41001 = int(FS_number / 65536)
    print(register_write_41001)
    register_write_41002 = FS_number % 65536
    print(register_write_41002)
    if Connect_status_meter == 2:
        # 解锁仪表
        unlock_meter_setting = WriteMultipleRegister('解锁仪表',
                                                     '未连接仪表！',
                                                     Meter_data_2_plus_write['41180'],  # 开始地址
                                                     [43690, 21845],  # 写入数据
                                                     '解锁仪表失败！',
                                                     '解锁仪表成功！')  # 初始化类
        unlock_meter_setting.write_data_to_meter_register_multiple()
    FS_change = WriteMultipleRegister('修改仪表FS编号',
                                      '未连接仪表！',
                                      Meter_data_write['41001'],
                                      [register_write_41001, register_write_41002],  # 写入数据
                                      '修改仪表FS编号失败！',
                                      '修改仪表FS编号成功！')  # 初始化类
    FS_change.write_data_to_meter_register_multiple()  # 写入寄存器


# 修改modbus地址
def change_modbus_address():
    # 改写Modbus从站地址
    global Connect_status_meter
    if Connect_status_meter == 0:
        messagebox_in_Chinese.information_messagebox('Modbus从站地址设置', '未连接仪表！')
        Connect.show()  # 打开连接仪表子窗体
    else:
        data_write = RS485.modbus_write(Modbus_parameter['PORT'],  # 端口号
                                        Modbus_parameter['baudrate'],  # 波特率
                                        Modbus_parameter['bytesize'],  # 数据位
                                        Modbus_parameter['parity'],  # 校验位
                                        Modbus_parameter['stopbits'],  # 停止位
                                        Modbus_parameter['address'],  # 从站地址
                                        Meter_data_write['41003'],  # Modbus地址寄存器地址
                                        int(parameter_setting.comboBox_2.currentText()),  # 新的Modbus地址
                                        )
        print(data_write)

        if (data_write == []) or (data_write == -1):
            messagebox_in_Chinese.information_messagebox('Modbus从站地址设置', '设置Modbus从站地址失败！')
            return -1  # 返回连接失败
        else:
            # 更新当前modbus地址
            Modbus_parameter['address'] = int(parameter_setting.comboBox_2.currentText())
            if Connect_status_meter == 1:
                Meter_data[70] = Modbus_parameter['address']
            elif Connect_status_meter == 2:
                Meter_data_2_plus[110] = Modbus_parameter['address']
            save_meter_config_log()  # 将配置参数导出至配置记录
            messagebox_in_Chinese.information_messagebox('Modbus从站地址设置', '成功设置Modbus从站地址！')
            return 0  # 返回连接成功


# 修改流量校正方式
def change_calibration_method():
    calibration_method = int(parameter_setting.comboBox_3.currentText())
    print(calibration_method)
    configure_calibration_method = WriteSingleRegister('修改流量校正方式',
                                                       '未连接仪表！',
                                                       Meter_data_write['41004'],  # 开始地址
                                                       calibration_method,  # 写入数据
                                                       '修改仪表流量校正方式失败！',
                                                       '修改仪表流量校正方式成功！')  # 初始化类
    configure_calibration_method.write_data_to_meter_register_single()


# 修改脉冲统计方式
def change_pulse_calculation_method():
    calculation_method = int(parameter_setting.comboBox_5.currentText())
    print(calculation_method)
    modify_calibration_method = WriteSingleRegister('修改脉冲统计方式',
                                                    '未连接仪表！',
                                                    Meter_data_write['41005'],  # 开始地址
                                                    calculation_method,  # 写入数据
                                                    '修改脉冲统计方式失败',
                                                    '修改脉冲统计方式成功！')  # 初始化类
    modify_calibration_method.write_data_to_meter_register_single()


# 修改采集周期
def change_pulse_period():
    period = int(parameter_setting.comboBox_6.currentText())
    print(period)
    modify_pulse_period = WriteSingleRegister('修改采集周期',
                                              '未连接仪表！',
                                              Meter_data_write['41006'],  # 开始地址
                                              period,  # 写入数据
                                              '修改采集周期失败！',
                                              '修改采集周期成功！')  # 初始化类
    modify_pulse_period.write_data_to_meter_register_single()


# 修改SDTU编号
def change_SDTU_number():
    # FS = Meter_data[3] * 65536 + Meter_data[4]
    # Modbus_parameter['address'] = int(Connect.comboBox_6.currentText())  # 仪表从站站号
    SDTU_number = parameter_setting.comboBox_4.currentText()
    print(SDTU_number)
    SDTU_number = int(SDTU_number[4:])
    print(SDTU_number)
    register_write_1 = int(SDTU_number / 65536)
    print(register_write_1)
    register_write_2 = SDTU_number % 65536
    print(register_write_2)
    if Connect_status_meter == 1:
        register_start = Meter_data_write['41038']
    elif Connect_status_meter == 2:
        register_start = Meter_data_2_plus_write['41050']
        # 解锁仪表
        unlock_meter_setting = WriteMultipleRegister('解锁仪表',
                                                     '未连接仪表！',
                                                     Meter_data_2_plus_write['41180'],  # 开始地址
                                                     [43690, 21845],  # 写入数据
                                                     '解锁仪表失败！',
                                                     '解锁仪表成功！')  # 初始化类
        unlock_meter_setting.write_data_to_meter_register_multiple()
    SDTU_change = WriteMultipleRegister('修改仪表SDTU编号',
                                        '未连接仪表！',
                                        register_start,
                                        [register_write_1, register_write_2],  # 写入数据
                                        '修改仪表SDTU编号失败！',
                                        '修改仪表SDTU编号成功！')  # 初始化类
    SDTU_change.write_data_to_meter_register_multiple()  # 写入寄存器


# 修改偏差报警系数
def change_flow_deviation():
    flow_deviation = int(parameter_setting.comboBox_10.currentText())
    print(flow_deviation)
    deviation_set = WriteSingleRegister('修改偏差报警系数',
                                        '未连接仪表！',
                                        Meter_data_write['41008'],  # 开始地址
                                        flow_deviation,  # 写入数据
                                        '修改偏差报警系数失败！',
                                        '修改偏差报警系数成功！')  # 初始化类
    deviation_set.write_data_to_meter_register_single()


# 修改偏差报警比例
def change_flow_deviation_ratio():
    flow_deviation_ratio = int(parameter_setting.comboBox_9.currentText())
    print(flow_deviation_ratio)
    deviation_ratio_set = WriteSingleRegister('修改偏差报警比例',
                                              '未连接仪表！',
                                              Meter_data_write['41009'],  # 开始地址
                                              flow_deviation_ratio,  # 写入数据
                                              '修改偏差报警比例失败！',
                                              '修改偏差报警比例成功！')  # 初始化类
    deviation_ratio_set.write_data_to_meter_register_single()


# 修改1路报警上限
def change_1_high_flow_alarm():
    combobox_text = parameter_setting.comboBox_8.currentText()
    if Connect_status_meter == 1:
        high_flow_alarm_1_integer = int(Decimal(combobox_text))
        high_flow_alarm_1_decimal = int((Decimal(combobox_text) - int(Decimal(combobox_text))) * 1000)
        print(high_flow_alarm_1_integer)
        print(high_flow_alarm_1_decimal)
        high_flow_alarm_1_set = WriteMultipleRegister('修改1路报警上限',
                                                      '未连接仪表！',
                                                      Meter_data_write['41011'],  # 开始地址
                                                      [high_flow_alarm_1_integer, high_flow_alarm_1_decimal],  # 写入数据
                                                      '修改1路报警上限失败！',
                                                      '修改1路报警上限成功！')  # 初始化类
        high_flow_alarm_1_set.write_data_to_meter_register_multiple()
    elif Connect_status_meter == 2:
        high_flow_alarm_1_integer_high = int(int(Decimal(combobox_text)) / 65536)
        high_flow_alarm_1_integer = int(int(Decimal(combobox_text)) % 65536)
        high_flow_alarm_1_decimal = int((Decimal(combobox_text) - int(Decimal(combobox_text))) * 1000)
        print(high_flow_alarm_1_integer_high)
        print(high_flow_alarm_1_integer)
        print(high_flow_alarm_1_decimal)
        high_flow_alarm_1_set = WriteMultipleRegister('修改1路报警上限',
                                                      '未连接仪表！',
                                                      Meter_data_2_plus_write['41011'],  # 开始地址
                                                      [high_flow_alarm_1_integer_high,
                                                       high_flow_alarm_1_integer,
                                                       high_flow_alarm_1_decimal],  # 写入数据
                                                      '修改1路报警上限失败！',
                                                      '修改1路报警上限成功！')  # 初始化类
        high_flow_alarm_1_set.write_data_to_meter_register_multiple()


# 修改1路报警下限
def change_1_low_flow_alarm():
    combobox_text = parameter_setting.comboBox_11.currentText()
    if Connect_status_meter == 1:
        low_flow_alarm_1_integer = int(Decimal(combobox_text))
        low_flow_alarm_1_decimal = int((Decimal(combobox_text) - int(Decimal(combobox_text))) * 1000)
        print(low_flow_alarm_1_integer)
        print(low_flow_alarm_1_decimal)
        register_start = Meter_data_write['41014']
        low_flow_alarm_1_set = WriteMultipleRegister('修改1路报警下限',
                                                     '未连接仪表！',
                                                     register_start,  # 开始地址
                                                     [low_flow_alarm_1_integer, low_flow_alarm_1_decimal],  # 写入数据
                                                     '修改1路报警下限失败！',
                                                     '修改1路报警下限成功！')  # 初始化类
        low_flow_alarm_1_set.write_data_to_meter_register_multiple()
    elif Connect_status_meter == 2:
        low_flow_alarm_1_integer_high = int(Decimal(combobox_text) / 65536)
        low_flow_alarm_1_integer = int(Decimal(combobox_text) % 65536)
        low_flow_alarm_1_decimal = int((Decimal(combobox_text) - int(Decimal(combobox_text))) * 1000)
        print(low_flow_alarm_1_integer_high)
        print(low_flow_alarm_1_integer)
        print(low_flow_alarm_1_decimal)
        register_start = Meter_data_2_plus_write['41015']
        low_flow_alarm_1_set = WriteMultipleRegister('修改1路报警下限',
                                                     '未连接仪表！',
                                                     register_start,  # 开始地址
                                                     [low_flow_alarm_1_integer_high,
                                                      low_flow_alarm_1_integer,
                                                      low_flow_alarm_1_decimal],  # 写入数据
                                                     '修改1路报警下限失败！',
                                                     '修改1路报警下限成功！')  # 初始化类
        low_flow_alarm_1_set.write_data_to_meter_register_multiple()


# 修改2路报警上限
def change_2_high_flow_alarm():
    combobox_text = parameter_setting.comboBox_12.currentText()
    if Connect_status_meter == 1:
        high_flow_alarm_2_integer = int(Decimal(combobox_text))
        high_flow_alarm_2_decimal = int((Decimal(combobox_text) - int(Decimal(combobox_text))) * 1000)
        print(high_flow_alarm_2_integer)
        print(high_flow_alarm_2_decimal)
        high_flow_alarm_2_set = WriteMultipleRegister('修改2路报警上限',
                                                      '未连接仪表！',
                                                      Meter_data_write['41017'],  # 开始地址
                                                      [high_flow_alarm_2_integer, high_flow_alarm_2_decimal],  # 写入数据
                                                      '修改2路报警上限失败！',
                                                      '修改2路报警上限成功！')  # 初始化类
        high_flow_alarm_2_set.write_data_to_meter_register_multiple()
    elif Connect_status_meter == 2:
        high_flow_alarm_2_integer_high = int(Decimal(combobox_text) / 65536)
        high_flow_alarm_2_integer = int(Decimal(combobox_text) % 65536)
        high_flow_alarm_2_decimal = int((Decimal(combobox_text) - int(Decimal(combobox_text))) * 1000)
        print(high_flow_alarm_2_integer_high)
        print(high_flow_alarm_2_integer)
        print(high_flow_alarm_2_decimal)
        register_start = Meter_data_2_plus_write['41019']
        high_flow_alarm_2_set = WriteMultipleRegister('修改2路报警上限',
                                                      '未连接仪表！',
                                                      register_start,  # 开始地址
                                                      [high_flow_alarm_2_integer_high,
                                                       high_flow_alarm_2_integer,
                                                       high_flow_alarm_2_decimal],  # 写入数据
                                                      '修改2路报警上限失败！',
                                                      '修改2路报警上限成功！')  # 初始化类
        high_flow_alarm_2_set.write_data_to_meter_register_multiple()


# 修改2路报警下限
def change_2_low_flow_alarm():
    combobox_text = parameter_setting.comboBox_13.currentText()
    if Connect_status_meter == 1:
        low_flow_alarm_2_integer = int(Decimal(combobox_text))
        low_flow_alarm_2_decimal = int((Decimal(combobox_text) - int(Decimal(combobox_text))) * 1000)
        print(low_flow_alarm_2_integer)
        print(low_flow_alarm_2_decimal)
        low_flow_alarm_2_set = WriteMultipleRegister('修改2路报警下限',
                                                     '未连接仪表！',
                                                     Meter_data_write['41020'],  # 开始地址
                                                     [low_flow_alarm_2_integer, low_flow_alarm_2_decimal],  # 写入数据
                                                     '修改2路报警下限失败！',
                                                     '修改2路报警下限成功！')  # 初始化类
        low_flow_alarm_2_set.write_data_to_meter_register_multiple()
    elif Connect_status_meter == 2:
        low_flow_alarm_2_integer_high = int(Decimal(combobox_text) / 65536)
        low_flow_alarm_2_integer = int(Decimal(combobox_text) % 65536)
        low_flow_alarm_2_decimal = int((Decimal(combobox_text) - int(Decimal(combobox_text))) * 1000)
        print(low_flow_alarm_2_integer_high)
        print(low_flow_alarm_2_integer)
        print(low_flow_alarm_2_decimal)
        register_start = Meter_data_2_plus_write['41023']
        low_flow_alarm_2_set = WriteMultipleRegister('修改2路报警下限',
                                                     '未连接仪表！',
                                                     register_start,  # 开始地址
                                                     [low_flow_alarm_2_integer_high,
                                                      low_flow_alarm_2_integer,
                                                      low_flow_alarm_2_decimal],  # 写入数据
                                                     '修改2路报警下限失败！',
                                                     '修改2路报警下限成功！')  # 初始化类
        low_flow_alarm_2_set.write_data_to_meter_register_multiple()


# 修改偏差报警使能
def enable_flow_deviation_alarm():
    flow_deviation_alarm = int(parameter_setting.comboBox_25.currentText())
    print(flow_deviation_alarm)
    deviation_enable_set = WriteSingleRegister('修改偏差报警使能',
                                               '未连接仪表！',
                                               Meter_data_write['41007'],  # 开始地址
                                               flow_deviation_alarm,  # 写入数据
                                               '修改偏差报警使能失败！',
                                               '修改偏差报警使能成功！')  # 初始化类
    deviation_enable_set.write_data_to_meter_register_single()


# 修改1路报警上限使能
def enable_1_flow_high_alarm():
    flow_high_1_alarm = int(parameter_setting.comboBox_26.currentText())
    print(flow_high_1_alarm)
    flow_high_1_alarm_enable_set = WriteSingleRegister('修改1路报警上限使能',
                                                       '未连接仪表！',
                                                       Meter_data_write['41010'],  # 开始地址
                                                       flow_high_1_alarm,  # 写入数据
                                                       '修改1路报警上限使能失败！',
                                                       '修改1路报警上限使能成功！')  # 初始化类
    flow_high_1_alarm_enable_set.write_data_to_meter_register_single()


# 修改1路报警下限使能
def enable_1_flow_low_alarm():
    flow_low_1_alarm = int(parameter_setting.comboBox_28.currentText())
    print(flow_low_1_alarm)
    if Connect_status_meter == 1:
        register_start = Meter_data_write['41013']
    elif Connect_status_meter == 2:
        register_start = Meter_data_2_plus_write['41014']
    flow_low_1_alarm_enable_set = WriteSingleRegister('修改1路报警下限使能',
                                                      '未连接仪表！',
                                                      register_start,  # 开始地址
                                                      flow_low_1_alarm,  # 写入数据
                                                      '修改1路报警下限使能失败！',
                                                      '修改1路报警下限使能成功！')  # 初始化类
    flow_low_1_alarm_enable_set.write_data_to_meter_register_single()


# 修改2路报警上限使能
def enable_2_flow_high_alarm():
    flow_high_2_alarm = int(parameter_setting.comboBox_27.currentText())
    print(flow_high_2_alarm)
    if Connect_status_meter == 1:
        register_start = Meter_data_write['41016']
    elif Connect_status_meter == 2:
        register_start = Meter_data_2_plus_write['41018']
    flow_high_2_enable_set = WriteSingleRegister('修改2路报警上限使能',
                                                 '未连接仪表！',
                                                 register_start,  # 开始地址
                                                 flow_high_2_alarm,  # 写入数据
                                                 '修改2路报警上限使能失败！',
                                                 '修改2路报警上限使能成功！')  # 初始化类
    flow_high_2_enable_set.write_data_to_meter_register_single()


# 修改2路报警下限使能
def enable_2_flow_low_alarm():
    flow_low_2_alarm = int(parameter_setting.comboBox_29.currentText())
    print(flow_low_2_alarm)
    if Connect_status_meter == 1:
        register_start = Meter_data_write['41019']
    elif Connect_status_meter == 2:
        register_start = Meter_data_2_plus_write['41022']
    flow_low_2_enable_set = WriteSingleRegister('修改2路报警下限使能',
                                                '未连接仪表！',
                                                register_start,  # 开始地址
                                                flow_low_2_alarm,  # 写入数据
                                                '修改2路报警下限使能失败！',
                                                '修改2路报警下限使能成功！')  # 初始化类
    flow_low_2_enable_set.write_data_to_meter_register_single()


# 修改校正1路A点脉冲
def change_1_a_pulse():
    calibration_1_a_pulse = int(parameter_setting.comboBox_7.currentText())
    print(calibration_1_a_pulse)
    if Connect_status_meter == 1:
        register_start = Meter_data_write['41026']
    elif Connect_status_meter == 2:
        register_start = Meter_data_2_plus_write['41032']
    calibration_1_a_pulse_set = WriteSingleRegister('修改校正1路A点脉冲',
                                                    '未连接仪表！',
                                                    register_start,  # 开始地址
                                                    calibration_1_a_pulse,  # 写入数据
                                                    '修改校正1路A点脉冲失败！',
                                                    '修改校正1路A点脉冲成功！')  # 初始化类
    calibration_1_a_pulse_set.write_data_to_meter_register_single()


# 修改校正1路A点容积
def change_1_a_volumn():
    calibration_1_a_volumn = int(parameter_setting.comboBox_14.currentText())
    print(calibration_1_a_volumn)
    if Connect_status_meter == 1:
        calibration_1_a_volumn_set = WriteSingleRegister('修改校正1路A点容积',
                                                         '未连接仪表！',
                                                         Meter_data_write['41027'],  # 开始地址
                                                         calibration_1_a_volumn,  # 写入数据
                                                         '修改校正1路A点容积失败！',
                                                         '修改校正1路A点容积成功！')  # 初始化类
        calibration_1_a_volumn_set.write_data_to_meter_register_single()
    elif Connect_status_meter == 2:
        calibration_1_a_volumn_high = int(calibration_1_a_volumn / 65536)
        print(calibration_1_a_volumn_high)
        calibration_1_a_volumn_low = int(calibration_1_a_volumn % 65536)
        print(calibration_1_a_volumn_low)
        print(Meter_data_2_plus_write['41033'])
        print([calibration_1_a_volumn_high, calibration_1_a_volumn_low])
        calibration_1_a_volumn_set = WriteMultipleRegister('修改校正1路A点容积',
                                                           '未连接仪表！',
                                                           Meter_data_2_plus_write['41033'],  # 开始地址
                                                           [calibration_1_a_volumn_high,
                                                            calibration_1_a_volumn_low],  # 写入数据
                                                           '修改校正1路A点容积失败！',
                                                           '修改校正1路A点容积成功！')  # 初始化类
        calibration_1_a_volumn_set.write_data_to_meter_register_multiple()


# 修改校正1路B点脉冲
def change_1_b_pulse():
    calibration_1_b_pulse = int(parameter_setting.comboBox_15.currentText())
    print(calibration_1_b_pulse)
    if Connect_status_meter == 1:
        register_start = Meter_data_write['41028']
    elif Connect_status_meter == 2:
        register_start = Meter_data_2_plus_write['41035']
    calibration_1_b_pulse_set = WriteSingleRegister('修改校正1路B点脉冲',
                                                    '未连接仪表！',
                                                    register_start,  # 开始地址
                                                    calibration_1_b_pulse,  # 写入数据
                                                    '修改校正1路B点脉冲失败！',
                                                    '修改校正1路B点脉冲成功！')  # 初始化类
    calibration_1_b_pulse_set.write_data_to_meter_register_single()


# 修改校正1路B点容积
def change_1_b_volumn():
    calibration_1_b_volumn = int(parameter_setting.comboBox_16.currentText())
    if Connect_status_meter == 1:
        print(calibration_1_b_volumn)
        calibration_1_b_volumn_set = WriteSingleRegister('修改校正1路B点容积',
                                                         '未连接仪表！',
                                                         Meter_data_write['41029'],  # 开始地址
                                                         calibration_1_b_volumn,  # 写入数据
                                                         '修改校正1路B点容积失败！',
                                                         '修改校正1路B点容积成功！')  # 初始化类
        calibration_1_b_volumn_set.write_data_to_meter_register_single()
    elif Connect_status_meter == 2:
        calibration_1_b_volumn_high = int(calibration_1_b_volumn / 65536)
        calibration_1_b_volumn_low = int(calibration_1_b_volumn % 65536)
        calibration_1_b_volumn_set = WriteMultipleRegister('修改校正1路B点容积',
                                                           '未连接仪表！',
                                                           Meter_data_2_plus_write['41036'],  # 开始地址
                                                           [calibration_1_b_volumn_high,
                                                            calibration_1_b_volumn_low],  # 写入数据
                                                           '修改校正1路B点容积失败！',
                                                           '修改校正1路B点容积成功！')  # 初始化类
        calibration_1_b_volumn_set.write_data_to_meter_register_multiple()


# 修改校正1路C点脉冲
def change_1_c_pulse():
    calibration_1_c_pulse = int(parameter_setting.comboBox_17.currentText())
    print(calibration_1_c_pulse)
    if Connect_status_meter == 1:
        register_start = Meter_data_write['41030']
    elif Connect_status_meter == 2:
        register_start = Meter_data_2_plus_write['41038']
    calibration_1_c_pulse_set = WriteSingleRegister('修改校正1路C点脉冲',
                                                    '未连接仪表！',
                                                    register_start,  # 开始地址
                                                    calibration_1_c_pulse,  # 写入数据
                                                    '修改校正1路C点脉冲失败！',
                                                    '修改校正1路C点脉冲成功！')  # 初始化类
    calibration_1_c_pulse_set.write_data_to_meter_register_single()


# 修改校正1路C点容积
def change_1_c_volumn():
    calibration_1_c_volumn = int(parameter_setting.comboBox_18.currentText())
    print(calibration_1_c_volumn)
    if Connect_status_meter == 1:
        calibration_1_c_volumn_set = WriteSingleRegister('修改校正1路C点容积',
                                                         '未连接仪表！',
                                                         Meter_data_write['41031'],  # 开始地址
                                                         calibration_1_c_volumn,  # 写入数据
                                                         '修改校正1路C点容积失败！',
                                                         '修改校正1路C点容积成功！')  # 初始化类
        calibration_1_c_volumn_set.write_data_to_meter_register_single()
    elif Connect_status_meter == 2:
        calibration_1_c_volumn_high = int(calibration_1_c_volumn / 65536)
        calibration_1_c_volumn_low = int(calibration_1_c_volumn % 65536)
        calibration_1_c_volumn_set = WriteMultipleRegister('修改校正1路C点容积',
                                                           '未连接仪表！',
                                                           Meter_data_2_plus_write['41039'],  # 开始地址
                                                           [calibration_1_c_volumn_high,
                                                            calibration_1_c_volumn_low],  # 写入数据
                                                           '修改校正1路C点容积失败！',
                                                           '修改校正1路C点容积成功！')  # 初始化类
        calibration_1_c_volumn_set.write_data_to_meter_register_multiple()


# 修改校正2路A点脉冲
def change_2_a_pulse():
    calibration_2_a_pulse = int(parameter_setting.comboBox_22.currentText())
    print(calibration_2_a_pulse)
    if Connect_status_meter == 1:
        register_start = Meter_data_write['41032']
    elif Connect_status_meter == 2:
        register_start = Meter_data_2_plus_write['41041']
    calibration_2_a_pulse_set = WriteSingleRegister('修改校正2路A点脉冲',
                                                    '未连接仪表！',
                                                    register_start,  # 开始地址
                                                    calibration_2_a_pulse,  # 写入数据
                                                    '修改校正2路A点脉冲失败！',
                                                    '修改校正2路A点脉冲成功！')  # 初始化类
    calibration_2_a_pulse_set.write_data_to_meter_register_single()


# 修改校正2路A点容积
def change_2_a_volumn():
    calibration_2_a_volumn = int(parameter_setting.comboBox_24.currentText())
    print(calibration_2_a_volumn)
    if Connect_status_meter == 1:
        calibration_2_a_volumn_set = WriteSingleRegister('修改校正2路A点容积',
                                                         '未连接仪表！',
                                                         Meter_data_write['41033'],  # 开始地址
                                                         calibration_2_a_volumn,  # 写入数据
                                                         '修改校正2路A点容积失败！',
                                                         '修改校正2路A点容积成功！')  # 初始化类
        calibration_2_a_volumn_set.write_data_to_meter_register_single()
    elif Connect_status_meter == 2:
        calibration_2_a_volumn_high = int(calibration_2_a_volumn / 65536)
        calibration_2_a_volumn_low = int(calibration_2_a_volumn % 65536)
        calibration_2_a_volumn_set = WriteMultipleRegister('修改校正2路A点容积',
                                                           '未连接仪表！',
                                                           Meter_data_2_plus_write['41042'],  # 开始地址
                                                           [calibration_2_a_volumn_high,
                                                            calibration_2_a_volumn_low],  # 写入数据
                                                           '修改校正2路A点容积失败！',
                                                           '修改校正2路A点容积成功！')  # 初始化类
        calibration_2_a_volumn_set.write_data_to_meter_register_multiple()


# 修改校正2路B点脉冲
def change_2_b_pulse():
    calibration_2_b_pulse = int(parameter_setting.comboBox_20.currentText())
    print(calibration_2_b_pulse)
    if Connect_status_meter == 1:
        register_start = Meter_data_write['41034']
    elif Connect_status_meter == 2:
        register_start = Meter_data_2_plus_write['41044']
    calibration_2_b_pulse_set = WriteSingleRegister('修改校正2路B点脉冲',
                                                    '未连接仪表！',
                                                    register_start,  # 开始地址
                                                    calibration_2_b_pulse,  # 写入数据
                                                    '修改校正2路B点脉冲失败！',
                                                    '修改校正2路B点脉冲成功！')  # 初始化类
    calibration_2_b_pulse_set.write_data_to_meter_register_single()


# 修改校正2路B点容积
def change_2_b_volumn():
    calibration_2_b_volumn = int(parameter_setting.comboBox_23.currentText())
    print(calibration_2_b_volumn)
    if Connect_status_meter == 1:
        calibration_2_b_volumn_set = WriteSingleRegister('修改校正2路B点容积',
                                                         '未连接仪表！',
                                                         Meter_data_2_plus_write['41035'],  # 开始地址
                                                         calibration_2_b_volumn,  # 写入数据
                                                         '修改校正2路B点容积失败！',
                                                         '修改校正2路B点容积成功！')  # 初始化类
        calibration_2_b_volumn_set.write_data_to_meter_register_single()
    elif Connect_status_meter == 2:
        calibration_2_b_volumn_high = int(calibration_2_b_volumn / 65536)
        calibration_2_b_volumn_low = int(calibration_2_b_volumn % 65536)
        calibration_2_b_volumn_set = WriteMultipleRegister('修改校正2路B点容积',
                                                           '未连接仪表！',
                                                           Meter_data_2_plus_write['41045'],  # 开始地址
                                                           [calibration_2_b_volumn_high,
                                                            calibration_2_b_volumn_low],  # 写入数据
                                                           '修改校正2路B点容积失败！',
                                                           '修改校正2路B点容积成功！')  # 初始化类
        calibration_2_b_volumn_set.write_data_to_meter_register_multiple()


# 修改校正2路C点脉冲
def change_2_c_pulse():
    calibration_2_c_pulse = int(parameter_setting.comboBox_21.currentText())
    print(calibration_2_c_pulse)
    if Connect_status_meter == 1:
        register_start = Meter_data_write['41036']
    elif Connect_status_meter == 2:
        register_start = Meter_data_2_plus_write['41047']
    calibration_2_c_pulse_set = WriteSingleRegister('修改校正2路C点脉冲',
                                                    '未连接仪表！',
                                                    register_start,  # 开始地址
                                                    calibration_2_c_pulse,  # 写入数据
                                                    '修改校正2路C点脉冲失败！',
                                                    '修改校正2路C点脉冲成功！')  # 初始化类
    calibration_2_c_pulse_set.write_data_to_meter_register_single()


# 修改校正2路C点容积
def change_2_c_volumn():
    calibration_2_c_volumn = int(parameter_setting.comboBox_19.currentText())
    print(calibration_2_c_volumn)
    if Connect_status_meter == 1:
        calibration_2_c_volumn_set = WriteSingleRegister('修改校正2路C点容积',
                                                         '未连接仪表！',
                                                         Meter_data_write['41037'],  # 开始地址
                                                         calibration_2_c_volumn,  # 写入数据
                                                         '修改校正2路C点容积失败！',
                                                         '修改校正2路C点容积成功！')  # 初始化类
        calibration_2_c_volumn_set.write_data_to_meter_register_single()
    elif Connect_status_meter == 2:
        calibration_2_c_volumn_high = int(calibration_2_c_volumn / 65536)
        calibration_2_c_volumn_low = int(calibration_2_c_volumn % 65536)
        calibration_2_c_volumn_set = WriteMultipleRegister('修改校正2路C点容积',
                                                           '未连接仪表！',
                                                           Meter_data_2_plus_write['41048'],  # 开始地址
                                                           [calibration_2_c_volumn_high,
                                                            calibration_2_c_volumn_low],  # 写入数据
                                                           '修改校正2路C点容积失败！',
                                                           '修改校正2路C点容积成功！')  # 初始化类
        calibration_2_c_volumn_set.write_data_to_meter_register_multiple()


# 修改1路4-20mA满刻度
def change_1_full_scale():
    combobox_text = parameter_setting.comboBox_30.currentText()
    if Connect_status_meter == 1:
        full_scale_1_integer = int(Decimal(combobox_text))
        full_scale_1_decimal = int((Decimal(combobox_text) - int(Decimal(combobox_text))) * 1000)
        print(full_scale_1_integer)
        print(full_scale_1_decimal)
        full_scale_1_set = WriteMultipleRegister('修改1路4-20mA满刻度',
                                                 '未连接仪表！',
                                                 Meter_data_write['41022'],  # 开始地址
                                                 [full_scale_1_integer, full_scale_1_decimal],  # 写入数据
                                                 '修改1路4-20mA满刻度失败！',
                                                 '修改1路4-20mA满刻度成功！')  # 初始化类
        full_scale_1_set.write_data_to_meter_register_multiple()
    elif Connect_status_meter == 2:
        full_scale_1_integer_high = int(Decimal(combobox_text) / 65536)
        full_scale_1_integer = int(Decimal(combobox_text) % 65536)
        full_scale_1_decimal = int((Decimal(combobox_text) - int(Decimal(combobox_text))) * 1000)
        print(full_scale_1_integer_high)
        print(full_scale_1_integer)
        print(full_scale_1_decimal)
        full_scale_1_set = WriteMultipleRegister('修改1路4-20mA满刻度',
                                                 '未连接仪表！',
                                                 Meter_data_2_plus_write['41026'],  # 开始地址
                                                 [full_scale_1_integer_high,
                                                  full_scale_1_integer,
                                                  full_scale_1_decimal],  # 写入数据
                                                 '修改1路4-20mA满刻度失败！',
                                                 '修改1路4-20mA满刻度成功！')  # 初始化类
        full_scale_1_set.write_data_to_meter_register_multiple()


# 修改2路4-20mA满刻度
def change_2_full_scale():
    combobox_text = parameter_setting.comboBox_31.currentText()
    if Connect_status_meter == 1:
        full_scale_2_integer = int(Decimal(combobox_text))
        full_scale_2_decimal = int((Decimal(combobox_text) - int(Decimal(combobox_text))) * 1000)
        print(full_scale_2_integer)
        print(full_scale_2_decimal)
        full_scale_2_set = WriteMultipleRegister('修改2路4-20mA满刻度',
                                                 '未连接仪表！',
                                                 Meter_data_write['41024'],  # 开始地址
                                                 [full_scale_2_integer, full_scale_2_decimal],  # 写入数据
                                                 '修改2路4-20mA满刻度失败！',
                                                 '修改2路4-20mA满刻度成功！')  # 初始化类
        full_scale_2_set.write_data_to_meter_register_multiple()
    elif Connect_status_meter == 2:
        full_scale_2_integer_high = int(Decimal(combobox_text) / 65536)
        full_scale_2_integer = int(Decimal(combobox_text) % 65536)
        full_scale_2_decimal = int((Decimal(combobox_text) - int(Decimal(combobox_text))) * 1000)
        print(full_scale_2_integer_high)
        print(full_scale_2_integer)
        print(full_scale_2_decimal)
        full_scale_2_set = WriteMultipleRegister('修改2路4-20mA满刻度',
                                                 '未连接仪表！',
                                                 Meter_data_2_plus_write['41029'],  # 开始地址
                                                 [full_scale_2_integer_high,
                                                  full_scale_2_integer,
                                                  full_scale_2_decimal],  # 写入数据
                                                 '修改2路4-20mA满刻度失败！',
                                                 '修改2路4-20mA满刻度成功！')  # 初始化类
        full_scale_2_set.write_data_to_meter_register_multiple()


# 修改开机字符串
def change_meter_start_string():
    meter_start_string_combobox = parameter_setting.comboBox_33.currentText()
    print(meter_start_string_combobox)
    if Connect_status_meter == 1:
        parameter_setting.label_134.setText('不可用')
        parameter_setting.label_134.setStyleSheet("background-color: rgb(255, 255, 0);\n")
    elif Connect_status_meter == 2:
        print(meter_start_string_combobox)
        meter_start_string_write = data_translation_modal.meter_string_write(meter_start_string_combobox,
                                                                             10)  # 写入字符串长度
        print(meter_start_string_write)
        meter_start_string_set = WriteMultipleRegister('修改开机字符串',
                                                       '未连接仪表！',
                                                       Meter_data_2_plus_write['41069'],  # 开始地址
                                                       meter_start_string_write,  # 写入数据
                                                       '修改开机字符串失败！',
                                                       '修改开机字符串成功！')  # 初始化类
        meter_start_string_set.write_data_to_meter_register_multiple()


# 修改探头1自定义字符
def change_meter_ch1_string():
    meter_ch1_string_combobox = parameter_setting.comboBox_34.currentText()
    print(meter_ch1_string_combobox)
    if Connect_status_meter == 1:
        parameter_setting.label_134.setText('不可用')
        parameter_setting.label_134.setStyleSheet("background-color: rgb(255, 255, 0);\n")
    elif Connect_status_meter == 2:
        print(meter_ch1_string_combobox)
        meter_ch1_string_write = data_translation_modal.meter_string_write(meter_ch1_string_combobox,
                                                                           4)  # 写入字符串长度
        print(meter_ch1_string_write)
        meter_ch1_string_set = WriteMultipleRegister('修改通道1字符串',
                                                     '未连接仪表！',
                                                     Meter_data_2_plus_write['41083'],  # 开始地址
                                                     meter_ch1_string_write,  # 写入数据
                                                     '修改通道1字符串失败！',
                                                     '修改通道1字符串成功！')  # 初始化类
        meter_ch1_string_set.write_data_to_meter_register_multiple()


# 修改探头2自定义字符
def change_meter_ch2_string():
    meter_ch2_string_combobox = parameter_setting.comboBox_35.currentText()
    print(meter_ch2_string_combobox)
    if Connect_status_meter == 1:
        parameter_setting.label_140.setText('不可用')
        parameter_setting.label_140.setStyleSheet("background-color: rgb(255, 255, 0);\n")
    elif Connect_status_meter == 2:
        print(meter_ch2_string_combobox)
        meter_ch2_string_write = data_translation_modal.meter_string_write(meter_ch2_string_combobox,
                                                                           4)  # 写入字符串长度
        print(meter_ch2_string_write)
        meter_ch2_string_set = WriteMultipleRegister('修改通道2字符串',
                                                     '未连接仪表！',
                                                     Meter_data_2_plus_write['41088'],  # 开始地址
                                                     meter_ch2_string_write,  # 写入数据
                                                     '修改通道2字符串失败！',
                                                     '修改通道2字符串成功！')  # 初始化类
        meter_ch2_string_set.write_data_to_meter_register_multiple()


#  上传扩展参数使能
def extension_parameter_upload_enable():
    if Connect_status_meter == 1:
        messagebox_in_Chinese.information_messagebox('设置扩展参数上传使能状态',
                                                     '标准2代仪表没有扩展参数上传功能！')
    elif Connect_status_meter == 2:
        extension_parameter_upload = int(parameter_setting.comboBox_32.currentText())
        print(extension_parameter_upload)
        extension_parameter_upload_set = WriteSingleRegister('修改扩展参数上传使能',
                                                             '未连接仪表！',
                                                             Meter_data_2_plus_write['41099'],  # 开始地址
                                                             extension_parameter_upload,  # 写入数据
                                                             '修改扩展参数上传使能失败！',
                                                             '修改扩展参数上传使能成功！')  # 初始化类
        extension_parameter_upload_set.write_data_to_meter_register_single()


# 修改平台域名
def change_web_address():
    web_address_string_combobox = parameter_setting.comboBox_36.currentText()
    print(web_address_string_combobox)
    if Connect_status_meter == 1:
        print(web_address_string_combobox)
        web_address_string_write = data_translation_modal.meter_string_write(web_address_string_combobox,
                                                                             15)  # 写入字符串长度
        print(web_address_string_write)
        web_address_string_set = WriteMultipleRegister('修改平台域名',
                                                       '未连接仪表！',
                                                       Meter_data_write['41040'],  # 开始地址
                                                       web_address_string_write,  # 写入数据
                                                       '修改平台域名失败！',
                                                       '修改平台域名成功！')  # 初始化类
        web_address_string_set.write_data_to_meter_register_multiple()
    elif Connect_status_meter == 2:
        print(web_address_string_combobox)
        web_address_string_write = data_translation_modal.meter_string_write(web_address_string_combobox,
                                                                             15)  # 写入字符串长度
        print(web_address_string_write)
        # 解锁仪表
        unlock_meter_setting = WriteMultipleRegister('解锁仪表',
                                                     '未连接仪表！',
                                                     Meter_data_2_plus_write['41180'],  # 开始地址
                                                     [43690, 21845],  # 写入数据
                                                     '解锁仪表失败！',
                                                     '解锁仪表成功！')  # 初始化类
        unlock_meter_setting.write_data_to_meter_register_multiple()
        web_address_string_set = WriteMultipleRegister('修改平台域名',
                                                       '未连接仪表！',
                                                       Meter_data_2_plus_write['41052'],  # 开始地址
                                                       web_address_string_write,  # 写入数据
                                                       '修改平台域名失败！',
                                                       '修改平台域名成功！')  # 初始化类
        web_address_string_set.write_data_to_meter_register_multiple()


#  修改端口号
def change_port_number():
    if Connect_status_meter == 1:
        messagebox_in_Chinese.information_messagebox('设置端口号',
                                                     '标准2代仪表不能设置端口号！')
    elif Connect_status_meter == 2:
        port_number = int(parameter_setting.comboBox_37.currentText())
        print(port_number)
        # 解锁仪表
        unlock_meter_setting = WriteMultipleRegister('解锁仪表',
                                                     '未连接仪表！',
                                                     Meter_data_2_plus_write['41180'],  # 开始地址
                                                     [43690, 21845],  # 写入数据
                                                     '解锁仪表失败！',
                                                     '解锁仪表成功！')  # 初始化类
        unlock_meter_setting.write_data_to_meter_register_multiple()
        port_number_set = WriteSingleRegister('修改端口号',
                                              '未连接仪表！',
                                              Meter_data_2_plus_write['41080'],  # 开始地址
                                              port_number,  # 写入数据
                                              '修改端口号失败！',
                                              '修改端口号成功！')  # 初始化类
        port_number_set.write_data_to_meter_register_single()


#  修改通道1流量显示单位
def change_ch1_display_unit():
    if Connect_status_meter == 1:
        messagebox_in_Chinese.information_messagebox('设置通道1流量显示单位',
                                                     '标准2代仪表没有修改通道1流量显示单位功能！')
    elif Connect_status_meter == 2:
        ch1_display_unit_setting = int(parameter_setting.comboBox_38.currentText())
        print(ch1_display_unit_setting)
        if ch1_display_unit_setting == 0:
            ch1_display_unit_setting_write = 256
        elif ch1_display_unit_setting == 1:
            ch1_display_unit_setting_write = 257
        elif ch1_display_unit_setting == 2:
            ch1_display_unit_setting_write = 258
        elif ch1_display_unit_setting == 3:
            ch1_display_unit_setting_write = 259
        ch1_display_unit_set = WriteSingleRegister('修改通道1流量显示单位',
                                                   '未连接仪表！',
                                                   Meter_data_2_plus_write['41081'],  # 开始地址
                                                   ch1_display_unit_setting_write,  # 写入数据
                                                   '修改通道1流量显示单位失败！',
                                                   '修改通道1流量显示单位成功！')  # 初始化类
        ch1_display_unit_set.write_data_to_meter_register_single()


#  修改通道2流量显示单位
def change_ch2_display_unit():
    if Connect_status_meter == 1:
        messagebox_in_Chinese.information_messagebox('设置通道2流量显示单位',
                                                     '标准2代仪表没有修改通道2流量显示单位功能！')
    elif Connect_status_meter == 2:
        ch2_display_unit_setting = int(parameter_setting.comboBox_39.currentText())
        print(ch2_display_unit_setting)
        if ch2_display_unit_setting == 0:
            ch2_display_unit_setting_write = 512
        elif ch2_display_unit_setting == 1:
            ch2_display_unit_setting_write = 513
        elif ch2_display_unit_setting == 2:
            ch2_display_unit_setting_write = 514
        elif ch2_display_unit_setting == 3:
            ch2_display_unit_setting_write = 515
        ch2_display_unit_set = WriteSingleRegister('修改通道2流量显示单位',
                                                   '未连接仪表！',
                                                   Meter_data_2_plus_write['41081'],  # 开始地址
                                                   ch2_display_unit_setting_write,  # 写入数据
                                                   '修改通道2流量显示单位失败！',
                                                   '修改通道2流量显示单位成功！')  # 初始化类
        ch2_display_unit_set.write_data_to_meter_register_single()


# TODO:3.3.7 累积容积清零
def ch1_cumulation_reset():
    if Connect_status_meter == 2:
        ch1_reset_cumulation = WriteSingleRegister('累积容积清零',
                                                   '未连接仪表！',
                                                   Meter_data_2_plus_write['41097'],
                                                   321,
                                                   '通道1累积容积清零失败！',
                                                   '通道1累积容积清零成功！')
        ch1_reset_cumulation.write_data_to_meter_register_single()
    elif Connect_status_meter == 1:
        messagebox_in_Chinese.information_messagebox('累积容积清零',
                                                     '2代仪表无此功能！')
    elif Connect_status_meter == 0:
        messagebox_in_Chinese.information_messagebox('累积容积清零',
                                                     '未连接仪表！')


def ch2_cumulation_reset():
    if Connect_status_meter == 2:
        ch2_reset_cumulation = WriteSingleRegister('累积容积清零',
                                                   '未连接仪表！',
                                                   Meter_data_2_plus_write['41098'],
                                                   321,
                                                   '通道2累积容积清零失败！',
                                                   '通道2累积容积清零成功！')
        ch2_reset_cumulation.write_data_to_meter_register_single()
    elif Connect_status_meter == 1:
        messagebox_in_Chinese.information_messagebox('累积容积清零',
                                                     '2代仪表无此功能！')
    elif Connect_status_meter == 0:
        messagebox_in_Chinese.information_messagebox('累积容积清零',
                                                     '未连接仪表！')


# TODO:4. 主窗体设计函数和方法


# 定义在主窗口打开各个子窗体的方法
MainWindow.actionconnect.triggered.connect(show_connect)  # 打开通信设置子窗口
MainWindow.actionsearch_meter_2.triggered.connect(search_meter)  # 打开“搜索仪表”子窗仪表配置参数”函数口
MainWindow.actionconfigure_modbus_address.triggered.connect(modify_modbus_address)  # 打开“设置Modbus地址”子窗口
MainWindow.actionchangePeriod.triggered.connect(modify_period)  # 打开“设置采集周期”子窗口
MainWindow.actionexportSetting.triggered.connect(export_meter_setting)  # 启用“导出仪表配置参数”函数
MainWindow.actionimportSetting.triggered.connect(import_meter_setting)  # 启用“导入仪表配置参数”函数
MainWindow.actionparameter_setting.triggered.connect(meter_parameter_setting)  # 启用“修改仪表参数”函数
MainWindow.actionreset_ch1_cumulation.triggered.connect(ch1_cumulation_reset)  # 通道1累积容积清零
MainWindow.actionch2_cumulation_reset.triggered.connect(ch2_cumulation_reset)  # 通道2累积容积清零

MainWindow.show()  # 显示主界面
sys.exit(app.exec_())  # 退出主界面
