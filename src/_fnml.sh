#!/bin/bash
# This file is used to define functions that are used in the JGTML (Jean Guillaume's Trading Machine Learning) project.  It assist now in wrapping the various command line tools in workflows.

# This file is meant to be sourced in the shell, so that the functions are available in the shell.  It is not meant to be executed directly.


#. $HOME/.bashrc &>/dev/null

#TCONDA_ENV=jgtsd

#CURR_CONDA_ENV=$(conda info | awk '/active environment/{print $4}' || echo "")
#if [ "$CURR_CONDA_ENV" != "$TCONDA_ENV" ];then 
#  # if conda command is not found, we will not activate the env
#	if [ "$(which conda)" != "" ];then
#		conda activate $TCONDA_ENV &>/dev/null && \
#			echo "Conda env $TCONDA_ENV Activated"
#	fi
#fi
#. $HOME/.bashrc &>/dev/null

if [ -e "/opt/anaconda3/bin/conda" ];then

	__conda_setup="$('/opt/anaconda3/bin/conda' 'shell.bash' 'hook' 2> /dev/null)"
	if [ $? -eq 0 ]; then
			eval "$__conda_setup"
	else
			if [ -f "/opt/anaconda3/etc/profile.d/conda.sh" ]; then
					# shellcheck disable=SC1091
					. "/opt/anaconda3/etc/profile.d/conda.sh"&>/dev/null
			else
					export PATH="/opt/anaconda3/bin:$PATH"
			fi
	fi
	unset __conda_setup
fi
conda activate hfsp_basjupyterlab2406&>/dev/null || conda activate "$CONDA_ENV_PROD"&>/dev/null || echo "Assuming Conda Environment is already set"
# || echo "Conda env hfsp_basjupyterlab2406 or CONDA_ENV_PROD not found.  We will try anyway...."

__functionusage__=' 
# Refresh the CDS for an instrument and timeframe
	jgtml_prep_cds_05 <instrument> <timeframe> 
# Refresh the TTF for an instrument and timeframe
	jgtml_prep_ttf_10 <instrument> <timeframe>
# Refresh the MX
	jgtml_post_mx_15 <instrument> <timeframe>     
# Refresh TTF preparation for an instrument
	jgtml_wf_ttf_prep_by_instrument_19 instrument <instrument> 
# Calculate the MX for an instrument
	jgtml_wf_mx_by_instrument_20 <instrument>
# Run for all instruments in I variable
	jgtml_wf_mx_all_20    
#run the pto tidealligator
	jgtml_ptojgtmltidealligator_by_instrument_tf_21 <instrument> <timeframe> <buysell>
	'

__usage()
{
	echo "Usage: $0 [all|instrument]"
	echo "  all: Run for all instruments"
	echo "  instrument: Run for a specific instrument"
	echo " OR Functions gets loaded and can be called directly"
	echo "$__functionusage__"
}


jgtml_setup_00_user()
{
	conda activate baseprod || conda activate base || echo "Conda env baseprod or base not found.  We will try anyway...."
	pip install --user -U jgtfxcon jgtfx2console jgtutils
}

jgtml_setup_00_current()
{
	conda activate baseprod || conda activate base || echo "Conda env baseprod or base not found.  We will try anyway...."
	pip install -U jgtfxcon jgtfx2console jgtutils
}

_jgtfxcli_execute_by_instrument_and_timeframe()
{
	local _i=$1
	if [ "$_i" == "" ];then echo "Instrument is required jgtfxcli";return;fi
	local _t=$2
	if [ "$_t" == "" ];then echo "Timeframe is required jgtfxcli";return;fi
	jgtfxcli -i $_i -t $_t --full

}

# 01 Refresh the PDS full for an instrument and timeframe
jgtml_prep_pds_01()
{
	local _i=$1
	if [ "$_i" == "" ];then echo "Instrument is required jgtml_prep_pds_01";return;fi
	local _t=$2
	if [ "$_t" == "" ];then echo "Timeframe is required" jgtml_prep_pds_01;return;fi

	_jgtfxcli_execute_by_instrument_and_timeframe $_i $_t

}

_jgtcli_execute_by_instrument_and_timeframe()
{
	local _i=$1
	if [ "$_i" == "" ];then echo "Instrument is required";return;fi
	local _t=$2
	if [ "$_t" == "" ];then echo "Timeframe is required";return;fi
	jgtcli -i $_i -t $_t --full -mfi -ba -ta 

}


# 05 Refresh the   CDS
jgtml_prep_cds_05()
{
	local _i=$1
	if [ "$_i" == "" ];then echo "Instrument is required jgtml_prep_cds_05";return;fi
	local _t=$2
	if [ "$_t" == "" ];then echo "Timeframe is required jgtml_prep_cds_05";return;fi

	local _fresh="$3"
	if [ "$_fresh" == "fresh" ];then
		echo "Freshening the dependent data for CDS $_i $_t, hopefully"
	  jgtml_prep_pds_01 $_i $_t
	fi

	_jgtcli_execute_by_instrument_and_timeframe $_i $_t

}

# 06 Refresh the   CDS from old PDS
jgtml_prep_cds_06_old()
{
	jgtcli -i $1 -t $2 --full -mfi -ba -ta -old

}

# 10 Refresh the TTF for an instrument and timeframe
jgtml_prep_ttf_10()
{
	local _i=$1
	if [ "$_i" == "" ];then echo "Instrument is required";return;fi
	local _t=$2
	if [ "$_t" == "" ];then echo "Timeframe is required";return;fi

	local _xarg3="-fr" #Means force READ (confusing issue with --fresh(-new) that jgtcli uses, but whatever for now)
	local _xarg4="--full"
	if [ "$3" == "fresh" ];then
		jgtml_prep_cds_05 $_i $_t fresh
		echo "Freshening the dependent data for TTF $_i $_t, hopefully"
	fi

	ptojgtmlttfprotocli -i $_i -t $_t  $_xarg3 $_xarg4
	ptojgtmlttfprotocli -i $_i -t $_t  $_xarg3 $_xarg4 -clh price_peak_above price_peak_bellow ao_peak_above ao_peak_bellow mfi_sig -pn peaksmfi
	ptojgtmlttfprotocli -i $_i -t $_t  $_xarg3 $_xarg4 -clh price_peak_above price_peak_bellow ao_peak_above ao_peak_bellow -pn peaks
	ptojgtmlttfprotocli -i $_i -t $_t  $_xarg3 $_xarg4 -clh ao ac -pn aoac
}

# 15 Refresh the MX (using the TTF) for an instrument and timeframe
jgtml_post_mx_15()
{
	if [ "$1" == "" ];then echo "Instrument is required";return;fi
	if [ "$2" == "" ];then echo "Timeframe is required";return;fi
	jgtmlcli -i $1 -t $2 -ba -ta -old
	jgtmlcli -i $1 -t $2 -ba -ta -old -pn peaks
	jgtmlcli -i $1 -t $2 -ba -ta -old -pn peaksmfi
	jgtmlcli -i $1 -t $2 -ba -ta -old -pn aoac

}

# 19 Refresh TTF preparation for an instrument (timeframes are predefined)
jgtml_wf_ttf_prep_by_instrument_19()
{
	local _i=$1
	if [ "$_i" == "" ];then echo "Instrument is required jgtml_wf_ttf_prep_by_instrument_19";return;fi

	echo "TTF for:$_i... $2..."
	for _t in M1 W1 D1 H4;do
					if [ "$NOUP" != "1" ];then 
					  echo "jgtml_wf_ttf_prep_by_instrument_19 is callingjgtml_prep_cds_05 with  -> i:$_i, t:$_t"
						jgtml_prep_cds_05 $_i $_t $2
					fi

	done
	echo " ## We have created all required CDS for $_i $2"
	
	echo " ## Creating TTF and them MX for desired TF $2"
	for _t in D1 H4;do
					echo "jgtml_wf_ttf_prep_by_instrument_19::Preping TTf for: $_i  $_t"
					jgtml_prep_ttf_10 $_i $_t
	done
	echo "------TTF------------------$_i------$2------done"
}

# 20 Calculate the MX for instruments defined in I
jgtml_wf_ttf_prep_all_19()
{
	for _i in $(echo "$I"|tr "," " ");do 
		jgtml_wf_ttf_prep_by_instrument_19 $_i $2
	done
}

# 20 Calculate the MX for an instrument (timeframes are predefined)
jgtml_wf_mx_by_instrument_20()
{
	local _i=$1
	echo "jgtml_wf_mx_by_instrument_20 for i:$_i"
	jgtml_wf_ttf_prep_by_instrument_19 $_i $2
	# for t in M1 W1 D1 H4;do

	#         if [ "$NOUP" != "1" ];then 
	# 					jgtml_prep_cds_05 $_i $t $2
	# 				fi

	# done
	# echo " ## We have created all required CDS for $_i"
	
	echo " ##  Creating MX for desired TF of instrument:$_i"
	for _t in D1 H4;do
					echo "  $_t"
					#jgtml_prep_ttf_10 $_i $t
					#
					jgtml_post_mx_15 $_i $_t
	done
	echo "---------$_i----jgtml_wf_mx_by_instrument_20--------done"
}


# 20 Calculate the MX for all instruments defined in I

# shellcheck disable=SC2120
jgtml_wf_mx_all_20()
{
	local _fresh="$2"
	for _i in $(echo "$I"|tr "," " ");do 
		jgtml_wf_mx_by_instrument_20 "$_i" "$_fresh"
	done
}

ttfmxwf()
{
	(for _i in $(echo "$I"|tr "," " ");do echo $_i;jgtapp ttfmxwf -i $_i;done)&
}

# 21 Run the pto tidealligator for an instrument, timeframe and buysell
jgtml_ptojgtmltidealligator_by_instrument_tf_21()
{
	ptojgtmltidealligator -i $1 -t $2 --buysell $3 -nf --dont_regenerate_cds 
}

jgtmlf_exec_by_instrument_tf_22()
{
	local _i=$1
	local _t=$2
	if [ "$_i" == "" ];then echo "Instrument is required";return;fi
	if [ "$_t" == "" ];then echo "Timeframe is required";return;fi
	jgtmlfcli -i $_i -t $_t --full

}

jgtmlf_wf_by_instrument_tf_22()
{
	local _i=$1
	if [ "$_i" == "" ];then echo "Instrument is required";return;fi
	jgtml_wf_mx_by_instrument_20 $_i $2
	for _t in D1 H4;do
		jgtmlf_exec_by_instrument_tf_22 $_i $_t
	done
}


jgtmlf_exec_all_22()
{
	for _i in $(echo "$I"|tr "," " ");do 
		jgtmlf_wf_by_instrument_tf_22 $_i $2
	  #  for _t in D1 H4 W1;do
    #     echo "  $_t"
	  # 		jgtmlfcli -i $_i -t $_t --full
		# 	done
	done

}

# Relative to JGT file manipulation
i2fn()
{
        local _i="$1"
        local ifn=${_i//\//-}
        echo $_ifn
}

topovfn()
{
        local _i="$1"
        local _t="$2"
        local ifn=${_i//\//-}
        local sep="_"
        if [ "$2" == "" ];then sep="";fi

        echo $ifn"$sep"$_t$3
}

# tojgtpy_data_path()
# {
# 				local _i="$1"
# 				local _t="$2"
# 				local ifn=${_i//\//-}
# 				local sep="_"
# 				if [ "$2" == "" ];then sep="";fi
# 				local data_path=$JGTPY_DATA_FULL

# 				echo $_data_path/$_ifn"$sep"$_t$3

# }

# SOME UTILITIES such as tail the full PDS/CDS/TTF/MX data for an instrument and its timeframe
jgtml_hail_pds_99()
{
	local _pov=$(topovfn $1 $2)
	local data_path=$JGTPY_DATA_FULL
	if [ "$3" != "" ];then data_path=$3;fi
	local _fp=$data_path'/pds/'$_pov'.csv'
	echo "$_fp"
	if [ -e $_fp ];then
	  head -n 1 $_fp
		tail -n 1 $_fp
	fi
}

jgtml_hail_cds_99()
{
	local _pov=$(topovfn $1 $2)
	local data_path=$JGTPY_DATA_FULL
	if [ "$3" != "" ];then data_path=$3;fi
	local _fp=$data_path'/cds/'$_pov'.csv'
	echo "$_fp"
	if [ -e $_fp ];then
	  head -n 1 $_fp
		tail -n 1 $_fp
	fi
}

jgtml_hail_ttf_99()
{
	local _pov=$(topovfn $1 $2)
	local data_path=$JGTPY_DATA_FULL
	if [ "$3" != "" ];then data_path=$3;fi
	local _fp=$data_path'/ttf/'$_pov'_ttf.csv'
	echo "$_fp"
	if [ -e $_fp ];then
	  head -n 1 $_fp
		tail -n 1 $_fp
	fi

}

jgtml_hail_mx_99()
{
	local _pov=$(topovfn $1 $2)
	local data_path=$JGTPY_DATA_FULL
	if [ "$3" != "" ];then data_path=$3;fi
	local _fp=$data_path'/targets/mx/'$_pov'.csv'
	echo "$_fp"
	if [ -e $_fp ];then
	  head -n 1 $_fp
		tail -n 1 $_fp
	fi
}

jgtml_hail_all()
{
	local _pov=$(topovfn $1 $2)
	echo "pov:$_pov"
	local data_path=$JGTPY_DATA_FULL
	if [ "$3" != "" ];then data_path=$3;fi
	echo "PDS"
	jgtml_hail_pds_99 $1 $2 $data_path
	echo "CDS"
	jgtml_hail_cds_99 $1 $2 $data_path
	echo "TTF"
	jgtml_hail_ttf_99 $1 $2 $data_path
	echo "MX"
	jgtml_hail_mx_99 $1 $2 $data_path

}







# Usage with --help or -h
if [ "$1" == "--help" ] || [ "$1" == "-h" ];then
	__usage
else 

	if [ "$1" == "all" ];then
		jgtml_wf_mx_all_20
	else
		# if $1 is not all and has a value, we assume it is an instrument
		if [ "$1" != "" ];then
			echo "Running for $1"
			jgtml_wf_mx_by_instrument_20 $1

		fi
	fi
fi



echo "jgtml.sh sourced"