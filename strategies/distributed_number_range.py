import numpy as np
from utils.get_numbers import get_numbers
def distributed_number_range(**kwargs):
    """
    Summary:
        generates a list of random integer value from a range based on some distribution

    Args:
        params (dict): holds the arguments on which stratgies are generated.
        df (padans.DataFrame): an empty dataframe or a dataframe which is generated from previous strategy or relation.
        operation (str): type operating the generated to the column.
        mask (pandas.Series, optional): a list of booleans to generate data for some specific rows, came from a relation
          Defaults to `False`.
        colName (str): column for which the data to be generate.
        rows (int): number of rows to generate.

    Returns:
        df (pandas.DataFrame): updted dataframe.
    """
    
    df = kwargs.get('df')
    colName = kwargs.get('col_name')
    null_mask = kwargs.get('mask',False) & df[colName].isnull()
    dist_sum = 0
    ranges =[]
    for i in kwargs.get('params').get("ranges"):
        t = [i['lowerbound'],i['upperbound'],i['distribution']]
        ranges.append(tuple(t))
        dist_sum += i['distribution']
    if dist_sum!=100:
        print("Error : Invalid distribution given, distributions sum should be equal to 100, but got {}".format(dist_sum))
        return df

    generated = []
    if kwargs.get('operation') == "insert":
        size = kwargs.get('rows')
    elif kwargs.get('operation') == "insert_if_empty":
        size = null_mask.sum() 
    for r in ranges:
        x = get_numbers(r[0],r[1], int(size*r[2]/100))
        generated.extend(x)

    np.random.shuffle(generated)
    if kwargs.get('operation') == "insert":
        df[colName] = generated
    elif kwargs.get('operation') == "insert_if_empty":
        while(len(generated)!=null_mask.sum()):
            generated.append(generated[-1]) 
        df.loc[null_mask, colName] = generated
    return df