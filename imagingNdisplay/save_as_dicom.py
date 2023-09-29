import os
import datetime
import numpy as np
from PIL import Image
import pydicom
from pydicom.dataset import Dataset, FileDataset
import cv2

def save_to_dcm(img, little_endian, sopInsUID, sopClaUID, stuInsUID, serInsUID, folderpath, PatNam, PatID, PatBirDate, PatSex):
    # 参考：https://blog.csdn.net/weixin_43229348/article/details/122538564
    print("Setting file meta information...")
    suffix = ".dcm"


    dcms = os.listdir(folderpath)
    num_dcms = str(len(dcms) + 1)

    filename = folderpath + "/test" + num_dcms + suffix

    # Populate required values for file meta information
    file_meta = Dataset()
    file_meta.MediaStorageSOPClassUID = sopClaUID
    file_meta.MediaStorageSOPInstanceUID = sopInsUID
    file_meta.ImplementationClassUID = "1.2.3.4"

    print("Setting dataset values...")
    # Create the FileDataset instance (initially no data elements, but file_meta
    # supplied)
    ds = FileDataset(little_endian, {}, file_meta=file_meta, preamble=b"\0" * 128)
                
   	# # Write as a different transfer syntax XXX shouldn't need this but pydicom
    # # 0.9.5 bug not recognizing transfer syntax
    ds.file_meta.TransferSyntaxUID = pydicom.uid.ImplicitVRLittleEndian
	# Set creation date/time
    dt = datetime.datetime.now()
    ds.ContentDate = dt.strftime('%Y%m%d')
    timeStr = dt.strftime('%H%M%S.%f')  # long format with micro seconds
    ds.ContentTime = timeStr
    ds.SOPClassUID = sopClaUID
    ds.SOPInstanceUID= sopInsUID
    ds.Modality = "US"
    ds.SeriesInstanceUID = serInsUID
    ds.StudyInstanceUID = stuInsUID
    ds.FrameOfReferenceUID = pydicom.uid.generate_uid()
    ds.PatientName = PatNam
    ds.PatientID = PatID
    ds.PatientBirthDate = PatBirDate
    ds.PatientSex = PatSex

    ds.BitsStored = 8
    ds.BitsAllocated = 8
    ds.SamplesPerPixel = 1
    ds.HighBit = 7
    ds.PlanarConfiguration = 0

    ds.InstanceNumber = 1
    ds.ImagePositionPatient = r"0\0\1"
    ds.ImageOrientationPatient = r"1\0\0\0\-1\0"

    ds.ImagesInAcquisition = "1"
    ds.Rows,ds.Columns = img.shape[:2]
    ds.PixelSpacing = [1, 1]
    ds.PixelRepresentation = 0
    ds.PixelData= img.tobytes()
    # import pdb;pdb.set_trace()
    ds.PhotometricInterpretation = "MONOCHROME1"
    
    print("Writing file", filename)
    ds.save_as(filename)
    print("File saved.")
