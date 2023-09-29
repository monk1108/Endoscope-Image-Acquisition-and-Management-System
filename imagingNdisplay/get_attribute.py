import pydicom
import sys

def get_attribute(dicom_path):
    try:
        dcm = pydicom.dcmread(dicom_path)
        print("Dicom file successfully loaded!")
        attributes = {
            # patient level
            "patnam": dcm.PatientName,
            "patid": dcm.PatientID,
            "patbirdate": dcm.PatientBirthDate,
            "patsex": dcm.PatientSex,
            # study level
            "stuid": dcm.StudyID,
            "stuinsuid": dcm.StudyInstanceUID,
            "studate": dcm.StudyDate,
            "stutime": dcm.StudyTime,
            "accnum": dcm.AccessionNumber if hasattr(dcm, 'AccessionNumber') else None,
            "patage": dcm.PatientAge,
            "patsize": dcm.PatientSize if hasattr(dcm, 'PatientSize') else None,
            "patweight": dcm.PatientWeight if hasattr(dcm, 'PatientWeight') else None,
            # series level
            "sernum": dcm.SeriesNumber,
            "serinsuid": dcm.SeriesInstanceUID,
            "modality": dcm.Modality,
            "pronam": dcm.ProtocolName if hasattr(dcm, 'ProtocolName') else None,
            "serdes": dcm.SeriesDescription if hasattr(dcm, 'SeriesDescription') else None,
            "bodparexa": dcm.BodyPartExamined if hasattr(dcm, 'BodyPartExamined') else None,
            # image level
            "imanum": dcm.ImageNumber if hasattr(dcm, 'ImageNumber') else None,
            "sopinsuid": dcm.SOPInstanceUID,
            "sopclauid": dcm.SOPClassUID,
            "transfersyntax": dcm.TransferSyntax if hasattr(dcm, 'TransferSyntax') else None,
        }
            
        # dcm.close()
        # print(attributes)
        return attributes

    except (pydicom.errors.InvalidDicomError, FileNotFoundError) as e:
        print("There isn't such dicom file!")
        sys.exit()
    finally:
        print("---------------------------------------------")

