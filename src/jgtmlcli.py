#!/usr/bin/env python

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# import .

from jgtutils import (
    jgtcommon as jgtcommon
)
import argparse

import pandas as pd

#import jgtml as jml
import  jtc

import jplt

import tlid



import pandas as pd


def parse_args():
    parser = argparse.ArgumentParser(description="Process command parameters.")
    # jgtfxcommon.add_main_arguments(parser)
    jgtcommon.add_instrument_timeframe_arguments(parser)
    
    jgtcommon.add_tlid_range_argument(parser)
    
    jgtcommon.add_verbose_argument(parser)
    
    jgtcommon.add_use_full_argument(parser)
    #add_use_fresh_argument
    jgtcommon.add_use_fresh_argument(parser)
    
    jgtcommon.add_keepbidask_argument(parser)

    jgtcommon.add_ids_mfi_argument(parser)
    jgtcommon.add_ids_gator_oscillator_argument(parser)
    jgtcommon.add_ids_balligator_argument(parser)
    jgtcommon.add_ids_talligator_argument(parser)
    jgtcommon.add_ids_fractal_largest_period_argument(parser)
    
    #add argument to regenerate the cds
    parser.add_argument('-rcds', '--regenerate_cds', action='store_true', help='Regenerate the CDS')

    parser.add_argument('-sc', '--selected-columns', nargs='+', help='List of selected columns to keep', default=['High','Low','ao','ac','jaw','teeth','lips','fh','fl','fdbb','fdbs','zlcb','zlcs','target','vaos','vaob'])

    # dont drop calculated columns
    parser.add_argument('-ddcc', '--dont_drop_calc_col', action='store_true', help='Dont drop calculated columns')
    
    parser.add_argument("-pn", "--patternname", help="Pattern Name", default="ttf")
  
    # jgtcommon.add_cds_argument(parser)
    args = parser.parse_args()
    return args


def main():
    
    args = parse_args()
    regenerate_cds=args.regenerate_cds

    verbose_level = args.verbose
    quiet = False
    if verbose_level == 0:
        quiet = True

    instrument = args.instrument
    timeframe = args.timeframe
    
    keep_bid_ask = True
    if args.rmbidask:
        keep_bid_ask = False
        
    full = True
    if args.notfull:
        full = False
        print_quiet(quiet, "USING FULL MODE TURNED OFF")

    fresh = True
    if args.notfresh:
        fresh = False
        print_quiet(quiet, "USING FRESH MODE TURNED OFF")

    date_from = None
    date_to = None
    tlid_range = None
    if args.tlidrange:
        # @STCGoal Get range prices from cache or request new
        tlid_range = args.tlidrange
        print("FUTURE Support for tlid range")
        
        print("-----------Stay tune -------- Quitting for now")
        return


    dont_drop_calc_col=True if args.dont_drop_calc_col else False

    

    if verbose_level > 1:
        if date_from:
            print("Date from : " + str(date_from))
        if date_to:
            print("Date to : " + str(date_to))

    try:

        print_quiet(quiet, "Getting for : " + instrument + "_" + timeframe)
        instruments = instrument.split(",")
        timeframes = timeframe.split(",")

        for instrument in instruments:
            for timeframe in timeframes:
                print("-------JTC Processing : " + instrument + "_" + timeframe)

                #selected_columns_to_keep  =['High','Low','ao','ac','jaw','teeth','lips','fh','fl','fdbb','fdbs','zlcb','zlcs','target','vaos','vaob']
                selected_columns_to_keep = args.selected_columns
   
                #selected_columns_to_keep=['Volume','High','Low','ao','ac','jaw','teeth','lips','fh','fl','fdbb','fdbs','aocolor','accolor','zcol','sz','bz','acs','acb','ss','sb','price_peak_above','price_peak_bellow','ao_peak_above','ao_peak_bellow']
                if full:
                    #Full column
                    selected_columns_to_keep = None
        
                r,s1,s2= jtc.pto_target_calculation( #@STCIssue Exception: 'NoneType' object has no attribute 'append';jgtmlcli.py", line 120;tc.py", line 189, in pto_target_calculation;line 337, in _pov_target_calculation_n_output240223selected_columns_to_keep.append(VECTOR_AO_FDB_COUNT) AttributeError: 'NoneType' object has no attribute 'append'
                    instrument,
                    timeframe,
                    pto_vec_fdb_ao_vector_window_flag=True,
                    drop_calc_col=dont_drop_calc_col,
                    selected_columns_to_keep=selected_columns_to_keep,
                    save_outputs=True,
                    keep_bid_ask=keep_bid_ask,
                    use_fresh=fresh,
                    regenerate_cds=regenerate_cds,
                    gator_oscillator_flag=args.gator_oscillator_flag,
                    balligator_flag=args.balligator_flag,largest_fractal_period=args.largest_fractal_period,
                    mfi_flag=args.mfi_flag,
                    balligator_period_jaws=args.balligator_period_jaws,
                    ttf_midfix=args.patternname
                    
                    )

    except Exception as e:
        jgtcommon.print_exception(e)

    # try:
    #    jgtpy.off()
    # except Exception as e:
    #    jgtfxcommon.print_exception(e)


# if __name__ == "__main__":
#     main()

# print("")
# #input("Done! Press enter key to exit\n")


def createMX_for_main(
    instrument,
    timeframe,
    quiet,
    verbose_level=0,
    tlid_range=None,
    use_full=False,
):
    print("----TODO:  createMX_for_main")

def print_quiet(quiet, content):
    if not quiet:
        print(content)


if __name__ == "__main__":
    main()
