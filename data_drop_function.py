# ！python3
# -*- coding: UTF-8 -*-

# @Time    :2020/10/8 15:28
# @Author  :Wu Yuming
# @Email   :61508712@qq.com
# @File    :
# @Software:PyCharm
# @Version :1.0.003

import pandas as pd
import os


def meter_data_drop(drop_before):
    dir_now = os.getcwd()
    print(dir_now)
    source_csv = pd.read_csv(dir_now + '\\meter_run_data.paddlerundata', index_col=0)
    source_csv.index = pd.to_datetime(source_csv.index)
    source_csv = source_csv[drop_before:]
    export_file_name = dir_now + '\\' + 'meter_run_data.paddlerundata'
    print(export_file_name)
    source_csv.to_csv(export_file_name, header=False)


if __name__ == '__main__':
    meter_data_drop('2020-07-14')
