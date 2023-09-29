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
import random

# random.seed(str(datetime.date.today()))

# 主键外键怎么设的？？

def insert_img(img_info, conn, c):
    NumPatRelStu, NumPatRelSer, NumPatRelIma, NumStuRelSer, NumStuRelIma, NumSerRelIma = 1, 1, 1, 1, 1, 1
                        
    attr = {            # image level
            "imanum": "",
            "sopinsuid": img_info[0],
            "sopclauid": img_info[1],
            "transfersyntax": img_info[4],
            "insert_date": img_info[2],
            "insert_time": img_info[3],
            "storagepath": img_info[5],
            "refserinsuid": img_info[6]
        } 

    #################################################################################
    # img_level
    img_id = attr["sopinsuid"]
    sql_select_img = "select 1 from imagelevel where sopinsuid='{}' limit 1;".format(img_id)
    cursor = c.execute(sql_select_img)
    for row in cursor:
        # not a new image
        if row[0] == 1:
            print("The image has been in the database!")
            sys.exit()


    # insert the new image into `imagelevel`
    img_insert_date = str(datetime.date.today())
    now = datetime.datetime.now()
    img_insert_time = str(now.strftime("%Y-%m-%d %H:%M:%S"))

    img_path = attr['storagepath']
    sql_ist_ima = "INSERT OR IGNORE INTO imagelevel (imanum, sopinsuid, sopclauid, insertdate, \
        inserttime, transfersyntax, storagepath, refserinsuid) VALUES (?, ?, ?, ?, ?, ?, ?, ?);"
    c.execute(sql_ist_ima, (attr['imanum'], attr['sopinsuid'], attr['sopclauid'], img_insert_date, \
        img_insert_time, attr['transfersyntax'], img_path, attr['refserinsuid']))
    conn.commit()


    update_imgnum = "UPDATE seriesLevel set NumSerRelIma = NumSerRelIma+1 WHERE SerInsUID ='{}'".format(attr['refserinsuid'])
    c.execute(update_imgnum)
    conn.commit()




    # sql_get_stuinsuid = "SELECT refStuInsUID FROM seriesLevel WHERE SerInsUID ='{}'".format(attr['refserinsuid'])

    # cursor = c.execute(sql_get_stuinsuid)
    # for row in cursor:
    #     stuinsuid = row[0] + 1

    # sql_stu_img_num = "SELECT NumStuRelIma FROM studyLevel WHERE StuInsUID ='{}'".format(stuinsuid)


    # cursor = c.execute(sql_stu_img_num)
    # for row in cursor:
    #     NumStuRelIma = row[0] + 1
    

    # sql_get_patinsuid = "SELECT refPatID FROM studyLevel WHERE StuInsUID ='{}'".format(stuinsuid)

    # cursor = c.execute(sql_get_patinsuid)
    # for row in cursor:
    #     patientID = row[0] + 1

    # sql_pat_img_num = "SELECT NumPatRelIma FROM patientLevel WHERE PatID ='{}'".format(patientID)

    # cursor = c.execute(sql_pat_img_num)
    # for row in cursor:
    #     NumPatRelIma = row[0] + 1