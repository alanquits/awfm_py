from . import DelimitedDataframe, XlsxDataframe
import os

def extension_map():
    return {
        ".xlsx": XlsxDataframe,
        ".xls": XlsxDataframe,
        ".csv": DelimitedDataframe,
        ".dat": DelimitedDataframe
    }

def Dataframe(infile):
    _, ext = os.path.splitext(infile)
    try:
        return extension_map()[ext](infile)
    except KeyError:
        return None
