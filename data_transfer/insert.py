import sqlite3
from pydicom import dcmread
import datetime
from time import strftime
import pandas as pd
import os
from glob import glob

def insert_all_dicom(filename):
    insert_dcm(filename,1)
   

def deliver_database(filename):
    
    if not os.path.exists('./DICOM_Database.db'):
        create_database()
    insert_all_dicom(filename)


def create_database():
    conn = sqlite3.connect('./DICOM_Database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE ImageLevel
                (ImaNum INT,
                SOPInsUID VARCHAR(20) PRIMARY KEY,
                SOPClaUID VARCHAR(20),
                InsertDate VARCHAR(8),
                InsertTime VARCHAR(30),
                TransferSyntax VARCHAR(30),
                storagePath VARCHAR(100),
                refSerInsUID VARCHAR(20),
                FOREIGN KEY (refSerInsUID) REFERENCES SeriesLevel (SerInsUID));''')
    
    c.execute('''CREATE TABLE patientlevel
                (PatNam VARCHAR(30) NOT NULL,
                PatID VARCHAR(20) PRIMARY KEY,
                PatBirDate VARCHAR(8),
                PatSex CHAR(2),
                
                --  检查数
                NumPatRelStu INT,
                --  序列数
                NumPatRelSer INT, 
                --   拍片数
                NumPatRelIma INT,
                InsertDate VARCHAR(8),
                InsertTime VARCHAR(30));''')

    c.execute('''CREATE TABLE SeriesLevel 
                (SerNum INT,
                SerInsUID VARCHAR(20) PRIMARY KEY,
                Modality VARCHAR(20),
                ProNam VARCHAR(20),
                SerDes VARCHAR(20),
                BodParExa VARCHAR(20),
                NumSerRelIma INT,
                InsertDate VARCHAR(8),
                InsertTime VARCHAR(30),
                refStuInsUID VARCHAR(20),
                FOREIGN KEY (refStuInsUID) REFERENCES StudyLevel(StuInsUID));''')



    c.execute('''CREATE TABLE StudyLevel
                (StuID INT NOT NULL,
                StuInsUID VARCHAR(20) PRIMARY KEY, 
                StuDate VARCHAR(8),
                StuTime VARCHAR(30),
                AccNum INT,
                PatNam VARCHAR(30),
                PatAge INT,
                PatSize INT,
                PatWeight VARCHAR(4),
                NumStuRelSer INT,
                NumStuRelIma INT,
                InsertDate VARCHAR(8),
                InsertTime VARCHAR(30),
                refPatID VARCHAR(20),
                FOREIGN KEY (refPatID) REFERENCES patientlevel(PatID));''')

    conn.commit()
    conn.close()

def insert_pat(ds,conn):
    attr=[]
    attr.append(str(ds.PatientName) if "PatientName" in ds else 'None')
    attr.append(ds.PatientID if "PatientID" in ds else 'None')
    attr.append(ds.PatientBirthDate if "PatientBirthDate" in ds else 'None')
    attr.append(ds.PatientSex if "PatientSex" in ds else 'None')
    
    attr.append(1)
    attr.append(1)
    attr.append(1)
    attr.append(datetime.datetime.now().strftime("%Y-%m-%d"))
    attr.append(datetime.datetime.now().strftime("%H:%M:%S"))
    
    strSQL="INSERT INTO patientlevel(PatNam,PatID,PatBirDate,PatSex,\
NumPatRelStu,NumPatRelSer,NumPatRelIma,InsertDate,InsertTime)\
 VALUES('{}','{}','{}','{}',{},{},{},'{}','{}')".format(attr[0],
    attr[1],attr[2],attr[3],attr[4],attr[5],attr[6],attr[7],attr[8])

    conn.execute(strSQL)


def insert_stu(ds,conn):
    attr=[]
    attr.append(ds.StudyID if "StudyID" in ds else 'None')
    attr.append(str(ds.StudyInstanceUID) if "StudyInstanceUID" in ds else 'None')
    attr.append(ds.StudyDate if "StudyDate" in ds else 'None')
    attr.append(ds.StudyTime if "StudyTime" in ds else 'None')
    attr.append(ds.AccessionNumber if "AccessionNumber" in ds else 'None')
    attr.append(str(ds.PatientName) if "PatientName" in ds else 'None')
    attr.append(ds.PatientAge if "PatientAge" in ds else 'None')
    attr.append(ds.PatientSize if "PatientSize" in ds else 'None')
    attr.append(str(ds.PatientWeight) if "PatientWeight" in ds else 'None')
    
    
    attr.append(1)
    attr.append(1)
    attr.append(datetime.datetime.now().strftime("%Y-%m-%d"))
    attr.append(datetime.datetime.now().strftime("%H:%M:%S"))
    attr.append(ds.PatientID if "PatientID" in ds else 'None')
    
    strSQL="INSERT INTO StudyLevel(StuID,StuInsUID,StuDate,StuTime,AccNum,\
    PatNam,PatAge,PatSize,PatWeight,NumStuRelSer,NumStuRelIma,InsertDate,InsertTime,refPatID)\
 VALUES('{}','{}','{}','{}','{}','{}','{}','{}','{}',{},{},'{}','{}','{}')".format(
    attr[0],attr[1],attr[2],attr[3],attr[4],attr[5],attr[6],attr[7],attr[8],
    attr[9],attr[10],attr[11],attr[12],attr[13])

    conn.execute(strSQL)


def insert_ser(ds,conn):
    attr=[]
    attr.append(str(ds.SeriesNumber) if "SeriesNumber" in ds else 'None')
    attr.append(str(ds.SeriesInstanceUID) if "SeriesInstanceUID" in ds else 'None')
    attr.append(ds.Modality if "Modality" in ds else 'None')
    attr.append(ds.ProtocolName if "ProtocolName" in ds else 'None')
    attr.append(ds.SeriesDescription if "SeriesDescription" in ds else 'None')
    attr.append(ds.BodyPartExamined if "BodyPartExamined" in ds else 'None')
    attr.append(1)
    attr.append(datetime.datetime.now().strftime("%H:%M:%S"))
    attr.append(datetime.datetime.now().strftime("%Y-%m-%d"))
    
    
    attr.append(str(ds.StudyInstanceUID) if "StudyInstanceUID" in ds else 'None')
    
    strSQL="INSERT INTO SeriesLevel(SerNum,SerInsUID,Modality,ProNam,\
     SerDes,BodParExa,NumSerRelIma,InsertTime,InsertDate,refStuInsUID)\
      VALUES('{}','{}','{}','{}','{}','{}','{}','{}','{}','{}')".format(attr[0],
    attr[1],attr[2],attr[3],attr[4],attr[5],attr[6],attr[7],attr[8],attr[9])

    conn.execute(strSQL)


def insert_img(ds,path,inum,conn):
    attr=[]
    attr.append(inum)
    attr.append(str(ds.SOPInstanceUID) if "SOPInstanceUID" in ds else 'None')
    attr.append(str(ds.SOPClassUID) if "SOPClassUID" in ds else 'None')
    attr.append(datetime.datetime.now().strftime("%Y-%m-%d"))
    attr.append(datetime.datetime.now().strftime("%H:%M:%S"))
    attr.append(str(ds.file_meta.TransferSyntaxUID) if "TransferSyntaxUID" in ds.file_meta else 'None')
    attr.append(path)
    attr.append(str(ds.SeriesInstanceUID) if "SeriesInstanceUID" in ds else 'None')

    strSQL="INSERT INTO ImageLevel(ImaNum,SOPInsUID,SOPClaUID,InsertDate,\
    InsertTime,TransferSyntax,storagePath,refSerInsUID)\
     VALUES({},'{}','{}','{}','{}','{}','{}','{}')".format(attr[0],attr[1],
    attr[2],attr[3],attr[4],attr[5],attr[6],attr[7])
    
    conn.execute(strSQL)
    
def insert_dcm(path,inum):
    ds=dcmread(path)
    conn = sqlite3.connect('./DICOM_Database.db')
    if check_exist(ds,path,inum,conn)==True:
        conn.commit()
        conn.close()
        return
    else:
        insert_pat(ds,conn)
        insert_stu(ds,conn)
        insert_ser(ds,conn)
        insert_img(ds,path,inum,conn)
        conn.commit()
        conn.close()

def check_exist(ds,path,inum,conn):
    is_exist=False
    Pname=str(ds.PatientName)
    strSQL="select * from patientlevel where PatNam='{}'".format(Pname)

    cursor=conn.execute(strSQL)
    if cursor.fetchall()==[]:
        return is_exist
    else:
        is_exist=True 
        update_all(ds,path,inum,conn)
        return is_exist

def update_all(ds,path,inum,conn):
    update_study(ds,path,inum,conn)
    
def update_study(ds,path,inum,conn):
    
    strSQL1="select * from StudyLevel where StuInsUID='{}'".format(str(ds.StudyInstanceUID))
    cursor=conn.execute(strSQL1)
    if cursor.fetchall()==[]:
        
        strSQL2="UPDATE patientlevel set  NumPatRelStu=NumPatRelStu+1 where PatID='{}'".format(ds.PatientID)
        strSQL3="UPDATE patientlevel set  NumPatRelSer=NumPatRelSer+1 where PatID='{}'".format(ds.PatientID)
        strSQL4="UPDATE patientlevel set  NumPatRelIma=NumPatRelIma+1 where PatID='{}'".format(ds.PatientID)

        conn.execute(strSQL2)
        conn.execute(strSQL3)
        conn.execute(strSQL4)
        
        insert_stu(ds,conn)
        insert_ser(ds,conn)
        insert_img(ds,path,inum,conn)
        return
    else:

        update_series(ds,path,inum,conn)

    
def update_series(ds,path,inum,conn):
    
    strSQL1="select * from SeriesLevel where SerInsUID='{}'".format(str(ds.SeriesInstanceUID))
    cursor=conn.execute(strSQL1)
    if cursor.fetchall()==[]:
        
        strSQL2="UPDATE patientlevel set  NumPatRelSer=NumPatRelSer+1 where PatID='{}'".format(ds.PatientID)
        strSQL3="UPDATE patientlevel set  NumPatRelIma=NumPatRelIma+1 where PatID='{}'".format(ds.PatientID)
        strSQL4="UPDATE StudyLevel set  NumStuRelSer=NumStuRelSer+1 where StuInsUID='{}'".format(str(ds.StudyInstanceUID))
        strSQL5="UPDATE StudyLevel set  NumStuRelIma=NumStuRelIma+1 where StuInsUID='{}'".format(str(ds.StudyInstanceUID))

        conn.execute(strSQL2)
        conn.execute(strSQL3)
        conn.execute(strSQL4)
        conn.execute(strSQL5)
        
        insert_ser(ds,conn)
        insert_img(ds,path,inum,conn)
        return
    else:
       
        update_image(ds,path,inum,conn)

def update_image(ds,path,inum,conn):
  
    strSQL="select * from ImageLevel where SOPInsUID='{}'".format(str(ds.SOPInstanceUID))
    cursor=conn.execute(strSQL)
    if cursor.fetchall()==[]:
        
        
        strSQL1="UPDATE patientlevel set  NumPatRelIma=NumPatRelIma+1 where PatID='{}'".format(ds.PatientID)
        strSQL2="UPDATE StudyLevel set  NumStuRelIma=NumStuRelIma+1 where StuInsUID='{}'".format(str(ds.StudyInstanceUID))
        strSQL3="UPDATE SeriesLevel set  NumSerRelIma=NumSerRelIma+1 where SerInsUID='{}'".format(str(ds.SeriesInstanceUID))
        
        conn.execute(strSQL1)
        conn.execute(strSQL2)
        conn.execute(strSQL3)
        
        
        insert_img(ds,path,inum,conn)
    else:
        
        return

def drop_table():
    conn = sqlite3.connect('./DICOM_Database.db')
    conn.execute('''DROP TABLE patientlevel''')
    conn.execute('''DROP TABLE StudyLevel''')
    conn.execute('''DROP TABLE SeriesLevel''')
    conn.execute('''DROP TABLE ImageLevel''')
    conn.commit()
    conn.close()
