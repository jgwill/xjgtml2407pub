# %% Imports
import pandas as pd
pd.options.mode.copy_on_write = True
import numpy as np
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from jgtpy import JGTPDSP as pds
import tlid


from jgtutils.jgtos import get_data_path
from mlutils import get_outfile_fullpath
from mlconstants import MX_NS

#from jgtutils.jgtconstants import *
from jgtutils.jgtconstants import VECTOR_AO_FDBS, VECTOR_AO_FDBB, VECTOR_AO_FDBS_COUNT, VECTOR_AO_FDBB_COUNT, VECTOR_AO_FDB_COUNT,ML_DEFAULT_COLUMNS_TO_KEEP,FDB_TARGET ,FDBB,FDBS,AO,ZLCB,ZLCS,OPEN,LOW,CLOSE,HIGH

# %% Functions
__TARGET=FDB_TARGET
def set_target_variable_name(target_name):
    global __TARGET
    __TARGET = target_name

def _crop_dataframe(df, crop_last_dt: str = None, crop_start_dt: str = None):
    if crop_last_dt is not None:
        df = df[df.index <= crop_last_dt]
    if crop_start_dt is not None:
        df = df[df.index >= crop_start_dt]
    return df


def calculate_target_variable_min_max(
    dfsrc,
    crop_last_dt=None,
    crop_start_dt=None,
    WINDOW_MIN=1,
    WINDOW_MAX=150,
    set_index=True,
    rounder=4,
    pipsize=-1,
):
    df = dfsrc.copy()
    
    
    if crop_last_dt is not None or crop_start_dt is not None:
        df = _crop_dataframe(df, crop_last_dt, crop_start_dt)

    # reset index before we iterate
    try:
        df.reset_index(drop=False, inplace=True)
    except:
        pass

    # Initialize the tmax and tmin columns with NaN values
    df["tmax"] = float("nan")
    df["tmin"] = float("nan")
    df["p"] = float("nan")
    df["l"] = float("nan")
    df[__TARGET] = float("nan")

    # Calculate the maximum and minimum Close value in the window range for each row
    for i in range(WINDOW_MIN, len(df) - WINDOW_MAX):
        # FDBS
        if df.loc[i, "fdbs"] == 1.0:
            df.loc[i, "tmax"] = df.loc[i : i + WINDOW_MAX, "Close"].min()
            df.loc[i, "tmin"] = df.loc[i : i + WINDOW_MAX, "Close"].max()

            if df.loc[i, "High"] < df.loc[i, "tmin"]:
                df.loc[i, "l"] = round(df.loc[i, "High"] - df.loc[i, "Low"], rounder)
                df.loc[i, __TARGET] = round(
                    -1 * (df.loc[i, "High"] - df.loc[i, "Low"]), rounder
                )
            else:
                df.loc[i, "p"] = round(df.loc[i, "Low"] - df.loc[i, "tmax"], rounder)
                df.loc[i, __TARGET] = round(
                    df.loc[i, "Low"] - df.loc[i, "tmax"], rounder
                )
        # FDBB
        if df.loc[i, "fdbb"] == 1.0:
            df.loc[i, "tmax"] = df.loc[i : i + WINDOW_MAX, "Close"].max()
            df.loc[i, "tmin"] = df.loc[i : i + WINDOW_MAX, "Close"].min()

            if df.loc[i, "Low"] > df.loc[i, "tmin"]:
                df.loc[i, "l"] = round(df.loc[i, "High"] - df.loc[i, "Low"], rounder)
                df.loc[i, __TARGET] = round(
                    -1 * (df.loc[i, "High"] - df.loc[i, "Low"]), rounder
                )
            else:
                df.loc[i, "p"] = round(df.loc[i, "tmax"] - df.loc[i, "High"], rounder)
                df.loc[i, __TARGET] = round(
                    df.loc[i, "tmax"] - df.loc[i, "High"], rounder
                )

    # Fill NaN with zero for columns tmax and tmin
    df["tmax"] = df["tmax"].fillna(0)
    df["tmin"] = df["tmin"].fillna(0)
    df["p"] = df["p"].fillna(0)
    df["l"] = df["l"].fillna(0)
    df[__TARGET] = df[__TARGET].fillna(0)
    # After calculating the 'target' column
    if pipsize != -1:
        df[__TARGET] = df[__TARGET] / pipsize

    # @q Maybe set backnthe index !??
    if set_index:
        #parse Date as datetime
        df['Date'] = pd.to_datetime(df['Date'])
        df.set_index("Date", inplace=True)
        
    return df


def pto_target_calculation(
    i:str,
    t:str,
    crop_start_dt=None,
    crop_end_dt=None,
    tlid_tag=None,
    WINDOW_MIN:int=1,
    WINDOW_MAX:int=150,
    output_report_dir=None,
    pto_vec_fdb_ao_vector_window_flag=True,
    drop_calc_col=True,
    write_reporting=True,
    calc_col_to_drop_names=["tmax", "tmin", "p", "l"],
    sel_1_suffix="_sel",
    sel_1_keeping_columns=[HIGH,LOW, FDBS, FDBB, "tmax", "tmin", "p", "l", __TARGET],
    sel_2_suffix="_tnd",
    sel_2_keeping_columns=[OPEN, HIGH, LOW, CLOSE, FDBS, FDBB, __TARGET],
    pto_vec_fdb_ao_out_s_name=VECTOR_AO_FDBS,#"vaos",
    pto_vec_fdb_ao_out_b_name=VECTOR_AO_FDBB,#"vaob",
    pto_vec_fdb_ao_in_s_sig_name=FDBS,#"fdbs",
    pto_vec_fdb_ao_in_s_win_end_sig_name=ZLCB,#"zlcb",
    pto_vec_fdb_ao_in_b_sig_name=FDBB,#"fdbb",
    pto_vec_fdb_ao_in_b_win_end_sig_name=ZLCS,#"zlcs",
    pto_vec_fdb_ao_in_t_val_name=AO,#"ao",
    additional_columns_to_drop=None,
    selected_columns_to_keep=None,
    save_outputs=True,
    only_if_target_exist_n_not_zero=True,
    use_fresh=True,
    keep_bid_ask=True,
    regenerate_cds=False,
    gator_oscillator_flag=False,
    mfi_flag=True,
    balligator_flag=False,
    balligator_period_jaws=89,
    largest_fractal_period=89,
    talligator_flag=False,
    talligator_period_jaws=377,
    use_ttf=True,
    ttf_midfix="ttf",
    drop_vector_ao_intermediate_array=True
):
    """
    Prototype Calculation of target based on the given POV parameters and output to file with report.

    Args:
        i (int): The value of i.get_fdb_ao_vector_window
        t (int): The value of t.
        crop_start_dt (datetime, optional): The start date for cropping. Defaults to None.
        crop_end_dt (datetime, optional): The end date for cropping. Defaults to None.
        tlid_tag (str, optional): The TLID tag. Defaults to None.
        output_report_dir (str, optional): The output report directory. Defaults to None.
        process_fdb_ao_vector_window (bool, optional): If True, process the fdb_ao_vector_window. Defaults to False.
        drop_calc_col (bool, optional): If True, drop the calculated columns. Defaults to False.
        write_reporting (bool, optional): If True, write the reporting. Defaults to True.
        calc_col_to_drop_names (list, optional): The list of column names to drop. Defaults to ["tmax", "tmin", "p", "l"].
        sel_1_suffix (str, optional): The suffix for the first selection. Defaults to "_sel".
        sel_1_keeping_columns (list, optional): The list of columns to keep for the first selection. Defaults to ["Low", "fdbs", "fdbb", "tmax", "tmin", "p", "l", __TARGET].
        sel_2_suffix (str, optional): The suffix for the second selection. Defaults to "_tnd".
        sel_2_keeping_columns (list, optional): The list of columns to keep for the second selection. Defaults to ["Open", "High", "Low", "Close", "fdbs", "fdbb", __TARGET].  
        pto_vec_fdb_ao_out_s_name (str, optional): The name of the output for fdb_ao_vector_window. Defaults to "vaos".
        pto_vec_fdb_ao_out_b_name (str, optional): The name of the output for fdb_ao_vector_window. Defaults to "vaob".
        pto_vec_fdb_ao_in_s_sig_name (str, optional): The name of the input for fdb_ao_vector_window. Defaults to "fdbs".
        pto_vec_fdb_ao_in_s_win_end_sig_name (str, optional): The name of the input for fdb_ao_vector_window. Defaults to "zlcb".
        pto_vec_fdb_ao_in_b_sig_name (str, optional): The name of the input for fdb_ao_vector_window. Defaults to "fdbb".
        pto_vec_fdb_ao_in_b_win_end_sig_name (str, optional): The name of the input for fdb_ao_vector_window. Defaults to "zlcs".
        pto_vec_fdb_ao_in_t_val_name (str, optional): The name of the input for fdb_ao_vector_window. Defaults to "ao".
        additional_columns_to_drop (list, optional): The list of additional columns to drop. Defaults to None.
        selected_columns_to_keep (list, optional): The list of selected columns to keep. Defaults to None.
        save_outputs (bool, optional): If True, save the outputs. Defaults to True.
        only_if_target_exist_n_not_zero (bool, optional): If True, only if target exists and not zero. Defaults to True.
        use_fresh (bool, optional): If True, use fresh data. Defaults to False.
        keep_bid_ask (bool, optional): If True, keep bid and ask. Defaults to True.
        regenerate_cds (bool, optional): If True, regenerate the CDS. Defaults to False.
        gator_oscillator_flag (bool, optional): If True, calculate the Gator Oscillator. Defaults to False.
        mfi_flag (bool, optional): If True, calculate the MFI. Defaults to False.
        balligator_flag (bool, optional): If True, calculate the Alligator. Defaults to False.
        balligator_period_jaws (int, optional): The period for the Alligator jaws. Defaults to 89.
        largest_fractal_period (int, optional): The period for the largest fractal. Defaults to 89.
        talligator_flag (bool, optional): If True, calculate the T-Alligator. Defaults to False.
        talligator_period_jaws (int, optional): The period for the T-Alligator jaws. Defaults to 377.
        use_ttf (bool, optional): If True, use TTF. Defaults to True.
        ttf_midfix (str, optional): The midfix for TTF. Defaults to "ttf".
        drop_vector_ao_intermediate_array (bool, optional): If True, drop the vector AO intermediate array. Defaults to True. (we have the Counts vaosc,vaosb)

        

    Returns:
        df_result_tmx (pandas.DataFrame): The DataFrame containing the calculated PTO target.
        sel1 (pandas.DataFrame): The DataFrame containing the selected columns.
        sel2 (pandas.DataFrame): The DataFrame containing the selected columns.
    """
    if tlid_tag is None:
        tlid_tag = tlid.get_minutes()

    #default_jgtpy_data_full = "full/data"
    default_jgtpy_data_full = "/var/lib/jgt/full/data"
    data_dir_full = os.getenv("JGTPY_DATA_FULL", default_jgtpy_data_full)
    indir_cds = os.path.join(data_dir_full, "cds")
    outdir_tmx = os.path.join(
        data_dir_full, "targets", "mx"
    )  # @STCIssue Hardcoded path future JGTPY_DATA_FULL/.../mx
    #make the outdir_tmx if not exist
    os.makedirs(outdir_tmx, exist_ok=True)
    
    df_result_tmx, sel1, sel2 = _pov_target_calculation_n_output240223(
        indir_cds=indir_cds,
        outdir_tmx=outdir_tmx,
        crop_start_dt=crop_start_dt,
        crop_end_dt=crop_end_dt,
        i=i,
        t=t,
        tlid_tag=tlid_tag,
        WINDOW_MIN=WINDOW_MIN,
        WINDOW_MAX=WINDOW_MAX,
        output_report_dir=output_report_dir,
        pto_vec_fdb_ao_vector_window_flag=pto_vec_fdb_ao_vector_window_flag,
        drop_calc_col=drop_calc_col,
        calc_col_to_drop_names=calc_col_to_drop_names,
        sel_1_suffix=sel_1_suffix,
        sel_1_keeping_columns=sel_1_keeping_columns,
        sel_2_suffix=sel_2_suffix,
        sel_2_keeping_columns=sel_2_keeping_columns,
        pto_vec_fdb_ao_out_s_name=pto_vec_fdb_ao_out_s_name,
        pto_vec_fdb_ao_out_b_name=pto_vec_fdb_ao_out_b_name,
        pto_vec_fdb_ao_in_s_sig_name=pto_vec_fdb_ao_in_s_sig_name,
        pto_vec_fdb_ao_in_s_win_end_sig_name=pto_vec_fdb_ao_in_s_win_end_sig_name,
        pto_vec_fdb_ao_in_b_sig_name=pto_vec_fdb_ao_in_b_sig_name,
        pto_vec_fdb_ao_in_b_win_end_sig_name=pto_vec_fdb_ao_in_b_win_end_sig_name,
        pto_vec_fdb_ao_in_t_val_name=pto_vec_fdb_ao_in_t_val_name,
        additional_columns_to_drop=additional_columns_to_drop,
        selected_columns_to_keep=selected_columns_to_keep,
        save_outputs=save_outputs,
        write_reporting=write_reporting,
        only_if_target_exist_n_not_zero=only_if_target_exist_n_not_zero,
        use_fresh=use_fresh,
        keep_bid_ask=keep_bid_ask,
        regenerate_cds=regenerate_cds,
        gator_oscillator_flag=gator_oscillator_flag,
        mfi_flag=mfi_flag,
        balligator_flag=balligator_flag,
        balligator_period_jaws=balligator_period_jaws,
        largest_fractal_period=largest_fractal_period,
        talligator_flag=talligator_flag,
        talligator_period_jaws=talligator_period_jaws, 
        use_ttf=use_ttf,
        ttf_midfix=ttf_midfix,
        drop_vector_ao_intermediate_array=drop_vector_ao_intermediate_array
    )
    return df_result_tmx, sel1, sel2


def _pov_target_calculation_n_output240223(
    indir_cds,
    outdir_tmx,
    crop_start_dt,
    crop_end_dt,
    i,
    t,
    tlid_tag,
    WINDOW_MIN=1,
    WINDOW_MAX=150,
    output_report_dir=None,
    pto_vec_fdb_ao_vector_window_flag=True,
    drop_calc_col=True,
    write_reporting=True,
    calc_col_to_drop_names=["tmax", "tmin", "p", "l"],
    sel_1_suffix="_sel",
    sel_1_keeping_columns=[HIGH,
                           LOW,                    FDBS,                   FDBB,                   "tmax",                 "tmin",
                           "p",
                           "l", 
                           __TARGET],
    sel_2_suffix="_tnd",
    sel_2_keeping_columns=[OPEN, HIGH, LOW, CLOSE, FDBS, FDBB, __TARGET],
    pto_vec_fdb_ao_out_s_name=VECTOR_AO_FDBS,
    pto_vec_fdb_ao_out_b_name=VECTOR_AO_FDBB,
    pto_vec_fdb_ao_in_s_sig_name=FDBS,
    pto_vec_fdb_ao_in_s_win_end_sig_name=ZLCB,
    pto_vec_fdb_ao_in_b_sig_name=FDBB,
    pto_vec_fdb_ao_in_b_win_end_sig_name=ZLCS,
    pto_vec_fdb_ao_in_t_val_name=AO,
    additional_columns_to_drop=None,
    selected_columns_to_keep=None,
    save_outputs=True,
    only_if_target_exist_n_not_zero=True,
    use_fresh=True,
    keep_fdb_count_separated_columns=False,
    keep_bid_ask=True,
    regenerate_cds=False,
    gator_oscillator_flag=False,
    mfi_flag=True,
    balligator_flag=False,
    balligator_period_jaws=89,
    largest_fractal_period=89,
    talligator_flag=False,
    talligator_period_jaws=377,
    use_ttf=True,
    ttf_midfix="ttf",
    drop_vector_ao_intermediate_array=True,
):
    if tlid_tag is None:
        tlid_tag = tlid.get_minutes()

    ifn = i.replace("/", "-")
    # read instrument prop
    iprop = pds.get_instrument_properties(i)
    pipsize = iprop["pipsize"]
    nb_decimal = (
        len(str(pipsize).split(".")[1]) if "." in str(pipsize) else len(str(pipsize))
    )
    rounder = nb_decimal

    # Possible crop of the dataframe to a specific date range

    # Read the source data of already calculated CDS
    
    #@STCIssue Generate if not exist
    cds_full_filename = f"{indir_cds}/{ifn}_{t}.csv"
    if not os.path.exists(cds_full_filename) or regenerate_cds or use_fresh:
        from jgtpy import JGTCDS as cds
        reason = "(dont exist)" if not os.path.exists(cds_full_filename) else "" 
        msg = f"JTC is generating the CDS file{reason}: "
        msg = msg + " regenerated flag active" if regenerate_cds else msg
        msg = msg + " use fresh flag active" if use_fresh else msg

        print(msg)
        use_full = True
        #@STCIssue UPGRADE to use JGTCDSSvc
        from jgtpy import JGTCDSSvc as svc
        svc.get(instrument=i, timeframe=t, use_full=use_full, use_fresh=use_fresh)
        # cds.createFromPDSFileToCDSFile(instrument=i, 
        #                                timeframe=t,
        #                                use_full=use_full,
        #                                use_fresh=use_fresh,keep_bid_ask=keep_bid_ask,
        #                                gator_oscillator_flag=gator_oscillator_flag,
        #                                mfi_flag=mfi_flag,
        #                                balligator_flag=balligator_flag,
        #                                balligator_period_jaws=balligator_period_jaws,
        #                                largest_fractal_period=largest_fractal_period,
        #                                talligator_flag=talligator_flag,
        #                                talligator_period_jaws=talligator_period_jaws)#@STCGoal Use Fresh
    if use_ttf:
        from ptottf import read_ttf_csv
        print("                                 jgtml is using ttf....")
        df_cds_source:pd.DataFrame = read_ttf_csv(i, t, use_full=True,midfix=ttf_midfix)
        #@STCGoal Pattern Name -> We have the Columns list serialized
        from mldatahelper import read_patternname_columns_list
        patternname=ttf_midfix
        columns_list_from_higher_tf = read_patternname_columns_list(i,t,use_full=True,midfix=patternname,ns="ttf")
        print("INFO::Columns list from higher TF:",columns_list_from_higher_tf)
        print(">   We would use that to filter the columns and get our training data out of this refactored module (JTC.py)  -or shall I say from prototype to production/new module.  -> OUTPUT:  Training Data and Reality Data with which we would predict using our model.")
        print(f"Does these columns read from the source we would use to create the MXTarget data align with the input pattern {patternname}:",df_cds_source.columns)
        #sys.exit(0)
        #print("JGTML::Debug len of df_cds_source:", len(df_cds_source))
    else:
        df_cds_source = pd.read_csv(
            cds_full_filename, index_col=0, parse_dates=True
        )

    df_result_tmx = calculate_target_variable_min_max(
        df_cds_source, 
        crop_end_dt, 
        crop_start_dt, 
        rounder=rounder, 
        pipsize=pipsize,
        WINDOW_MIN=WINDOW_MIN,
        WINDOW_MAX=WINDOW_MAX,
    )
    #print("calculate_target_variable_min_max::",df_result_tmx.columns)

    if pto_vec_fdb_ao_vector_window_flag:
        df_result_tmx = get_fdb_ao_vector_window(
            df_result_tmx,
            out_s_name=pto_vec_fdb_ao_out_s_name,
            out_b_name=pto_vec_fdb_ao_out_b_name,
            in_s_sig_name=pto_vec_fdb_ao_in_s_sig_name,
            in_s_win_end_sig_name=pto_vec_fdb_ao_in_s_win_end_sig_name,
            in_b_sig_name=pto_vec_fdb_ao_in_b_sig_name,
            in_b_win_end_sig_name=pto_vec_fdb_ao_in_b_win_end_sig_name,
            in_t_val_name=pto_vec_fdb_ao_in_t_val_name,
            only_if_target_exist_n_not_zero=only_if_target_exist_n_not_zero,
            
        )
        #print("after : get_fdb_ao_vector_window::",df_result_tmx.columns)
        # print(df_result_tmx.tail(14))
        #@STCGoal Count of the ao vector in the window
        df_result_tmx.loc[:, VECTOR_AO_FDBS_COUNT] = df_result_tmx[VECTOR_AO_FDBS].apply(lambda x: len(x.split(',')) if isinstance(x, str) else 0)
        df_result_tmx.loc[:, VECTOR_AO_FDBB_COUNT] = df_result_tmx[VECTOR_AO_FDBB].apply(lambda x: len(x.split(',')) if isinstance(x, str) else 0)
       
        df_result_tmx.loc[:, VECTOR_AO_FDBS_COUNT] = df_result_tmx.apply(lambda x: 0 if x[VECTOR_AO_FDBS_COUNT] == 1 else x[VECTOR_AO_FDBS_COUNT], axis=1)
        df_result_tmx.loc[:, VECTOR_AO_FDBB_COUNT] = df_result_tmx.apply(lambda x: 0 if x[VECTOR_AO_FDBB_COUNT] == 1 else x[VECTOR_AO_FDBB_COUNT], axis=1)
        
        if drop_vector_ao_intermediate_array:
            df_result_tmx.drop(columns=[VECTOR_AO_FDBS, VECTOR_AO_FDBB], inplace=True)
    
        
        #df_result_tmx.to_csv("debug.csv",index=True)
        #sys.exit(0)
        if keep_fdb_count_separated_columns:                
            sel_1_keeping_columns.append(VECTOR_AO_FDBS_COUNT)
            sel_2_keeping_columns.append(VECTOR_AO_FDBS_COUNT)
            sel_1_keeping_columns.append(VECTOR_AO_FDBB_COUNT)
            sel_2_keeping_columns.append(VECTOR_AO_FDBB_COUNT)
            
        
        #VECTOR_AO_FDB_COUNT
        try:sel_1_keeping_columns.append(VECTOR_AO_FDB_COUNT)
        except:pass
        try:sel_2_keeping_columns.append(VECTOR_AO_FDB_COUNT)
        except:pass
        try:selected_columns_to_keep.append(VECTOR_AO_FDB_COUNT)
        except:pass
        
        df_result_tmx.loc[:, VECTOR_AO_FDB_COUNT] = df_result_tmx[VECTOR_AO_FDBS_COUNT] + df_result_tmx[VECTOR_AO_FDBB_COUNT]
        #VECTOR_AO_FDB_COUNT column gets the value of the vector ao fdbs count or fdbb count if not 1
        #df_result_tmx.loc[:, VECTOR_AO_FDB_COUNT] = df_result_tmx.apply(lambda x: x[VECTOR_AO_FDBS_COUNT] if x[VECTOR_AO_FDBS_COUNT] != 0 else x[VECTOR_AO_FDBB_COUNT] != 0, axis=1)
        
        # df_result_tmx.loc[:, VECTOR_AO_FDB_COUNT] = df_result_tmx.apply(lambda x: x[VECTOR_AO_FDBS_COUNT] if x[VECTOR_AO_FDBS_COUNT] != 1 else x[VECTOR_AO_FDBB_COUNT] != 1, axis=1)
        
        # df_result_tmx.loc[:, VECTOR_AO_FDB_COUNT] = df_result_tmx.apply(lambda x: 0 if x[VECTOR_AO_FDB_COUNT] == 1 else x[VECTOR_AO_FDB_COUNT], axis=1)
        
        # #fill with zero if nan or 1
        df_result_tmx[VECTOR_AO_FDB_COUNT] = df_result_tmx[VECTOR_AO_FDB_COUNT].fillna(0)
        #VECTOR_AO_FDB_COUNT column gets the value of the vector ao fdbs count or fdbb count if not 0
        #df_result_tmx.loc[:, VECTOR_AO_FDB_COUNT] = df_result_tmx.apply(lambda x: x[VECTOR_AO_FDBS_COUNT] if x[VECTOR_AO_FDBS_COUNT] != 0 else x[VECTOR_AO_FDBB_COUNT] != 0, axis=1)
        #df_result_tmx.loc[:, VECTOR_AO_FDB_COUNT] =
        
        #df_result_tmx[VECTOR_AO_FDB_COUNT] = df_result_tmx[VECTOR_AO_FDB_COUNT].fillna(0)
        
        if pto_vec_fdb_ao_out_s_name  not in sel_1_keeping_columns and not drop_vector_ao_intermediate_array:
            sel_1_keeping_columns.append(pto_vec_fdb_ao_out_s_name )
        
        if pto_vec_fdb_ao_out_b_name not in sel_1_keeping_columns and not drop_vector_ao_intermediate_array:
            sel_1_keeping_columns.append(pto_vec_fdb_ao_out_b_name )
            
        if pto_vec_fdb_ao_out_s_name  not in sel_2_keeping_columns and not drop_vector_ao_intermediate_array:
            sel_2_keeping_columns.append(pto_vec_fdb_ao_out_s_name )
        
        if pto_vec_fdb_ao_out_b_name not in sel_2_keeping_columns and not drop_vector_ao_intermediate_array:
            sel_2_keeping_columns.append(pto_vec_fdb_ao_out_b_name )      
        
        

    """  #@STCIssue We will Want those columns in the output selections
        out_s_name = 'vector_ao_fdbs', # REPLACED 240506 vaos
        out_b_name = 'vector_ao_fdbb', # REPLACED 240506 vaob
        in_s_sig_name = 'fdbs',
        in_s_win_end_sig_name = 'zlcb',            
        in_b_sig_name = 'fdbb',
        in_b_win_end_sig_name = 'zlcs',
        in_t_val_name = 'ao'
    """

    # Selection 1
    sel1 = df_result_tmx[sel_1_keeping_columns].copy()
    
    # Select only rows where profit or loss
    sel1 = sel1[(sel1["p"] != 0) | (sel1["l"] != 0)]


    if save_outputs:
        print("INFO::Saving MX Target data to file...")
        output_sel_cols_fn = get_outfile_fullpath(i,t,use_full=True,ns=MX_NS,midfix=ttf_midfix,suffix=sel_1_suffix)
        #output_sel_cols_fn = f"{outdir_tmx}/{ifn}_{t}{sel_1_suffix}.csv"
        try:
            sel1.to_csv(output_sel_cols_fn, index=True)
            print(f"Saved to {output_sel_cols_fn}")
        except Exception as e:
            print(f"Error occurred while saving to {output_sel_cols_fn}: {str(e)}")
    
    sel2 = df_result_tmx[sel_2_keeping_columns].copy()
    sel2[__TARGET] = sel2[__TARGET].round(rounder)
    sel2 = sel2[(sel2[__TARGET] != 0)]

    output_tnd_targetNdata_fn =get_outfile_fullpath(i,t,use_full=True,ns=MX_NS,midfix=ttf_midfix,suffix=sel_2_suffix)
    #output_tnd_targetNdata_fn = f"{outdir_tmx}/{ifn}_{t}{sel_2_suffix}.csv"
    
    if save_outputs:
        try:
            sel2.to_csv(output_tnd_targetNdata_fn, index=True)
            print(f"INFO::Saved to {output_tnd_targetNdata_fn}")
        except Exception as e:
            print(f"ERROR::occurred while saving to {output_tnd_targetNdata_fn}: {str(e)}")

    if selected_columns_to_keep is not None:
        print("INFO::   Selected columns to keep:", selected_columns_to_keep)

    # if drop_calc_col and selected_columns_to_keep is None:
    #     print("INFO::   Dropping calculated columns:", calc_col_to_drop_names)
    #     df_result_tmx.drop(columns=calc_col_to_drop_names, inplace=True)
    for col in calc_col_to_drop_names:
        if col in df_result_tmx.columns:
            df_result_tmx.drop(columns=[col], inplace=True)
    #print("calc_col_to_drop_names::",calc_col_to_drop_names)
    #print("selected_columns_to_keep::",selected_columns_to_keep)
    
        
    if additional_columns_to_drop is not None and selected_columns_to_keep is not None:
        print("ERROR::  You cannot use both additional_columns_to_drop and selected_columns_to_keep. Please use only one of them.")
        return df_result_tmx, sel1, sel2
    
    if additional_columns_to_drop is not None:
        #print("Dropping additional columns:", additional_columns_to_drop)
        try:
            df_result_tmx.drop(columns=additional_columns_to_drop, inplace=True)
        except:
            pass
    
    if selected_columns_to_keep is not None:
        try:
            df_result_tmx = df_result_tmx[selected_columns_to_keep].copy()
        except:
            pass
    
    if save_outputs:
        # Save the result to a csv file
        output_all_cols_fn = get_outfile_fullpath(i,t,use_full=True,ns=MX_NS,midfix=ttf_midfix)
        #output_all_cols_fn = f"{outdir_tmx}/{ifn}_{t}.csv"
        try:
            df_result_tmx.to_csv(output_all_cols_fn, index=True)
            print(f"INFO::Saved to {output_all_cols_fn}")
        except Exception as e:
            print(f"ERROR::Error occurred while saving to {output_all_cols_fn}: {str(e)}")

    if write_reporting:
        _reporting(sel2, ifn, t, pipsize, tlid_tag, output_report_dir=output_report_dir)

    return df_result_tmx, sel1, sel2


def _reporting(df_selection2, ifn, t, pipsize, tlid_tag, output_report_dir=None):

    if output_report_dir is None:
        output_report_dir = os.path.join(os.getenv("JGTPY_DATA_FULL"),"reports")
    if not os.path.exists(output_report_dir):
        os.makedirs(output_report_dir, exist_ok=True)

    report_file = f"{output_report_dir}/report-calc-{tlid_tag}.txt"
    reporting_flag=True if os.getenv("JGT_REPORTING_FLAG") == "True" else False
    if reporting_flag:
        print("INFO::Reporting to:", report_file)
        print(" tail -f ", report_file)
        with open(report_file, "a") as f:
            f.write(f"--- {ifn}_{t} --pipsize:{pipsize}---\n")
            f.write(f"Sum of target: {df_selection2['target'].sum()}\n\n")
            # f.write(f" (rounded): {(df_selection2['target'].sum()).round(2)}\n\n")


def readMXFile(
    instrument,
    timeframe,
    columns_to_remove=None,
    quiet=True,
    use_full=True,
    crop_last_dt=None,
    quote_count=None,
    sel_1_suffix="_sel",
    sel_2_suffix="_tnd",
    also_read_selections=False,
    generate_if_not_exist=True,
    dropna=True,
    mx_targets_sub_path = "targets/mx",
    ttf_midfix="ttf",
):
    """
    Read a MX Target file and return a pandas DataFrame.

    Parameters:
    instrument (str): The instrument name.
    timeframe (str): The timeframe of the data.
    columns_to_remove (list, optional): List of column names to remove from the DataFrame. Default is None.
    quiet (bool, optional): If True, suppresses the output messages. Default is True.
    use_full (bool, optional): If True, reads the full MX file. Default is True (there wont be MX in current data I think)).
    crop_last_dt  (str, optional): The last date to crop the data. Default is None.
    quote_count (int, optional): The number of quotes to keep. Default is None.
    sel_1_suffix (str, optional): The suffix for the first selection. Defaults to "_sel".
    sel_2_suffix (str, optional): The suffix for the second selection. Defaults to "_tnd".
    also_read_selections (bool, optional): If True, also read the selections. Defaults to False.
    generate_if_not_exist (bool, optional): If True, generate the MX Target data if it does not exist. Default is True.
    dropna (bool, optional): If True, drop the NaN values. Default is True.
    mx_targets_sub_path (str, optional): The sub-path for the MX Targets. Default is "targets/mx".
    ttf_midfix (str, optional): The midfix for the file name. Default is "".  We might use variation of the TTF (peaks,aoac, or other and the MX Will be saved with that midfix)

    Returns:
    pandas.DataFrame: The DataFrame containing the MX Target data.
    OR
    tuple: A tuple containing the DataFrame and the selections DataFrames.
    """
    # Define the file path based on the environment variable or local path
    fpath=get_outfile_fullpath(instrument, timeframe,use_full=use_full,midfix=ttf_midfix,ns=mx_targets_sub_path)
    #data_path_cds = get_data_path(mx_targets_sub_path, use_full=use_full,ttf_midfix=ttf_midfix)
    #fpath = pds.mk_fullpath(instrument, timeframe, "csv", data_path_cds)
    
    try:
        mdf = pd.read_csv(fpath)
    except:
        print(f"WARN::Error reading file {fpath}")
        print("INFO::  GENERATING THE MX Targets")
        try:
            pto_target_calculation(instrument,timeframe,pto_vec_fdb_ao_vector_window_flag=True,
                drop_calc_col=False,
                selected_columns_to_keep=ML_DEFAULT_COLUMNS_TO_KEEP,
                ttf_midfix=ttf_midfix)
        except:
            raise ValueError(f"ERROR:: generating file {fpath}")
        try:
            mdf = pd.read_csv(fpath)
        except:
            raise ValueError(f"Error reading file {fpath}")
    

    # Set 'Date' as the index and convert it to datetime
    mdf["Date"] = pd.to_datetime(mdf["Date"])
    mdf.set_index("Date", inplace=True)

    if dropna:
        mdf.dropna(inplace=True)
    # Remove the specified columns
    if columns_to_remove is not None:
        mdf = mdf.drop(columns=columns_to_remove, errors="ignore")

    if crop_last_dt is not None:
        mdf = mdf[mdf.index <= crop_last_dt]
    if quote_count is not None:
        mdf = mdf[-quote_count:]

    if also_read_selections:
        sel1 = pd.read_csv(
            fpath.replace(".csv", f"{sel_1_suffix}.csv"), index_col=0, parse_dates=True
        )
        sel2 = pd.read_csv(
            fpath.replace(".csv", f"{sel_2_suffix}.csv"), index_col=0, parse_dates=True
        )
        return mdf, sel1, sel2
    return mdf




def get_fdb_ao_vector_window(
    df,
    out_s_name=VECTOR_AO_FDBS,#"vaos",#VECTOR_AO_FDBS_COUNT
    out_b_name=VECTOR_AO_FDBB,#"vaob",#VECTOR_AO_FDBB
    in_s_sig_name=FDBS,#"fdbs",
    in_s_win_end_sig_name=ZLCB,#"zlcb",
    in_b_sig_name=FDBB,#"fdbb",
    in_b_win_end_sig_name=ZLCS,#"zlcs",
    in_t_val_name=AO,#"ao",
    only_if_target_exist_n_not_zero=True,
):

    # reset index before we iterate
    try:
        df.reset_index(drop=False, inplace=True)
    except:
        pass

    df[out_s_name] = np.nan
    df[out_b_name] = np.nan

    col_target_exist_in_dataset = __TARGET in df.columns
    
    
    for index, row in df.iterrows():
        process_row = True
        if only_if_target_exist_n_not_zero:
            col_target_exist_in_dataset and row[__TARGET] != 0
            
        if row[in_s_sig_name] == 1 and row[in_t_val_name] > 0 and process_row:
            window_start = index
            window_end = None
            for i in range(index, -1, -1):
                if df.at[i, in_s_win_end_sig_name] == 1:
                    window_end = i
                    break
            window = (
                df.loc[window_end:window_start, in_t_val_name]
                if window_end is not None
                else df.loc[:window_start, in_t_val_name]
            )
            df.at[index, out_s_name] = str(window.astype(float).tolist())
            
        if row[in_b_sig_name] == 1 and row[in_t_val_name] < 0 and process_row:
            window_start = index
            window_end = None
            for i in range(index, -1, -1):
                if df.at[i, in_b_win_end_sig_name] == 1:
                    window_end = i
                    break
            window = (
                df.loc[window_end:window_start, in_t_val_name]
                if window_end is not None
                else df.loc[:window_start, in_t_val_name]
            )
            df.at[index, out_b_name] = str(window.astype(float).tolist())
    # restore index
    try:
        df.set_index("Date", inplace=True)
    except:
        pass

    # for nan values, fill with empty string corresponding to an empty array
    #df[out_s_name].fillna("[]", inplace=True)
    #df[out_b_name].fillna("[]",inplace=True)
    df.fillna({out_s_name: "[]", out_b_name: "[]"}, inplace=True)
    return df



#@STCGoal Features the Fractals in Relationship to the AO



def get_fdb_ao_vector_window_v2(
    df,
    out_s_name="vaos",
    out_b_name="vaob",
    in_s_sig_name="fdbs",
    in_s_win_end_sig_name="zlcb",
    in_b_sig_name="fdbb",
    in_b_win_end_sig_name="zlcs",
    in_t_val_name="ao",
    only_if_target_exist_n_not_zero=True,
    fractal_count_pto=True,
    fractal_count_col_name="f_aow_cnt", #@STCIssue What do we want to know ?
):

    # reset index before we iterate
    try:
        df.reset_index(drop=False, inplace=True)
    except:
        pass

    df[out_s_name] = np.nan
    df[out_b_name] = np.nan

    col_target_exist_in_dataset = __TARGET in df.columns
    
    
    for index, row in df.iterrows():
        process_row = True
        if only_if_target_exist_n_not_zero:
            col_target_exist_in_dataset and row[__TARGET] != 0
            
        if row[in_s_sig_name] == 1 and row[in_t_val_name] > 0 and process_row:
            window_start = index
            window_end = None
            for i in range(index, -1, -1):
                if df.at[i, in_s_win_end_sig_name] == 1:
                    window_end = i
                    break
            window = (
                df.loc[window_end:window_start, in_t_val_name]
                if window_end is not None
                else df.loc[:window_start, in_t_val_name]
            )
            df.at[index, out_s_name] = str(window.astype(float).tolist())
            
        if row[in_b_sig_name] == 1 and row[in_t_val_name] < 0 and process_row:
            window_start = index
            window_end = None
            for i in range(index, -1, -1):
                if df.at[i, in_b_win_end_sig_name] == 1:
                    window_end = i
                    break
            window = (
                df.loc[window_end:window_start, in_t_val_name]
                if window_end is not None
                else df.loc[:window_start, in_t_val_name]
            )
            df.at[index, out_b_name] = str(window.astype(float).tolist())
    # restore index
    try:
        df.set_index("Date", inplace=True)
    except:
        pass

    # for nan values, fill with empty string corresponding to an empty array
    df[out_s_name].fillna("[]", inplace=True)
    df[out_b_name].fillna("[]",inplace=True)

    return df



