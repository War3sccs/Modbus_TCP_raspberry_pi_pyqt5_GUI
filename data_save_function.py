# ！python3
# -*- coding: UTF-8 -*-

# @Time    :2020/10/8 15:28
# @Author  :Wu Yuming
# @Email   :61508712@qq.com
# @File    :
# @Software:PyCharm
# @Version :1.0.003

import pandas as pd
import numpy as np
import os
import datetime


def meter_record_save(start_date_time, end_date_time):
    data_from_file = list(np.arange(109) + 40001)
    for i in range(len(data_from_file)):
        data_from_file[i] = str(data_from_file[i])
    data_from_file.append('ModbusAddress')
    data_from_file.append('water_flow_1_high')
    data_from_file.append('water_flow_1_low')
    data_from_file.append('water_flow_2_high')
    data_from_file.append('water_flow_2_low')
    dir_now = os.getcwd()
    print(dir_now)
    source_csv = pd.read_csv(dir_now + '\\meter_run_data.paddlerundata', index_col=0)
    source_csv.columns = data_from_file
    source_csv.index.name = 'DateTime'
    source_csv.index = pd.to_datetime(source_csv.index)
    source_csv = source_csv[start_date_time:end_date_time]
    source_csv['仪表编号'] = source_csv['40003'] * 65536 + source_csv['40004']
    source_csv['仪表编号'].astype(np.unicode_)
    source_csv['仪表编号'] = source_csv['仪表编号'].astype(np.unicode_)
    for i in range(len(source_csv['仪表编号'])):
        source_csv['仪表编号'][i] = source_csv['仪表编号'][i].rjust(9, '0')
    source_csv['仪表编号'] = 'FS' + source_csv['仪表编号']
    meter_record = pd.DataFrame(source_csv['仪表编号'])
    meter_record['瞬时流量1'] = source_csv['40005'] * 32768 + source_csv['40006'] + source_csv['40007'] / 1000
    meter_record['瞬时流量2'] = source_csv['40008'] * 32768 + source_csv['40009'] + source_csv['40010'] / 1000
    meter_record['累积容积1'] = source_csv['40011'] * 32768 * 32768 * 32768 + source_csv['40012'] * 32768 * 32768 + \
                            source_csv['40013'] * 32768 + source_csv['40014'] + source_csv['40015'] / 1000
    meter_record['累积容积2'] = source_csv['40016'] * 32768 * 32768 * 32768 + source_csv['40017'] * 32768 * 32768 + \
                            source_csv['40018'] * 32768 + source_csv['40019'] + source_csv['40020'] / 1000
    meter_record['通道1流量过高'] = source_csv['water_flow_1_high']
    meter_record['通道1流量过低'] = source_csv['water_flow_1_low']
    meter_record['通道2流量过高'] = source_csv['water_flow_2_high']
    meter_record['通道2流量过低'] = source_csv['water_flow_2_low']
    meter_number = meter_record['仪表编号'].drop_duplicates()
    date_time_now = datetime.datetime.now()  # 获取当前时间
    export_file_name = dir_now + '\\' + str(date_time_now.year) + str(date_time_now.month).rjust(2, '0') + str(
        date_time_now.day).rjust(2, '0') + '导出数据.xlsx'
    export_data_excel = pd.ExcelWriter(export_file_name)
    for i in range(len(meter_number)):
        meter_record[meter_record['仪表编号'] == meter_number[i]].to_excel(export_data_excel, meter_number[i])
    export_data_excel.save()


if __name__ == '__main__':
    meter_record_save('2020-07-14', '2021-2-22')
