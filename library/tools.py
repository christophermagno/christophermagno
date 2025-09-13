import pandas as pd

from . import logger

log = logger.getLogger(__name__)


def set_display_options(columns=None, rows=None):
    """
    Set some common options for display

    :param columns:
    :param rows:
    :return:
    """
    # Display options for pandas
    pd.options.display.max_columns = columns
    pd.options.display.max_rows = rows

def backup(df):
    """
    Create a backup of the given dataframe.

    :param df: Pandas DataFrame
    :type df: pandas.DataFrame
    :return: Copy of dataframe
    """
    return df.copy()

def isna(df):
    return pd.isna(df).sum()

def _get_null_indices(df, key=None, axis=1):
    if key is None:
        return df[df.isnull().any(axis=axis)].index.tolist()
    return df[df[key].isnull()].index.tolist()

def get_null_indices(df):
    """
    Need to fix

    :param df:
    :return:
    """
    df_null_idx = {}
    for column in df.columns:
        indices = _get_null_indices(df, column)
        if indices:
            df_null_idx[column] = indices
    return df_null_idx

def get_null_columns(df):
    result = []
    cols = df.isnull().all(axis=0)
    for key, col in zip(df.columns, cols):
        if col:
            result.append(key)
    return result

def get_null_rows(df):
    return df[df.isnull().all(axis=1)].index.tolist()

def get_nulls(df):
    return get_null_columns(df), get_null_rows(df)

def drop_nulls(df, x):
    if isinstance(x, int):
        return df.drop(x)
    elif isinstance(x, str):
        return df.drop(x, axis=1)

    raise NotImplementedError('Unsupported type')

def get_unique_values(s):
    return set(s.tolist())

