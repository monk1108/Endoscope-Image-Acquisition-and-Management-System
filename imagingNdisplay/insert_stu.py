import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import pydicom
import os
import scipy.ndimage
import matplotlib.pyplot as plt

from skimage import measure, morphology
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import sqlite3
import datetime
from get_attribute import *
import sqlite3

def insert_stu(info, conn, c):
    patNam, patAge, patSize, patWeight, StuInsUID, refPatID = info
    StuID = ""
    AccNum = ""

    # study level
    if_exist_stu = False

    # if a new patient
    sql_select_stu = "select 1 from studylevel where stuinsuid='{}';".format(StuInsUID)    # 这个series是否已经存在
    cursor = c.execute(sql_select_stu)
    for row in cursor:
        if row == (1,):
            if_exist_stu = True

    # a new study
    if if_exist_stu == False:
        stu_insert_date = str(datetime.date.today())
        now = datetime.datetime.now()
        stu_insert_time = str(now.strftime("%Y-%m-%d %H:%M:%S"))


        sql_ist_stu = 'INSERT INTO studylevel (stuid, stuinsuid, studate, stutime, accnum, patnam, patage, patsize,\
            patweight, numStuRelSer, NumStuRelIma, insertdate, inserttime, refPatID) VALUES \
                (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
 
            
        # TODO: NumStuRelSer, NumStuRelIma == 0??
        c.execute(sql_ist_stu, (StuID, StuInsUID, stu_insert_date, stu_insert_time, AccNum, patNam, patAge, patSize, \
            patWeight, 1, 1, stu_insert_date, stu_insert_time, refPatID))

        conn.commit()
        print("Study infomation successfully inserted!")
        
    # not a new patient
    else:
        print("The study is already in the database!")

