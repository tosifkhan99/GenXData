import pandas as pd
def map_values(val, lst):
    if pd.isna(val):
        return lst.pop(0)
    else:
        return val