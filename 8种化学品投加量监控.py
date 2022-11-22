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
import RS485  # 导入ＲＳ－４８５连接模块
import Mainwidow  # 导入主界面
import connect_dialog  # 导入通信设置子窗体
import messagebox_in_Chinese  # 导入提示信息框
import data_translation_modal  # 导入数据转换模块
import data_save  # 导入数据导出窗体
import data_save_function  # 导入数据导出处理函数
import data_drop  # 导入清理数据窗体
import data_drop_function  # 导入清理数据处理函数
import threading  # 导入多线程模块

if hasattr(sys, 'frozen'):
    os.environ['PATH'] = sys._MEIPASS + ";" + os.environ['PATH']  # 导入Qt5Core库
sys.setrecursionlimit(4000)  # set the maximum depth as 4000  修改最大归递次数

# TODO:1.1 全局变量
# TODO:1.全局变量/公用函数/初始化
Time_count = 0  # 定时器始值
frame_flash = 0  # frame闪烁
display_length = {'length': '5min',
                  '5min': 30,
                  '10min': 600,
                  '30min': 1800,
                  '1hour': 3600,
                  '4hour': 14400,
                  '8hour': 28800}

#  定义读取仪表后返回的显示数据
refresh_return_data = {'meter_1': {'flow_1': 0,  # 通道1流量
                                   'flow_2': 0,  # 通道2流量
                                   'total_1': 0,  # 通道1累积容积
                                   'total_2': 0,  # 通道2累积容积
                                   'high_flow_1': 0,  # 通道1流量高报警
                                   'high_flow_2': 0,  # 通道2流量高报警
                                   'low_flow_1': 0,  # 通道1流量低报警
                                   'low_flow_2': 0,  # 通道2流量低报警
                                   'meter_connection': 0,  # 仪表连接状态
                                   },
                       'meter_2': {'flow_1': 0,  # 通道1流量
                                   'flow_2': 0,  # 通道2流量
                                   'total_1': 0,  # 通道1累积容积
                                   'total_2': 0,  # 通道2累积容积
                                   'high_flow_1': 0,  # 通道1流量高报警
                                   'high_flow_2': 0,  # 通道2流量高报警
                                   'low_flow_1': 0,  # 通道1流量低报警
                                   'low_flow_2': 0,  # 通道2流量低报警
                                   'meter_connection': 0,  # 仪表连接状态
                                   },
                       'meter_3': {'flow_1': 0,  # 通道1流量
                                   'flow_2': 0,  # 通道2流量
                                   'total_1': 0,  # 通道1累积容积
                                   'total_2': 0,  # 通道2累积容积
                                   'high_flow_1': 0,  # 通道1流量高报警
                                   'high_flow_2': 0,  # 通道2流量高报警
                                   'low_flow_1': 0,  # 通道1流量低报警
                                   'low_flow_2': 0,  # 通道2流量低报警
                                   'meter_connection': 0,  # 仪表连接状态
                                   },
                       'meter_4': {'flow_1': 0,  # 通道1流量
                                   'flow_2': 0,  # 通道2流量
                                   'total_1': 0,  # 通道1累积容积
                                   'total_2': 0,  # 通道2累积容积
                                   'high_flow_1': 0,  # 通道1流量高报警
                                   'high_flow_2': 0,  # 通道2流量高报警
                                   'low_flow_1': 0,  # 通道1流量低报警
                                   'low_flow_2': 0,  # 通道2流量低报警
                                   'meter_connection': 0,  # 仪表连接状态
                                   },
                       }

# 定义水量报警数据结构
water_flow_data = {'meter_1': {'flow_1_high': 0,
                               'flow_1_low': 0,
                               'flow_2_high': 0,
                               'flow_2_low': 0,
                               },
                   'meter_2': {'flow_1_high': 0,
                               'flow_1_low': 0,
                               'flow_2_high': 0,
                               'flow_2_low': 0,
                               },
                   'meter_3': {'flow_1_high': 0,
                               'flow_1_low': 0,
                               'flow_2_high': 0,
                               'flow_2_low': 0,
                               },
                   'meter_4': {'flow_1_high': 0,
                               'flow_1_low': 0,
                               'flow_2_high': 0,
                               'flow_2_low': 0,
                               },
                   }


# TODO:1.2  公用函数
# 将Meter_data转换为导出配置记录的格式
def translate_meter_data_to_save_parlance(meter_data, meter_data_column):
    meter_setting = pd.DataFrame(meter_data, index=meter_data_column)
    meter_setting = meter_setting.T
    print(meter_setting)
    return meter_setting


# 保存运行数据
def save_data(log_data):
    dir_now = os.getcwd()  # 获取当前工作目录
    print(dir_now)
    export_file_name = dir_now + '\\' + 'meter_run_data.paddlerundata'
    print(export_file_name)
    log_data.to_csv(export_file_name, index=False, header=False, mode='a')


# TODO:1.3 初始化
# 设置matplotlib中文字体
mpl.rcParams['font.sans-serif'] = ['SimHei']  # 正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 正常显示负号
plt.rcParams['figure.facecolor'] = '#F0F0F0'  # 修改曲线背景颜色


# TODO:2.仪表类
class FlowMeter:
    def __init__(self):
        # TODO: 2.1定义主要数据属性
        self.Connect_status_meter = 0  # 仪表连接状态，0：断开;1：连接2代仪表;2：连接2代plus仪表;3：连接3代仪表
        self.Serial_ports = []  # 可用串口列表
        self.Modbus_parameter = {'PORT': '无串口!',  # 串口号
                                 'baudrate': 9600,  # 9600 波特率
                                 'bytesize': 8,  # 8 数据位
                                 'parity': 'N',  # 'N'  校验位
                                 'stopbits': 1,  # 1   停止位
                                 'address': 1,  # PLC站号
                                 }  # Modbus连接参数

        # TODO:2.2数据结构
        # 2代仪表的数据结构
        # 读
        self.Meter_data_column = ['DateTime',  # 当前时间
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
                                  '40051',
                                  # 'R', '平台域名', '第1个字符', '', '', ''], [None, None, None, '第2个字符', '', '', ''],
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
                                  '40064',
                                  # 'R', None, '第27个字符', '', '', ''], [None, None, None, '第28个字符', '', '', ''],
                                  '40065',
                                  # 'R', None, '第29个字符', '', '', ''], [None, None, None, '第30个字符', '', '', ''],
                                  '40066',  # 'R', 'Solenoid_Charge_Time', '1-499', '', '', '泵1'],
                                  '40067',  # 'R', 'Max_SPM', '0-999', '', '', '泵2'],
                                  '40068',  # 'R', 'Solenoid_Charge_Time', '1-499', '', '', '泵1'],
                                  '40069',  # 'R', 'Max_SPM', '0-999', '', '', '泵2'],
                                  'ModbusAddress',  # 当前设置modbus地址
                                  ]
        self.Meter_data = list(np.zeros(71).astype(int))
        # 写
        self.Meter_data_write_index = list(np.arange(60) + 41001)
        self.Meter_data_write_value = list(np.arange(60) + 1000)
        self.Meter_data_write = pd.Series(self.Meter_data_write_value, index=self.Meter_data_write_index)
        # 2代plus仪表数据结构
        # 读
        self.Meter_data_column_2_plus = list(np.arange(109) + 40001)
        # 未曾加水流量报警前
        # self.Meter_data_2_plus = list(np.zeros(111).astype(int))
        # 曾加水流量报警后
        self.Meter_data_2_plus = list(np.zeros(115).astype(int))
        # 写
        self.Meter_data_2_plus_write_index = list(np.arange(181) + 41001)
        self.Meter_data_2_plus_write_value = list(np.arange(181) + 1000)
        self.Meter_data_2_plus_write = pd.Series(self.Meter_data_2_plus_write_value,
                                                 index=self.Meter_data_2_plus_write_index)
        # 显示曲线初始化
        self.display_data_ch1 = {'x': list(np.zeros(28800)),
                                 'y': list(np.zeros(28800))}
        self.display_data_ch2 = {'x': list(np.zeros(28800)),
                                 'y': list(np.zeros(28800))}
        # TODO:2.3初始化函数
        # 标准2代仪表
        self.Meter_data[0] = datetime.datetime.now()  # 获取当前时间
        for item in range(len(self.Meter_data_write_index)):
            self.Meter_data_write_index[item] = str(self.Meter_data_write_index[item])
        # 2代plus仪表
        for i in range(len(self.Meter_data_column_2_plus)):
            self.Meter_data_column_2_plus[i] = str(self.Meter_data_column_2_plus[i])
        self.Meter_data_column_2_plus.insert(0, 'DateTime')
        self.Meter_data_column_2_plus.append('ModbusAddress')
        self.Meter_data_column_2_plus.append('water_flow_1_high')
        self.Meter_data_column_2_plus.append('water_flow_1_low')
        self.Meter_data_column_2_plus.append('water_flow_2_high')
        self.Meter_data_column_2_plus.append('water_flow_2_low')
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
# 定义4个仪表,仪表连接参数初始化
flow_meter_1 = FlowMeter()
flow_meter_1.Modbus_parameter['PORT'] = 'COM7'
flow_meter_1.Modbus_parameter['baudrate'] = 9600
flow_meter_1.Modbus_parameter['bytesize'] = 8
flow_meter_1.Modbus_parameter['parity'] = 'N'
flow_meter_1.Modbus_parameter['stopbits'] = 1
flow_meter_1.Modbus_parameter['address'] = 1
flow_meter_2 = FlowMeter()
flow_meter_2.Modbus_parameter['PORT'] = 'COM8'
flow_meter_2.Modbus_parameter['baudrate'] = 9600
flow_meter_2.Modbus_parameter['bytesize'] = 8
flow_meter_2.Modbus_parameter['parity'] = 'N'
flow_meter_2.Modbus_parameter['stopbits'] = 1
flow_meter_2.Modbus_parameter['address'] = 1
flow_meter_3 = FlowMeter()
flow_meter_3.Modbus_parameter['PORT'] = 'COM9'
flow_meter_3.Modbus_parameter['baudrate'] = 9600
flow_meter_3.Modbus_parameter['bytesize'] = 8
flow_meter_3.Modbus_parameter['parity'] = 'N'
flow_meter_3.Modbus_parameter['stopbits'] = 1
flow_meter_3.Modbus_parameter['address'] = 1
flow_meter_4 = FlowMeter()
flow_meter_4.Modbus_parameter['PORT'] = 'COM10'
flow_meter_4.Modbus_parameter['baudrate'] = 9600
flow_meter_4.Modbus_parameter['bytesize'] = 8
flow_meter_4.Modbus_parameter['parity'] = 'N'
flow_meter_4.Modbus_parameter['stopbits'] = 1
flow_meter_4.Modbus_parameter['address'] = 1

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
def refresh_parameter_for_1_meter(flowmeter):
    # 定义返回数据结构
    return_data = {'flow_1': 0,  # 通道1流量
                   'flow_2': 0,  # 通道2流量
                   'total_1': 0,  # 通道1累积容积
                   'total_2': 0,  # 通道2累积容积
                   'high_flow_1': 0,  # 通道1流量高报警
                   'high_flow_2': 0,  # 通道2流量高报警
                   'low_flow_1': 0,  # 通道1流量低报警
                   'low_flow_2': 0,  # 通道2流量低报警
                   'meter_connection': 0,  # 仪表连接状态
                   }
    # 刷新仪表数据结构中的数据
    if flowmeter.Connect_status_meter == 1:
        flowmeter.Meter_data[0] = datetime.datetime.now()
    elif flowmeter.Connect_status_meter == 2:
        flowmeter.Meter_data_2_plus[0] = datetime.datetime.now()

    # 读取仪表信息
    get_meter_data = RS485.modbus_read(flowmeter.Modbus_parameter['PORT'],  # 串口号
                                       flowmeter.Modbus_parameter['baudrate'],  # 波特率
                                       flowmeter.Modbus_parameter['bytesize'],  # 数据位
                                       flowmeter.Modbus_parameter['parity'],  # 校验位
                                       flowmeter.Modbus_parameter['stopbits'],  # 停止位
                                       flowmeter.Modbus_parameter['address'],  # 仪表从站站号
                                       0,  # 起始寄存器
                                       1,  # 读寄存器的数量
                                       )
    if (get_meter_data == []) or (get_meter_data[0] == -1):
        print('Can not connect meter.')
        flowmeter.Connect_status_meter = 0  # 连接modbus错误
        # flowmeter.modbus_parameter_reset()  # 复位modbus参数
    else:
        if get_meter_data[0] == 6:
            flowmeter.Connect_status_meter = 1
        elif get_meter_data[0] == 7:
            flowmeter.Connect_status_meter = 2
    if flowmeter.Connect_status_meter == 1:
        get_meter_data = RS485.modbus_read(flowmeter.Modbus_parameter['PORT'],  # 串口号
                                           flowmeter.Modbus_parameter['baudrate'],  # 波特率
                                           flowmeter.Modbus_parameter['bytesize'],  # 数据位
                                           flowmeter.Modbus_parameter['parity'],  # 校验位
                                           flowmeter.Modbus_parameter['stopbits'],  # 停止位
                                           flowmeter.Modbus_parameter['address'],  # 仪表从站站号
                                           0,  # 起始寄存器
                                           65,  # 读寄存器的数量
                                           )
    elif flowmeter.Connect_status_meter == 2:
        get_meter_data = RS485.modbus_read(flowmeter.Modbus_parameter['PORT'],  # 串口号
                                           flowmeter.Modbus_parameter['baudrate'],  # 波特率
                                           flowmeter.Modbus_parameter['bytesize'],  # 数据位
                                           flowmeter.Modbus_parameter['parity'],  # 校验位
                                           flowmeter.Modbus_parameter['stopbits'],  # 停止位
                                           flowmeter.Modbus_parameter['address'],  # 仪表从站站号
                                           0,  # 起始寄存器
                                           109,  # 读寄存器的数量
                                           )
    # 刷新仪表数据结构中的数据
    if flowmeter.Connect_status_meter == 1:
        for item in range(65):
            flowmeter.Meter_data[item + 1] = get_meter_data[item]

        # 保存运行记录
        save_run_data = translate_meter_data_to_save_parlance(flowmeter.Meter_data, flowmeter.Meter_data_column)
        save_data(save_run_data)

    elif flowmeter.Connect_status_meter == 2:
        for item in range(109):
            flowmeter.Meter_data_2_plus[item + 1] = get_meter_data[item]

        # 保存运行记录
        save_run_data = translate_meter_data_to_save_parlance(flowmeter.Meter_data_2_plus,
                                                              flowmeter.Meter_data_column_2_plus)
        save_data(save_run_data)

    # 更新当前modbus地址
    if flowmeter.Connect_status_meter == 1:
        flowmeter.Meter_data[70] = flowmeter.Modbus_parameter['address']
    elif flowmeter.Connect_status_meter == 2:
        flowmeter.Meter_data_2_plus[110] = flowmeter.Modbus_parameter['address']

    # 刷新流量
    if flowmeter.Connect_status_meter == 0:
        return_data['flow_1'] = 0
        return_data['flow_2'] = 0
    elif flowmeter.Connect_status_meter == 1:
        # 通道1
        return_data['flow_1'] = float(flowmeter.Meter_data[5]) + float(
            flowmeter.Meter_data[6] / 1000)  # 40005为通道1流量整数，40006为通道1流量小数
        # 通道2
        return_data['flow_2'] = float(flowmeter.Meter_data[7]) + float(
            flowmeter.Meter_data[8] / 1000)  # 40007为通道1流量整数，40008为通道1流量小数
    elif flowmeter.Connect_status_meter == 2:
        # 通道1
        return_data['flow_1'] = float(32768 * flowmeter.Meter_data_2_plus[5]) + \
                                float(flowmeter.Meter_data_2_plus[6] +
                                      float(flowmeter.Meter_data_2_plus[7]) / 1000)
        # 40005为通道1流量整数高位，40006为通道1流量整数,40007为通道1流量小数
        # 通道2
        return_data['flow_2'] = float(32768 * flowmeter.Meter_data_2_plus[8]) + \
                                float(flowmeter.Meter_data_2_plus[9] +
                                      float(flowmeter.Meter_data_2_plus[10]) / 1000)
        # 40008为通道1流量整数高位，40009为通道1流量整数,40010为通道1流量小数

    # 刷新累积容积
    if flowmeter.Connect_status_meter == 0:
        return_data['total_1'] = 0
        return_data['total_2'] = 0
    elif flowmeter.Connect_status_meter == 1:
        # 通道1
        return_data['total_1'] = float(flowmeter.Meter_data[9]) * 65536 + float(flowmeter.Meter_data[10]) + float(
            flowmeter.Meter_data[11]) / 10  # 40009整数高位，40010整数低位，40011小数
        return_data['total_1'] = return_data['total_1'] / 1000  # 单位转换为m3
        # 通道2
        return_data['total_2'] = float(flowmeter.Meter_data[12]) * 65536 + float(flowmeter.Meter_data[13]) + float(
            flowmeter.Meter_data[14]) / 10  # 40010整数高位，40011整数低位，40012小数
        return_data['total_2'] = return_data['total_2'] / 1000  # 单位转换为m3
    elif flowmeter.Connect_status_meter == 2:
        # 通道1
        return_data['total_1'] = float(flowmeter.Meter_data_2_plus[11]) * 32768 * 32768 * 32768 + \
                                 float(flowmeter.Meter_data_2_plus[12]) * 32768 * 32768 + \
                                 float(flowmeter.Meter_data_2_plus[13]) * 32768 + \
                                 float(flowmeter.Meter_data_2_plus[14]) + float(flowmeter.Meter_data_2_plus[15]) / 1000
        return_data['total_1'] = return_data['total_1'] / 1000  # 单位转换为m3
        # 通道2
        return_data['total_2'] = float(flowmeter.Meter_data_2_plus[16]) * 32768 * 32768 * 32768 + \
                                 float(flowmeter.Meter_data_2_plus[17]) * 32768 * 32768 + \
                                 float(flowmeter.Meter_data_2_plus[18]) * 32768 + \
                                 float(flowmeter.Meter_data_2_plus[19]) + float(flowmeter.Meter_data_2_plus[20]) / 1000
        return_data['total_2'] = return_data['total_2'] / 1000  # 单位转换为m3

    # 刷新报警 -- 0：正常；1：报警
    if flowmeter.Connect_status_meter == 0:
        # 仪表连接状态 -- -1:未连接； 0：已连接
        return_data['meter_connection'] = -1
    else:
        return_data['meter_connection'] = 0
        if flowmeter.Connect_status_meter == 1:
            flow_alarm = data_translation_modal.decimal_to_binary(flowmeter.Meter_data[15])  # 40015 标志状态寄存器
        elif flowmeter.Connect_status_meter == 2:
            flow_alarm = data_translation_modal.decimal_to_binary(flowmeter.Meter_data_2_plus[21])  # 40021 标志状态寄存器
        # # 通道1流量报警
        # # 过高
        return_data['high_flow_1'] = int(flow_alarm[-3])
        # 过低
        return_data['low_flow_1'] = int(flow_alarm[-4])
        # 通道2流量报警
        # # 过高
        return_data['high_flow_2'] = int(flow_alarm[-5])
        # 过低
        return_data['low_flow_2'] = int(flow_alarm[-6])
        del get_meter_data  # 删除创建的连接对象
    return return_data


#  更新所有仪表
def refresh_parameter_all():
    # 更新时间
    date_time = date_time_now_text(datetime.datetime.now())
    MainWindow.label_28.setText(date_time)
    # frame闪烁
    global frame_flash
    if frame_flash == 0:
        frame_flash = frame_flash + 1
    else:
        frame_flash = frame_flash - 1

    for i in range(28799):
        flow_meter_1.display_data_ch1['x'][i] = flow_meter_1.display_data_ch1['x'][i + 1]
        flow_meter_1.display_data_ch2['x'][i] = flow_meter_1.display_data_ch2['x'][i + 1]
        flow_meter_2.display_data_ch1['x'][i] = flow_meter_2.display_data_ch1['x'][i + 1]
        flow_meter_2.display_data_ch2['x'][i] = flow_meter_2.display_data_ch2['x'][i + 1]
        flow_meter_3.display_data_ch1['x'][i] = flow_meter_3.display_data_ch1['x'][i + 1]
        flow_meter_3.display_data_ch2['x'][i] = flow_meter_3.display_data_ch2['x'][i + 1]
        flow_meter_4.display_data_ch1['x'][i] = flow_meter_4.display_data_ch1['x'][i + 1]
        flow_meter_4.display_data_ch2['x'][i] = flow_meter_4.display_data_ch2['x'][i + 1]

    flow_meter_1.display_data_ch1['x'][28799] = time_now_text(datetime.datetime.now())
    flow_meter_1.display_data_ch2['x'][28799] = flow_meter_1.display_data_ch1['x'][28799]
    flow_meter_2.display_data_ch1['x'][28799] = flow_meter_1.display_data_ch1['x'][28799]
    flow_meter_2.display_data_ch2['x'][28799] = flow_meter_1.display_data_ch1['x'][28799]
    flow_meter_3.display_data_ch1['x'][28799] = flow_meter_1.display_data_ch1['x'][28799]
    flow_meter_3.display_data_ch2['x'][28799] = flow_meter_1.display_data_ch1['x'][28799]
    flow_meter_4.display_data_ch1['x'][28799] = flow_meter_1.display_data_ch1['x'][28799]
    flow_meter_4.display_data_ch2['x'][28799] = flow_meter_1.display_data_ch1['x'][28799]

    # 仪表1
    # 在界面显示
    MainWindow.lcdNumber_2.display(refresh_return_data['meter_1']['flow_1'])  # 流量1 L/h
    flow_ml_min_1 = refresh_return_data['meter_1']['flow_1'] * 1000 / 60  # 流量1 ml/min
    MainWindow.lcdNumber.display(flow_ml_min_1)  # 流量1 ml/min
    MainWindow.lcdNumber_19.display(refresh_return_data['meter_1']['flow_2'])  # 流量2 L/h
    flow_ml_min_2 = refresh_return_data['meter_1']['flow_2'] * 1000 / 60  # 流量2 ml/min
    MainWindow.lcdNumber_24.display(flow_ml_min_2)  # 流量2 ml/min
    MainWindow.lcdNumber_3.display(refresh_return_data['meter_1']['total_1'])  # 累积1 L
    MainWindow.lcdNumber_17.display(refresh_return_data['meter_1']['total_2'])  # 累积2 L
    # 更新曲线
    for i in range(28799):
        flow_meter_1.display_data_ch1['y'][i] = flow_meter_1.display_data_ch1['y'][i + 1]
        flow_meter_1.display_data_ch2['y'][i] = flow_meter_1.display_data_ch2['y'][i + 1]
    flow_meter_1.display_data_ch1['y'][28799] = flow_ml_min_1
    flow_meter_1.display_data_ch2['y'][28799] = flow_ml_min_2
    # 显示报警
    if refresh_return_data['meter_1']['meter_connection'] == -1:
        #     通道1流量报警
        #     过高
        MainWindow.label_20.setText("未连接")
        MainWindow.label_20.setStyleSheet("background-color: rgb(255, 255, 0);\n")
        # 过低
        MainWindow.label_19.setText("未连接")
        MainWindow.label_19.setStyleSheet("background-color: rgb(255, 255, 0);\n")
        # 通道2流量报警
        # 过高
        MainWindow.label_39.setText("未连接")
        MainWindow.label_39.setStyleSheet("background-color: rgb(255, 255, 0);\n")
        # 过低
        MainWindow.label_40.setText("未连接")
        MainWindow.label_40.setStyleSheet("background-color: rgb(255, 255, 0);\n")
    else:
        #     通道1流量报警
        #     过高
        if refresh_return_data['meter_1']['high_flow_1'] == 1:
            MainWindow.label_20.setText("报警")
            MainWindow.label_20.setStyleSheet("background-color: rgb(255, 0, 0);\n")
        else:
            MainWindow.label_20.setText("正常")
            MainWindow.label_20.setStyleSheet("background-color: rgb(240, 240, 240);\n")
        # 过低
        if refresh_return_data['meter_1']['low_flow_1'] == 1:
            MainWindow.label_19.setText("报警")
            MainWindow.label_19.setStyleSheet("background-color: rgb(255, 0, 0);\n")
        else:
            MainWindow.label_19.setText("正常")
            MainWindow.label_19.setStyleSheet("background-color: rgb(240, 240, 240);\n")
        if refresh_return_data['meter_1']['high_flow_1'] == 0 and refresh_return_data['meter_1']['low_flow_1'] == 0:
            MainWindow.frame.setStyleSheet('background-color: rgb(240, 240, 240);\n')
            MainWindow.textEdit.setStyleSheet('background-color: rgb(240, 240, 240);\n')
        else:
            if frame_flash == 0:
                MainWindow.frame.setStyleSheet('background-color: rgb(240, 240, 240);\n')
                MainWindow.textEdit.setStyleSheet('background-color: rgb(240, 240, 240);\n')
            else:
                MainWindow.frame.setStyleSheet('background-color: rgb(255, 255, 0);\n')
                MainWindow.textEdit.setStyleSheet('background-color: rgb(255, 255, 0);\n')
        # 通道2流量报警
        # 过高
        if refresh_return_data['meter_1']['high_flow_2'] == 1:
            MainWindow.label_39.setText("报警")
            MainWindow.label_39.setStyleSheet("background-color: rgb(255, 0, 0);\n")
        else:
            MainWindow.label_39.setText("正常")
            MainWindow.label_39.setStyleSheet("background-color: rgb(240, 240, 240);\n")
        # 过低
        if refresh_return_data['meter_1']['low_flow_2'] == 1:
            MainWindow.label_40.setText("报警")
            MainWindow.label_40.setStyleSheet("background-color: rgb(255, 0, 0);\n")
        else:
            MainWindow.label_40.setText("正常")
            MainWindow.label_40.setStyleSheet("background-color: rgb(240, 240, 240);\n")
        if refresh_return_data['meter_1']['high_flow_1'] == 0 and refresh_return_data['meter_1']['low_flow_1'] == 0:
            MainWindow.frame_8.setStyleSheet('background-color: rgb(240, 240, 240);\n')
            MainWindow.textEdit_2.setStyleSheet('background-color: rgb(240, 240, 240);\n')
        else:
            if frame_flash == 0:
                MainWindow.frame_8.setStyleSheet('background-color: rgb(240, 240, 240);\n')
                MainWindow.textEdit_2.setStyleSheet('background-color: rgb(240, 240, 240);\n')
            else:
                MainWindow.frame_8.setStyleSheet('background-color: rgb(255, 255, 0);\n')
                MainWindow.textEdit_2.setStyleSheet('background-color: rgb(255, 255, 0);\n')

    # 仪表2
    # 在界面显示
    MainWindow.lcdNumber_5.display(refresh_return_data['meter_2']['flow_1'])  # 流量1 L/h
    flow_ml_min_1 = refresh_return_data['meter_2']['flow_1'] * 1000 / 60  # 流量1 ml/min
    MainWindow.lcdNumber_6.display(flow_ml_min_1)  # 流量1 ml/min
    MainWindow.lcdNumber_15.display(refresh_return_data['meter_2']['flow_2'])  # 流量2 L/h
    flow_ml_min_2 = refresh_return_data['meter_2']['flow_2'] * 1000 / 60  # 流量2 ml/min
    MainWindow.lcdNumber_22.display(flow_ml_min_2)  # 流量2 ml/min
    MainWindow.lcdNumber_4.display(refresh_return_data['meter_2']['total_1'])  # 累积1 L
    MainWindow.lcdNumber_13.display(refresh_return_data['meter_2']['total_2'])  # 累积2 L
    # 更新曲线
    for i in range(28799):
        flow_meter_2.display_data_ch1['y'][i] = flow_meter_2.display_data_ch1['y'][i + 1]
        flow_meter_2.display_data_ch2['y'][i] = flow_meter_2.display_data_ch2['y'][i + 1]
    flow_meter_2.display_data_ch1['y'][28799] = flow_ml_min_1
    flow_meter_2.display_data_ch2['y'][28799] = flow_ml_min_2
    # 显示报警
    if refresh_return_data['meter_2']['meter_connection'] == -1:
        #     通道1流量报警
        #     过高
        MainWindow.label_21.setText("未连接")
        MainWindow.label_21.setStyleSheet("background-color: rgb(255, 255, 0);\n")
        # 过低
        MainWindow.label_22.setText("未连接")
        MainWindow.label_22.setStyleSheet("background-color: rgb(255, 255, 0);\n")
        # 通道2流量报警
        # 过高
        MainWindow.label_56.setText("未连接")
        MainWindow.label_56.setStyleSheet("background-color: rgb(255, 255, 0);\n")
        # 过低
        MainWindow.label_57.setText("未连接")
        MainWindow.label_57.setStyleSheet("background-color: rgb(255, 255, 0);\n")
    else:
        #     通道1流量报警
        #     过高
        if refresh_return_data['meter_2']['high_flow_1'] == 1:
            MainWindow.label_21.setText("报警")
            MainWindow.label_21.setStyleSheet("background-color: rgb(255, 0, 0);\n")
        else:
            MainWindow.label_21.setText("正常")
            MainWindow.label_21.setStyleSheet("background-color: rgb(240, 240, 240);\n")
        # 过低
        if refresh_return_data['meter_2']['low_flow_1'] == 1:
            MainWindow.label_22.setText("报警")
            MainWindow.label_22.setStyleSheet("background-color: rgb(255, 0, 0);\n")
        else:
            MainWindow.label_22.setText("正常")
            MainWindow.label_22.setStyleSheet("background-color: rgb(240, 240, 240);\n")
        if refresh_return_data['meter_2']['high_flow_1'] == 0 and refresh_return_data['meter_2']['low_flow_1'] == 0:
            MainWindow.frame_2.setStyleSheet('background-color: rgb(240, 240, 240);\n')
            MainWindow.textEdit_3.setStyleSheet('background-color: rgb(240, 240, 240);\n')
        else:
            if frame_flash == 0:
                MainWindow.frame_2.setStyleSheet('background-color: rgb(240, 240, 240);\n')
                MainWindow.textEdit_3.setStyleSheet('background-color: rgb(240, 240, 240);\n')
            else:
                MainWindow.frame_2.setStyleSheet('background-color: rgb(255, 255, 0);\n')
                MainWindow.textEdit_3.setStyleSheet('background-color: rgb(255, 255, 0);\n')
        # 通道2流量报警
        # 过高
        if refresh_return_data['meter_2']['high_flow_2'] == 1:
            MainWindow.label_56.setText("报警")
            MainWindow.label_56.setStyleSheet("background-color: rgb(255, 0, 0);\n")
        else:
            MainWindow.label_56.setText("正常")
            MainWindow.label_56.setStyleSheet("background-color: rgb(240, 240, 240);\n")
        # 过低
        if refresh_return_data['meter_2']['low_flow_2'] == 1:
            MainWindow.label_57.setText("报警")
            MainWindow.label_57.setStyleSheet("background-color: rgb(255, 0, 0);\n")
        else:
            MainWindow.label_57.setText("正常")
            MainWindow.label_57.setStyleSheet("background-color: rgb(240, 240, 240);\n")
        if refresh_return_data['meter_2']['high_flow_1'] == 0 and refresh_return_data['meter_2']['low_flow_1'] == 0:
            MainWindow.frame_6.setStyleSheet('background-color: rgb(240, 240, 240);\n')
            MainWindow.textEdit_4.setStyleSheet('background-color: rgb(240, 240, 240);\n')
        else:
            if frame_flash == 0:
                MainWindow.frame_6.setStyleSheet('background-color: rgb(240, 240, 240);\n')
                MainWindow.textEdit_4.setStyleSheet('background-color: rgb(240, 240, 240);\n')
            else:
                MainWindow.frame_6.setStyleSheet('background-color: rgb(255, 255, 0);\n')
                MainWindow.textEdit_4.setStyleSheet('background-color: rgb(255, 255, 0);\n')

    # 仪表3
    # 在界面显示
    MainWindow.lcdNumber_8.display(refresh_return_data['meter_3']['flow_1'])  # 流量1 L/h
    flow_ml_min_1 = refresh_return_data['meter_3']['flow_1'] * 1000 / 60  # 流量1 ml/min
    MainWindow.lcdNumber_9.display(flow_ml_min_1)  # 流量1 ml/min
    MainWindow.lcdNumber_20.display(refresh_return_data['meter_3']['flow_2'])  # 流量2 L/h
    flow_ml_min_2 = refresh_return_data['meter_3']['flow_2'] * 1000 / 60  # 流量2 ml/min
    MainWindow.lcdNumber_14.display(flow_ml_min_2)  # 流量2 ml/min
    MainWindow.lcdNumber_7.display(refresh_return_data['meter_3']['total_1'])  # 累积1 L
    MainWindow.lcdNumber_18.display(refresh_return_data['meter_3']['total_2'])  # 累积2 L
    # 更新曲线
    for i in range(28799):
        flow_meter_3.display_data_ch1['y'][i] = flow_meter_3.display_data_ch1['y'][i + 1]
        flow_meter_3.display_data_ch2['y'][i] = flow_meter_3.display_data_ch2['y'][i + 1]
    flow_meter_3.display_data_ch1['y'][28799] = flow_ml_min_1
    flow_meter_3.display_data_ch2['y'][28799] = flow_ml_min_2
    # 显示报警
    if refresh_return_data['meter_3']['meter_connection'] == -1:
        #     通道1流量报警
        #     过高
        MainWindow.label_25.setText("未连接")
        MainWindow.label_25.setStyleSheet("background-color: rgb(255, 255, 0);\n")
        # 过低
        MainWindow.label_26.setText("未连接")
        MainWindow.label_26.setStyleSheet("background-color: rgb(255, 255, 0);\n")
        # 通道2流量报警
        # 过高
        MainWindow.label_46.setText("未连接")
        MainWindow.label_46.setStyleSheet("background-color: rgb(255, 255, 0);\n")
        # 过低
        MainWindow.label_47.setText("未连接")
        MainWindow.label_47.setStyleSheet("background-color: rgb(255, 255, 0);\n")
    else:
        #     通道1流量报警
        #     过高
        if refresh_return_data['meter_3']['high_flow_1'] == 1:
            MainWindow.label_25.setText("报警")
            MainWindow.label_25.setStyleSheet("background-color: rgb(255, 0, 0);\n")
        else:
            MainWindow.label_25.setText("正常")
            MainWindow.label_25.setStyleSheet("background-color: rgb(240, 240, 240);\n")
        # 过低
        if refresh_return_data['meter_3']['low_flow_1'] == 1:
            MainWindow.label_26.setText("报警")
            MainWindow.label_26.setStyleSheet("background-color: rgb(255, 0, 0);\n")
        else:
            MainWindow.label_26.setText("正常")
            MainWindow.label_26.setStyleSheet("background-color: rgb(240, 240, 240);\n")
        if refresh_return_data['meter_3']['high_flow_1'] == 0 and refresh_return_data['meter_3']['low_flow_1'] == 0:
            MainWindow.frame_3.setStyleSheet('background-color: rgb(240, 240, 240);\n')
            MainWindow.textEdit_5.setStyleSheet('background-color: rgb(240, 240, 240);\n')
        else:
            if frame_flash == 0:
                MainWindow.frame_3.setStyleSheet('background-color: rgb(240, 240, 240);\n')
                MainWindow.textEdit_5.setStyleSheet('background-color: rgb(240, 240, 240);\n')
            else:
                MainWindow.frame_3.setStyleSheet('background-color: rgb(255, 255, 0);\n')
                MainWindow.textEdit_5.setStyleSheet('background-color: rgb(255, 255, 0);\n')
        # 通道2流量报警
        # 过高
        if refresh_return_data['meter_3']['high_flow_2'] == 1:
            MainWindow.label_46.setText("报警")
            MainWindow.label_46.setStyleSheet("background-color: rgb(255, 0, 0);\n")
        else:
            MainWindow.label_46.setText("正常")
            MainWindow.label_46.setStyleSheet("background-color: rgb(240, 240, 240);\n")
        # 过低
        if refresh_return_data['meter_3']['low_flow_2'] == 1:
            MainWindow.label_47.setText("报警")
            MainWindow.label_47.setStyleSheet("background-color: rgb(255, 0, 0);\n")
        else:
            MainWindow.label_47.setText("正常")
            MainWindow.label_47.setStyleSheet("background-color: rgb(240, 240, 240);\n")
        if refresh_return_data['meter_3']['high_flow_1'] == 0 and refresh_return_data['meter_3']['low_flow_1'] == 0:
            MainWindow.frame_5.setStyleSheet('background-color: rgb(240, 240, 240);\n')
            MainWindow.textEdit_8.setStyleSheet('background-color: rgb(240, 240, 240);\n')
        else:
            if frame_flash == 0:
                MainWindow.frame_5.setStyleSheet('background-color: rgb(240, 240, 240);\n')
                MainWindow.textEdit_8.setStyleSheet('background-color: rgb(240, 240, 240);\n')
            else:
                MainWindow.frame_5.setStyleSheet('background-color: rgb(255, 255, 0);\n')
                MainWindow.textEdit_8.setStyleSheet('background-color: rgb(255, 255, 0);\n')

    # 仪表4
    # 在界面显示
    MainWindow.lcdNumber_11.display(refresh_return_data['meter_4']['flow_1'])  # 流量1 L/h
    flow_ml_min_1 = refresh_return_data['meter_4']['flow_1'] * 1000 / 60  # 流量1 ml/min
    MainWindow.lcdNumber_12.display(flow_ml_min_1)  # 流量1 ml/min
    MainWindow.lcdNumber_16.display(refresh_return_data['meter_4']['flow_2'])  # 流量2 L/h
    flow_ml_min_2 = refresh_return_data['meter_4']['flow_2'] * 1000 / 60  # 流量2 ml/min
    MainWindow.lcdNumber_21.display(flow_ml_min_2)  # 流量2 ml/min
    MainWindow.lcdNumber_10.display(refresh_return_data['meter_4']['total_1'])  # 累积1 L
    MainWindow.lcdNumber_23.display(refresh_return_data['meter_4']['total_2'])  # 累积2 L
    # 更新曲线
    for i in range(28799):
        flow_meter_4.display_data_ch1['y'][i] = flow_meter_4.display_data_ch1['y'][i + 1]
        flow_meter_4.display_data_ch2['y'][i] = flow_meter_4.display_data_ch2['y'][i + 1]
    flow_meter_4.display_data_ch1['y'][28799] = flow_ml_min_1
    flow_meter_4.display_data_ch2['y'][28799] = flow_ml_min_2
    # 显示报警
    if refresh_return_data['meter_4']['meter_connection'] == -1:
        #     通道1流量报警
        #     过高
        MainWindow.label_35.setText("未连接")
        MainWindow.label_35.setStyleSheet("background-color: rgb(255, 255, 0);\n")
        # 过低
        MainWindow.label_36.setText("未连接")
        MainWindow.label_36.setStyleSheet("background-color: rgb(255, 255, 0);\n")
        # 通道2流量报警
        # 过高
        MainWindow.label_50.setText("未连接")
        MainWindow.label_50.setStyleSheet("background-color: rgb(255, 255, 0);\n")
        # 过低
        MainWindow.label_51.setText("未连接")
        MainWindow.label_51.setStyleSheet("background-color: rgb(255, 255, 0);\n")
    else:
        #     通道1流量报警
        #     过高
        if refresh_return_data['meter_4']['high_flow_1'] == 1:
            MainWindow.label_35.setText("报警")
            MainWindow.label_35.setStyleSheet("background-color: rgb(255, 0, 0);\n")
        else:
            MainWindow.label_35.setText("正常")
            MainWindow.label_35.setStyleSheet("background-color: rgb(240, 240, 240);\n")
        # 过低
        if refresh_return_data['meter_4']['low_flow_1'] == 1:
            MainWindow.label_36.setText("报警")
            MainWindow.label_36.setStyleSheet("background-color: rgb(255, 0, 0);\n")
        else:
            MainWindow.label_36.setText("正常")
            MainWindow.label_36.setStyleSheet("background-color: rgb(240, 240, 240);\n")
        if refresh_return_data['meter_4']['high_flow_1'] == 0 and refresh_return_data['meter_4']['low_flow_1'] == 0:
            MainWindow.frame_4.setStyleSheet('background-color: rgb(240, 240, 240);\n')
            MainWindow.textEdit_6.setStyleSheet('background-color: rgb(240, 240, 240);\n')
        else:
            if frame_flash == 0:
                MainWindow.frame_4.setStyleSheet('background-color: rgb(240, 240, 240);\n')
                MainWindow.textEdit_6.setStyleSheet('background-color: rgb(240, 240, 240);\n')
            else:
                MainWindow.frame_4.setStyleSheet('background-color: rgb(255, 255, 0);\n')
                MainWindow.textEdit_6.setStyleSheet('background-color: rgb(255, 255, 0);\n')
        # 通道2流量报警
        # 过高
        if refresh_return_data['meter_4']['high_flow_2'] == 1:
            MainWindow.label_50.setText("报警")
            MainWindow.label_50.setStyleSheet("background-color: rgb(255, 0, 0);\n")
        else:
            MainWindow.label_50.setText("正常")
            MainWindow.label_50.setStyleSheet("background-color: rgb(240, 240, 240);\n")
        # 过低
        if refresh_return_data['meter_4']['low_flow_2'] == 1:
            MainWindow.label_51.setText("报警")
            MainWindow.label_51.setStyleSheet("background-color: rgb(255, 0, 0);\n")
        else:
            MainWindow.label_51.setText("正常")
            MainWindow.label_51.setStyleSheet("background-color: rgb(240, 240, 240);\n")
        if refresh_return_data['meter_4']['high_flow_1'] == 0 and refresh_return_data['meter_4']['low_flow_1'] == 0:
            MainWindow.frame_7.setStyleSheet('background-color: rgb(240, 240, 240);\n')
            MainWindow.textEdit_7.setStyleSheet('background-color: rgb(240, 240, 240);\n')
        else:
            if frame_flash == 0:
                MainWindow.frame_7.setStyleSheet('background-color: rgb(240, 240, 240);\n')
                MainWindow.textEdit_7.setStyleSheet('background-color: rgb(240, 240, 240);\n')
            else:
                MainWindow.frame_7.setStyleSheet('background-color: rgb(255, 255, 0);\n')
                MainWindow.textEdit_7.setStyleSheet('background-color: rgb(255, 255, 0);\n')

    # 水量报警
    # 仪表1
    # 通道1
    # 过高
    if water_flow_data['meter_1']['flow_1_high'] == 1:
        MainWindow.label_78.setText("水量高")
        MainWindow.label_78.setStyleSheet("background-color: rgb(255, 0, 0);\n")
    else:
        MainWindow.label_78.setText("")
        MainWindow.label_78.setStyleSheet("background-color: rgb(240, 240, 240);\n")
    # 过低
    if water_flow_data['meter_1']['flow_1_low'] == 1:
        MainWindow.label_79.setText("水量低")
        MainWindow.label_79.setStyleSheet("background-color: rgb(255, 0, 0);\n")
    else:
        MainWindow.label_79.setText("")
        MainWindow.label_79.setStyleSheet("background-color: rgb(240, 240, 240);\n")
    # 通道2
    # 过高
    if water_flow_data['meter_1']['flow_2_high'] == 1:
        MainWindow.label_81.setText("水量高")
        MainWindow.label_81.setStyleSheet("background-color: rgb(255, 0, 0);\n")
    else:
        MainWindow.label_81.setText("")
        MainWindow.label_81.setStyleSheet("background-color: rgb(240, 240, 240);\n")
    # 过低
    if water_flow_data['meter_1']['flow_2_low'] == 1:
        MainWindow.label_80.setText("水量低")
        MainWindow.label_80.setStyleSheet("background-color: rgb(255, 0, 0);\n")
    else:
        MainWindow.label_80.setText("")
        MainWindow.label_80.setStyleSheet("background-color: rgb(240, 240, 240);\n")
    # 仪表2
    # 通道1
    # 过高
    if water_flow_data['meter_2']['flow_1_high'] == 1:
        MainWindow.label_83.setText("水量高")
        MainWindow.label_83.setStyleSheet("background-color: rgb(255, 0, 0);\n")
    else:
        MainWindow.label_83.setText("")
        MainWindow.label_83.setStyleSheet("background-color: rgb(240, 240, 240);\n")
    # 过低
    if water_flow_data['meter_2']['flow_1_low'] == 1:
        MainWindow.label_82.setText("水量低")
        MainWindow.label_82.setStyleSheet("background-color: rgb(255, 0, 0);\n")
    else:
        MainWindow.label_82.setText("")
        MainWindow.label_82.setStyleSheet("background-color: rgb(240, 240, 240);\n")
    # 通道2
    # 过高
    if water_flow_data['meter_2']['flow_2_high'] == 1:
        MainWindow.label_85.setText("水量高")
        MainWindow.label_85.setStyleSheet("background-color: rgb(255, 0, 0);\n")
    else:
        MainWindow.label_85.setText("")
        MainWindow.label_85.setStyleSheet("background-color: rgb(240, 240, 240);\n")
    # 过低
    if water_flow_data['meter_2']['flow_2_low'] == 1:
        MainWindow.label_84.setText("水量低")
        MainWindow.label_84.setStyleSheet("background-color: rgb(255, 0, 0);\n")
    else:
        MainWindow.label_84.setText("")
        MainWindow.label_84.setStyleSheet("background-color: rgb(240, 240, 240);\n")
    # 仪表3
    # 通道1
    # 过高
    if water_flow_data['meter_3']['flow_1_high'] == 1:
        MainWindow.label_87.setText("水量高")
        MainWindow.label_87.setStyleSheet("background-color: rgb(255, 0, 0);\n")
    else:
        MainWindow.label_87.setText("")
        MainWindow.label_87.setStyleSheet("background-color: rgb(240, 240, 240);\n")
    # 过低
    if water_flow_data['meter_3']['flow_1_low'] == 1:
        MainWindow.label_86.setText("水量低")
        MainWindow.label_86.setStyleSheet("background-color: rgb(255, 0, 0);\n")
    else:
        MainWindow.label_86.setText("")
        MainWindow.label_86.setStyleSheet("background-color: rgb(240, 240, 240);\n")
    # 通道2
    # 过高
    if water_flow_data['meter_3']['flow_2_high'] == 1:
        MainWindow.label_89.setText("水量高")
        MainWindow.label_89.setStyleSheet("background-color: rgb(255, 0, 0);\n")
    else:
        MainWindow.label_89.setText("")
        MainWindow.label_89.setStyleSheet("background-color: rgb(240, 240, 240);\n")
    # 过低
    if water_flow_data['meter_3']['flow_2_low'] == 1:
        MainWindow.label_88.setText("水量低")
        MainWindow.label_88.setStyleSheet("background-color: rgb(255, 0, 0);\n")
    else:
        MainWindow.label_88.setText("")
        MainWindow.label_88.setStyleSheet("background-color: rgb(240, 240, 240);\n")
    # 仪表4
    # 通道1
    # 过高
    if water_flow_data['meter_4']['flow_1_high'] == 1:
        MainWindow.label_91.setText("水量高")
        MainWindow.label_91.setStyleSheet("background-color: rgb(255, 0, 0);\n")
    else:
        MainWindow.label_91.setText("")
        MainWindow.label_91.setStyleSheet("background-color: rgb(240, 240, 240);\n")
    # 过低
    if water_flow_data['meter_4']['flow_1_low'] == 1:
        MainWindow.label_90.setText("水量低")
        MainWindow.label_90.setStyleSheet("background-color: rgb(255, 0, 0);\n")
    else:
        MainWindow.label_90.setText("")
        MainWindow.label_90.setStyleSheet("background-color: rgb(240, 240, 240);\n")
    # 通道2
    # 过高
    if water_flow_data['meter_4']['flow_2_high'] == 1:
        MainWindow.label_93.setText("水量高")
        MainWindow.label_93.setStyleSheet("background-color: rgb(255, 0, 0);\n")
    else:
        MainWindow.label_93.setText("")
        MainWindow.label_93.setStyleSheet("background-color: rgb(240, 240, 240);\n")
    # 过低
    if water_flow_data['meter_4']['flow_2_low'] == 1:
        MainWindow.label_92.setText("水量低")
        MainWindow.label_92.setStyleSheet("background-color: rgb(255, 0, 0);\n")
    else:
        MainWindow.label_92.setText("")
        MainWindow.label_92.setStyleSheet("background-color: rgb(240, 240, 240);\n")

    # 更新 曲线
    Plot_meter_data.update_figure()


# 更新水流量
def refresh_water_flow(in_flow_meter_1, in_flow_meter_2, in_flow_meter_3, in_flow_meter_4):
    get_boolean_data = RS485.modbus_read_boolean_data('COM7', 9600, 8, 'N', 1, 2, 0, 16)
    if (get_boolean_data == []) or (get_boolean_data[0] == -1):
        print('water_flow_not_connect')
    else:
        print('get_data=' + str(get_boolean_data))
        # water_flow_data['meter_1']['flow_1_high'] = int(not int(get_boolean_data[0]))
        # water_flow_data['meter_1']['flow_1_low'] = int(get_boolean_data[1])
        # water_flow_data['meter_1']['flow_2_high'] = int(not int(get_boolean_data[2]))
        # water_flow_data['meter_1']['flow_2_low'] = int(get_boolean_data[3])
        water_flow_data['meter_1']['flow_1_high'] = 0
        water_flow_data['meter_1']['flow_1_low'] = 0
        water_flow_data['meter_1']['flow_2_high'] = 0
        water_flow_data['meter_1']['flow_2_low'] = 0
        water_flow_data['meter_2']['flow_1_high'] = int(not int(get_boolean_data[4]))
        water_flow_data['meter_2']['flow_1_low'] = int(get_boolean_data[5])
        water_flow_data['meter_2']['flow_2_high'] = int(not int(get_boolean_data[6]))
        water_flow_data['meter_2']['flow_2_low'] = int(get_boolean_data[7])
        water_flow_data['meter_3']['flow_1_high'] = int(not int(get_boolean_data[8]))
        water_flow_data['meter_3']['flow_1_low'] = int(get_boolean_data[9])
        water_flow_data['meter_3']['flow_2_high'] = int(not int(get_boolean_data[10]))
        water_flow_data['meter_3']['flow_2_low'] = int(get_boolean_data[11])
        water_flow_data['meter_4']['flow_1_high'] = int(not int(get_boolean_data[12]))
        water_flow_data['meter_4']['flow_1_low'] = int(get_boolean_data[13])
        water_flow_data['meter_4']['flow_2_high'] = int(not int(get_boolean_data[14]))
        water_flow_data['meter_4']['flow_2_low'] = int(get_boolean_data[15])
        in_flow_meter_1.Meter_data_2_plus[111] = water_flow_data['meter_1']['flow_1_high']
        in_flow_meter_1.Meter_data_2_plus[112] = water_flow_data['meter_1']['flow_1_low']
        in_flow_meter_1.Meter_data_2_plus[113] = water_flow_data['meter_1']['flow_2_high']
        in_flow_meter_1.Meter_data_2_plus[114] = water_flow_data['meter_1']['flow_2_low']
        in_flow_meter_2.Meter_data_2_plus[111] = water_flow_data['meter_2']['flow_1_high']
        in_flow_meter_2.Meter_data_2_plus[112] = water_flow_data['meter_2']['flow_1_low']
        in_flow_meter_2.Meter_data_2_plus[113] = water_flow_data['meter_2']['flow_2_high']
        in_flow_meter_2.Meter_data_2_plus[114] = water_flow_data['meter_2']['flow_2_low']
        in_flow_meter_3.Meter_data_2_plus[111] = water_flow_data['meter_3']['flow_1_high']
        in_flow_meter_3.Meter_data_2_plus[112] = water_flow_data['meter_3']['flow_1_low']
        in_flow_meter_3.Meter_data_2_plus[113] = water_flow_data['meter_3']['flow_2_high']
        in_flow_meter_3.Meter_data_2_plus[114] = water_flow_data['meter_3']['flow_2_low']
        in_flow_meter_4.Meter_data_2_plus[111] = water_flow_data['meter_4']['flow_1_high']
        in_flow_meter_4.Meter_data_2_plus[112] = water_flow_data['meter_4']['flow_1_low']
        in_flow_meter_4.Meter_data_2_plus[113] = water_flow_data['meter_4']['flow_2_high']
        in_flow_meter_4.Meter_data_2_plus[114] = water_flow_data['meter_4']['flow_2_low']
    return [get_boolean_data, in_flow_meter_1, in_flow_meter_2, in_flow_meter_3, in_flow_meter_4]


#  定时连接RS-485函数
def refresh_rs485_connect():
    refresh_water_flow(flow_meter_1, flow_meter_2, flow_meter_3, flow_meter_4)
    print(water_flow_data)
    refresh_return_data['meter_1'] = refresh_parameter_for_1_meter(flow_meter_1)
    refresh_return_data['meter_2'] = refresh_parameter_for_1_meter(flow_meter_2)
    refresh_return_data['meter_3'] = refresh_parameter_for_1_meter(flow_meter_3)
    refresh_return_data['meter_4'] = refresh_parameter_for_1_meter(flow_meter_4)
    print(refresh_return_data)
    # 更新水流量
    rs485_connect_refresh = threading.Timer(0.5, refresh_rs485_connect)  # 初始化threading定时器
    # 主进程存活时继续运行，主进程停止时停止
    if threading.main_thread().is_alive():
        rs485_connect_refresh.start()  # 启动threading定时器


#  定时更新界面
MainWindow.timer = QTimer()  # 初始化定时器
MainWindow.timer.timeout.connect(refresh_parameter_all)  # 定时操作
MainWindow.timer.start(1000)  # 每秒刷新1次

#  定时连接RS-485
rs485_connect_refresh = threading.Timer(0.5, refresh_rs485_connect)  # 初始化threading定时器
rs485_connect_refresh.start()  # 启动threading定时器


# TODO:3.1.2 运行曲线界面-类
class PlotCanvas(FigureCanvas):

    def __init__(self, parent=None, width=14, height=10, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        fig.subplots_adjust(left=0.07, right=0.95, top=0.95, bottom=0.07)  # 调整图像占画布大小
        self.axes = fig.add_subplot(111)
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self,
                                   QSizePolicy.Expanding,
                                   QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        self.init_plot()  # 打开App时可以初始化图片
        # self.plot()

    def init_plot(self):
        self.axes.plot(flow_meter_1.display_data_ch1['x'], flow_meter_1.display_data_ch1['y'])
        self.axes.plot(flow_meter_1.display_data_ch2['x'], flow_meter_1.display_data_ch2['y'])
        self.axes.plot(flow_meter_2.display_data_ch1['x'], flow_meter_2.display_data_ch1['y'])
        self.axes.plot(flow_meter_2.display_data_ch2['x'], flow_meter_2.display_data_ch2['y'])
        self.axes.plot(flow_meter_3.display_data_ch1['x'], flow_meter_3.display_data_ch1['y'])
        self.axes.plot(flow_meter_3.display_data_ch2['x'], flow_meter_3.display_data_ch2['y'])
        self.axes.plot(flow_meter_4.display_data_ch1['x'], flow_meter_4.display_data_ch1['y'])
        self.axes.plot(flow_meter_4.display_data_ch2['x'], flow_meter_4.display_data_ch2['y'])
        self.axes.set_ylabel('ml/min')
        self.axes.set_title('化学品投加瞬时流量曲线')

    def update_figure(self):
        # for i in range(3600):
        #     test_data['y'][i] = test_data['y'][i + 1]
        self.axes.cla()
        # self.axes.set_ylim(0, 100)
        if display_length['length'] == '5min':
            meter_1_ch1_display_x = flow_meter_1.display_data_ch1['x'][-300:]
            meter_1_ch1_display_y = flow_meter_1.display_data_ch1['y'][-300:]
            meter_1_ch2_display_x = flow_meter_1.display_data_ch2['x'][-300:]
            meter_1_ch2_display_y = flow_meter_1.display_data_ch2['y'][-300:]
            meter_2_ch1_display_x = flow_meter_2.display_data_ch1['x'][-300:]
            meter_2_ch1_display_y = flow_meter_2.display_data_ch1['y'][-300:]
            meter_2_ch2_display_x = flow_meter_2.display_data_ch2['x'][-300:]
            meter_2_ch2_display_y = flow_meter_2.display_data_ch2['y'][-300:]
            meter_3_ch1_display_x = flow_meter_3.display_data_ch1['x'][-300:]
            meter_3_ch1_display_y = flow_meter_3.display_data_ch1['y'][-300:]
            meter_3_ch2_display_x = flow_meter_3.display_data_ch2['x'][-300:]
            meter_3_ch2_display_y = flow_meter_3.display_data_ch2['y'][-300:]
            meter_4_ch1_display_x = flow_meter_4.display_data_ch1['x'][-300:]
            meter_4_ch1_display_y = flow_meter_4.display_data_ch1['y'][-300:]
            meter_4_ch2_display_x = flow_meter_4.display_data_ch2['x'][-300:]
            meter_4_ch2_display_y = flow_meter_4.display_data_ch2['y'][-300:]
        elif display_length['length'] == '10min':
            meter_1_ch1_display_x = flow_meter_1.display_data_ch1['x'][-600:]
            meter_1_ch1_display_y = flow_meter_1.display_data_ch1['y'][-600:]
            meter_1_ch2_display_x = flow_meter_1.display_data_ch2['x'][-600:]
            meter_1_ch2_display_y = flow_meter_1.display_data_ch2['y'][-600:]
            meter_2_ch1_display_x = flow_meter_2.display_data_ch1['x'][-600:]
            meter_2_ch1_display_y = flow_meter_2.display_data_ch1['y'][-600:]
            meter_2_ch2_display_x = flow_meter_2.display_data_ch2['x'][-600:]
            meter_2_ch2_display_y = flow_meter_2.display_data_ch2['y'][-600:]
            meter_3_ch1_display_x = flow_meter_3.display_data_ch1['x'][-600:]
            meter_3_ch1_display_y = flow_meter_3.display_data_ch1['y'][-600:]
            meter_3_ch2_display_x = flow_meter_3.display_data_ch2['x'][-600:]
            meter_3_ch2_display_y = flow_meter_3.display_data_ch2['y'][-600:]
            meter_4_ch1_display_x = flow_meter_4.display_data_ch1['x'][-600:]
            meter_4_ch1_display_y = flow_meter_4.display_data_ch1['y'][-600:]
            meter_4_ch2_display_x = flow_meter_4.display_data_ch2['x'][-600:]
            meter_4_ch2_display_y = flow_meter_4.display_data_ch2['y'][-600:]
        elif display_length['length'] == '30min':
            meter_1_ch1_display_x = flow_meter_1.display_data_ch1['x'][-1800:]
            meter_1_ch1_display_y = flow_meter_1.display_data_ch1['y'][-1800:]
            meter_1_ch2_display_x = flow_meter_1.display_data_ch2['x'][-1800:]
            meter_1_ch2_display_y = flow_meter_1.display_data_ch2['y'][-1800:]
            meter_2_ch1_display_x = flow_meter_2.display_data_ch1['x'][-1800:]
            meter_2_ch1_display_y = flow_meter_2.display_data_ch1['y'][-1800:]
            meter_2_ch2_display_x = flow_meter_2.display_data_ch2['x'][-1800:]
            meter_2_ch2_display_y = flow_meter_2.display_data_ch2['y'][-1800:]
            meter_3_ch1_display_x = flow_meter_3.display_data_ch1['x'][-1800:]
            meter_3_ch1_display_y = flow_meter_3.display_data_ch1['y'][-1800:]
            meter_3_ch2_display_x = flow_meter_3.display_data_ch2['x'][-1800:]
            meter_3_ch2_display_y = flow_meter_3.display_data_ch2['y'][-1800:]
            meter_4_ch1_display_x = flow_meter_4.display_data_ch1['x'][-1800:]
            meter_4_ch1_display_y = flow_meter_4.display_data_ch1['y'][-1800:]
            meter_4_ch2_display_x = flow_meter_4.display_data_ch2['x'][-1800:]
            meter_4_ch2_display_y = flow_meter_4.display_data_ch2['y'][-1800:]
        elif display_length['length'] == '1hour':
            meter_1_ch1_display_x = flow_meter_1.display_data_ch1['x'][-3600:]
            meter_1_ch1_display_y = flow_meter_1.display_data_ch1['y'][-3600:]
            meter_1_ch2_display_x = flow_meter_1.display_data_ch2['x'][-3600:]
            meter_1_ch2_display_y = flow_meter_1.display_data_ch2['y'][-3600:]
            meter_2_ch1_display_x = flow_meter_2.display_data_ch1['x'][-3600:]
            meter_2_ch1_display_y = flow_meter_2.display_data_ch1['y'][-3600:]
            meter_2_ch2_display_x = flow_meter_2.display_data_ch2['x'][-3600:]
            meter_2_ch2_display_y = flow_meter_2.display_data_ch2['y'][-3600:]
            meter_3_ch1_display_x = flow_meter_3.display_data_ch1['x'][-3600:]
            meter_3_ch1_display_y = flow_meter_3.display_data_ch1['y'][-3600:]
            meter_3_ch2_display_x = flow_meter_3.display_data_ch2['x'][-3600:]
            meter_3_ch2_display_y = flow_meter_3.display_data_ch2['y'][-3600:]
            meter_4_ch1_display_x = flow_meter_4.display_data_ch1['x'][-3600:]
            meter_4_ch1_display_y = flow_meter_4.display_data_ch1['y'][-3600:]
            meter_4_ch2_display_x = flow_meter_4.display_data_ch2['x'][-3600:]
            meter_4_ch2_display_y = flow_meter_4.display_data_ch2['y'][-3600:]
        elif display_length['length'] == '4hour':
            meter_1_ch1_display_x = flow_meter_1.display_data_ch1['x'][-14400:]
            meter_1_ch1_display_y = flow_meter_1.display_data_ch1['y'][-14400:]
            meter_1_ch2_display_x = flow_meter_1.display_data_ch2['x'][-14400:]
            meter_1_ch2_display_y = flow_meter_1.display_data_ch2['y'][-14400:]
            meter_2_ch1_display_x = flow_meter_2.display_data_ch1['x'][-14400:]
            meter_2_ch1_display_y = flow_meter_2.display_data_ch1['y'][-14400:]
            meter_2_ch2_display_x = flow_meter_2.display_data_ch2['x'][-14400:]
            meter_2_ch2_display_y = flow_meter_2.display_data_ch2['y'][-14400:]
            meter_3_ch1_display_x = flow_meter_3.display_data_ch1['x'][-14400:]
            meter_3_ch1_display_y = flow_meter_3.display_data_ch1['y'][-14400:]
            meter_3_ch2_display_x = flow_meter_3.display_data_ch2['x'][-14400:]
            meter_3_ch2_display_y = flow_meter_3.display_data_ch2['y'][-14400:]
            meter_4_ch1_display_x = flow_meter_4.display_data_ch1['x'][-14400:]
            meter_4_ch1_display_y = flow_meter_4.display_data_ch1['y'][-14400:]
            meter_4_ch2_display_x = flow_meter_4.display_data_ch2['x'][-14400:]
            meter_4_ch2_display_y = flow_meter_4.display_data_ch2['y'][-14400:]
        elif display_length['length'] == '8hour':
            meter_1_ch1_display_x = flow_meter_1.display_data_ch1['x'][-28800:]
            meter_1_ch1_display_y = flow_meter_1.display_data_ch1['y'][-28800:]
            meter_1_ch2_display_x = flow_meter_1.display_data_ch2['x'][-28800:]
            meter_1_ch2_display_y = flow_meter_1.display_data_ch2['y'][-28800:]
            meter_2_ch1_display_x = flow_meter_2.display_data_ch1['x'][-28800:]
            meter_2_ch1_display_y = flow_meter_2.display_data_ch1['y'][-28800:]
            meter_2_ch2_display_x = flow_meter_2.display_data_ch2['x'][-28800:]
            meter_2_ch2_display_y = flow_meter_2.display_data_ch2['y'][-28800:]
            meter_3_ch1_display_x = flow_meter_3.display_data_ch1['x'][-28800:]
            meter_3_ch1_display_y = flow_meter_3.display_data_ch1['y'][-28800:]
            meter_3_ch2_display_x = flow_meter_3.display_data_ch2['x'][-28800:]
            meter_3_ch2_display_y = flow_meter_3.display_data_ch2['y'][-28800:]
            meter_4_ch1_display_x = flow_meter_4.display_data_ch1['x'][-28800:]
            meter_4_ch1_display_y = flow_meter_4.display_data_ch1['y'][-28800:]
            meter_4_ch2_display_x = flow_meter_4.display_data_ch2['x'][-28800:]
            meter_4_ch2_display_y = flow_meter_4.display_data_ch2['y'][-28800:]

        self.axes.plot(meter_1_ch1_display_x, meter_1_ch1_display_y, label='未确定')
        self.axes.plot(meter_1_ch2_display_x, meter_1_ch2_display_y, label='未确定')
        self.axes.plot(meter_2_ch1_display_x, meter_2_ch1_display_y, label='芬齐敏化液')
        self.axes.plot(meter_2_ch2_display_x, meter_2_ch2_display_y, label='氯化钯')
        self.axes.plot(meter_3_ch1_display_x, meter_3_ch1_display_y, label='硝酸银')
        self.axes.plot(meter_3_ch2_display_x, meter_3_ch2_display_y, label='芬齐还原剂')
        self.axes.plot(meter_4_ch1_display_x, meter_4_ch1_display_y, label='钝化剂A')
        self.axes.plot(meter_4_ch2_display_x, meter_4_ch2_display_y, label='钝化剂B')
        self.axes.legend()
        self.axes.set_ylabel('ml/min')
        if display_length['length'] == '5min':
            self.axes.xaxis.set_major_locator(ticker.MultipleLocator(30))
            self.axes.xaxis.set_minor_locator(ticker.MultipleLocator(6))
        elif display_length['length'] == '10min':
            self.axes.xaxis.set_major_locator(ticker.MultipleLocator(60))
            self.axes.xaxis.set_minor_locator(ticker.MultipleLocator(12))
        elif display_length['length'] == '30min':
            self.axes.xaxis.set_major_locator(ticker.MultipleLocator(180))
            self.axes.xaxis.set_minor_locator(ticker.MultipleLocator(36))
        elif display_length['length'] == '1hour':
            self.axes.xaxis.set_major_locator(ticker.MultipleLocator(360))
            self.axes.xaxis.set_minor_locator(ticker.MultipleLocator(72))
        elif display_length['length'] == '4hour':
            self.axes.xaxis.set_major_locator(ticker.MultipleLocator(1440))
            self.axes.xaxis.set_minor_locator(ticker.MultipleLocator(288))
        elif display_length['length'] == '8hour':
            self.axes.xaxis.set_major_locator(ticker.MultipleLocator(2880))
            self.axes.xaxis.set_minor_locator(ticker.MultipleLocator(576))
        self.axes.yaxis.grid(True)
        self.axes.xaxis.grid(True)
        self.axes.set_title('化学品投加瞬时流量曲线')
        self.draw()


# TODO:3.1.3 运行曲线界面-定义
Plot_meter_data = PlotCanvas(MainWindow)
Plot_meter_data.move(500, 25)


# TODO:3.2 连接仪表界面
# TODO:3.2.1 连接仪表公共函数


# TODO:3.2.2 连接仪表-类
class MeterConnect(connect_dialog.Ui_Dialog):
    def __init__(self, flow_meter):
        connect_dialog.Ui_Dialog.__init__(self)
        self.Serial_ports = RS485.Search_Serial()
        self.flow_meter = flow_meter

    # TODO:3.2.2.1 RS-485连接  搜索可用串口
    def search_serial(self):
        self.Serial_ports = RS485.Search_Serial()
        self.comboBox.clear()
        self.comboBox.addItems(self.Serial_ports)

    # TODO:3.2.2.2 打开各个子窗体的方法
    # 定义打开“通信设置”子窗体方法
    def show_connect(self):
        self.show()  # 显示"通信设置"子窗体
        self.connect_config_modbus_option()  # 初始化modbus参数选项
        self.pushButton.clicked.connect(self.search_serial)  # 初始化搜索串口按钮动作
        self.pushButton_2.clicked.connect(self.try_connect_meter)  # 初始化仪表连接按钮动作

    # TODO:3.2.2.3 设置modbus参数选项
    # 连接仪表-通信设置菜单设置Modbus参数
    def connect_config_modbus_option(self):
        self.comboBox.addItems(['无串口!'])  # 可用串口
        self.comboBox_2.addItems(
            ['9600', '4800', '2400', '19200', '38400', '43000', '56000', '57600', '115200', '128000'])  # 波特率
        self.comboBox_3.addItems(['8', '5', '6', '7'])  # 数据位
        self.comboBox_4.addItems(['N', 'O', 'E', 'M', 'S'])  # 校验位
        self.comboBox_5.addItems(['1', '1.5', '2'])  # 停止位
        self.comboBox_6.addItems(['1', '2', '3', '4', '5', '6', '7', '8', '9', '10'])  # 仪表从站站号

    # TODO:3.2.2.4   连接仪表函数
    def try_connect_meter(self):
        self.flow_meter.Connect_status_meter = 1
        port_current = self.comboBox.currentText().split()
        self.flow_meter.Modbus_parameter['PORT'] = port_current[0]  # 串口号
        self.flow_meter.Modbus_parameter['baudrate'] = int(self.comboBox_2.currentText())  # 波特率
        self.flow_meter.Modbus_parameter['bytesize'] = int(self.comboBox_3.currentText())  # 数据位
        self.flow_meter.Modbus_parameter['parity'] = self.comboBox_4.currentText()  # 校验位
        self.flow_meter.Modbus_parameter['stopbits'] = float(self.comboBox_5.currentText())  # 停止位
        self.flow_meter.Modbus_parameter['address'] = int(self.comboBox_6.currentText())  # 仪表从站站号
        # modbus连接有可能有2种错误：一是连接过程中就出错，没有返回，通过except中的程序处理；二是返回-1，通过if data_get[0]==-1处理。
        data_get = RS485.modbus_read(self.flow_meter.Modbus_parameter['PORT'],  # 串口号
                                     self.flow_meter.Modbus_parameter['baudrate'],  # 波特率
                                     self.flow_meter.Modbus_parameter['bytesize'],  # 数据位
                                     self.flow_meter.Modbus_parameter['parity'],  # 校验位
                                     self.flow_meter.Modbus_parameter['stopbits'],  # 停止位
                                     self.flow_meter.Modbus_parameter['address'],  # 仪表从站站号
                                     0,  # 起始寄存器
                                     1,  # 读寄存器的数量
                                     )
        # 处理连接过程中出错
        if (data_get == []) or (data_get[0] == -1):
            self.flow_meter.Connect_status_meter = 0  # 连接modbus错误
            # print('Connect_status_meter='+str(Connect_status_meter))
            self.flow_meter.modbus_parameter_reset()  # 复位modbus参数
            result_retry = messagebox_in_Chinese.retry_messagebox('连接仪表', '连接仪表失败，是否重试？')
            if result_retry == 1:
                print('retry')
            else:
                self.close()
                print('cancel')
            return -1  # 返回连接失败
        else:
            if data_get[0] == 6:
                self.flow_meter.Connect_status_meter = 1
            elif data_get[0] == 7:
                self.flow_meter.Connect_status_meter = 2
            self.close()
            print('Connect_status_meter=' + str(self.flow_meter.Connect_status_meter))
            messagebox_in_Chinese.information_messagebox('连接仪表', '成功连接仪表！')
            return 0  # 返回连接成功


# TODO:3.2.3 连接仪表界面定义
flow_meter_connect_1 = MeterConnect(flow_meter_1)
flow_meter_connect_2 = MeterConnect(flow_meter_2)
flow_meter_connect_3 = MeterConnect(flow_meter_3)
flow_meter_connect_4 = MeterConnect(flow_meter_4)


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
# 定义在主窗口打开各个子窗体的方法
MainWindow.actionconnect1.triggered.connect(flow_meter_connect_1.show_connect)  # 仪表1连接窗口
MainWindow.actionconnect2.triggered.connect(flow_meter_connect_2.show_connect)  # 仪表2连接窗口
MainWindow.actionconnect3.triggered.connect(flow_meter_connect_3.show_connect)  # 仪表3连接窗口
MainWindow.actionconnect4.triggered.connect(flow_meter_connect_4.show_connect)  # 仪表4连接窗口
MainWindow.action5min.triggered.connect(display_5min)  # 时间长度
MainWindow.action10min.triggered.connect(display_10min)  # 时间长度
MainWindow.action30min.triggered.connect(display_30min)  # 时间长度
MainWindow.action1hour.triggered.connect(display_1hour)  # 时间长度
MainWindow.action4hour.triggered.connect(display_4hour)  # 时间长度
MainWindow.action8hour.triggered.connect(display_8hour)  # 时间长度
MainWindow.actionoutput_data.triggered.connect(export_data_period)  # 导出数据
MainWindow.actiondata_clear.triggered.connect(data_drop_show)  # 清理数据

MainWindow.show()  # 显示主界面
sys.exit(app.exec_())  # 退出主界面
