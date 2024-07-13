import os

import pandas as pd
pd.options.mode.copy_on_write = True
from jgtutils.jgtconstants import VOLUME
# import warnings
# warnings.filterwarnings("ignore", category=FutureWarning)
# #SettingWithCopyWarning
# warnings.filterwarnings("ignore", category=pd.errors.PerformanceWarning)
# warnings.filterwarnings("ignore", category=pd.errors.SettingWithCopyWarning)

def drop_columns_if_exists(df:pd.DataFrame, columns_to_drop=None, inplace=True):
  if columns_to_drop is not None:
    if not inplace:
      df = df.copy()
    for col in columns_to_drop:
      if col in df.columns:
        df.drop(columns=[col], inplace=True)
  return df

def dropna_volume_in_dataframe(df:pd.DataFrame, volume_colname="", inplace=True):
  if volume_colname == "":
    volume_colname = VOLUME
  if not inplace:
    df = df.copy()
  if volume_colname in df.columns:
    df = df[df[volume_colname] != 0]
  return df


def convert_col_to_int(df:pd.DataFrame, colname, inplace=True):
  if not inplace:
    df = df.copy()
  if colname in df.columns:
    df[colname] = df[colname].astype(int)
  return df


def get_basedir(use_full,ns):
    if use_full:
        bd=os.getenv("JGTPY_DATA_FULL")
        if bd is None:
            raise Exception("JGTPY_DATA_FULL environment variable is not set.")
    else:
        bd=os.getenv("JGTPY_DATA")
        if bd is None:
            raise Exception("JGTPY_DATA environment variable is not set.")
    fulldir=os.path.join(bd,ns)
    #mkdir -p fulldir
    os.makedirs(fulldir, exist_ok=True)
    return fulldir

def get_outfile_fullpath(i,t,use_full,ns,midfix="",suffix="",ext="csv"):
  save_basedir=get_basedir(use_full,ns)
  ifn=i.replace("/","-")
  output_filename = f"{ifn}_{t}_{midfix}{suffix}.{ext}"
  return os.path.join(save_basedir,output_filename.replace("__","_").replace("_.","."))