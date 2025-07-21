"""
Utility for managing intermediate columns in data generation.

Intermediate columns are used for internal calculations and transformations
but are not included in the final output.
"""


def mark_as_intermediate(df, column_name):
    """
    Mark a column as intermediate (to be excluded from final output)

    Args:
        df (pandas.DataFrame): The dataframe containing the column
        column_name (str): The name of the column to mark as intermediate

    Returns:
        pandas.DataFrame: The same dataframe with metadata updated
    """
    if not hasattr(df, "_intermediate_columns"):
        df._intermediate_columns = set()

    df._intermediate_columns.add(column_name)
    return df


def get_intermediate_columns(df):
    """
    Get the list of intermediate columns in a dataframe

    Args:
        df (pandas.DataFrame): The dataframe to check

    Returns:
        set: Set of column names marked as intermediate
    """
    if not hasattr(df, "_intermediate_columns"):
        df._intermediate_columns = set()

    return df._intermediate_columns


def filter_intermediate_columns(df):
    """
    Remove intermediate columns from the dataframe

    Args:
        df (pandas.DataFrame): The dataframe to filter

    Returns:
        pandas.DataFrame: A new dataframe with intermediate columns removed
    """
    if not hasattr(df, "_intermediate_columns"):
        return df

    intermediate_cols = get_intermediate_columns(df)
    if not intermediate_cols:
        return df

    # Filter out intermediate columns
    return df.drop(columns=list(intermediate_cols))
