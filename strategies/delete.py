import numpy as np
def deletion_strategy(**kwargs):
    """
    Summary:
        Removes the data from a column

    Args:
        df (padans.DataFrame): an empty dataframe or a dataframe which is generated from previous strategy or relation.
        operation (str): type operating the generated to the column.
        mask (pandas.Series, optional): a list of booleans to delete data of some specific rows, came from a relation
          Defaults to `True`, will delete all the data if mask is not supplied.
        colName (str): column for which the data to be generate.
    Returns:
        df (pandas.DataFrame): updted dataframe.
    """
    df = kwargs.get('df')
    if kwargs.get('operation') == 'insert':
       df.loc[kwargs.get('mask', True), kwargs.get('col_name')] = kwargs.get('params').get(("value_to_replace"),np.nan )
    else :
        print("Error Invalid Operation {}".format(kwargs.get('operation')))
    return df