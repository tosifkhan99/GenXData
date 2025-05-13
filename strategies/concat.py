import numpy as np
import pandas as pd
def concat(**kwargs):
    
    df = kwargs.get('df')
    params = kwargs.get('params')
    col_name = kwargs.get('col_name')
    
    if len(params.get('lhs_cols')) != len(params.get('rhs_cols')) :
        print(
            'invalid concat defination, columnn length didn\'t matched lhs: {}, rhs: {}'
              .format(
                    len(params.get('lhs_cols')),
                    len(params.get('rhs_cols'))
                    )
                )
    mask = kwargs.get('mask', True)
    if kwargs.get('operation') == 'insert':
        for col1, col2 in zip(kwargs.get('params').get('lhs_cols'),kwargs.get('params').get('rhs_cols')):
            if mask is True:
                df[col_name] = params.get('lhs').get('prefix','') + df[col1].astype(str) + params.get('lhs').get('suffix','') + params.get('rhs').get('prefix','') + df[col2].astype(str) + params.get('rhs').get('suffix','')
            else:
                df.loc[mask, col_name] = params.get('lhs').get('prefix','') + df.loc[mask,col1].astype(str) + params.get('lhs').get('suffix','') + params.get('rhs').get('prefix','') + df.loc[mask,col2].astype(str) + params.get('rhs').get('suffix','')

    elif kwargs.get('operation') == 'insert_if_empty':
        null_mask = mask & df[col_name].isnull()
        for col1, col2 in zip(kwargs.get('params').get('lhs_cols'),kwargs.get('params').get('rhs_cols')):
            df.loc[null_mask, col_name] = params.get('lhs').get('prefix','') + df[col1].astype(str) + params.get('lhs').get('suffix','') + params.get('rhs').get('prefix','') + df[col2].astype(str) + params.get('rhs').get('suffix','')
    
    else :
        print("Error Invalid Operation {}".format(kwargs.get('operation')))
    return df