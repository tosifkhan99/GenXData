from utils.get_names import get_names
def random_name_strategy(**kwargs):
    """
    Summary:
        generates a random name

    Args:
        df (padans.DataFrame): an empty dataframe or a dataframe which is generated from previous strategy or relation.
        operation (str): type operating the generated to the column.
        mask (pandas.Series, optional): a list of booleans to generate data for some specific rows, came from a relation
          Defaults to `False`.
        colName: column for which the data to be generate.
        rows (int): number of rows to generate.
        
    Returns:
        df (pandas.DataFrame): updted dataframe.
    """
    df = kwargs.get('df')
    colName = kwargs.get('col_name')
    
    if kwargs.get('operation') == "insertIfEmpty":
        null_mask = kwargs.get('mask',False) & df[colName].isnull()
        if null_mask.sum() == 0:
            return df
        df.loc[null_mask, colName] = get_names(null_mask.sum())
    elif kwargs.get('operation') == "insert":
        df[colName] = get_names(kwargs.get('rows'))
    return df