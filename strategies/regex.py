import numpy as np
import rstr

def regex(**kwargs):
    """
    Summary:
        generates a regex pattern

    Args:
        params (dict): holds the arguments on which strategies are generated.
        df (pandas.DataFrame): an empty dataframe or a dataframe which is generated from previous strategy or relation.
        operation (str): type operating the generated to the column.
        col_name: column for which the data to be generate.
        rows (int): number of rows to generate.
        is_unique (boolean): to generate a unique value or not
        
    Returns:
        df (pandas.DataFrame): updated dataframe.
    """
    
    df = kwargs.get('df')
    already_present = []
    new_generated = []
    total_missing = None
    colName = kwargs.get('col_name')

    total_missing = kwargs.get('rows')
    
    while total_missing > 0:
        temp = rstr.xeger(kwargs.get('params').get('regex'))
        if kwargs.get('is_unique'):
            if temp not in already_present:
                already_present.append(temp)
                new_generated.append(temp)
                total_missing -= 1
        else:
            new_generated.append(temp)
            total_missing -= 1
    
    if kwargs.get('operation').lower() == 'insert_if_empty':
        df.loc[df[colName].isna(), colName] = new_generated
    elif kwargs.get('operation').lower() == 'overwrite':
        df[colName] = new_generated
    
    return df