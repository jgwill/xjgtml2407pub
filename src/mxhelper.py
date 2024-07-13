import numpy as np
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from jgtutils.jgtconstants import VOLUME
from mlconstants import TARGET
from mlconstants import MFI_DEFAULT_COLNAME,ZONE_DEFAULT_COLNAME
import mfihelper2 as mfihelper
from mfihelper2 import get_mfi_features_column_list_by_timeframe
import anhelper
from mxconstants import readmx_drop_columns_arr

import jtc
import pandas as pd

def _read_mx_and_prep_02(i,t,drop_columns_arr = None,dropna_volume=True):
 
    
  df=jtc.readMXFile(instrument=i,timeframe=t)
  try:
    if drop_columns_arr is not None:
      for col in drop_columns_arr:
        if col in df.columns:
          df.drop(columns=[col],inplace=True)    
  except:
    pass
  #drop rows with Volume=0
  if dropna_volume:
    df=df[df[VOLUME]!=0]
  return df





# utility
def mk_safename_namespace_path(i,t,x_fn_namespace,sub_namespace,suffix_base="",out_dir="",bs=""):
  ifn=i.replace('/','-')
  bs = "_sell" if bs=="S" else "_buy" if bs=="B" else ""

  fn=f"{x_fn_namespace}_{sub_namespace}_{ifn}_{t}{suffix_base}{bs}.csv"
  if out_dir!="":
    fn=os.path.join(out_dir,fn)
    #make sure the directory exists   
    os.makedirs(os.path.dirname(fn), exist_ok=True)
  return fn


from mxconstants import mx_common_columns
def _extract_mfi_structure_dataframe(mxdf,t,common_columns = mx_common_columns):
  
  mfi_feature_columns_list = get_mfi_features_column_list_by_timeframe(t)
  print("Extracted MFI Features columns list:",mfi_feature_columns_list)
  combined_columns = mfi_feature_columns_list+common_columns
  df_with_features=mxdf[combined_columns]
  return df_with_features

#@STCIssue Location could move to a Common to MX and Reality analysis (mfihelper??)
def _add_lag_features_to_dataframe(df: pd.DataFrame, t, lag_period=1, total_lagging_periods=5,out_lag_midfix_str='_lag_',inplace=True):
  if not inplace:
    df = df.copy()
  columns_to_add_lags_to = get_mfi_features_column_list_by_timeframe(t, MFI_DEFAULT_COLNAME)
  #columns_to_add_lags_to.append(MFI_DEFAULT_COLNAME) #We want a lag for the current TF
  
  anhelper.add_lagging_columns(df, columns_to_add_lags_to, lag_period, total_lagging_periods, out_lag_midfix_str)
  #convert columns_to_add_lags_to to type int
  # for col in columns_to_add_lags_to: #@STCIssue Isn't that done already ???  Or it thinks they are Double !!!!
  #   for j in range(1, total_lagging_periods + 1):
  #     df[f'{col}{out_lag_midfix_str}{j}']=df[f'{col}{out_lag_midfix_str}{j}'].astype(int)
  
  return df




  
def wf_get_mxdf_and_add_mfi_features_to_df(i,t,common_columns = [MFI_DEFAULT_COLNAME,TARGET, 'vaoc','fdb'],drop_columns_arr = None)->pd.DataFrame:
  if drop_columns_arr is None:
    drop_columns_arr = readmx_drop_columns_arr
    
  df=_read_mx_and_prep_02(i,t,drop_columns_arr)
  mfihelper.column_mfi_str_in_dataframe_to_id(df,t) #@STCIssue WE WONT NEED THIS when using MFI_SIGNAL instead of MFI_VAL
  _extract_mfi_structure_dataframe(df,t,common_columns)
  #add lag
  _add_lag_features_to_dataframe(df,t)
  return df




def _select_where_target_is_not_zero(df, target_colname='target'):
  dfresult=df[df[target_colname]!=0].copy()
  return dfresult


def get_analysis_data_240702(i,t,bs,target_colname='target',signal_column='fdb',drop_signal_column=True,signal_column_sell_value=-1,signal_column_buy_value=1,quiet=False):
  """
  Get the analysis data for the prototype. This is a wrapper function that calls the other functions in this module. 
  """
  df=wf_get_mxdf_and_add_mfi_features_to_df(i,t)
  df=_select_where_target_is_not_zero(df,target_colname)
  if bs=='S' or bs=='s' or bs=='sell' or bs=='SELL' or bs=='Sell':
    print('Selecting sell signals') if not quiet else None
    df=df[df[signal_column]==signal_column_sell_value]
  else:
    df=df[df[signal_column]==signal_column_buy_value]
    print('Selecting buy signals') if not quiet else None
  if drop_signal_column:
    df.drop(columns=[signal_column],inplace=True)
  return df

def _drop_column_part01(df,columnsToDrop = ['vaos','vaob','vaosc','vaobc','fh8', 'fl8', 'fh89', 'fl89','mfi','aoaz','aobz','sz','bz','acb','acs','ss','sb','mfi_sq', 'mfi_green','mfi_fade', 'mfi_fake','tmax', 'tmin', 'p', 'l'],inplace=True):
  """
  Drop columns from the dataframe part 01 of our prototype
  
  Parameters:
  df: pd.DataFrame - the dataframe to drop columns from
  columnsToDrop: list - the list of columns to drop
  
  Returns:
  pd.DataFrame - the dataframe with the columns dropped
  """
  if not inplace:
    df = df.copy()
  for col in columnsToDrop:
    if col in df.columns:
      df.drop(columns=[col],inplace=True)
  return df

def _drop_column_part02(df,more2dropcolumns=['Volume', 'Open', 'High', 'Low', 'Close', 'Median', 'ac', 'mfi_sig', 'zcol_M1', 'zcol_W1', 'ao_W1', 'vaoc','zlc', 'zlcb', 'zlcs', 'zcol','fh', 'fl', 'fh3', 'fl3', 'fh5', 'fl5', 'fdbb', 'fdbs','jaw', 'teeth', 'lips', 'bjaw', 'bteeth', 'blips', 'tjaw','tteeth', 'tlips','zcol_D1'],inplace=True):
  """
  Drop columns from the dataframe part 02 of our prototype
  
  Parameters:
  df: pd.DataFrame - the dataframe to drop columns from
  more2dropcolumns: list - the list of columns to drop
  
  Returns:
  pd.DataFrame - the dataframe with the columns dropped
  """
  if not inplace:
    df = df.copy()
  for col in more2dropcolumns:
    if col in df.columns:
      df.drop(columns=[col],inplace=True)
  return df

def get_analysis_data_240702_cleaned(i,t,bs,target_colname='target',signal_column='fdb',drop_signal_column=True):
  """Get the analysis data for the prototype. This is a wrapper function that calls the other functions in this module. It also drops columns that are not needed for the prototype.
  """
  df=get_analysis_data_240702(i,t,bs,target_colname,signal_column,drop_signal_column)
  df=_drop_column_part01(df)
  df=_drop_column_part02(df)
  return df

