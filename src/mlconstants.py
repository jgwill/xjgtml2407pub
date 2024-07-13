

from jgtutils.jgtconstants import ( AO,MFI_SIGNAL)

from jgtutils.jgtconstants import ZONE_SIGNAL as ZONE_DEFAULT_COLNAME
from jgtutils.jgtconstants import MFI_SIGNAL as MFI_DEFAULT_COLNAME
from jgtutils.jgtconstants import FDB_TARGET as TARGET
MFI_DEFAULT_COLTYPE=int
ZONE_DEFAULT_COLTYPE=int
TARGET_COLTYPE=float

from jgtutils.coltypehelper import DTYPE_DEFINITIONS as DTYPE_DEFINITIONS__CDS

 
TTF_DTYPE_DEFINITION = {MFI_DEFAULT_COLNAME: MFI_DEFAULT_COLTYPE,ZONE_DEFAULT_COLNAME: ZONE_DEFAULT_COLTYPE, 'zone_sig_M1':int,'zone_sig_W1':int,'zone_sig_D1':int,'zone_sig_H4':int,'zone_sig_H1':int, 'mfi_sig_M1':int,'mfi_sig_W1':int,'mfi_sig_D1':int,'mfi_sig_H4':int,'mfi_sig_H1':int,'zcol':str,'mfi_sq':int,'mfi_green':int,'mfi_fade':int,'mfi_fake':int,'price_peak_above':int,'price_peak_bellow':int,'ao_peak_above':int,'ao_peak_bellow':int,'ao_sig_M1':float,'ao_sig_W1':float,'ao_sig_D1':float,'ao_sig_H4':float,'ao_sig_H1':float,'ao_sig_m15':float,'ao_sig_m5':float,'mfi_str':str}


default_columns_to_get_from_higher_tf = [MFI_DEFAULT_COLNAME, ZONE_DEFAULT_COLNAME, AO]

TTF_NOT_NEEDED_COLUMNS_LIST=[ 'mfi_str','mfi_sq', 'mfi_green', 'mfi_fade', 'mfi_fake','zcol','price_peak_above', 'price_peak_bellow','ao_peak_above','ao_peak_bellow']

NORMAL_MOUTH_IS_OPEN_COLNAME='normal_mouth_is_open'
CURRENT_BAR_IS_OUT_OF_NORMAL_MOUTH_COLNAME='current_bar_is_out_of_normal_mouth'

CURRENT_BAR_IS_IN_BIG_TEETH_COLNAME='current_bar_is_in_big_teeth'
BIG_MOUTH_IS_OPEN_AND_CURRENT_BAR_IS_IN_BIG_LIPS_COLNAME='big_mouth_is_open_and_current_bar_is_in_big_lips'

MOUTH_IS_OPEN_AND_CURRENT_BAR_IS_IN_BIG_TEETH_COLNAME='mouth_is_open_and_current_bar_is_in_big_teeth'


CURRENT_BAR_IS_IN_TIDE_TEETH_COLNAME='current_bar_is_in_tide_teeth'
TIDE_MOUTH_IS_OPEN_AND_CURRENT_BAR_IS_IN_TIDE_LIPS_COLNAME='tide_mouth_is_open_and_current_bar_is_in_tide_lips'

MOUTH_IS_OPEN_AND_CURRENT_BAR_IS_IN_TIDE_TEETH_COLNAME='mouth_is_open_and_current_bar_is_in_tide_teeth'


MX_NS="targets/mx"