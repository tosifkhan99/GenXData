from utils.get_numbers import get_numbers
from utils.intermediate_column import mark_as_intermediate

def number_range_strategy(**kwargs):
    """
    Summary:
        generates a random number range

    Args:
        params (dict): holds the arguments on which strategies are generated.
        df (pandas.DataFrame): an empty dataframe or a dataframe which is generated from previous strategy or relation.
        operation (str): type operating the generated to the column.
        col_name: column for which the data to be generated.
        rows (int): number of rows to generate.
        intermediate (bool): whether this column is intermediate (not in final output).
        
    Returns:
        df (pandas.DataFrame): updated dataframe.
    """
    df = kwargs.get('df')
    colName = kwargs.get('col_name')
    ub = kwargs.get('params').get('range').get('upperbound')
    lb = kwargs.get('params').get('range').get('lowerbound')
    
    if kwargs.get('operation').lower() == "insert_if_empty":
        null_mask = df[colName].isnull()
        if null_mask.sum() == 0:
            return df
        df.loc[null_mask, colName] = get_numbers(lb, ub, null_mask.sum())
    elif kwargs.get('operation').lower() == "overwrite":
        df[colName] = get_numbers(lb, ub, kwargs.get('rows'))
    else:
        raise ValueError(f"Invalid operation: {kwargs.get('operation')}. Use 'insert_if_empty' or 'overwrite'")
    
    # Mark as intermediate if needed
    if kwargs.get('intermediate', False):
        df = mark_as_intermediate(df, colName)
    
    return df