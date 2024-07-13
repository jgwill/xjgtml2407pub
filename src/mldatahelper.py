
"""
Here we would have common data functions such as : write_patternname_columns_list and read_patternname_columns_list

Therefore: 
 * ttfcli would  
"""
import pandas as pd
from mlutils import get_basedir,get_outfile_fullpath
from mlconstants import TTF_NOT_NEEDED_COLUMNS_LIST, default_columns_to_get_from_higher_tf,TTF_DTYPE_DEFINITION

#ttf


def get_ttf_outfile_fullpath(i,t,use_full=True,suffix="",ns="ttf",midfix="ttf"):
  return get_outfile_fullpath(i,t,use_full,ns,midfix=midfix,suffix=suffix)


def write_patternname_columns_list(i,t,use_full=True,columns_list_from_higher_tf=None,midfix="ttf",ns="ttf",suffix="_columns"):
  if columns_list_from_higher_tf is None:
    columns_list_from_higher_tf = default_columns_to_get_from_higher_tf
  output_filename=get_ttf_outfile_fullpath(i,t,use_full,suffix=suffix,midfix=midfix,ns=ns)
  with open(output_filename, 'w') as f:
    for item in columns_list_from_higher_tf:
      f.write("%s\n" % item)
  print(f"    Pattern:{midfix} Output columns :'{output_filename}'")
  return output_filename

def read_patternname_columns_list(i,t,use_full=True,midfix="ttf",ns="ttf",suffix="_columns")->list:
  output_filename=get_ttf_outfile_fullpath(i,t,use_full,suffix=suffix,midfix=midfix,ns=ns)
  with open(output_filename, 'r') as f:
    columns_list_from_higher_tf = f.readlines()
  columns_list_from_higher_tf = [x.strip() for x in columns_list_from_higher_tf]
  return columns_list_from_higher_tf

def create_filebase_from_patternname(i,t,midfix="ttf")->str:
  ifn=i.replace("/","-")
  output_filename = f"{ifn}_{t}_{midfix}"
  return output_filename.replace("__","_")

def create_filensbase_from_patternname(i,t,midfix="ttf",ns="ttf")->str:
  filebase=create_filebase_from_patternname(i,t,midfix)
  return f"{ns}/{filebase}"


#@STCIssue Future Generic we would use for other patterns (ex.  targets/mx)
def read_pattern_raw(i, t,midfix,ns, use_full=True)->pd.DataFrame:
  patternname=midfix
  outfile_fullpath=get_outfile_fullpath(i,t,use_full,ns,midfix=patternname)
  df=pd.read_csv(outfile_fullpath, index_col=0,dtype=TTF_DTYPE_DEFINITION)
  return df


def read_ttf_pattern_raw(i, t, use_full=True,midfix="ttf",ns="ttf")->pd.DataFrame:
  patternname=midfix
  ttf_outfile_fullpath=get_ttf_outfile_fullpath(i,t,midfix=patternname,ns=ns,use_full=use_full)
  df=pd.read_csv(ttf_outfile_fullpath, index_col=0,dtype=TTF_DTYPE_DEFINITION)
  return df
  

def read_ttf_feature_columns_pattern(i, t, use_full=True,midfix="ttf",ns="ttf"):
  patternname=midfix
  df=read_ttf_pattern_raw(i, t, use_full=use_full,midfix=patternname,ns=ns)
  pattern_columns_list:list=read_patternname_columns_list(i,t,midfix=patternname,ns=ns)
  #keep only the columns from the list
  df=df[pattern_columns_list]
  return df
  