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
refresh_return_data = {'meter_1': {'flow_1': 0,  # 通道1流量
                                   'flow_2': 0,  # 通道2流量
                                   'flow_3': 0,  # 通道3流量
                                   'flow_4': 0,  # 通道4流量
                                   'flow_5': 0,  # 通道5流量
                                   'flow_6': 0,  # 通道6流量
                                   'pulse_1': 0,  # 通道1脉冲
                                   'pulse_2': 0,  # 通道2脉冲
                                   'pulse_3': 0,  # 通道3脉冲
                                   'pulse_4': 0,  # 通道4脉冲
                                   'pulse_5': 0,  # 通道5脉冲
                                   'pulse_6': 0,  # 通道6脉冲
                                   'SPM1': 0,
                                   'SPM2': 0,
                                   'SPM3': 0,
                                   'SPM4': 0,
                                   'SPM_max': 0,  # SPM上限
                                   '4-20mA_1': 0,
                                   '4-20mA_2': 0,
                                   '4-20mA_3': 0,
                                   '4-20mA_4': 0,
                                   'flow_cylinder_100': 0,  # 标定流量 100ml标定柱
                                   'flow_cylinder_2000': 0,  # 标定流量 2000ml标定柱
                                   'meter_connection': 0,  # 仪表连接状态
                                   'pump_1_status': 0,  # 泵1状态
                                   'pump_2_status': 0,  # 泵2状态
                                   'pump_3_status': 0,  # 泵3状态
                                   'pump_4_status': 0,  # 泵4状态
                                   'SPM-auto_1': 0,  # SPM自变
                                   'SPM-auto_2': 0,  # SPM自变
                                   'SPM-auto_3': 0,  # SPM自变
                                   'SPM-auto_4': 0,  # SPM自变
                                   '4-20mA_auto_1': 0,  # 4-20mA自变
                                   '4-20mA_auto_2': 0,  # 4-20mA自变
                                   '4-20mA_auto_3': 0,  # 4-20mA自变
                                   '4-20mA_auto_4': 0,  # 4-20mA自变
                                   'pid_control': 0,  # 0非PID控制，1PID控制
                                   'pid_control_channel': 0,  # PID控制通道
                                   'pid_set_point': 0,  # PID设定流量
                                   'calibration_pot_select': 0,  # 选择的标定柱
                                   'sensor_k_factor': 0,  # 探头的K值
                                   'pid_flow': 0,  # PID反馈流量
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
        # self.Meter_data_column_2_plus = list(np.arange(34) + 40001)
        self.Meter_data_column_2_plus = list(np.arange(42) + 40001)
        # self.Meter_data_2_plus = list(np.zeros(36).astype(int))
        self.Meter_data_2_plus = list(np.zeros(44).astype(int))
        # 写
        # self.Meter_data_2_plus_write_index = list(np.arange(36) + 40001)
        self.Meter_data_2_plus_write_index = list(np.arange(44) + 40001)
        # self.Meter_data_2_plus_write_value = list(np.arange(36))
        self.Meter_data_2_plus_write_value = list(np.arange(44))
        self.Meter_data_2_plus_write = pd.Series(self.Meter_data_2_plus_write_value,
                                                 index=self.Meter_data_2_plus_write_index)
        # 显示曲线初始化
        self.display_data_ch1 = {'x': list(np.zeros(28800)),
                                 'y': list(np.zeros(28800))}
        self.display_data_ch2 = {'x': list(np.zeros(28800)),
                                 'y': list(np.zeros(28800))}
        self.display_data_ch3 = {'x': list(np.zeros(28800)),
                                 'y': list(np.zeros(28800))}
        self.display_data_ch4 = {'x': list(np.zeros(28800)),
                                 'y': list(np.zeros(28800))}
        self.display_data_ch5 = {'x': list(np.zeros(28800)),
                                 'y': list(np.zeros(28800))}
        self.display_data_ch6 = {'x': list(np.zeros(28800)),
                                 'y': list(np.zeros(28800))}
        self.display_pid_flow = {'x': list(np.zeros(28800)),
                                 'y': list(np.zeros(28800))}
        self.display_valve_position = {'x': list(np.zeros(28800)),
                                       'y': list(np.zeros(28800))}
        self.display_pid_set_point = {'x': list(np.zeros(28800)),
                                      'y': list(np.zeros(28800))}
        # TODO:2.3初始化函数
        for i in range(len(self.Meter_data_column_2_plus)):
            self.Meter_data_column_2_plus[i] = str(self.Meter_data_column_2_plus[i])
        self.Meter_data_column_2_plus.insert(0, 'DateTime')
        self.Meter_data_column_2_plus.append('ModbusAddress')
        self.Meter_data_2_plus[0] = datetime.datetime.now()  # 获取当前时间
        for i in range(len(self.Meter_data_2_plus_write_index)):
            self.Meter_data_2_plus_write_index[i] = str(self.Meter_data_2_plus_write_index[i])
        # print(type(self.Connect))

    # TODO:2.4 modbus参数复位
    def modbus_parameter_reset(self):
        self.Modbus_parameter['PORT'] = "无串口!"  # 串口号
        self.Modbus_parameter['baudrate'] = 9600  # 波特率
        self.Modbus_parameter['bytesize'] = 8  # 数据位
        self.Modbus_parameter['parity'] = 'N'  # 校验位
        self.Modbus_parameter['stopbits'] = 1  # 停止位
        self.Modbus_parameter['address'] = 1  # 仪表从站站号


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
    return_data = {'flow_1': 0,  # 通道1流量
                   'flow_2': 0,  # 通道2流量
                   'flow_3': 0,  # 通道3流量
                   'flow_4': 0,  # 通道4流量
                   'flow_5': 0,  # 通道5流量
                   'flow_6': 0,  # 通道6流量
                   'pulse_1': 0,  # 通道1脉冲
                   'pulse_2': 0,  # 通道2脉冲
                   'pulse_3': 0,  # 通道3脉冲
                   'pulse_4': 0,  # 通道4脉冲
                   'pulse_5': 0,  # 通道5脉冲
                   'pulse_6': 0,  # 通道6脉冲
                   'SPM1': 0,
                   'SPM2': 0,
                   'SPM3': 0,
                   'SPM4': 0,
                   'SPM_max': 0,  # SPM上限
                   '4-20mA_1': 0,
                   '4-20mA_2': 0,
                   '4-20mA_3': 0,
                   '4-20mA_4': 0,
                   'flow_cylinder_100': 0,  # 标定流量 100ml标定柱
                   'flow_cylinder_2000': 0,  # 标定流量 2000ml标定柱
                   'meter_connection': 0,  # 仪表连接状态
                   'pump_1_status': 0,  # 泵1状态
                   'pump_2_status': 0,  # 泵2状态
                   'pump_3_status': 0,  # 泵3状态
                   'pump_4_status': 0,  # 泵4状态
                   'SPM-auto_1': 0,  # SPM自变
                   'SPM-auto_2': 0,  # SPM自变
                   'SPM-auto_3': 0,  # SPM自变
                   'SPM-auto_4': 0,  # SPM自变
                   '4-20mA_auto_1': 0,  # 4-20mA自变
                   '4-20mA_auto_2': 0,  # 4-20mA自变
                   '4-20mA_auto_3': 0,  # 4-20mA自变
                   '4-20mA_auto_4': 0,  # 4-20mA自变
                   'pid_control': 0,  # 0非PID控制，1PID控制
                   'pid_control_channel': 0,  # PID控制通道
                   'pid_set_point': 0,  # PID设定流量
                   'calibration_pot_select': 0,  # 选择的标定柱
                   'sensor_k_factor': 0,  # 探头的K值
                   'pid_flow': 0,  # PID反馈流量
                   }
    # 刷新仪表数据结构中的数据
    flowmeter.Meter_data_2_plus[0] = datetime.datetime.now()

    # 读取仪表信息
    try:
        get_meter_data = Modbus_TCP.read_modbus_tcp(modbus_tcp_connection,
                                                    0,  # 起始寄存器
                                                    42,  # 读寄存器的数量
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
        for item in range(42):
            flowmeter.Meter_data_2_plus[item + 1] = get_meter_data[item]
        logger_paddle.info(flowmeter.Meter_data_2_plus)
        flowmeter.Connect_status_meter = 1  # 连接modbus错误


        # 保存运行记录
        # save_run_data = translate_meter_data_to_save_parlance(flowmeter.Meter_data_2_plus,
        #                                                       flowmeter.Meter_data_column_2_plus)
        # save_data(save_run_data)

    # 刷新脉冲数
    if flowmeter.Connect_status_meter == 0:
        return_data['pulse_1'] = -1
        return_data['pulse_2'] = -1
        return_data['pulse_3'] = -1
        return_data['pulse_4'] = -1
        return_data['pulse_5'] = -1
        return_data['pulse_6'] = -1
        return_data['SPM1'] = -1
        return_data['SPM2'] = -1
        return_data['SPM3'] = -1
        return_data['SPM4'] = -1
        return_data['4-20mA_1'] = -1
        return_data['4-20mA_2'] = -1
        return_data['4-20mA_3'] = -1
        return_data['4-20mA_4'] = -1
    elif flowmeter.Connect_status_meter == 1:
        return_data['pulse_1'] = flowmeter.Meter_data_2_plus[1]
        return_data['pulse_2'] = flowmeter.Meter_data_2_plus[2]
        return_data['pulse_3'] = flowmeter.Meter_data_2_plus[3]
        return_data['pulse_4'] = flowmeter.Meter_data_2_plus[4]
        return_data['pulse_5'] = flowmeter.Meter_data_2_plus[5]
        return_data['pulse_6'] = flowmeter.Meter_data_2_plus[6]
        return_data['SPM1'] = flowmeter.Meter_data_2_plus[7]
        return_data['SPM2'] = flowmeter.Meter_data_2_plus[8]
        return_data['SPM3'] = flowmeter.Meter_data_2_plus[9]
        return_data['SPM4'] = flowmeter.Meter_data_2_plus[10]
        return_data['4-20mA_1'] = flowmeter.Meter_data_2_plus[12]
        return_data['4-20mA_2'] = flowmeter.Meter_data_2_plus[13]
        return_data['4-20mA_3'] = flowmeter.Meter_data_2_plus[14]
        return_data['4-20mA_4'] = flowmeter.Meter_data_2_plus[15]
        return_data['flow_cylinder_100'] = float(flowmeter.Meter_data_2_plus[16]) + \
                                           float(flowmeter.Meter_data_2_plus[17]) / 10000
        return_data['flow_cylinder_2000'] = float(flowmeter.Meter_data_2_plus[18]) + \
                                            float(flowmeter.Meter_data_2_plus[19]) / 10000
        return_data['pump_1_status'] = flowmeter.Meter_data_2_plus[24]
        return_data['pump_2_status'] = flowmeter.Meter_data_2_plus[25]
        return_data['pump_3_status'] = flowmeter.Meter_data_2_plus[26]
        return_data['pump_4_status'] = flowmeter.Meter_data_2_plus[27]
        return_data['SPM-auto_1'] = flowmeter.Meter_data_2_plus[28]
        return_data['SPM-auto_2'] = flowmeter.Meter_data_2_plus[29]
        return_data['SPM-auto_3'] = flowmeter.Meter_data_2_plus[30]
        return_data['SPM-auto_4'] = flowmeter.Meter_data_2_plus[31]
        return_data['4-20mA_auto_1'] = flowmeter.Meter_data_2_plus[32]
        return_data['4-20mA_auto_2'] = flowmeter.Meter_data_2_plus[33]
        return_data['4-20mA_auto_3'] = flowmeter.Meter_data_2_plus[34]
        return_data['4-20mA_auto_4'] = flowmeter.Meter_data_2_plus[35]
        return_data['pid_control'] = flowmeter.Meter_data_2_plus[36]
        return_data['pid_control_channel'] = flowmeter.Meter_data_2_plus[37]
        return_data['pid_set_point'] = flowmeter.Meter_data_2_plus[38]
        return_data['calibration_pot_select'] = flowmeter.Meter_data_2_plus[39]
        return_data['sensor_k_factor'] = flowmeter.Meter_data_2_plus[40]
        return_data['pid_flow'] = float(flow_meter_1.Meter_data_2_plus[41]) + \
                                  float(flowmeter.Meter_data_2_plus[42]) / 10000
    return return_data


#  更新所有仪表
def refresh_parameter_all():
    # 更新时间
    date_time = date_time_now_text(datetime.datetime.now())
    MainWindow.label_28.setText(date_time)
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
        flow_meter_1.display_pid_flow['x'][i] = flow_meter_1.display_pid_flow['x'][i + 1]
        flow_meter_1.display_valve_position['x'][i] = flow_meter_1.display_valve_position['x'][i + 1]
        flow_meter_1.display_pid_set_point['x'][i] = flow_meter_1.display_pid_set_point['x'][i + 1]

    flow_meter_1.display_data_ch1['x'][28799] = time_now_text(datetime.datetime.now())
    flow_meter_1.display_data_ch2['x'][28799] = flow_meter_1.display_data_ch1['x'][28799]
    flow_meter_1.display_data_ch3['x'][28799] = flow_meter_1.display_data_ch1['x'][28799]
    flow_meter_1.display_data_ch4['x'][28799] = flow_meter_1.display_data_ch1['x'][28799]
    flow_meter_1.display_data_ch5['x'][28799] = flow_meter_1.display_data_ch1['x'][28799]
    flow_meter_1.display_data_ch6['x'][28799] = flow_meter_1.display_data_ch1['x'][28799]
    flow_meter_1.display_pid_flow['x'][28799] = flow_meter_1.display_data_ch1['x'][28799]
    flow_meter_1.display_valve_position['x'][28799] = flow_meter_1.display_data_ch1['x'][28799]
    flow_meter_1.display_pid_set_point['x'][28799] = flow_meter_1.display_data_ch1['x'][28799]

    # 在界面显示
    pulse_1 = refresh_return_data['meter_1']['pulse_1']
    MainWindow.lcdNumber.display(pulse_1)  # 脉冲1
    pulse_2 = refresh_return_data['meter_1']['pulse_2']
    MainWindow.lcdNumber_24.display(pulse_2)  # 脉冲2
    pulse_3 = refresh_return_data['meter_1']['pulse_3']
    MainWindow.lcdNumber_6.display(pulse_3)  # 脉冲3
    pulse_4 = refresh_return_data['meter_1']['pulse_4']
    MainWindow.lcdNumber_22.display(pulse_4)  # 脉冲4
    pulse_5 = refresh_return_data['meter_1']['pulse_5']
    MainWindow.lcdNumber_9.display(pulse_5)  # 脉冲5
    pulse_6 = refresh_return_data['meter_1']['pulse_6']
    MainWindow.lcdNumber_14.display(pulse_6)  # 脉冲6
    spm_1 = refresh_return_data['meter_1']['SPM1']
    MainWindow.lcdNumber_10.display(spm_1)  # SPM1
    spm_2 = refresh_return_data['meter_1']['SPM2']
    MainWindow.lcdNumber_21.display(spm_2)  # SPM2
    spm_3 = refresh_return_data['meter_1']['SPM3']
    MainWindow.lcdNumber_13.display(spm_3)  # SPM3
    spm_4 = refresh_return_data['meter_1']['SPM4']
    MainWindow.lcdNumber_16.display(spm_4)  # SPM4
    ma_signal_1 = refresh_return_data['meter_1']['4-20mA_1']
    ma_signal_1 = ma_signal_1 / 27648 * 20
    MainWindow.lcdNumber_17.display(ma_signal_1)  # 4-20mA1
    ma_signal_2 = refresh_return_data['meter_1']['4-20mA_2']
    ma_signal_2 = ma_signal_2 / 27648 * 20
    MainWindow.lcdNumber_12.display(ma_signal_2)  # 4-20mA2
    ma_signal_3 = refresh_return_data['meter_1']['4-20mA_3']
    ma_signal_3 = ma_signal_3 / 27648 * 20
    MainWindow.lcdNumber_18.display(ma_signal_3)  # 4-20mA3
    ma_signal_4 = refresh_return_data['meter_1']['4-20mA_4']
    ma_signal_4 = ma_signal_4 / 27648 * 20
    MainWindow.lcdNumber_23.display(ma_signal_4)  # 4-20mA4
    flow_cylinder_100 = refresh_return_data['meter_1']['flow_cylinder_100']
    MainWindow.lcdNumber_11.display(flow_cylinder_100)  # 标定柱标定流量
    flow_cylinder_2000 = refresh_return_data['meter_1']['flow_cylinder_2000']
    MainWindow.lcdNumber_25.display(flow_cylinder_2000)  # 标定柱标定流量

    # pid控制流量显示
    # 控制状态
    pid_control_status = refresh_return_data['meter_1']['pid_control']
    if pid_control_status == 1:
        MainWindow.label_44.setStyleSheet("background-color: rgb(0, 255, 0);\n")
    else:
        MainWindow.label_44.setStyleSheet("background-color: rgb(255, 0, 0);\n")
    # pid-流量
    MainWindow.lcdNumber_4.display(refresh_return_data['meter_1']['pid_flow'])
    # 标定柱容积
    MainWindow.lcdNumber_8.display(refresh_return_data['meter_1']['calibration_pot_select'])
    # 阀门开度
    pid_valve_position = ma_signal_4 / 20 * 100
    MainWindow.lcdNumber_3.display(pid_valve_position)
    # 探头通道
    MainWindow.lcdNumber_5.display(refresh_return_data['meter_1']['pid_control_channel'])
    # 探头K值
    MainWindow.lcdNumber_7.display(refresh_return_data['meter_1']['sensor_k_factor'])
    # 流量设置值
    MainWindow.lcdNumber_15.display(refresh_return_data['meter_1']['pid_set_point'])

    pump_1_status = refresh_return_data['meter_1']['pump_1_status']
    if pump_1_status == 1:
        MainWindow.label_39.setStyleSheet("background-color: rgb(0, 255, 0);\n")
    else:
        MainWindow.label_39.setStyleSheet("background-color: rgb(255, 0, 0);\n")
    pump_2_status = refresh_return_data['meter_1']['pump_2_status']
    if pump_2_status == 1:
        MainWindow.label_40.setStyleSheet("background-color: rgb(0, 255, 0);\n")
    else:
        MainWindow.label_40.setStyleSheet("background-color: rgb(255, 0, 0);\n")
    pump_3_status = refresh_return_data['meter_1']['pump_3_status']
    if pump_3_status == 1:
        MainWindow.label_41.setStyleSheet("background-color: rgb(0, 255, 0);\n")
    else:
        MainWindow.label_41.setStyleSheet("background-color: rgb(255, 0, 0);\n")
    pump_4_status = refresh_return_data['meter_1']['pump_4_status']
    if pump_4_status == 1:
        MainWindow.label_42.setStyleSheet("background-color: rgb(0, 255, 0);\n")
    else:
        MainWindow.label_42.setStyleSheet("background-color: rgb(255, 0, 0);\n")
    # 更新曲线
    for i in range(28799):
        flow_meter_1.display_data_ch1['y'][i] = flow_meter_1.display_data_ch1['y'][i + 1]
        flow_meter_1.display_data_ch2['y'][i] = flow_meter_1.display_data_ch2['y'][i + 1]
        flow_meter_1.display_data_ch3['y'][i] = flow_meter_1.display_data_ch3['y'][i + 1]
        flow_meter_1.display_data_ch4['y'][i] = flow_meter_1.display_data_ch4['y'][i + 1]
        flow_meter_1.display_data_ch5['y'][i] = flow_meter_1.display_data_ch5['y'][i + 1]
        flow_meter_1.display_data_ch6['y'][i] = flow_meter_1.display_data_ch6['y'][i + 1]
        flow_meter_1.display_pid_flow['y'][i] = flow_meter_1.display_pid_flow['y'][i + 1]
        flow_meter_1.display_valve_position['y'][i] = flow_meter_1.display_valve_position['y'][i + 1]
        flow_meter_1.display_pid_set_point['y'][i] = flow_meter_1.display_pid_set_point['y'][i + 1]
    flow_meter_1.display_data_ch1['y'][28799] = pulse_1
    flow_meter_1.display_data_ch2['y'][28799] = pulse_2
    flow_meter_1.display_data_ch3['y'][28799] = pulse_3
    flow_meter_1.display_data_ch4['y'][28799] = pulse_4
    flow_meter_1.display_data_ch5['y'][28799] = pulse_5
    flow_meter_1.display_data_ch6['y'][28799] = pulse_6
    flow_meter_1.display_pid_flow['y'][28799] = refresh_return_data['meter_1']['pid_flow']
    flow_meter_1.display_valve_position['y'][28799] = pid_valve_position
    flow_meter_1.display_pid_set_point['y'][28799] = refresh_return_data['meter_1']['pid_set_point']


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
    Plot_pid_flow.update_figure()
    Plot_valve_position.update_figure()

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
                 set_point_enable,
                 set_point_x,
                 set_point_y,
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
        self.set_point_enable = set_point_enable
        self.set_point_x = set_point_x
        self.set_point_y = set_point_y
        self.plot_tittle = plot_tittle

    def update_figure(self):
        self.axes.cla()
        if display_length['length'] == '5min':
            meter_1_ch1_display_x = self.plot_x[-300:]
            meter_1_ch1_display_y = self.plot_y[-300:]
            set_point_display_x = self.set_point_x[-300:]
            set_point_display_y = self.set_point_y[-300:]
        elif display_length['length'] == '10min':
            meter_1_ch1_display_x = self.plot_x[-600:]
            meter_1_ch1_display_y = self.plot_y[-600:]
            set_point_display_x = self.set_point_x[-600:]
            set_point_display_y = self.set_point_y[-600:]
        elif display_length['length'] == '30min':
            meter_1_ch1_display_x = self.plot_x[-1800:]
            meter_1_ch1_display_y = self.plot_y[-1800:]
            set_point_display_x = self.set_point_x[-1800:]
            set_point_display_y = self.set_point_y[-1800:]
        elif display_length['length'] == '1hour':
            meter_1_ch1_display_x = self.plot_x[-3600:]
            meter_1_ch1_display_y = self.plot_y[-3600:]
            set_point_display_x = self.set_point_x[-3600:]
            set_point_display_y = self.set_point_y[-3600:]
        elif display_length['length'] == '4hour':
            meter_1_ch1_display_x = self.plot_x[-14400:]
            meter_1_ch1_display_y = self.plot_y[-14400:]
            set_point_display_x = self.set_point_x[-14400:]
            set_point_display_y = self.set_point_y[-14400:]
        elif display_length['length'] == '8hour':
            meter_1_ch1_display_x = self.plot_x[-28800:]
            meter_1_ch1_display_y = self.plot_y[-28800:]
            set_point_display_x = self.set_point_x[-28800:]
            set_point_display_y = self.set_point_y[-28800:]

        self.axes.plot(meter_1_ch1_display_x, meter_1_ch1_display_y, label=self.plot_tittle, color='red')
        if self.set_point_enable == 1:
            self.axes.plot(set_point_display_x, set_point_display_y, label='流量设定', color='black')
        self.axes.legend()
        if display_length['length'] == '5min':
            self.axes.xaxis.set_major_locator(ticker.MultipleLocator(75))
            self.axes.xaxis.set_minor_locator(ticker.MultipleLocator(15))
        elif display_length['length'] == '10min':
            self.axes.xaxis.set_major_locator(ticker.MultipleLocator(150))
            self.axes.xaxis.set_minor_locator(ticker.MultipleLocator(30))
        elif display_length['length'] == '30min':
            self.axes.xaxis.set_major_locator(ticker.MultipleLocator(450))
            self.axes.xaxis.set_minor_locator(ticker.MultipleLocator(90))
        elif display_length['length'] == '1hour':
            self.axes.xaxis.set_major_locator(ticker.MultipleLocator(900))
            self.axes.xaxis.set_minor_locator(ticker.MultipleLocator(180))
        elif display_length['length'] == '4hour':
            self.axes.xaxis.set_major_locator(ticker.MultipleLocator(3600))
            self.axes.xaxis.set_minor_locator(ticker.MultipleLocator(720))
        elif display_length['length'] == '8hour':
            self.axes.xaxis.set_major_locator(ticker.MultipleLocator(7200))
            self.axes.xaxis.set_minor_locator(ticker.MultipleLocator(1440))
        self.axes.yaxis.grid(True)
        self.axes.xaxis.grid(True)
        self.axes.set_title(self.plot_tittle)
        self.draw()


# TODO:3.1.3 运行曲线界面-定义
Plot_pid_flow = PlotCanvas(MainWindow, 3.5, 3, 100,
                           flow_meter_1.display_pid_flow['x'],
                           flow_meter_1.display_pid_flow['y'],
                           1,
                           flow_meter_1.display_pid_set_point['x'],
                           flow_meter_1.display_pid_set_point['y'],
                           'PID流量')
Plot_pid_flow.move(480, 30)
Plot_valve_position = PlotCanvas(MainWindow, 3.5, 3, 100,
                                 flow_meter_1.display_valve_position['x'],
                                 flow_meter_1.display_valve_position['y'],
                                 0,
                                 flow_meter_1.display_pid_set_point['x'],
                                 flow_meter_1.display_pid_set_point['y'],
                                 '阀门开度')
Plot_valve_position.move(800, 30)
Plot_meter_data = PlotCanvas(MainWindow, 3.5, 3, 100,
                             flow_meter_1.display_data_ch1['x'],
                             flow_meter_1.display_data_ch1['y'],
                             0,
                             flow_meter_1.display_pid_set_point['x'],
                             flow_meter_1.display_pid_set_point['y'],
                             '通道1')
Plot_meter_data.move(480, 310)
Plot_meter_data_2 = PlotCanvas(MainWindow, 3.5, 3, 100,
                               flow_meter_1.display_data_ch2['x'],
                               flow_meter_1.display_data_ch2['y'],
                               0,
                               flow_meter_1.display_pid_set_point['x'],
                               flow_meter_1.display_pid_set_point['y'],
                               '通道2')
Plot_meter_data_2.move(800, 310)
Plot_meter_data_3 = PlotCanvas(MainWindow, 3.5, 3, 100,
                               flow_meter_1.display_data_ch3['x'],
                               flow_meter_1.display_data_ch3['y'],
                               0,
                               flow_meter_1.display_pid_set_point['x'],
                               flow_meter_1.display_pid_set_point['y'],
                               '通道3')
Plot_meter_data_3.move(1120, 310)
Plot_meter_data_4 = PlotCanvas(MainWindow, 3.5, 3, 100,
                               flow_meter_1.display_data_ch4['x'],
                               flow_meter_1.display_data_ch4['y'],
                               0,
                               flow_meter_1.display_pid_set_point['x'],
                               flow_meter_1.display_pid_set_point['y'],
                               '通道4')
Plot_meter_data_4.move(480, 590)
Plot_meter_data_5 = PlotCanvas(MainWindow, 3.5, 3, 100,
                               flow_meter_1.display_data_ch5['x'],
                               flow_meter_1.display_data_ch5['y'],
                               0,
                               flow_meter_1.display_pid_set_point['x'],
                               flow_meter_1.display_pid_set_point['y'],
                               '通道5')
Plot_meter_data_5.move(800, 590)
Plot_meter_data_6 = PlotCanvas(MainWindow, 3.5, 3, 100,
                               flow_meter_1.display_data_ch6['x'],
                               flow_meter_1.display_data_ch6['y'],
                               0,
                               flow_meter_1.display_pid_set_point['x'],
                               flow_meter_1.display_pid_set_point['y'],
                               '通道6')
Plot_meter_data_6.move(1120, 590)


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
MainWindow.comboBox_2.addItem('60')
MainWindow.comboBox_3.addItem('60')
MainWindow.comboBox_6.addItem('60')
MainWindow.comboBox_7.addItem('60')
MainWindow.comboBox_8.addItem('12')
MainWindow.comboBox_9.addItem('12')
MainWindow.comboBox_10.addItem('12')
MainWindow.comboBox_11.addItem('12')
MainWindow.comboBox_12.addItems(['100', '2000'])
MainWindow.comboBox_4.addItems(['1', '2', '3', '4', '5', '6'])
MainWindow.comboBox_5.addItem('150')

# TODO:7.3 各功能链接函数
# 定义在主窗口打开各个子窗体的方法
MainWindow.action5min.triggered.connect(display_5min)  # 时间长度
MainWindow.action10min.triggered.connect(display_10min)  # 时间长度
MainWindow.action30min.triggered.connect(display_30min)  # 时间长度
MainWindow.action1hour.triggered.connect(display_1hour)  # 时间长度
MainWindow.action4hour.triggered.connect(display_4hour)  # 时间长度
MainWindow.action8hour.triggered.connect(display_8hour)  # 时间长度
MainWindow.actionoutput_data.triggered.connect(export_data_period)  # 导出数据
MainWindow.actiondata_clear.triggered.connect(data_drop_show)  # 清理数据

# TODO:7.4 按键函数连接
MainWindow.pushButton_2.clicked.connect(push_button_2_function)  # SPM1
MainWindow.pushButton_3.clicked.connect(push_button_3_function)  # SPM2
MainWindow.pushButton_4.clicked.connect(push_button_4_function)  # SPM3
MainWindow.pushButton_5.clicked.connect(push_button_5_function)  # SPM4
MainWindow.pushButton_6.clicked.connect(push_button_6_function)  # 4-20mA1
MainWindow.pushButton_7.clicked.connect(push_button_7_function)  # 4-20mA2
MainWindow.pushButton_8.clicked.connect(push_button_8_function)  # 4-20mA3
MainWindow.pushButton_9.clicked.connect(push_button_9_function)  # 4-20mA4
MainWindow.pushButton_10.clicked.connect(push_button_10_function)  # 1#380V
MainWindow.pushButton_11.clicked.connect(push_button_11_function)  # 1#380V
MainWindow.pushButton_12.clicked.connect(push_button_12_function)  # 2#380V
MainWindow.pushButton_13.clicked.connect(push_button_13_function)  # 2#380V
MainWindow.pushButton_14.clicked.connect(push_button_14_function)  # 3#380V
MainWindow.pushButton_15.clicked.connect(push_button_15_function)  # 3#380V
MainWindow.pushButton_16.clicked.connect(push_button_16_function)  # 4#380V
MainWindow.pushButton_17.clicked.connect(push_button_17_function)  # 4#380V
MainWindow.pushButton_19.clicked.connect(push_button_19_function)  # 1#SPM自变
MainWindow.pushButton_23.clicked.connect(push_button_23_function)  # 2#SPM自变
MainWindow.pushButton_20.clicked.connect(push_button_20_function)  # 3#SPM自变
MainWindow.pushButton_24.clicked.connect(push_button_24_function)  # 4#SPM自变
MainWindow.pushButton_21.clicked.connect(push_button_21_function)  # 1#4-20mA自变
MainWindow.pushButton_25.clicked.connect(push_button_25_function)  # 2#4-20mA自变
MainWindow.pushButton_22.clicked.connect(push_button_22_function)  # 3#4-20mA自变
MainWindow.pushButton_26.clicked.connect(push_button_26_function)  # 4#4-20mA自变
MainWindow.pushButton_29.clicked.connect(push_button_29_function)  # pid控制设定
MainWindow.pushButton_28.clicked.connect(push_button_28_function)  # pid控制设定
MainWindow.pushButton_30.clicked.connect(push_button_30_function)  # 选择标定柱
MainWindow.pushButton_18.clicked.connect(push_button_18_function)  # 选择通道
MainWindow.pushButton_31.clicked.connect(push_button_31_function)  # 计算K值
MainWindow.pushButton_27.clicked.connect(push_button_27_function)  # 设定目标流量

MainWindow.show()  # 显示主界面
sys.exit(app.exec_())  # 退出主界面
