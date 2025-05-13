import pandas as pd
def readExcel(filename, sheet_name, skiprows) :
    return pd.read_excel(filename, sheet_name=sheet_name, skiprows=skiprows)