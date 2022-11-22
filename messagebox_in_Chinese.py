#！python3
# -*- coding: UTF-8 -*-

# @Time    :2019/12/24 21:17
# @Author  :Wu Yuming
# @Email   :61508712@qq.com
# @File    :
# @Software:PyCharm
# @Version :1.0

import sys
from PyQt5.QtWidgets import *   #导入ＰｙＱｔ５库，绘制ＧＵＩ界面
from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(QDialog):
    #初始化
    def __init__(self):
        QDialog.__init__(self)
    def retry(self):
        retry_messagebox()

#TODO:重试
def retry_messagebox(Title,Text):
    retry = QMessageBox()
    retry.setWindowTitle(Title)
    retry.setText(Text)
    retry.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
    retry_retry = retry.button(QMessageBox.Ok)
    retry_retry.setText('重试')
    retry_cancel = retry.button(QMessageBox.Cancel)
    retry_cancel.setText('取消')
    retry.exec_()  # 退出必须要有
    if retry.clickedButton() == retry_retry:
        print('retry')
        return 1
    else:
        print('cancel')
        return 0

#TODO：成功
def information_messagebox(Title,Text):
    message= QMessageBox()
    message.setWindowTitle(Title)
    message.setText(Text)
    message.setStandardButtons(QMessageBox.Ok)
    message_ok = message.button(QMessageBox.Ok)
    message_ok.setText('确定')
    message.exec_()  # 退出必须要有

# if __name__=='__main__':
#     # result=retry_messagebox()
#     # print(result)
#     Dialog=Ui_Dialog()
#     Dialog.show()