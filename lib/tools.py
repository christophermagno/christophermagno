"""
Pandas tool lib for common functions/processes
"""

from collections import Counter

import pandas as pd
from spellchecker import SpellChecker

from . import logger, path


log = logger.getLogger(__name__)


def set_display_options(columns=None, rows=None):
    """
    Set some common options for display

    :param columns:
    :param rows:
    :return:
    """
    # Display options for pandas
    pd.set_option('display.max_columns', columns)
    pd.set_option('display.max_rows', rows)

def read_data(p, fn=pd.read_csv, encoding=None, strip_whitespaces=False,
              *args, **kwargs):
    """
    Helper function to read data and detect encoding of file if no encoding
    argument is passed.

    >>> data = read_data('dataset.csv', strip_whitespaces=True)

    :param p: Path to file
    :param fn: Function to read file
    :param encoding: Encoding of file
    :param strip_whitespaces: Clean whitespaces
    :return: DataFrame
    """

    # Get the encoding of the file if no encoding is found
    # Can take a while for large files
    encoding = encoding or path.detect_encoding(p)
    log.info(f'Encoding: {encoding}')

    # Run reach method
    df = fn(p, encoding=encoding, *args, **kwargs)

    # Strip whitespaces
    if strip_whitespaces:
        df = str_strip(df)

    return df

def export_data(p, df_export_fn, suffix='CLEAN', *args, **kwargs):
    """
    Export DataFrame to format of your choice using one of
    the DataFrame's to_* methods. Default is DataFrame.to_csv.

    >>> import pandas as pd
    >>>
    >>> df = pd.DataFrame([1, 2, 3], columns=['a', 'b', 'c'])
    >>> export_data(p)
    >>> export_data(p, df.to_json)
    >>> export_data(p, df.to_excel)

    :param p: Path to file
    :param df_export_fn: Dataframe method to execute (i.e. df.to_csv)
    :return:
    """
    export_path = path.get_cleaned_path(p, suffix=suffix)
    df_export_fn(export_path, *args, **kwargs)
    return export_path

def data_err_rate(df_or_s):
    """
    Given a DataFrame or Series, get the error rate based on null values to
    total size of the provided DataFrame/Series.

    >>> import pandas as pd
    >>> df = pd.DataFrame(
    >>>     {'A': [1,pd.NA,3],
    >>>     'B': [4,5,6],
    >>>     'C': [pd.NA,pd.NA,9],
    >>>     'D': [pd.NA,pd.NA,pd.NA]}
    >>> )
    >>>
    >>> data_err_rate(df)
    >>> data_err_rate(df['B'])
    >>> data_err_rate(df['C'])

    :param df_or_s: DataFrame or Series
    :return: float error rate
    """
    if isinstance(df_or_s, pd.DataFrame):
        # Get all null count
        return df_or_s.isnull().sum().sum()/df_or_s.size
    return df_or_s.isnull().sum()/df_or_s.size

def isrisky(df_or_s, err_rate=.75):
    """
    Given a  DataFrame or Series, check whether the Series is too error-prone
    to use based on the provided DataFrame and the `err_rate`.

    >>> import pandas as pd
    >>> df = pd.DataFrame(
    >>>     {'A': [1,pd.NA,3],
    >>>     'B': [4,5,6],
    >>>     'C': [pd.NA,pd.NA,9],
    >>>     'D': [pd.NA,pd.NA,pd.NA]}
    >>> )
    >>>
    >>> data_err_rate(df)
    >>> data_err_rate(df, err_rate=.75)
    >>> data_err_rate(df['C'])

    :param df_or_s: DataFrame or Series
    :param err_rate: Acceptable error rate
    :type err_rate: float
    :return: bool
    """
    return data_err_rate(df_or_s) > err_rate

def data_risks_rate(df, err_rate=None):
    """
    Given a DataFrame, check error rate of all Series in DataFrame. If argument
    `err_rate` is provided, only return Series that exceed rate.

    >>> import pandas as pd
    >>> df = pd.DataFrame(
    >>>     {'A': [1,pd.NA,3],
    >>>     'B': [4,5,6],
    >>>     'C': [pd.NA,pd.NA,9],
    >>>     'D': [pd.NA,pd.NA,pd.NA]}
    >>> )
    >>>
    >>> data_risks_rate(df)
    >>> data_risks_rate(df, err_rate=.75)

    :param df: Dataframe
    :param err_rate: Acceptable error rate
    :type err_rate: float
    :return: Series of error rates and their respective columns
    """

    risky = pd.Series(dtype=float)
    for col, series in df.items():
        if err_rate is None or isrisky(series, err_rate):
            risky[col] = data_err_rate(series)
    return risky

def get_filler_value(s, default=None, method='mean'):
    """
    Given a Series, get an appropriate filler value.
    # Todo: Make this a little more robust

    :param s: Series
    :param default:
    :param method:
    :return: filler value
    """

    if s.dtype == object or s.dtype == str:
        return 'Not Available'
    elif s.dtype == int or s.dtype == float:
        if method == 'mean':
            return s.mean()+1
        elif method == 'median':
            return s.median()
        elif method == 'min':
            return s.min()
        elif method == 'max':
            return s.max()
        raise AttributeError('')
    elif pd.core.dtypes.common.is_datetime64_dtype(s):
        return pd.Timestamp.max
    return default

def notnull(df_or_s):
    """
    Given either a DataFrame or a Series, return DataFrame/Series whose values
    are ALL not null.

    >>> import pandas as pd
    >>> df = pd.DataFrame(
    >>>     {'A': [1,pd.NA,3],
    >>>     'B': [4,5,6],
    >>>     'C': [pd.NA,pd.NA,9],
    >>>     'D': [pd.NA,pd.NA,pd.NA]}
    >>> )
    >>>
    >>> notnull(df)
    >>> notnull(df['C'])

    :param df_or_s: DataFrame or Series
    :return: DataFrame or Series of non-null values
    """
    if issubclass(type(df_or_s), pd.DataFrame):
        return df_or_s.loc[:, df_or_s.notnull().all(axis=0)]
    elif issubclass(type(df_or_s), pd.Series):
        return df_or_s.loc[df_or_s.notnull()]
    raise AttributeError(
        f'{type(df_or_s)} object has no attribute "notnull"')

def hasnull(df_or_s):
    """
    Given either a DataFrame or a Series, return DataFrame/Series whose values
    have any null values.

    >>> import pandas as pd
    >>> df = pd.DataFrame(
    >>>     {'A': [1,pd.NA,3],
    >>>     'B': [4,5,6],
    >>>     'C': [pd.NA,pd.NA,9],
    >>>     'D': [pd.NA,pd.NA,pd.NA]}
    >>> )
    >>>
    >>> hasnull(df)
    >>> hasnull(df['C'])

    :param df_or_s: DataFrame or Series
    :return: DataFrame or Series of null values
    """

    if issubclass(type(df_or_s), pd.DataFrame):
        null_cols = []
        for col, series in df_or_s.loc[:, df_or_s.isnull().any(axis=0)].items():
            if series.isnull().any():
                null_cols.append(col)

        # Return only rows that have nulls in them (ignore valid rows)
        rows = df_or_s.loc[df_or_s.isnull().any(axis=1)].index.to_list()
        return df_or_s.loc[rows, null_cols]

    elif issubclass(type(df_or_s), pd.Series):
        return df_or_s.loc[df_or_s.isnull()]

    raise AttributeError(
        f'{type(df_or_s)} object has no attribute "notnull"')

def allnull(df_or_s, axis=0):
    """
    Get columns and rows whose values are ALL null. These are essentially
    invalid rows/columns because we can't use them.

    For some reason.. axis in df.isnull().any(axis=*) is the opposite to
    everything else... 0 for columns and 1 for rows. Switching this function
    to keep with convention of 0 for rows and 1 for columns.

    >>> import pandas as pd
    >>> df = pd.DataFrame(
    >>>     {'A': [1,pd.NA,3],
    >>>     'B': [4,5,6],
    >>>     'C': [pd.NA,pd.NA,9],
    >>>     'D': [pd.NA,pd.NA,pd.NA]}
    >>> )
    >>>
    >>> allnull(df_or_s)
    >>> allnull(df_or_s.loc['C'])

    :param df_or_s: DataFrame
    :param axis: 0 for rows, 1 for columns
    :return: DataFrame or Series of null values
    """

    if isinstance(df_or_s, pd.DataFrame):
        if axis == 0:
            # Get all null rows
            if df_or_s.isnull().all(axis=1).sum():
                return df_or_s.loc[df_or_s.isnull().all(axis=1), :]
        elif axis == 1:
            # Get all null columns
            if df_or_s.isnull().all(axis=0).sum():
                return df_or_s.loc[:, df_or_s.isnull().all(axis=0)]
        return pd.DataFrame()
    else:
        # Get all null rows of Series
        if df_or_s.isnull().all():
            return df_or_s.loc[df_or_s.isnull().all()]
        return pd.Series()

def fillnull(df_or_s, err_rate=None, default=None, *args, **kwargs):
    """
    Given a Dataframe or Series, fill it with null values.


    >>> import pandas as pd
    >>> df = pd.DataFrame(
    >>>     {'A': [1,pd.NA,3],
    >>>     'B': [4,5,6],
    >>>     'C': [pd.NA,pd.NA,9],
    >>>     'D': [pd.NA,pd.NA,pd.NA]}
    >>> )
    >>>
    >>> fillnull(df['C'])
    >>> fillnull(df)


    :param df_or_s: Dataframe or Series
    :param err_rate: Acceptable error rate
    :type err_rate: float
    :param default: Default value
    :param args:
    :param kwargs:
    :return:
    """

    filler_values = {}
    # Copy or DataFrame or Series
    df_or_s_copy = df_or_s.copy()

    if isinstance(df_or_s_copy, pd.DataFrame):
        for col in df_or_s_copy.columns:
            if ((err_rate is None) or
                    (err_rate and not isrisky(df_or_s_copy[col], err_rate))):
                # Update filler_values dictionary
                filler_values[col] = get_filler_value(df_or_s_copy[col], default=default)

                # Update the Series
                df_or_s_copy[col] = df_or_s_copy[col].fillna(
                    filler_values[col],
                    *args,
                    **kwargs
                )

    else:

        if ((err_rate is None) or
                (err_rate and not isrisky(df_or_s_copy, err_rate))):
            # Update the filler_values dictionary
            filler_values[df_or_s_copy.name] = get_filler_value(df_or_s_copy, default=default)

            # Update the Series
            df_or_s_copy = df_or_s_copy.fillna(
                filler_values[df_or_s_copy.name],
                *args,
                **kwargs
            )

    return df_or_s_copy, filler_values

def null_info(df):
    """
    Get null info about the provided DataFrame.

    >>> import pandas as pd
    >>> df = pd.DataFrame(
    >>>     {'A': [1,pd.NA,3],
    >>>     'B': [4,5,6],
    >>>     'C': [pd.NA,pd.NA,9],
    >>>     'D': [pd.NA,pd.NA,pd.NA]}
    >>> )
    >>>
    >>> null_info(df)

    :param df: DataFrame
    :return:
    """

    # Get columns that contain null values and their indices
    nulls = hasnull(df)

    # Get all rows and columns whose values are ALL null
    all_null_rows = allnull(df, axis=0)
    all_null_columns = allnull(df, axis=1)

    log.info(f'{nulls.shape[1]}/{df.shape[1]} columns contain null values')
    log.info(f'{df.isnull().sum().sum()} total null values')
    if not all_null_rows.empty:
        log.info(f'Rows {all_null_rows.index.tolist()} contain null values')
    if not all_null_columns.empty:
        log.info(f'Columns {all_null_columns.columns.tolist()} contain null values')

    return nulls, all_null_rows, all_null_columns


def str_strip(df_or_s, to_strip=None):
    """
    Strip whitespaces from a DataFrame and its column names or Series and from
    the Series name if name is stored in class.

    This is assuming we ALWAYS want to strip any leading and trailing
    whitespaces (because who really needs those).

    :param df_or_s: DataFrame or Series
    :param to_strip: Strings to strip. If None, strips whitespace.
    :return: DataFrame or Series
    """

    # Copy object
    df_or_s_copy = df_or_s.copy()

    if isinstance(df_or_s_copy, pd.DataFrame):
        # Strip whitespaces from the columns
        df_or_s_copy.columns = df_or_s_copy.columns.str.strip()

        # Strip whitespaces from the Series
        for col in df_or_s_copy.select_dtypes(include=['object']).columns:
            df_or_s_copy[col] = df_or_s_copy[col].str.strip(to_strip)
    else:
        # Strip whitespaces from the Series
        df_or_s_copy = df_or_s_copy.str.strip(to_strip)

        # Strip whitespaces from the column name
        if df_or_s_copy.name:
            df_or_s_copy.name = df_or_s_copy.name.strip()

    return df_or_s_copy

def values_counter(s):
    """
    Get a count of all unique values in a Series.
    (Just a wrapper for the `collections.Counter` class)

    :param s: Series
    :return: Counter
    """
    return Counter(s)

def has_duplicates(s):
    """
    Check if a Series has duplicate values.

    :param s: Series
    :return: bool
    """
    return len(values_counter(s)) > 1

def _values_counter_series_info(series, maximum=20):
    """
    Helper function to log information of value counts for a Series.

    :param series: Series
    :param maximum: Maximum number of values before having to inspect the
    Series manually.
    :return:
    """
    counter = values_counter(series)
    log.info(f'{series.name}: {series.dtype} BEGIN')
    if len(counter) < maximum:
        for value, count in counter.items():
            log.info(f'\t{value}: {count}')
        log.info(f'{series.name}: {series.dtype} END\n')
    else:
        log.info(
            f'{series.name}: Has more than {maximum} values ({len(counter)} values)\n')

def values_counter_info(df_or_s, max_values=20):
    """
    Get information of values for a DataFrame or Series.

    :param df_or_s: DataFrame or Series
    :param max_values: Maximum number of values before ignoring and having to
    inspect manually.
    """

    if isinstance(df_or_s, pd.DataFrame):
        for column, series in df_or_s.items():
            _values_counter_series_info(series, max_values)
    else:
        _values_counter_series_info(df_or_s, max_values)


def min_mean_median_max(s):
    """
    Just a helper function to get min, mean, median, and max values from
    a Series.

    :param s: Series
    :return:
    """
    return s.min(), s.mean(), s.median(), s.max()

def dtypes(df_or_s, flatten=False):
    """
    Get dtypes for a DataFrame or Series and return a DataFrame or Series
    of the same shape with data types for its values.

    :param df_or_s: DataFrame or Series
    :param flatten: Flatten to a Series of just the data types found
    :return: DataFrame or Series
    """

    df = df_or_s.copy()
    types = set()

    if isinstance(df_or_s, pd.DataFrame):

        for col, series in df_or_s.items():
            # The different types per index of series
            _types = []
            for index, value in series.items():
                # Get the value data type of series index
                _types.append(str(type(value)))
                if flatten:
                    types.add(str(type(value)))

            # Assign them to the return DataFrame
            df.loc[:, col] = _types
    else:
        for index, value in df_or_s.items():
            # Get the value data type of series index
            df.loc[index] = str(type(value))
            if flatten:
                types.add(str(type(value)))

    return pd.Series(list(types)) if flatten else df

def dtypes_counter(df_or_s):
    """
    Get a count of data types for a DataFrame or Series. Returns a Dataframe
    or Series with the data types as its index and a count of each type for
    its values.

    :param df_or_s: DataFrame or Series
    :return: Dataframe or Series
    """

    types = dtypes(df_or_s, flatten=True)
    if isinstance(df_or_s, pd.DataFrame):
        # Create return DataFrame
        result = pd.DataFrame(index=types, columns=df_or_s.columns)

        # Iterate through the data types found
        for col, series in dtypes(df_or_s).items():
            # Get duplicates count
            counter = values_counter(series)
            for value, count in counter.items():
                result.loc[value, col] = count
    else:
        # Create turn Series
        result = pd.Series(index=types, name=df_or_s.name)

        # Get duplicates count
        counter = values_counter(dtypes(df_or_s))
        for value, count in counter.items():
            result.loc[value] = count

    result = result.fillna(0)
    result = result.astype(int)
    return result

def has_different_dtypes(df_or_s):
    """
    Check if DataFrame or Series has different dtypes.

    :param df_or_s: DataFrame or Series
    :return: Series of bools whether a DataFrame or Series has different
    dtypes.
    """
    result = pd.Series()
    types = dtypes(df_or_s)

    if isinstance(df_or_s, pd.DataFrame):
        for col, series in types.items():
            result[col] = len(series.unique()) > 1
    else:
        return len(types.unique()) > 1
    return result


def check_typos(txt, split=None):
    """
    Check if a string contains typos.

    :param txt:
    :param split:
    :return:
    """
    spell = SpellChecker()
    return spell.unknown(txt.split(split))


def typos_corrections(misspelled):
    """

    :param misspelled:
    :return:
    """
    spell = SpellChecker()
    return {spell.correction(misspell) for misspell in misspelled}
