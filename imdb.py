import pandas as pd
from pathlib import Path
import logging

import library

log = library.logger.getLogger(__name__)
log.setLevel(logging.INFO)

# Get the path to the csv dataset
path = Path().cwd().joinpath('imdb', 'messy_imdb_dataset.csv')

# Get encoding of csv
encoding = library.path.detect_encoding(path)
log.debug(f'Detecting Encoding {encoding}')

# Read the csv into a Pandas Dataframe
df = pd.read_csv(path, sep=';', encoding=encoding)

# Getting the general info to see what we're working with
log.info(f'General Info {df.info()}')

# Checking for null indices and rows
na_items = pd.isnull(df).sum()
log.debug(f'na_items {na_items}')
log.debug(df.columns)
null_indices = library.tools.get_null_indices(df)
log.info(f'Null indices {len(df.columns)}/{len(null_indices)}\n{null_indices}')
log.info(f'Null rows {library.tools.get_null_rows(df)}')


