def replacement(**kwargs):
    """
    Summary:
        replace a value to other, in a column

    Args:
        params (dict): holds the arguments on which stratgies are generated.
        df (padans.DataFrame): an empty dataframe or a dataframe which is generated from previous strategy or relation.
        colName (str): column for which the data to be generate.
        from_value (str): value which is being replaced
        to_value (str): new value to placed

    Returns:
        df (pandas.DataFrame): updted dataframe.
    """
    df = kwargs.get('df')
    colName = kwargs.get('col_name')
    mask = kwargs.get('mask',True)
    df[colName] = df[colName].replace(kwargs.get('params').get('from_value'), kwargs.get('params').get('to_value'))
    return df