import numpy as np
def distributed_choice_strategy(**kwargs):
    """
    Summary:
        generates a list of `choices` based on some distribution

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
    col_name = kwargs.get('col_name')
    null_mask = kwargs.get('mask',False) & df[col_name].isnull()

    if sum(kwargs.get('params').get('choices').values())==100:
        choices_with_dist = {}
        choices = []
        params = kwargs.get('params')
        for key in params.get('choices'):
            choices_with_dist[key] = (kwargs.get('params').get('choices')[key]/100)
            choices.append(key)
        already_present = df.value_counts().to_dict()
        for i in choices:
            if i in already_present.keys():
                choices_with_dist[i] -= already_present[i]

    else :
        print("Error : Invalid distribution given, distributions sum should be equal to 100, but got {}".format(sum(kwargs.get('params').get('choices').values())))
    if kwargs.get('operation') == "insert_if_empty" :
        new_generated = np.random.choice(choices, size=null_mask.sum(), p=list(choices_with_dist.values()))
        df.loc[null_mask, col_name] = new_generated
    elif kwargs.get('operation') == "insert":
        new_generated = np.random.choice(choices, size=kwargs.get('rows'), p=list(choices_with_dist.values()))
        df[col_name] = new_generated
    return df