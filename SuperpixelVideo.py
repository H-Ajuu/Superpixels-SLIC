import sys
import cv2
import time
import os
import numpy as np
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

class GUI(QtWidgets.QWidget):
    def __init__(self):
        #初始化————init__
        super().__init__()
        self.initGUI()
    def initGUI(self):
        self.cwd = os.getcwd()  #程序路径
        #定义文本标签
        self.vedioDirLabel = QLabel('视频路径')
        self.argLabel1 = QLabel('像素尺寸')
        self.argLabel2 = QLabel('平滑因子')
        self.argLabel3 = QLabel('迭代次数')
        self.pic1 = QLabel()
        self.pic2 = QLabel()
        #视频展示窗口填充默认背景
        Im = cv2.imread('C:/Users/zyw/Desktop/background.png')  # 通过Opencv读入一张图片
        image_height, image_width, image_depth = Im.shape  # 获取图像的高，宽以及深度。
        QIm = cv2.cvtColor(Im, cv2.COLOR_BGR2RGB)  # opencv读图片是BGR，qt显示要RGB，所以需要转换一下
        QIm = QImage(QIm.data, image_width, image_height,  # 创建QImage格式的图像，并读入图像信息
                     image_width * image_depth,
                     QImage.Format_RGB888)
        self.pic1.setPixmap(QPixmap.fromImage(QIm))  # 将QImage显示在之前创建的QLabel控件中
        self.pic2.setPixmap(QPixmap.fromImage(QIm))  # 将QImage显示在之前创建的QLabel控件中
        #定义文本框
        self.vedioDirEdit = QLineEdit()
        self.argEdit1 = QLineEdit()
        self.argEdit2 = QLineEdit()
        self.argEdit3 = QLineEdit()
        #定义按钮
        self.choosebtn = QPushButton('选择文件')
        self.choosebtn.clicked.connect(self.choosebtnAction)
        self.beginbtn = QPushButton('开始处理')
        self.beginbtn.clicked.connect(self.beginbtnAction)
        #定义网格布局
        grid = QGridLayout()
        grid.setSpacing(10)
        #添加控件
        grid.addWidget(self.vedioDirLabel, 1, 1)
        grid.addWidget(self.vedioDirEdit, 1, 2, 1, 10)
        grid.addWidget(self.choosebtn, 1, 12)
        grid.addWidget(self.pic1, 2, 1, 5, 5)
        grid.addWidget(self.argLabel1, 2, 6)
        grid.addWidget(self.argEdit1, 2, 7)
        grid.addWidget(self.argLabel2, 3, 6)
        grid.addWidget(self.argEdit2, 3, 7)
        grid.addWidget(self.argLabel3, 4, 6)
        grid.addWidget(self.argEdit3, 4, 7)
        grid.addWidget(self.beginbtn, 6, 6, 1, 2)
        grid.addWidget(self.pic2, 2, 8, 5, 5)
        #新建窗体
        self.setLayout(grid)
        self.setGeometry(0, 0, 1800, 900)
        self.setWindowTitle('超像素视频生成软件')
        self.show()

    #设置按钮事件
    def choosebtnAction(self):
        fileName_choose, filetype = QFileDialog.getOpenFileName(self,
                                                                "选取文件",
                                                                self.cwd,  # 起始路径
                                                                "All Files (*)")  # 设置文件扩展名过滤,用双分号间隔
        self.vedioDirEdit.setText(fileName_choose)  #显示所选取视频的完整文件名

    def beginbtnAction(self):
        #获得参数
        mp4Dir = self.vedioDirEdit.text()
        averageSize = self.argEdit1.text()
        smoothingFactor = self.argEdit2.text()
        iterate_num = self.argEdit3.text()

        #对视频每一帧进行处理
        cap = cv2.VideoCapture(mp4Dir)
        while cap.isOpened():
            rval, frame = cap.read()  # rval返回True表示成功读取到一帧，frame为捕获帧
            if rval == False:
                break  #视频读完结束循环

            #slic算法
            slic = cv2.ximgproc.createSuperpixelSLIC(frame, region_size=int(averageSize), ruler=int(smoothingFactor))
            slic.iterate(int(iterate_num))  # 迭代次数，越大效果越好
            mask_slic = slic.getLabelContourMask()  # 获取Mask，超像素边缘Mask==1
            label_slic = slic.getLabels()  # 获取超像素标签
            number_slic = slic.getNumberOfSuperpixels()  # 获取超像素数目
            mask_inv_slic = cv2.bitwise_not(mask_slic)
            img_slic = cv2.bitwise_and(frame, frame, mask=mask_inv_slic)  # 在原图上绘制超像素边界

            #输出处理后的帧
            image_height, image_width, image_depth = img_slic.shape  
            QIm = cv2.cvtColor(img_slic, cv2.COLOR_BGR2RGB)  
            QIm = QImage(QIm.data, image_width, image_height,  
                         image_width * image_depth,
                         QImage.Format_RGB888)
            self.pic2.setPixmap(QPixmap.fromImage(QIm))  

            #输出处理前的帧
            image_height, image_width, image_depth = frame.shape  
            QIm = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  
            QIm = QImage(QIm.data, image_width, image_height,  
                         image_width * image_depth,
                         QImage.Format_RGB888)
            self.pic1.setPixmap(QPixmap.fromImage(QIm))  

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        cap.release()

    #关闭窗口事件
    def closeEvent(self, QCloseEvent):
        reply = QtWidgets.QMessageBox.question(self, '确认',"确定关闭当前窗口？", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            QCloseEvent.accept()
        else:
            QCloseEvent.ignore()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    gui = GUI()
    sys.exit(app.exec_())