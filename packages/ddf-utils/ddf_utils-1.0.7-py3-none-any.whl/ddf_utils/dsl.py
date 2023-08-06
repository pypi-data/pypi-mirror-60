# -*- coding: utf-8 -*-

"""A DSL for ETL
"""

# this lib is made to use as wildcard import
__all__ = ['has_duplicates']

import pandas as pd
import numpy as np

def has_duplicates(df, subset):
    """assert there is no duplicated key for a dataframe."""
    return np.any(df.duplicated(subset=subset))


## Planning ...

# I guess we can move dsl.py into factory/ module.

# 1. downloading all files.
# 2. general functions to modify csv/excel files.
# 3. general functions to detect errors in csv/excel files.
# 4. generating DDF concepts/entities/datapoints from those files.
