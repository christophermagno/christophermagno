"""
Pandas tool library for common functions/processes
"""

import pandas as pd

from . import logger, path

log = logger.getLogger(__name__)


class DataTask(pd.DataFrame):
    """
    Helper class to handle tasks
    """

    _internal_names = pd.DataFrame._internal_names + ['backups']
    _internal_names_set = set(_internal_names)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.backups = []

    @property
    def _constructor(self):
        return DataTask

    def backup(self):
        copy = self.copy()
        self.backups.append(copy)
        return copy


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

def read_data(p, fn=pd.read_csv, *args, **kwargs):
    """
    Helper function to read data and detect encoding of file if no encoding argument is passed.

    :param p: Path to file
    :param fn: Function to read file
    :param args:
    :param kwargs:
    :return: DataFrame
    """

    encoding = kwargs.pop('encoding', path.detect_encoding(p))
    log.debug(f'Encoding: {encoding}')

    return fn(p, encoding=encoding, *args, **kwargs)

def notnull(df_or_s):
    """
    Given either a DataFrame or a Series, get all non-null values

    :param df_or_s: DataFrame or Series
    :return: DataFrame or Series of non-null values
    """
    if issubclass(type(df_or_s), pd.DataFrame):
        return df_or_s.loc[:, df_or_s.notnull().all(axis=0)]
    elif issubclass(type(df_or_s), pd.Series):
        return df_or_s[df_or_s.notnull()]
    raise AttributeError(
        f'{type(df_or_s)} object has no attribute "notnull"')

def isnull(df_or_s):
    """
    Given either a DataFrame or a Series, get all null values

    :param df_or_s: DataFrame or Series
    :return: DataFrame or Series of null values
    """
    if issubclass(type(df_or_s), pd.DataFrame):
        return df_or_s.loc[:, df_or_s.isnull().any(axis=0)]
    elif issubclass(type(df_or_s), pd.Series):
        return df_or_s[df_or_s.isnull()]
    raise AttributeError(
        f'{type(df_or_s)} object has no attribute "notnull"')

def get_null_indices(df):
    """
    Get indices of non-null values in a DataFrame.
    # Todo: Is this needed if i have the notnull and null fns?

    :param df: DataFrame
    :return: dictionary of columns and the indices of non-null values
    """
    df_null_idx = {}
    for column in df.columns:
        indices = isnull(df[column]).index
        if not indices.empty:
            df_null_idx[column] = indices
    return df_null_idx

def get_all_nulls(df):
    """
    Get columns and rows whose values are ALL null

    :param df: DataFrame
    :return: Tuple of that contain all null values
    """
    null_columns = df.loc[:, df.isnull().all(axis=0)].columns
    null_rows = df[df.isnull().all(axis=1)].index
    return null_columns, null_rows

def get_filler_value(s):
    """
    Given a Series, get an appropriate filler value
    # Todo: Make this a little more robust

    :param s: Series
    :return: filler value
    """
    if s.dtype == object or s.dtype == str:
        return 'Not Available'
    elif s.dtype == int or s.dtype == float:
        return s.max()+1
    elif pd.core.dtypes.common.is_datetime64_dtype(s):
        return pd.Timestamp.max
    return None

def series_err_rate(df, s):
    """
    Given a Series, get the error rate based on null values to total index of
    the provided DataFrame

    :param df: DataFrame
    :param s: Series
    :return: float error rate
    """
    if isinstance(s, str):
        s = df[s]
    return s.isnull().sum()/len(df)

def series_risk(df, s, err_pct=.75):
    """
    Given a Series, check whether the Series is too error-prone
    to use based on the provided DataFrame

    :param df: DataFrame
    :param s: Series
    :param err_pct: Acceptable error rate
    :return: bool
    """
    return series_err_rate(df, s) > err_pct


def strip_whitespaces(s):
    pass

