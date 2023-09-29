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

def insert_ser(serinsuid, refstuinsuid, conn, c):
    # series level
    if_exist_ser = False

    # if a new patient
    sql_select_ser = "select 1 from serieslevel where serinsuid='{}';".format(serinsuid)    # 这个series是否已经存在
    cursor = c.execute(sql_select_ser)
    for row in cursor:
        if row == (1,):
            if_exist_ser = True

    # a new series
    if if_exist_ser == False:
        # insert the new series into the series table
        series_insert_date = str(datetime.date.today())
        now = datetime.datetime.now()
        series_insert_time = str(now.strftime("%Y-%m-%d %H:%M:%S"))

        sql_ist_ser = 'INSERT INTO serieslevel (sernum, serinsuid, modality, pronam, serdes, bodparexa, numserrelima, \
            insertdate, inserttime, refstuinsuid) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
        c.execute(sql_ist_ser, ("", serinsuid, "", "", "", "", 0, series_insert_date, series_insert_time, refstuinsuid))

        conn.commit()
        print("Series infomation successfully inserted!")
        
    # not a new patient
    else:
        print("The series is already in the database!")

