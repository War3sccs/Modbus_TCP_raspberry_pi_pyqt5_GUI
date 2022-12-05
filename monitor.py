# ！python3
# -*- coding: UTF-8 -*-

# @Time    :2021/2/7 21:57
# @Author  :Wu Yuming
# @Email   :61508712@qq.com
# @File    :
# @Software:PyCharm
# @Version :1.1.003

import sys
import os
# from PyQt5.QtGui import *
from PyQt5.QtWidgets import *  # 导入ＰｙＱｔ５库，绘制ＧＵＩ界面
# from PyQt5 import QtCore, QtGui, QtWidgets  # 导入ＰｙＱｔ５库，绘制ＧＵＩ界面
import datetime  # 导入日期时间模块
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.ticker as ticker
from matplotlib.figure import Figure
# import matplotlib.pyplot as plt
from pylab import *  # 导入设置matplotlib的模块
from PyQt5.QtCore import QTimer
import numpy as np  # 导入numpy模块
import pandas as pd  # 导入pandas模块
import RS485  # 导入RS485模块
import Modbus_TCP  # 导入Modbus_TCP模块
import Mainwidow  # 导入主界面
import messagebox_in_Chinese  # 导入提示信息框
import data_translation_modal  # 导入数据转换模块
import data_save  # 导入数据导出窗体
import data_save_function  # 导入数据导出处理函数
import data_drop  # 导入清理数据窗体
import data_drop_function  # 导入清理数据处理函数
import threading  # 导入多线程模块
from logging.handlers import RotatingFileHandler  # 导入日志模块

if hasattr(sys, 'frozen'):
    os.environ['PATH'] = sys._MEIPASS + ";" + os.environ['PATH']  # 导入Qt5Core库
sys.setrecursionlimit(4000)  # set the maximum depth as 4000  修改最大归递次数

# TODO:1.全局变量/公用函数/初始化
# TODO:1.1 开启logging
logger_paddle = logging.getLogger('logging_paddle')

# TODO:1.1.1日志格式
log_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# TODO:1.1.2 日志纪录的目的地
# 定义日志信息发送的目的地，可以是控制台，也可以是文件，也可以多个
logger_handler = logging.StreamHandler()  # log在控制台显示
logger_handler.setFormatter(log_format)
logger_paddle.addHandler(logger_handler)

file_handler = RotatingFileHandler('operationg_log.txt', maxBytes=10000000, backupCount=3)  # log写入文件
file_handler.setFormatter(log_format)
logger_paddle.addHandler(file_handler)

# TODO:1.1.3 记录的等级
# logger_paddle.setLevel(logging.DEBUG)
logger_paddle.setLevel(logging.INFO)
# logger_paddle.setLevel(logging.WARNING)

# TODO:1.2 全局变量
Time_count = 0  # 定时器始值
frame_flash = 0  # frame闪烁
display_length = {'length': '5min',
                  '5min': 30,
                  '10min': 600,
                  '30min': 1800,
                  '1hour': 3600,
                  '4hour': 14400,
                  '8hour': 28800}
write_to_plc = {'status': 0,  # 状态
                'register': 0,  # 寄存器地址
                'data': 0,  # 写入数据
                }

#  定义读取仪表后返回的显示数据
refresh_return_data = {'meter_1': {'DateTime': 0,  # 日期时间
                                   'plan': 1,  # 投加方案
                                   'flow_1': 0,  # 通道1流量
                                   'flow_1_decimal': 0,  # 通道1流量
                                   'flow_2': 0,  # 通道2流量
                                   'flow_2_decimal': 0,  # 通道1流量
                                   'flow_3': 0,  # 通道3流量
                                   'flow_3_decimal': 0,  # 通道1流量
                                   'flow_4': 0,  # 通道4流量
                                   'flow_4_decimal': 0,  # 通道1流量
                                   'flow_5': 0,  # 通道5流量
                                   'flow_5_decimal': 0,  # 通道1流量
                                   'flow_6': 0,  # 通道6流量
                                   'flow_6_decimal': 0,  # 通道1流量
                                   'flow_7': 0,  # 通道7流量
                                   'flow_7_decimal': 0,  # 通道1流量
                                   'flow_8': 0,  # 通道8流量
                                   'flow_8_decimal': 0,  # 通道1流量
                                   'flow_9': 0,  # 通道9流量
                                   'flow_9_decimal': 0,  # 通道1流量
                                   'flow_10': 0,  # 通道10流量
                                   'flow_10_decimal': 0,  # 通道1流量
                                   'flow_11': 0,  # 通道11流量
                                   'flow_11_decimal': 0,  # 通道1流量
                                   'flow_12': 0,  # 通道12流量
                                   'flow_12_decimal': 0,  # 通道1流量
                                   'flow_13': 0,  # 通道13流量
                                   'flow_13_decimal': 0,  # 通道1流量
                                   'flow_14': 0,  # 通道14流量
                                   'flow_14_decimal': 0,  # 通道1流量
                                   'high_flow_1': 0,  # 通道1流量高报警
                                   'high_flow_2': 0,  # 通道2流量高报警
                                   'high_flow_3': 0,  # 通道3流量高报警
                                   'high_flow_4': 0,  # 通道4流量高报警
                                   'high_flow_5': 0,  # 通道5流量高报警
                                   'high_flow_6': 0,  # 通道6流量高报警
                                   'high_flow_7': 0,  # 通道7流量高报警
                                   'high_flow_8': 0,  # 通道8流量高报警
                                   'high_flow_9': 0,  # 通道9流量高报警
                                   'high_flow_10': 0,  # 通道10流量高报警
                                   'high_flow_11': 0,  # 通道11流量高报警
                                   'high_flow_12': 0,  # 通道12流量高报警
                                   'high_flow_13': 0,  # 通道13流量高报警
                                   'high_flow_14': 0,  # 通道14流量高报警
                                   'low_flow_1': 0,  # 通道1流量低报警
                                   'low_flow_2': 0,  # 通道2流量低报警
                                   'low_flow_3': 0,  # 通道3流量低报警
                                   'low_flow_4': 0,  # 通道4流量低报警
                                   'low_flow_5': 0,  # 通道5流量低报警
                                   'low_flow_6': 0,  # 通道6流量低报警
                                   'low_flow_7': 0,  # 通道7流量低报警
                                   'low_flow_8': 0,  # 通道8流量低报警
                                   'low_flow_9': 0,  # 通道9流量低报警
                                   'low_flow_10': 0,  # 通道10流量低报警
                                   'low_flow_11': 0,  # 通道11流量低报警
                                   'low_flow_12': 0,  # 通道12流量低报警
                                   'low_flow_13': 0,  # 通道13流量低报警
                                   'low_flow_14': 0,  # 通道14流量低报警
                                   'conductivity': 0,  # 电导率
                                   'conductivity_high': 0,  # 电导率
                                   'conductivity_low': 0,  # 电导率
                                   'total_1': 0,  # 累积1
                                   'total_2': 0,  # 累积1
                                   'total_3': 0,  # 累积1
                                   'total_4': 0,  # 累积1
                                   'total_5': 0,  # 累积1
                                   'total_6': 0,  # 累积1
                                   'total_7': 0,  # 累积1
                                   'total_8': 0,  # 累积1
                                   'total_9': 0,  # 累积1
                                   'total_10': 0,  # 累积1
                                   'total_11': 0,  # 累积1
                                   'total_12': 0,  # 累积1
                                   'total_13': 0,  # 累积1
                                   'total_14': 0,  # 累积1
                                   },
                       }


# TODO:1.2  公用函数
# 将Meter_data转换为导出配置记录的格式
def translate_meter_data_to_save_parlance(meter_data, meter_data_column):
    meter_setting = pd.DataFrame(meter_data, index=meter_data_column)
    meter_setting = meter_setting.T
    logger_paddle.debug(meter_setting)
    return meter_setting


# 保存运行数据
def save_data(log_data):
    dir_now = os.getcwd()  # 获取当前工作目录
    logger_paddle.debug('保存目录' + dir_now)
    export_file_name = dir_now + '\\' + 'meter_run_data.csv'
    logger_paddle.info('保存文件' + export_file_name)
    log_data.to_csv(export_file_name, index=False, header=False, mode='a')


# TODO:1.3 初始化
# TODO:1.3.1 设置曲线参数
# 设置matplotlib中文字体
mpl.rcParams['font.sans-serif'] = ['SimHei']  # 正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 正常显示负号
plt.rcParams['figure.facecolor'] = '#F0F0F0'  # 修改曲线背景颜色

# TODO:1.3.2 建立Modbus_TCP连接
tcp_conncetion = Modbus_TCP.define_modbus_tcp_connection("192.168.1.150")
logger_paddle.info(tcp_conncetion)

# TODO:1.3.3 单位转换
# ml/min转换为L/h
def ml_min_to_l_h(flow_in):
    flow_out = flow_in / 1000 * 60
    logger_paddle.debug(flow_out)
    return flow_out


# TODO:2.仪表类
class FlowMeter:
    def __init__(self):
        # TODO: 2.1定义主要数据属性
        self.Connect_status_meter = 0  # 仪表连接状态，0：断开;1：连接
        self.Serial_ports = []  # 可用串口列表
        self.Modbus_parameter = {'PORT': '无串口!',  # 串口号
                                 'baudrate': 9600,  # 9600 波特率
                                 'bytesize': 8,  # 8 数据位
                                 'parity': 'N',  # 'N'  校验位
                                 'stopbits': 1,  # 1   停止位
                                 'address': 1,  # PLC站号
                                 }  # Modbus连接参数

        # TODO:2.2数据结构
        # 读
        self.Meter_data_column_2_plus = list(np.arange(88) + 40001)
        self.Meter_data_2_plus = list(np.zeros(89).astype(int))
        # 写
        self.Meter_data_2_plus_write_index = list(np.arange(89) + 40001)
        self.Meter_data_2_plus_write_value = list(np.arange(89))
        self.Meter_data_2_plus_write = pd.Series(self.Meter_data_2_plus_write_value,
                                                 index=self.Meter_data_2_plus_write_index)
        # 显示曲线初始化
        self.display_data_ch1 = {'x': list(np.zeros(28800)),
                                 'y': list(np.zeros(28800)),
                                 'h': list(np.zeros(28800)),
                                 'l': list(np.zeros(28800))}
        self.display_data_ch2 = {'x': list(np.zeros(28800)),
                                 'y': list(np.zeros(28800)),
                                 'h': list(np.zeros(28800)),
                                 'l': list(np.zeros(28800))}
        self.display_data_ch3 = {'x': list(np.zeros(28800)),
                                 'y': list(np.zeros(28800)),
                                 'h': list(np.zeros(28800)),
                                 'l': list(np.zeros(28800))}
        self.display_data_ch4 = {'x': list(np.zeros(28800)),
                                 'y': list(np.zeros(28800)),
                                 'h': list(np.zeros(28800)),
                                 'l': list(np.zeros(28800))}
        self.display_data_ch5 = {'x': list(np.zeros(28800)),
                                 'y': list(np.zeros(28800)),
                                 'h': list(np.zeros(28800)),
                                 'l': list(np.zeros(28800))}
        self.display_data_ch6 = {'x': list(np.zeros(28800)),
                                 'y': list(np.zeros(28800)),
                                 'h': list(np.zeros(28800)),
                                 'l': list(np.zeros(28800))}
        self.display_data_ch7 = {'x': list(np.zeros(28800)),
                                 'y': list(np.zeros(28800)),
                                 'h': list(np.zeros(28800)),
                                 'l': list(np.zeros(28800))}
        self.display_data_ch8 = {'x': list(np.zeros(28800)),
                                 'y': list(np.zeros(28800)),
                                 'h': list(np.zeros(28800)),
                                 'l': list(np.zeros(28800))}
        self.display_data_ch9 = {'x': list(np.zeros(28800)),
                                 'y': list(np.zeros(28800)),
                                 'h': list(np.zeros(28800)),
                                 'l': list(np.zeros(28800))}
        self.display_data_ch10 = {'x': list(np.zeros(28800)),
                                  'y': list(np.zeros(28800)),
                                  'h': list(np.zeros(28800)),
                                  'l': list(np.zeros(28800))}
        self.display_data_ch11 = {'x': list(np.zeros(28800)),
                                  'y': list(np.zeros(28800)),
                                  'h': list(np.zeros(28800)),
                                  'l': list(np.zeros(28800))}
        self.display_data_ch12 = {'x': list(np.zeros(28800)),
                                  'y': list(np.zeros(28800)),
                                  'h': list(np.zeros(28800)),
                                  'l': list(np.zeros(28800))}
        self.display_data_ch13 = {'x': list(np.zeros(28800)),
                                  'y': list(np.zeros(28800)),
                                  'h': list(np.zeros(28800)),
                                  'l': list(np.zeros(28800))}
        self.display_data_ch14 = {'x': list(np.zeros(28800)),
                                  'y': list(np.zeros(28800)),
                                  'h': list(np.zeros(28800)),
                                  'l': list(np.zeros(28800))}
        # TODO:2.3初始化函数
        for i in range(len(self.Meter_data_column_2_plus)):
            self.Meter_data_column_2_plus[i] = str(self.Meter_data_column_2_plus[i])
        self.Meter_data_column_2_plus.insert(0, 'DateTime')
        self.Meter_data_column_2_plus.append('ModbusAddress')
        self.Meter_data_2_plus[0] = datetime.datetime.now()  # 获取当前时间
        for i in range(len(self.Meter_data_2_plus_write_index)):
            self.Meter_data_2_plus_write_index[i] = str(self.Meter_data_2_plus_write_index[i])

# TODO:2.5 定义仪表
flow_meter_1 = FlowMeter()

# TODO:3.GUI界面运行
app = QApplication(sys.argv)

# TODO:3.1主界面运行方法设计
MainWindow = Mainwidow.Ui_MainWindow()  # 主界面定义


# TODO:3.1.1定时刷新主界面参数
# 获取当前日期时间
def date_time_now_text(date_time_now):
    date_time_text = str(date_time_now.year) + '年' + \
                     str(date_time_now.month) + '月' + \
                     str(date_time_now.day) + '日' + \
                     str(date_time_now.hour).rjust(2, '0') + ':' + \
                     str(date_time_now.minute).rjust(2, '0') + ':' + \
                     str(date_time_now.second).rjust(2, '0')
    return date_time_text


# 当前时间
def time_now_text(date_time_now):
    time_text = str(date_time_now.hour).rjust(2, '0') + ':' + \
                str(date_time_now.minute).rjust(2, '0') + ':' + \
                str(date_time_now.second).rjust(2, '0')
    return time_text


# 刷新函数
def refresh_parameter_for_1_meter(flowmeter, modbus_tcp_connection):
    global tcp_conncetion
    # 定义返回数据结构
    return_data = {'DateTime': 0,  # 日期时间
                   'plan': 1,  # 投加方案
                   'flow_1': 0,  # 通道1流量
                   'flow_1_decimal': 0,  # 通道1流量
                   'flow_2': 0,  # 通道2流量
                   'flow_2_decimal': 0,  # 通道1流量
                   'flow_3': 0,  # 通道3流量
                   'flow_3_decimal': 0,  # 通道1流量
                   'flow_4': 0,  # 通道4流量
                   'flow_4_decimal': 0,  # 通道1流量
                   'flow_5': 0,  # 通道5流量
                   'flow_5_decimal': 0,  # 通道1流量
                   'flow_6': 0,  # 通道6流量
                   'flow_6_decimal': 0,  # 通道1流量
                   'flow_7': 0,  # 通道7流量
                   'flow_7_decimal': 0,  # 通道1流量
                   'flow_8': 0,  # 通道8流量
                   'flow_8_decimal': 0,  # 通道1流量
                   'flow_9': 0,  # 通道9流量
                   'flow_9_decimal': 0,  # 通道1流量
                   'flow_10': 0,  # 通道10流量
                   'flow_10_decimal': 0,  # 通道1流量
                   'flow_11': 0,  # 通道11流量
                   'flow_11_decimal': 0,  # 通道1流量
                   'flow_12': 0,  # 通道12流量
                   'flow_12_decimal': 0,  # 通道1流量
                   'flow_13': 0,  # 通道13流量
                   'flow_13_decimal': 0,  # 通道1流量
                   'flow_14': 0,  # 通道14流量
                   'flow_14_decimal': 0,  # 通道1流量
                   'high_flow_1': 0,  # 通道1流量高报警
                   'high_flow_2': 0,  # 通道2流量高报警
                   'high_flow_3': 0,  # 通道3流量高报警
                   'high_flow_4': 0,  # 通道4流量高报警
                   'high_flow_5': 0,  # 通道5流量高报警
                   'high_flow_6': 0,  # 通道6流量高报警
                   'high_flow_7': 0,  # 通道7流量高报警
                   'high_flow_8': 0,  # 通道8流量高报警
                   'high_flow_9': 0,  # 通道9流量高报警
                   'high_flow_10': 0,  # 通道10流量高报警
                   'high_flow_11': 0,  # 通道11流量高报警
                   'high_flow_12': 0,  # 通道12流量高报警
                   'high_flow_13': 0,  # 通道13流量高报警
                   'high_flow_14': 0,  # 通道14流量高报警
                   'low_flow_1': 0,  # 通道1流量低报警
                   'low_flow_2': 0,  # 通道2流量低报警
                   'low_flow_3': 0,  # 通道3流量低报警
                   'low_flow_4': 0,  # 通道4流量低报警
                   'low_flow_5': 0,  # 通道5流量低报警
                   'low_flow_6': 0,  # 通道6流量低报警
                   'low_flow_7': 0,  # 通道7流量低报警
                   'low_flow_8': 0,  # 通道8流量低报警
                   'low_flow_9': 0,  # 通道9流量低报警
                   'low_flow_10': 0,  # 通道10流量低报警
                   'low_flow_11': 0,  # 通道11流量低报警
                   'low_flow_12': 0,  # 通道12流量低报警
                   'low_flow_13': 0,  # 通道13流量低报警
                   'low_flow_14': 0,  # 通道14流量低报警
                   'conductivity': 0,  # 电导率
                   'conductivity_high': 0,  # 电导率
                   'conductivity_low': 0,  # 电导率
                   'display_length': 0,  # 展示长度
                   'total_1': 0,  # 累积1
                   'total_2': 0,  # 累积1
                   'total_3': 0,  # 累积1
                   'total_4': 0,  # 累积1
                   'total_5': 0,  # 累积1
                   'total_6': 0,  # 累积1
                   'total_7': 0,  # 累积1
                   'total_8': 0,  # 累积1
                   'total_9': 0,  # 累积1
                   'total_10': 0,  # 累积1
                   'total_11': 0,  # 累积1
                   'total_12': 0,  # 累积1
                   'total_13': 0,  # 累积1
                   'total_14': 0,  # 累积1
                   }
    # 刷新仪表数据结构中的数据
    flowmeter.Meter_data_2_plus[0] = datetime.datetime.now()

    # 读取仪表信息
    try:
        get_meter_data = Modbus_TCP.read_modbus_tcp(modbus_tcp_connection,
                                                    0,  # 起始寄存器
                                                    88,  # 读寄存器的数量
                                                    )
    except Exception as err:
        logger_paddle.error('Can not connect meter.')
    finally:
        logger_paddle.info('register_reed:' + str(get_meter_data))

    if (get_meter_data == []) or (get_meter_data[0] == -1):
        logger_paddle.error('Can not connect meter.')
        flowmeter.Connect_status_meter = 0  # 连接modbus错误
        tcp_conncetion = Modbus_TCP.define_modbus_tcp_connection("192.168.1.150")
    else:
        # 刷新仪表数据结构中的数据
        for item in range(88):
            flowmeter.Meter_data_2_plus[item + 1] = get_meter_data[item]
        logger_paddle.info(flowmeter.Meter_data_2_plus)
        flowmeter.Connect_status_meter = 1  # 连接modbus错误


        # 保存运行记录
        # save_run_data = translate_meter_data_to_save_parlance(flowmeter.Meter_data_2_plus,
        #                                                       flowmeter.Meter_data_column_2_plus)
        # save_data(save_run_data)

    # 刷新脉冲数
    if flowmeter.Connect_status_meter == 0:
        return_data['flow_1'] = -1
        return_data['flow_2'] = -1
        return_data['flow_3'] = -1
        return_data['flow_4'] = -1
        return_data['flow_5'] = -1
        return_data['flow_6'] = -1
        return_data['flow_7'] = -1
        return_data['flow_8'] = -1
        return_data['flow_9'] = -1
        return_data['flow_10'] = -1
        return_data['flow_11'] = -1
        return_data['flow_12'] = -1
        return_data['flow_13'] = -1
        return_data['flow_14'] = -1
        return_data['high_flow_1'] = -1
        return_data['high_flow_2'] = -1
        return_data['high_flow_3'] = -1
        return_data['high_flow_4'] = -1
        return_data['high_flow_5'] = -1
        return_data['high_flow_6'] = -1
        return_data['high_flow_7'] = -1
        return_data['high_flow_8'] = -1
        return_data['high_flow_9'] = -1
        return_data['high_flow_10'] = -1
        return_data['high_flow_11'] = -1
        return_data['high_flow_12'] = -1
        return_data['high_flow_13'] = -1
        return_data['high_flow_14'] = -1
        return_data['low_flow_1'] = -1
        return_data['low_flow_2'] = -1
        return_data['low_flow_3'] = -1
        return_data['low_flow_4'] = -1
        return_data['low_flow_5'] = -1
        return_data['low_flow_6'] = -1
        return_data['low_flow_7'] = -1
        return_data['low_flow_8'] = -1
        return_data['low_flow_9'] = -1
        return_data['low_flow_10'] = -1
        return_data['low_flow_11'] = -1
        return_data['low_flow_12'] = -1
        return_data['low_flow_13'] = -1
        return_data['low_flow_14'] = -1
        return_data['conductivity'] = -1
        return_data['conductivity_high'] = -1
        return_data['conductivity_low'] = -1
        return_data['display_length'] = -1
        return_data['total_1'] = -1
        return_data['total_2'] = -1
        return_data['total_3'] = -1
        return_data['total_4'] = -1
        return_data['total_5'] = -1
        return_data['total_6'] = -1
        return_data['total_7'] = -1
        return_data['total_8'] = -1
        return_data['total_9'] = -1
        return_data['total_10'] = -1
        return_data['total_11'] = -1
        return_data['total_12'] = -1
        return_data['total_13'] = -1
        return_data['total_14'] = -1
    elif flowmeter.Connect_status_meter == 1:
        return_data['plan'] = flowmeter.Meter_data_2_plus[1]
        return_data['flow_1'] = flowmeter.Meter_data_2_plus[2]
        return_data['flow_1_decimal'] = flowmeter.Meter_data_2_plus[3]
        return_data['flow_2'] = flowmeter.Meter_data_2_plus[4]
        return_data['flow_2_decimal'] = flowmeter.Meter_data_2_plus[5]
        return_data['flow_3'] = flowmeter.Meter_data_2_plus[6]
        return_data['flow_3_decimal'] = flowmeter.Meter_data_2_plus[7]
        return_data['flow_4'] = flowmeter.Meter_data_2_plus[8]
        return_data['flow_4_decimal'] = flowmeter.Meter_data_2_plus[9]
        return_data['flow_5'] = flowmeter.Meter_data_2_plus[10]
        return_data['flow_5_decimal'] = flowmeter.Meter_data_2_plus[11]
        return_data['flow_6'] = flowmeter.Meter_data_2_plus[12]
        return_data['flow_6_decimal'] = flowmeter.Meter_data_2_plus[13]
        return_data['flow_7'] = flowmeter.Meter_data_2_plus[14]
        return_data['flow_7_decimal'] = flowmeter.Meter_data_2_plus[15]
        return_data['flow_8'] = flowmeter.Meter_data_2_plus[16]
        return_data['flow_8_decimal'] = flowmeter.Meter_data_2_plus[17]
        return_data['flow_9'] = flowmeter.Meter_data_2_plus[18]
        return_data['flow_9_decimal'] = flowmeter.Meter_data_2_plus[19]
        return_data['flow_10'] = flowmeter.Meter_data_2_plus[20]
        return_data['flow_10_decimal'] = flowmeter.Meter_data_2_plus[21]
        return_data['flow_11'] = flowmeter.Meter_data_2_plus[22]
        return_data['flow_11_decimal'] = flowmeter.Meter_data_2_plus[23]
        return_data['flow_12'] = flowmeter.Meter_data_2_plus[24]
        return_data['flow_12_decimal'] = flowmeter.Meter_data_2_plus[25]
        return_data['flow_13'] = flowmeter.Meter_data_2_plus[26]
        return_data['flow_13_decimal'] = flowmeter.Meter_data_2_plus[27]
        return_data['flow_14'] = flowmeter.Meter_data_2_plus[28]
        return_data['flow_14_decimal'] = flowmeter.Meter_data_2_plus[29]
        return_data['high_flow_1'] = flowmeter.Meter_data_2_plus[30]
        return_data['high_flow_2'] = flowmeter.Meter_data_2_plus[31]
        return_data['high_flow_3'] = flowmeter.Meter_data_2_plus[32]
        return_data['high_flow_4'] = flowmeter.Meter_data_2_plus[33]
        return_data['high_flow_5'] = flowmeter.Meter_data_2_plus[34]
        return_data['high_flow_6'] = flowmeter.Meter_data_2_plus[35]
        return_data['high_flow_7'] = flowmeter.Meter_data_2_plus[36]
        return_data['high_flow_8'] = flowmeter.Meter_data_2_plus[37]
        return_data['high_flow_9'] = flowmeter.Meter_data_2_plus[38]
        return_data['high_flow_10'] = flowmeter.Meter_data_2_plus[39]
        return_data['high_flow_11'] = flowmeter.Meter_data_2_plus[40]
        return_data['high_flow_12'] = flowmeter.Meter_data_2_plus[41]
        return_data['high_flow_13'] = flowmeter.Meter_data_2_plus[42]
        return_data['high_flow_14'] = flowmeter.Meter_data_2_plus[43]
        return_data['low_flow_1'] = flowmeter.Meter_data_2_plus[44]
        return_data['low_flow_2'] = flowmeter.Meter_data_2_plus[45]
        return_data['low_flow_3'] = flowmeter.Meter_data_2_plus[46]
        return_data['low_flow_4'] = flowmeter.Meter_data_2_plus[47]
        return_data['low_flow_5'] = flowmeter.Meter_data_2_plus[48]
        return_data['low_flow_6'] = flowmeter.Meter_data_2_plus[49]
        return_data['low_flow_7'] = flowmeter.Meter_data_2_plus[50]
        return_data['low_flow_8'] = flowmeter.Meter_data_2_plus[51]
        return_data['low_flow_9'] = flowmeter.Meter_data_2_plus[52]
        return_data['low_flow_10'] = flowmeter.Meter_data_2_plus[53]
        return_data['low_flow_11'] = flowmeter.Meter_data_2_plus[54]
        return_data['low_flow_12'] = flowmeter.Meter_data_2_plus[55]
        return_data['low_flow_13'] = flowmeter.Meter_data_2_plus[56]
        return_data['low_flow_14'] = flowmeter.Meter_data_2_plus[57]
        return_data['conductivity'] = flow_meter_1.Meter_data_2_plus[58]
        return_data['conductivity_high'] = flow_meter_1.Meter_data_2_plus[59]
        return_data['conductivity_low'] = flow_meter_1.Meter_data_2_plus[60]
        return_data['display_length'] = flow_meter_1.Meter_data_2_plus[61]
        return_data['total_1'] = flow_meter_1.Meter_data_2_plus[62]
        return_data['total_2'] = flow_meter_1.Meter_data_2_plus[63]
        return_data['total_3'] = flow_meter_1.Meter_data_2_plus[64]
        return_data['total_4'] = flow_meter_1.Meter_data_2_plus[65]
        return_data['total_5'] = flow_meter_1.Meter_data_2_plus[66]
        return_data['total_6'] = flow_meter_1.Meter_data_2_plus[67]
        return_data['total_7'] = flow_meter_1.Meter_data_2_plus[68]
        return_data['total_8'] = flow_meter_1.Meter_data_2_plus[69]
        return_data['total_9'] = flow_meter_1.Meter_data_2_plus[71]
        return_data['total_10'] = flow_meter_1.Meter_data_2_plus[72]
        return_data['total_11'] = flow_meter_1.Meter_data_2_plus[73]
        return_data['total_12'] = flow_meter_1.Meter_data_2_plus[74]
        return_data['total_13'] = flow_meter_1.Meter_data_2_plus[75]
        return_data['total_14'] = flow_meter_1.Meter_data_2_plus[76]
    return return_data


#  更新所有仪表
def refresh_parameter_all():
    # 更新时间
    date_time = date_time_now_text(datetime.datetime.now())
    # frame闪烁
    # global frame_flash
    # if frame_flash == 0:
    #     frame_flash = frame_flash + 1
    # else:
    #     frame_flash = frame_flash - 1

    for i in range(28799):
        flow_meter_1.display_data_ch1['x'][i] = flow_meter_1.display_data_ch1['x'][i + 1]
        flow_meter_1.display_data_ch2['x'][i] = flow_meter_1.display_data_ch2['x'][i + 1]
        flow_meter_1.display_data_ch3['x'][i] = flow_meter_1.display_data_ch3['x'][i + 1]
        flow_meter_1.display_data_ch4['x'][i] = flow_meter_1.display_data_ch4['x'][i + 1]
        flow_meter_1.display_data_ch5['x'][i] = flow_meter_1.display_data_ch5['x'][i + 1]
        flow_meter_1.display_data_ch6['x'][i] = flow_meter_1.display_data_ch6['x'][i + 1]

    flow_meter_1.display_data_ch1['x'][28799] = time_now_text(datetime.datetime.now())
    flow_meter_1.display_data_ch2['x'][28799] = flow_meter_1.display_data_ch1['x'][28799]
    flow_meter_1.display_data_ch3['x'][28799] = flow_meter_1.display_data_ch1['x'][28799]
    flow_meter_1.display_data_ch4['x'][28799] = flow_meter_1.display_data_ch1['x'][28799]
    flow_meter_1.display_data_ch5['x'][28799] = flow_meter_1.display_data_ch1['x'][28799]
    flow_meter_1.display_data_ch6['x'][28799] = flow_meter_1.display_data_ch1['x'][28799]

    # 在界面显示
    # 仪表1
    flow_1_int = refresh_return_data['meter_1']['flow_1']
    flow_1_decimal = refresh_return_data['meter_1']['flow_1_decimal']
    flow_1 = flow_1_int + flow_1_decimal / 1000
    MainWindow.lcdNumber_6.display(flow_1)  # 流量1
    flow_1_lph = ml_min_to_l_h(flow_1)
    MainWindow.lcdNumber_5.display(flow_1_lph)  # 流量1
    total_1 = refresh_return_data['meter_1']['total_1']
    # MainWindow.lcdNumber_4.display(total_1)  # 累积1
    flow_2_int = refresh_return_data['meter_1']['flow_2']
    flow_2_decimal = refresh_return_data['meter_1']['flow_2_decimal']
    flow_2 = flow_2_int + flow_2_decimal / 1000
    MainWindow.lcdNumber_22.display(flow_2)  # 流量2
    flow_2_lph = ml_min_to_l_h(flow_2)
    MainWindow.lcdNumber_15.display(flow_2_lph)  # 流量2
    total_2 = refresh_return_data['meter_1']['total_2']
    # MainWindow.lcdNumber_13.display(total_2)  # 累积1

    high_flow_1 = refresh_return_data['meter_1']['high_flow_1']
    high_flow_2 = refresh_return_data['meter_1']['high_flow_2']
    low_flow_1 = refresh_return_data['meter_1']['low_flow_1']
    low_flow_2 = refresh_return_data['meter_1']['low_flow_2']

    #     通道1流量报警
    #     过高
    if  high_flow_1:
        MainWindow.label_21.setText("报警")
        MainWindow.label_21.setStyleSheet("background-color: rgb(255, 0, 0);\n")
    else:
        MainWindow.label_21.setText("正常")
        MainWindow.label_21.setStyleSheet("background-color: rgb(240, 240, 240);\n")
    # 过低
    if  low_flow_1:
        MainWindow.label_22.setText("报警")
        MainWindow.label_22.setStyleSheet("background-color: rgb(255, 0, 0);\n")
    else:
        MainWindow.label_22.setText("正常")
        MainWindow.label_22.setStyleSheet("background-color: rgb(240, 240, 240);\n")

    #     通道2流量报警
    #     过高
    if  high_flow_2:
        MainWindow.label_56.setText("报警")
        MainWindow.label_56.setStyleSheet("background-color: rgb(255, 0, 0);\n")
    else:
        MainWindow.label_56.setText("正常")
        MainWindow.label_56.setStyleSheet("background-color: rgb(240, 240, 240);\n")
    # 过低
    if  low_flow_2:
        MainWindow.label_57.setText("报警")
        MainWindow.label_57.setStyleSheet("background-color: rgb(255, 0, 0);\n")
    else:
        MainWindow.label_57.setText("正常")
        MainWindow.label_57.setStyleSheet("background-color: rgb(240, 240, 240);\n")

    # 仪表2
    flow_3_int = refresh_return_data['meter_1']['flow_3']
    flow_3_decimal = refresh_return_data['meter_1']['flow_3_decimal']
    flow_3 = flow_3_int + flow_3_decimal / 1000
    MainWindow.lcdNumber_21.display(flow_3)  # 流量3
    flow_3_lph = ml_min_to_l_h(flow_3)
    MainWindow.lcdNumber_16.display(flow_3_lph)  # 流量3
    total_3 = refresh_return_data['meter_1']['total_3']
    # MainWindow.lcdNumber_23.display(total_3)  # 累积3
    flow_4_int = refresh_return_data['meter_1']['flow_4']
    flow_4_decimal = refresh_return_data['meter_1']['flow_4_decimal']
    flow_4 = flow_4_int + flow_4_decimal / 1000
    MainWindow.lcdNumber_9.display(flow_4)  # 流量3
    flow_4_lph = ml_min_to_l_h(flow_4)
    MainWindow.lcdNumber_8.display(flow_4_lph)  # 流量3
    total_4 = refresh_return_data['meter_1']['total_3']
    # MainWindow.lcdNumber_7.display(total_4)  # 累积3

    high_flow_3 = refresh_return_data['meter_1']['high_flow_3']
    high_flow_4 = refresh_return_data['meter_1']['high_flow_4']
    low_flow_3 = refresh_return_data['meter_1']['low_flow_3']
    low_flow_4 = refresh_return_data['meter_1']['low_flow_4']

    #     通道3流量报警
    #     过高
    if  high_flow_3:
        MainWindow.label_50.setText("报警")
        MainWindow.label_50.setStyleSheet("background-color: rgb(255, 0, 0);\n")
    else:
        MainWindow.label_50.setText("正常")
        MainWindow.label_50.setStyleSheet("background-color: rgb(240, 240, 240);\n")
    # 过低
    if  low_flow_3:
        MainWindow.label_51.setText("报警")
        MainWindow.label_51.setStyleSheet("background-color: rgb(255, 0, 0);\n")
    else:
        MainWindow.label_51.setText("正常")
        MainWindow.label_51.setStyleSheet("background-color: rgb(240, 240, 240);\n")

    #     通道4流量报警
    #     过高
    if  high_flow_4:
        MainWindow.label_25.setText("报警")
        MainWindow.label_25.setStyleSheet("background-color: rgb(255, 0, 0);\n")
    else:
        MainWindow.label_25.setText("正常")
        MainWindow.label_25.setStyleSheet("background-color: rgb(240, 240, 240);\n")
    # 过低
    if  low_flow_4:
        MainWindow.label_26.setText("报警")
        MainWindow.label_26.setStyleSheet("background-color: rgb(255, 0, 0);\n")
    else:
        MainWindow.label_26.setText("正常")
        MainWindow.label_26.setStyleSheet("background-color: rgb(240, 240, 240);\n")

    # 仪表3
    flow_5_int = refresh_return_data['meter_1']['flow_5']
    flow_5_decimal = refresh_return_data['meter_1']['flow_5_decimal']
    flow_5 = flow_5_int + flow_5_decimal / 1000
    MainWindow.lcdNumber_14.display(flow_5)  # 流量5
    flow_5_lph = ml_min_to_l_h(flow_5)
    MainWindow.lcdNumber_20.display(flow_5_lph)  # 流量5
    total_5 = refresh_return_data['meter_1']['total_5']
    # MainWindow.lcdNumber_18.display(total_5)  # 累积5
    flow_6_int = refresh_return_data['meter_1']['flow_6']
    flow_6_decimal = refresh_return_data['meter_1']['flow_6_decimal']
    flow_6 = flow_6_int + flow_6_decimal / 1000
    MainWindow.lcdNumber_12.display(flow_6)  # 流量6
    flow_6_lph = ml_min_to_l_h(flow_6)
    MainWindow.lcdNumber_11.display(flow_6_lph)  # 流量6
    total_6 = refresh_return_data['meter_1']['total_6']
    # MainWindow.lcdNumber_10.display(total_6)  # 累积5

    high_flow_5 = refresh_return_data['meter_1']['high_flow_5']
    high_flow_6 = refresh_return_data['meter_1']['high_flow_6']
    low_flow_5 = refresh_return_data['meter_1']['low_flow_5']
    low_flow_6 = refresh_return_data['meter_1']['low_flow_6']

    #     通道5流量报警
    #     过高
    if  high_flow_5:
        MainWindow.label_46.setText("报警")
        MainWindow.label_46.setStyleSheet("background-color: rgb(255, 0, 0);\n")
    else:
        MainWindow.label_46.setText("正常")
        MainWindow.label_46.setStyleSheet("background-color: rgb(240, 240, 240);\n")
    # 过低
    if  low_flow_5:
        MainWindow.label_47.setText("报警")
        MainWindow.label_47.setStyleSheet("background-color: rgb(255, 0, 0);\n")
    else:
        MainWindow.label_47.setText("正常")
        MainWindow.label_47.setStyleSheet("background-color: rgb(240, 240, 240);\n")

    #     通道6流量报警
    #     过高
    if  high_flow_6:
        MainWindow.label_35.setText("报警")
        MainWindow.label_35.setStyleSheet("background-color: rgb(255, 0, 0);\n")
    else:
        MainWindow.label_35.setText("正常")
        MainWindow.label_35.setStyleSheet("background-color: rgb(240, 240, 240);\n")
    # 过低
    if  low_flow_6:
        MainWindow.label_36.setText("报警")
        MainWindow.label_36.setStyleSheet("background-color: rgb(255, 0, 0);\n")
    else:
        MainWindow.label_36.setText("正常")
        MainWindow.label_36.setStyleSheet("background-color: rgb(240, 240, 240);\n")

    # 更新曲线
    for i in range(28799):
        flow_meter_1.display_data_ch1['y'][i] = flow_meter_1.display_data_ch1['y'][i + 1]
        flow_meter_1.display_data_ch1['h'][i] = flow_meter_1.display_data_ch1['h'][i + 1]
        flow_meter_1.display_data_ch1['l'][i] = flow_meter_1.display_data_ch1['l'][i + 1]
        flow_meter_1.display_data_ch2['y'][i] = flow_meter_1.display_data_ch2['y'][i + 1]
        flow_meter_1.display_data_ch2['h'][i] = flow_meter_1.display_data_ch2['h'][i + 1]
        flow_meter_1.display_data_ch2['l'][i] = flow_meter_1.display_data_ch2['l'][i + 1]
        flow_meter_1.display_data_ch3['y'][i] = flow_meter_1.display_data_ch3['y'][i + 1]
        flow_meter_1.display_data_ch3['h'][i] = flow_meter_1.display_data_ch3['h'][i + 1]
        flow_meter_1.display_data_ch3['l'][i] = flow_meter_1.display_data_ch3['l'][i + 1]
        flow_meter_1.display_data_ch4['y'][i] = flow_meter_1.display_data_ch4['y'][i + 1]
        flow_meter_1.display_data_ch4['h'][i] = flow_meter_1.display_data_ch4['h'][i + 1]
        flow_meter_1.display_data_ch4['l'][i] = flow_meter_1.display_data_ch4['l'][i + 1]
        flow_meter_1.display_data_ch5['y'][i] = flow_meter_1.display_data_ch5['y'][i + 1]
        flow_meter_1.display_data_ch5['h'][i] = flow_meter_1.display_data_ch5['h'][i + 1]
        flow_meter_1.display_data_ch5['l'][i] = flow_meter_1.display_data_ch5['l'][i + 1]
        flow_meter_1.display_data_ch6['y'][i] = flow_meter_1.display_data_ch6['y'][i + 1]
        flow_meter_1.display_data_ch6['h'][i] = flow_meter_1.display_data_ch6['h'][i + 1]
        flow_meter_1.display_data_ch6['l'][i] = flow_meter_1.display_data_ch6['l'][i + 1]
    flow_meter_1.display_data_ch1['y'][28799] = flow_1
    flow_meter_1.display_data_ch1['h'][28799] = high_flow_1
    flow_meter_1.display_data_ch1['l'][28799] = low_flow_1
    flow_meter_1.display_data_ch2['y'][28799] = flow_2
    flow_meter_1.display_data_ch2['h'][28799] = high_flow_2
    flow_meter_1.display_data_ch2['l'][28799] = low_flow_2
    flow_meter_1.display_data_ch3['y'][28799] = flow_3
    flow_meter_1.display_data_ch3['h'][28799] = high_flow_3
    flow_meter_1.display_data_ch3['l'][28799] = low_flow_3
    flow_meter_1.display_data_ch4['y'][28799] = flow_4
    flow_meter_1.display_data_ch4['h'][28799] = high_flow_4
    flow_meter_1.display_data_ch4['l'][28799] = low_flow_4
    flow_meter_1.display_data_ch5['y'][28799] = flow_5
    flow_meter_1.display_data_ch5['h'][28799] = high_flow_5
    flow_meter_1.display_data_ch5['l'][28799] = low_flow_5
    flow_meter_1.display_data_ch6['y'][28799] = flow_6
    flow_meter_1.display_data_ch6['h'][28799] = high_flow_6
    flow_meter_1.display_data_ch6['l'][28799] = low_flow_6


#  定时连接RS-485函数
def refresh_rs485_connect():
    global tcp_conncetion
    # 读plc状态
    refresh_return_data['meter_1'] = refresh_parameter_for_1_meter(flow_meter_1, tcp_conncetion)
    logger_paddle.info(refresh_return_data)

    # 写plc数据
    if write_to_plc['status'] == 1:
        write_data = Modbus_TCP.write_modbus_tcp(tcp_conncetion,
                                                 write_to_plc['register'],
                                                 write_to_plc['data'])
        if (write_data == []) or (write_data == -1):
            # messagebox_in_Chinese.information_messagebox('修改控制参数', '修改控制参数失败')
            logger_paddle.error('修改控制参数失败')
        else:
            # messagebox_in_Chinese.information_messagebox('修改控制参数', '成功修改控制参数')
            print('成功修改控制参数')
            logger_paddle.info('成功修改控制参数')
        write_to_plc['status'] = 0

    rs485_connect_refresh = threading.Timer(0.5, refresh_rs485_connect)  # 初始化threading定时器
    # 主进程存活时继续运行，主进程停止时停止
    if threading.main_thread().is_alive():
        rs485_connect_refresh.start()  # 启动threading定时器


#  定时更新界面
MainWindow.timer = QTimer()  # 初始化定时器
MainWindow.timer.timeout.connect(refresh_parameter_all)  # 定时操作
MainWindow.timer.start(1000)  # 每2秒刷新1次

#  定时连接RS-485
rs485_connect_refresh = threading.Timer(1.0, refresh_rs485_connect)  # 初始化threading定时器
rs485_connect_refresh.start()  # 启动threading定时器

# 定时更新曲线显示
def figure_refresh():
    # 更新 曲线
    Plot_meter_data.update_figure()
    Plot_meter_data_2.update_figure()
    Plot_meter_data_3.update_figure()
    Plot_meter_data_4.update_figure()
    Plot_meter_data_5.update_figure()
    Plot_meter_data_6.update_figure()

    update_figure = threading.Timer(1.0, figure_refresh)  # 初始化threading定时器
    # 主进程存活时继续运行，主进程停止时停止
    if threading.main_thread().is_alive():
        update_figure.start()  # 启动threading定时器

update_figure = threading.Timer(1.0, figure_refresh)
update_figure.start()  # 启动threading定时器


# TODO:3.1.2 运行曲线界面-类
class PlotCanvas(FigureCanvas):

    def __init__(self,
                 parent,
                 width,
                 height,
                 dpi,
                 plot_x,
                 plot_y,
                 plot_h,
                 plot_l,
                 plot_tittle):
        fig = Figure(figsize=(width, height), dpi=dpi)
        fig.subplots_adjust(left=0.17, right=0.85, top=0.85, bottom=0.17)  # 调整图像占画布大小
        self.axes = fig.add_subplot(111)
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self,
                                   QSizePolicy.Expanding,
                                   QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        self.plot_x = plot_x
        self.plot_y = plot_y
        self.plot_h = plot_h
        self.plot_l = plot_l
        self.plot_tittle = plot_tittle

    def update_figure(self):
        self.axes.cla()
        if display_length['length'] == '5min':
            meter_1_ch1_display_x = self.plot_x[-60:]
            meter_1_ch1_display_y = self.plot_y[-60:]
            meter_1_ch1_display_h = self.plot_h[-60:]
            meter_1_ch1_display_l = self.plot_l[-60:]
        elif display_length['length'] == '10min':
            meter_1_ch1_display_x = self.plot_x[-120:]
            meter_1_ch1_display_y = self.plot_y[-120:]
            meter_1_ch1_display_h = self.plot_h[-120:]
            meter_1_ch1_display_l = self.plot_l[-120:]
        elif display_length['length'] == '30min':
            meter_1_ch1_display_x = self.plot_x[-180:]
            meter_1_ch1_display_y = self.plot_y[-180:]
            meter_1_ch1_display_h = self.plot_h[-180:]
            meter_1_ch1_display_l = self.plot_l[-180:]
        elif display_length['length'] == '1hour':
            # 5min
            meter_1_ch1_display_x = self.plot_x[-300:]
            meter_1_ch1_display_y = self.plot_y[-300:]
            meter_1_ch1_display_h = self.plot_h[-300:]
            meter_1_ch1_display_l = self.plot_l[-300:]
        elif display_length['length'] == '4hour':
            # 10min
            meter_1_ch1_display_x = self.plot_x[-600:]
            meter_1_ch1_display_y = self.plot_y[-600:]
            meter_1_ch1_display_h = self.plot_h[-600:]
            meter_1_ch1_display_l = self.plot_l[-600:]
        elif display_length['length'] == '8hour':
            # 15min
            meter_1_ch1_display_x = self.plot_x[-900:]
            meter_1_ch1_display_y = self.plot_y[-900:]
            meter_1_ch1_display_h = self.plot_h[-900:]
            meter_1_ch1_display_l = self.plot_l[-900:]

        self.axes.plot(meter_1_ch1_display_x, meter_1_ch1_display_y, label=self.plot_tittle, color='red')
        self.axes.plot(meter_1_ch1_display_x, meter_1_ch1_display_h, label='高报警', color='green')
        self.axes.plot(meter_1_ch1_display_x, meter_1_ch1_display_l, label='低报警', color='black')
        self.axes.legend()
        if display_length['length'] == '5min':
            self.axes.xaxis.set_major_locator(ticker.MultipleLocator(15))
            self.axes.xaxis.set_minor_locator(ticker.MultipleLocator(3))
        elif display_length['length'] == '10min':
            self.axes.xaxis.set_major_locator(ticker.MultipleLocator(30))
            self.axes.xaxis.set_minor_locator(ticker.MultipleLocator(6))
        elif display_length['length'] == '30min':
            self.axes.xaxis.set_major_locator(ticker.MultipleLocator(45))
            self.axes.xaxis.set_minor_locator(ticker.MultipleLocator(9))
        elif display_length['length'] == '1hour':
            # 5min
            self.axes.xaxis.set_major_locator(ticker.MultipleLocator(75))
            self.axes.xaxis.set_minor_locator(ticker.MultipleLocator(15))
        elif display_length['length'] == '4hour':
            self.axes.xaxis.set_major_locator(ticker.MultipleLocator(150))
            self.axes.xaxis.set_minor_locator(ticker.MultipleLocator(30))
        elif display_length['length'] == '8hour':
            self.axes.xaxis.set_major_locator(ticker.MultipleLocator(225))
            self.axes.xaxis.set_minor_locator(ticker.MultipleLocator(45))
        self.axes.yaxis.grid(True)
        self.axes.xaxis.grid(True)
        self.axes.set_title(self.plot_tittle)
        self.draw()


# TODO:3.1.3 运行曲线界面-定义
# TODO:3.1.3.1 A方案
Plot_meter_data = PlotCanvas(MainWindow.tab, 4.5, 3, 100,
                             flow_meter_1.display_data_ch1['x'],
                             flow_meter_1.display_data_ch1['y'],
                             flow_meter_1.display_data_ch1['h'],
                             flow_meter_1.display_data_ch1['l'],
                             'B1')
Plot_meter_data.move(50, 160)
Plot_meter_data_2 = PlotCanvas(MainWindow.tab, 4.5, 3, 100,
                               flow_meter_1.display_data_ch2['x'],
                               flow_meter_1.display_data_ch2['y'],
                               flow_meter_1.display_data_ch2['h'],
                               flow_meter_1.display_data_ch2['l'],
                               'B2')
Plot_meter_data_2.move(50, 600)
Plot_meter_data_3 = PlotCanvas(MainWindow.tab, 4.5, 3, 100,
                               flow_meter_1.display_data_ch3['x'],
                               flow_meter_1.display_data_ch3['y'],
                               flow_meter_1.display_data_ch3['h'],
                               flow_meter_1.display_data_ch3['l'],
                               'B3')
Plot_meter_data_3.move(550, 160)
Plot_meter_data_4 = PlotCanvas(MainWindow.tab, 4.5, 3, 100,
                               flow_meter_1.display_data_ch4['x'],
                               flow_meter_1.display_data_ch4['y'],
                               flow_meter_1.display_data_ch4['h'],
                               flow_meter_1.display_data_ch4['l'],
                               'B4')
Plot_meter_data_4.move(550, 600)
Plot_meter_data_5 = PlotCanvas(MainWindow.tab, 4.5, 3, 100,
                               flow_meter_1.display_data_ch5['x'],
                               flow_meter_1.display_data_ch5['y'],
                               flow_meter_1.display_data_ch5['h'],
                               flow_meter_1.display_data_ch5['l'],
                               'B5')
Plot_meter_data_5.move(1050, 160)
Plot_meter_data_6 = PlotCanvas(MainWindow.tab, 4.5, 3, 100,
                               flow_meter_1.display_data_ch6['x'],
                               flow_meter_1.display_data_ch6['y'],
                               flow_meter_1.display_data_ch6['h'],
                               flow_meter_1.display_data_ch6['l'],
                               'B6')
Plot_meter_data_6.move(1050, 600)

# TODO:3.3 时间长度设置
def display_5min():
    display_length['length'] = '5min'


def display_10min():
    display_length['length'] = '10min'


def display_30min():
    display_length['length'] = '30min'


def display_1hour():
    display_length['length'] = '1hour'


def display_4hour():
    display_length['length'] = '4hour'


def display_8hour():
    display_length['length'] = '8hour'


# TODO:5. 导出一段时间的数据
def button_export_data():
    start_date_time = export_data_dialog.dateTimeEdit.dateTime().toString('yyyy-MM-dd hh:mm:ss')
    end_date_time = export_data_dialog.dateTimeEdit_2.dateTime().toString('yyyy-MM-dd hh:mm:ss')
    data_save_function.meter_record_save(start_date_time, end_date_time)  # 导出数据功能
    export_data_dialog.close()  # 关闭导出数据对话框


export_data_dialog = data_save.Ui_Dialog()  # 导出数据窗体
export_data_dialog.pushButton_2.clicked.connect(button_export_data)  # 初始化导出数据按钮


def export_data_period():
    export_data_dialog.dateTimeEdit.setDateTime(datetime.datetime.now())
    export_data_dialog.dateTimeEdit_2.setDateTime(datetime.datetime.now())
    export_data_dialog.show()  # 显示对话框


# TODO:6. 清理过时的数据
def button_data_drop():
    drop_before = data_drop_dialog.dateTimeEdit.dateTime().toString('yyyy-MM-dd hh:mm:ss')
    data_drop_function.meter_data_drop(drop_before)  # 清理数据功能
    data_drop_dialog.close()  # 关闭清理数据对话框


data_drop_dialog = data_drop.Ui_Dialog()  # 清理数据窗体
data_drop_dialog.pushButton_2.clicked.connect(button_data_drop)  # 初始化清理数据按钮


def data_drop_show():
    data_drop_dialog.show()  # 显示对话框


# TODO:7. 主窗体设计函数和方法
# TODO:7.1 定义按键功能
# 写入数据公共函数
def button_function_to_plc(register, data):
    write_to_plc['status'] = 1
    write_to_plc['register'] = register
    write_to_plc['data'] = data


def data_translation_for_4_20ma(ma_in):
    ma_in = float(ma_in)
    data_out = ma_in / 20 * 27648
    data_out = int(data_out)
    return data_out


# SPM1
def push_button_2_function():
    spm_signal = MainWindow.comboBox_2.currentText()
    spm_signal = int(spm_signal)
    button_function_to_plc(6, spm_signal)


# SPM2
def push_button_3_function():
    spm_signal = MainWindow.comboBox_3.currentText()
    spm_signal = int(spm_signal)
    button_function_to_plc(7, spm_signal)


# SPM3
def push_button_4_function():
    spm_signal = MainWindow.comboBox_6.currentText()
    spm_signal = int(spm_signal)
    button_function_to_plc(8, spm_signal)


# SPM4
def push_button_5_function():
    spm_signal = MainWindow.comboBox_7.currentText()
    spm_signal = int(spm_signal)
    button_function_to_plc(9, spm_signal)


# 4-20mA1
def push_button_6_function():
    ma_signal = MainWindow.comboBox_8.currentText()
    ma_signal = data_translation_for_4_20ma(ma_signal)
    button_function_to_plc(11, ma_signal)


# 4-20mA2
def push_button_7_function():
    ma_signal = MainWindow.comboBox_9.currentText()
    ma_signal = data_translation_for_4_20ma(ma_signal)
    button_function_to_plc(12, ma_signal)


# 4-20mA3
def push_button_8_function():
    ma_signal = MainWindow.comboBox_10.currentText()
    ma_signal = data_translation_for_4_20ma(ma_signal)
    button_function_to_plc(13, ma_signal)


# 4-20mA4
def push_button_9_function():
    ma_signal = MainWindow.comboBox_11.currentText()
    ma_signal = data_translation_for_4_20ma(ma_signal)
    button_function_to_plc(14, ma_signal)


# 标定柱容积
def push_button_18_function():
    cylinder_volume = MainWindow.comboBox_12.currentText()
    cylinder_volume = int(cylinder_volume)
    button_function_to_plc(15, cylinder_volume)


# 1#380V
def push_button_10_function():
    button_function_to_plc(19, 1)


def push_button_11_function():
    button_function_to_plc(19, 0)


# 2#380V
def push_button_12_function():
    button_function_to_plc(20, 1)


def push_button_13_function():
    button_function_to_plc(20, 0)


# 3#380V
def push_button_14_function():
    button_function_to_plc(21, 1)


def push_button_15_function():
    button_function_to_plc(21, 0)


# 4#380V
def push_button_16_function():
    button_function_to_plc(22, 1)


def push_button_17_function():
    button_function_to_plc(22, 0)


# 1#SPM自变
def push_button_19_function():
    if refresh_return_data['meter_1']['SPM-auto_1'] == 1:
        button_function_to_plc(27, 0)
    else:
        button_function_to_plc(27, 1)


# 2#SPM自变
def push_button_23_function():
    if refresh_return_data['meter_1']['SPM-auto_2'] == 1:
        button_function_to_plc(28, 0)
    else:
        button_function_to_plc(28, 1)


# 3#SPM自变
def push_button_20_function():
    if refresh_return_data['meter_1']['SPM-auto_3'] == 1:
        button_function_to_plc(29, 0)
    else:
        button_function_to_plc(29, 1)


# 4#SPM自变
def push_button_24_function():
    if refresh_return_data['meter_1']['SPM-auto_4'] == 1:
        button_function_to_plc(30, 0)
    else:
        button_function_to_plc(30, 1)


# 1#4-2mA自变
def push_button_21_function():
    if refresh_return_data['meter_1']['4-20mA_auto_1'] == 1:
        button_function_to_plc(31, 0)
    else:
        button_function_to_plc(31, 1)


# 2#4-2mA自变
def push_button_25_function():
    if refresh_return_data['meter_1']['4-20mA_auto_2'] == 1:
        button_function_to_plc(32, 0)
    else:
        button_function_to_plc(32, 1)


# 3#4-2mA自变
def push_button_22_function():
    if refresh_return_data['meter_1']['4-20mA_auto_3'] == 1:
        button_function_to_plc(33, 0)
    else:
        button_function_to_plc(33, 1)


# 4#4-2mA自变
def push_button_26_function():
    if refresh_return_data['meter_1']['4-20mA_auto_4'] == 1:
        button_function_to_plc(34, 0)
    else:
        button_function_to_plc(34, 1)


# pid控制设定
def push_button_29_function():
    button_function_to_plc(35, 1)


def push_button_28_function():
    button_function_to_plc(35, 0)


# 选择标定柱
def push_button_30_function():
    cylinder_volume_slect = MainWindow.comboBox_12.currentText()
    cylinder_volume_slect = int(cylinder_volume_slect)
    button_function_to_plc(38, cylinder_volume_slect)


# 选择标定柱
def push_button_18_function():
    flow_channel_select = MainWindow.comboBox_4.currentText()
    flow_channel_select = int(flow_channel_select)
    button_function_to_plc(36, flow_channel_select)


# 计算K值
def push_button_31_function():
    if refresh_return_data['meter_1']['pid_control_channel'] == 1:
        if refresh_return_data['meter_1']['calibration_pot_select'] == 100:
            k_factor_calculation = (refresh_return_data['meter_1']['pulse_1'] / 30) / \
                                   (refresh_return_data['meter_1']['flow_cylinder_100'] / 3600)
        elif refresh_return_data['meter_1']['calibration_pot_select'] == 2000:
            k_factor_calculation = (refresh_return_data['meter_1']['pulse_1'] / 30) / \
                                   (refresh_return_data['meter_1']['flow_cylinder_2000'] / 3600)
            print('k-factor=' + str(k_factor_calculation))
    elif refresh_return_data['meter_1']['pid_control_channel'] == 2:
        if refresh_return_data['meter_1']['calibration_pot_select'] == 100:
            k_factor_calculation = (refresh_return_data['meter_1']['pulse_2'] / 30) / \
                                   (refresh_return_data['meter_1']['flow_cylinder_100'] / 3600)
        elif refresh_return_data['meter_1']['calibration_pot_select'] == 2000:
            k_factor_calculation = (refresh_return_data['meter_1']['pulse_2'] / 30) / \
                                   (refresh_return_data['meter_1']['flow_cylinder_2000'] / 3600)
    elif refresh_return_data['meter_1']['pid_control_channel'] == 3:
        if refresh_return_data['meter_1']['calibration_pot_select'] == 100:
            k_factor_calculation = (refresh_return_data['meter_1']['pulse_3'] / 30) / \
                                   (refresh_return_data['meter_1']['flow_cylinder_100'] / 3600)
        elif refresh_return_data['meter_1']['calibration_pot_select'] == 2000:
            k_factor_calculation = (refresh_return_data['meter_1']['pulse_3'] / 30) / \
                                   (refresh_return_data['meter_1']['flow_cylinder_2000'] / 3600)
    elif refresh_return_data['meter_1']['pid_control_channel'] == 4:
        if refresh_return_data['meter_1']['calibration_pot_select'] == 100:
            k_factor_calculation = (refresh_return_data['meter_1']['pulse_4'] / 30) / \
                                   (refresh_return_data['meter_1']['flow_cylinder_100'] / 3600)
        elif refresh_return_data['meter_1']['calibration_pot_select'] == 2000:
            k_factor_calculation = (refresh_return_data['meter_1']['pulse_4'] / 30) / \
                                   (refresh_return_data['meter_1']['flow_cylinder_2000'] / 3600)
    elif refresh_return_data['meter_1']['pid_control_channel'] == 5:
        if refresh_return_data['meter_1']['calibration_pot_select'] == 100:
            k_factor_calculation = (refresh_return_data['meter_1']['pulse_5'] / 30) / \
                                   (refresh_return_data['meter_1']['flow_cylinder_100'] / 3600)
        elif refresh_return_data['meter_1']['calibration_pot_select'] == 2000:
            k_factor_calculation = (refresh_return_data['meter_1']['pulse_5'] / 30) / \
                                   (refresh_return_data['meter_1']['flow_cylinder_2000'] / 3600)
    elif refresh_return_data['meter_1']['pid_control_channel'] == 6:
        if refresh_return_data['meter_1']['calibration_pot_select'] == 100:
            k_factor_calculation = (refresh_return_data['meter_1']['pulse_6'] / 30) / \
                                   (refresh_return_data['meter_1']['flow_cylinder_100'] / 3600)
        elif refresh_return_data['meter_1']['calibration_pot_select'] == 2000:
            k_factor_calculation = (refresh_return_data['meter_1']['pulse_6'] / 30) / \
                                   (refresh_return_data['meter_1']['flow_cylinder_2000'] / 3600)
    k_factor_calculation = int(k_factor_calculation)
    print(k_factor_calculation)
    button_function_to_plc(39, k_factor_calculation)


# 选择标定柱
def push_button_27_function():
    pid_set_flow_point = MainWindow.comboBox_5.currentText()
    pid_set_flow_point = int(pid_set_flow_point)
    button_function_to_plc(37, pid_set_flow_point)


# TODO:7.2 界面显示初始化

# TODO:7.3 各功能链接函数
# 定义在主窗口打开各个子窗体的方法

# TODO:7.4 按键函数连接

MainWindow.show()  # 显示主界面
sys.exit(app.exec_())  # 退出主界面
