

from mlconstants import TARGET

# Dropped by the MX Reading
readmx_drop_columns_arr = ['BidOpen', 'BidHigh', 'BidLow', 'BidClose', 'AskOpen', 'AskHigh','AskLow', 'AskClose', 'fh13', 'fl13', 'fh21', 'fl21', 'fh34', 'fl34', 'fh55','fl55','price_peak_above', 'price_peak_bellow', 'ao_peak_above','ao_peak_bellow'] #@STCissue Could :'price_peak_above', 'price_peak_bellow', 'ao_peak_above','ao_peak_bellow' be usefull features ??

mx_common_columns=[TARGET, 'vaoc','fdb']

columnsToDrop_part01_2407 = ['vaos','vaob','vaosc','vaobc','fh8', 'fl8', 'fh89', 'fl89','mfi','aoaz','aobz','sz','bz','acb','acs','ss','sb','mfi_sq', 'mfi_green','mfi_fade', 'mfi_fake','tmax', 'tmin', 'p', 'l']


