import sys 
import Ui_EndoMainWindow # pyuic5 -o EndoMainWindow.py EndoMainWindow.ui
import Ui_RegisterDialog as RegisterDialog # pyuic5 -o RegisterDialog.py RegisterDialog.ui
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import QTimer
from PyQt5.Qt import *
import datetime
import os
import pydicom
from pydicom.dataset import FileDataset, FileMetaDataset
from pydicom.uid import UID
import qimage2ndarray
import time
import numpy as np
import cv2
from PIL import Image
from insert_pat import *
from insert_img import *
from insert_stu import *
from insert_ser import *
from save_as_dicom import *
# from open_camera import *
import random
import sqlite3


class endo_window(QMainWindow):
    def __init__(self, parent=None):
        super(QMainWindow,self).__init__(parent)
        self.ui = Ui_EndoMainWindow.Ui_MainWindow()
        self.ui.setupUi(self)
        self.RegisterDialog = register_dialog()

        # initialize the UI
        self._initUI()
        

    def _initUI(self):
        # connect signal and slots
        self.ui.RegisterBtn.clicked.connect(self._on_clicked_registerBtn)
        # self.RegisterDialog.ui.ConfirmBtn.clicked.connect(self._load_as_dicom)
        self.ui.RegisterBtn.clicked.connect(self._load_as_dicom)
        self.ui.CameraBtn.clicked.connect(self._open_camera)

        self.ui.CatchBtn.clicked.connect(self._taking_pictures)
        self.ui.CatchBtn.clicked.connect(self._catch_endo_image)

        self.ui.DiscardBtn.clicked.connect(self._discard_pat)
        self.ui.CancelBtn.clicked.connect(self.close)      

        self.ui.selectPathBtn.clicked.connect(self._new_path)

        # self.ui.nStudyCheck.toggled.connect(self._change_status)

        self.camera_timer = QTimer()
        self.RegisterDialog = register_dialog()
        self.showVideo = self.ui.ShowVideo
        self.showImage = self.ui.ShowImage

        self.cap = cv2.VideoCapture()  # 初始化摄像头
        self.showVideo.setScaledContents(True)  # 自适应
        self.showImage.setScaledContents(True)
        self.camera_timer = QTimer()

        
    # def _change_status(self):
    #     self.ui.nSeriesCheck.setCheckable(self.ui.nStudyCheck.isChecked())

    def _new_path(self):
        directory = QtWidgets.QFileDialog.getExistingDirectory(None, "选取文件夹", "E:/project4/519021910124_姚一诺_模块二")  # 起始路径
        self.ui.pathname.setText(directory)
        self.folderpath = self.ui.pathname.text()

    def _open_camera(self):
        self.cap = cv2.VideoCapture(0)  # 摄像头
        self.camera_timer.start(1)  # 每40毫秒读取一次，即刷新率为25帧
        self.camera_timer.timeout.connect(self._show_image)
        self._show_image()
        
    
    def _show_image(self):
        # self.camera_timer.start(40)  # 每40毫秒读取一次，即刷新率为25帧
        flag, self.image = self.cap.read()  # 从视频流中读取图片

        if flag:
            self._display_video()


    def _display_video(self):
        img = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
        self.qimg = qimage2ndarray.array2qimage(img)
        self.showVideo.setPixmap(QPixmap(self.qimg))
        self.showVideo.show()

    def _taking_pictures(self):
        self.showImage.setPixmap(QPixmap(self.qimg))
        # self.showImage.show()


    def _catch_endo_image(self):
        # # if catchBtn is pushed, get the image from endoscope
        catch_img = self.ui.ShowImage.pixmap().toImage()
        ptr = catch_img.constBits()
        ptr.setsize(catch_img.byteCount())
        mat = np.array(ptr).reshape(catch_img.height(), catch_img.width(), 4)  
        # img = Image.fromarray(cv2.cvtColor(mat, cv2.COLOR_BGR2RGB)).convert('RGB') 
        img = Image.fromarray(cv2.cvtColor(mat, cv2.COLOR_BGR2GRAY)) 
        img = np.array(img)
        # image = np.array(img)
        # img.save("out.bmp")  

        if self.ui.nStudyCheck.isChecked():
            # add new study
            self.RegisterDialog._insert_stu()
            # add new series
            self.RegisterDialog._insert_ser()

        if self.ui.nSeriesCheck.isChecked():
            # add new series
            self.RegisterDialog._insert_ser()


        # save to the database
        dt = datetime.datetime.now()
        self.InsertDate = dt.strftime('%Y%m%d')
        timeStr = dt.strftime('%H%M%S.%f')  # long format with micro seconds
        self.InsertTime = timeStr
        self.TransferSyntax = ""

        # TODO: 截取图像时选择保存路径
        self.StoragePath = "D:"
        # self.SopInsUID = "1.3.6.1.4.1." + str(self.InsertDate) + "." + str(random.randint(10000, 99999))
        # self.SOPClaUID = "1.2.840.5.1." + str(self.InsertDate) + "." + str(random.randint(1000, 9999))
        self.SopInsUID = pydicom.uid.generate_uid()
        self.SopClaUID = "1.2.840.10008.5.1.4.1.1.77.1.1"


        conn = sqlite3.connect('imagedb.db')
        c = conn.cursor()
        self.img_info = [self.SopInsUID, self.SopClaUID, self.InsertDate, self.InsertTime, self.TransferSyntax, \
            self.StoragePath, self.RegisterDialog.SerInsUID]

        insert_img(self.img_info, conn, c)
        print("Successfully inserted into the image database!")

        save_to_dcm(img, self.filename_little_endian, self.SopInsUID, self.SopClaUID, \
                    self.RegisterDialog.StuInsUID, self.RegisterDialog.SerInsUID, self.folderpath, \
                    self.RegisterDialog.patientName, self.RegisterDialog.patientID, \
                    self.RegisterDialog.patientBirthDate, self.RegisterDialog.patientSex )


    def _load_as_dicom(self):
        # define file_meta
        file_meta = FileMetaDataset()
        file_meta.MediaStorageSOPClassUID = UID('1.2.840.10008.5.1.4.1.1.2')
        file_meta.MediaStorageSOPInstanceUID = UID("1.2.3")
        file_meta.ImplementationClassUID = UID("1.2.3.4")

        self.filename_little_endian = "./test.dcm" # TODO

        # Create the FileDataset instance (initially no data elements, but file_meta supplied)
        ds = FileDataset(self.filename_little_endian, {},
                        file_meta=file_meta, preamble=b"\0" * 128)


        ds.PatientName = self.RegisterDialog.patientName
        ds.PatientID = self.RegisterDialog.patientID
        ds.PatientSex = self.RegisterDialog.patientSex
        ds.PatientAge = self.RegisterDialog.patientAge
        ds.PatientBirthDate = self.RegisterDialog.patientBirthDate
        ds.PatientWeight = self.RegisterDialog.patientWeight

        # yinuoyao
        self.ui.PatID.setText(ds.PatientID)
        self.ui.PatName.setText(str(ds.PatientName))
        self.ui.PatSex.setText(str(ds.PatientSex))
        self.ui.PatID.setText(str(ds.PatientID))
        
        self.ds = ds

        # Set the transfer syntax
        self.ds.is_little_endian = True
        self.ds.is_implicit_VR = True

        # Set creation date/time
        dt = datetime.datetime.now()
        self.ds.ContentDate = dt.strftime('%Y%m%d')
        timeStr = dt.strftime('%H%M%S.%f')  # long format with micro seconds
        self.ds.ContentTime = timeStr


    def _on_clicked_registerBtn(self):
        self.RegisterDialog.exec()

    def _discard_pat(self):
        self.ui.PatID.setText("")
        self.ui.PatName.setText("")
        self.ui.PatSex.setText("")
        self.ui.PatID.setText("")

        patid = self.ds.PatientID
        stuid = self.RegisterDialog.StuInsUID
        serid = self.RegisterDialog.SerInsUID

        # delete from the database
        del_pat = "DELETE FROM patientLevel WHERE PatID = '{}'".format(patid)
        del_stu = "DELETE FROM studyLevel WHERE StuInsUID = '{}'".format(stuid)
        del_ser = "DELETE FROM seriesLevel WHERE SerInsUID = '{}'".format(serid)
        del_imgs = "DELETE FROM imageLevel WHERE refSerInsUID = '{}'".format(serid)
        
        conn = sqlite3.connect('../week8/imagedb.db')
        c = conn.cursor()

        c.execute(del_imgs)
        c.execute(del_ser)
        c.execute(del_stu)
        c.execute(del_pat)

        conn.commit()


        print("Successfully discarded the patient's information!")


class register_dialog(QDialog):
    def __init__(self,parent=None):
        super(QDialog,self).__init__(parent)
        self.ui = RegisterDialog.Ui_Dialog()
        self.ui.setupUi(self)
        # self.main_ui = endo_window()
        # self.main_ui.setupUi(self)

        # # yinuoyao
        # self.mainWindow = Ui_EndoMainWindow.Ui_MainWindow()

        self.patientName = " "
        self.patientSex = " "
        self.patientID = " "
        self.patientWeight = " "
        self.patientBirthDate = " "
        self.patientAge = "001Y"

        self._initUI()

    def _initUI(self):
        self.ui.ConfirmBtn.clicked.connect(self._on_clicked_ConfirmBtn)
        # self.ui.ConfirmBtn.clicked.connect(self.main_ui._load_as_dicom)
        self.ui.ConfirmBtn.clicked.connect(self.close)
        self.ui.CancelBtn.clicked.connect(self.close)


    def _on_clicked_ConfirmBtn(self):
        # Confirm whether the info is permitted
        # get the info from lineEdit
        self.patientName = self.ui.PatName.text()
        self.patientAge = str(self.ui.PatAge.text())
        self.patientSize = self.ui.PatSize.text()
        self.patientBirthDate = self.ui.PatBirthDate.text()
        self.patientSex = self.ui.PatSex.text()
        self.patientWeight = self.ui.PatWeight.text()
        
        # yinuoyao
        # ID 自动生成！
        # self.patientID = self.ui.PatID.text()
        dt = datetime.datetime.now()
        InsertDate = dt.strftime('%Y%m%d')
        self.patientID = "1.22.55.44." + str(InsertDate) + "." + str(random.randint(10000, 99999))
        # self.ui.PatID.setText(self.patientID)


        conn = sqlite3.connect('imagedb.db')
        c = conn.cursor()
        self.info = [self.patientName,  self.patientID, self.patientBirthDate, self.patientSex]
        insert_pat(self.info, conn, c)
        
        self._insert_stu()
        self._insert_ser()
    

    def _insert_stu(self):
        conn = sqlite3.connect('imagedb.db')
        c = conn.cursor()

        dt = datetime.datetime.now()
        InsertDate = dt.strftime('%Y%m%d')
        self.StuInsUID = pydicom.uid.generate_uid()

        info2 = [self.patientName, self.patientAge, self.patientSize, self.patientWeight, self.StuInsUID, \
            self.patientID]
        insert_stu(info2, conn, c)



    def _insert_ser(self):
        conn = sqlite3.connect('imagedb.db')
        c = conn.cursor()

        dt = datetime.datetime.now()
        InsertDate = dt.strftime('%Y%m%d')

        self.SerInsUID = pydicom.uid.generate_uid()
        insert_ser(self.SerInsUID, self.StuInsUID, conn, c)
        


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)     
    myWindow = endo_window()
    myWindow.show()
    sys.exit(app.exec_())   
