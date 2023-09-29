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

def insert_pat(info, conn, c):
    patnam, pat_id, patbirdate, patsex = info

    # patient level
    if_exist_pat = False

    # if a new patient
    sql_select_pat = "select 1 from patientlevel where patid='{}';".format(pat_id)    # 这个series是否已经存在
    cursor = c.execute(sql_select_pat)
    for row in cursor:
        if row == (1,):
            if_exist_pat = True

    # a new patient
    if if_exist_pat == False:
        pat_insert_date = str(datetime.date.today())
        now = datetime.datetime.now()
        pat_insert_time = str(now.strftime("%Y-%m-%d %H:%M:%S"))

        sql_ist_pat = 'INSERT INTO patientlevel (patnam, patid, patbirdate, patsex, numpatrelstu, numpatrelser, \
            numpatrelima, insertdate, inserttime) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)'
            
        NumPatRelStu, NumPatRelSer, NumPatRelIma = 1, 1, 1
        c.execute(sql_ist_pat, (patnam, pat_id, patbirdate, patsex, NumPatRelStu, NumPatRelSer, NumPatRelIma, \
            pat_insert_date, pat_insert_time))

        conn.commit()
        print("Patient infomation successfully inserted!")
        
    # not a new patient
    else:
        print("The patient is already in the database!")

