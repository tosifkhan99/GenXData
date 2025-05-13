from utils.time_generator import timeGenerator
def time_range_strategy(**kwargs):
    """
    Summary:
        generates a random time

    Args:
        params (dict): holds the arguments on which stratgies are generated.
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
    col_name = kwargs.get('col_name')
    null_mask = kwargs.get('mask',False) & df[col_name].isnull()

    if null_mask.sum() == 0:
        return df
    upperbound = kwargs.get('params').get('range').get('upperbound')
    lowerbound = kwargs.get('params').get('range').get('lowerbound')
    res = []
   
    if kwargs.get('operation') == "insert_if_empty":
        size = null_mask.sum()
    elif kwargs.get('operation') == "insert":
        size = kwargs.get('rows')
        
    while(size > 0) :
        t = timeGenerator(upperbound, lowerbound)
        res.append(t)
        size-=1
        
    if kwargs.get('operation') == "insert_if_empty":
         df.loc[null_mask, col_name] = res
    elif kwargs.get('operation') == "insert":
        df[col_name] = res
    return df