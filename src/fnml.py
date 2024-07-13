import argparse
import subprocess

def tide(instrument, timeframe, buysell):
  subprocess.run(['tide', instrument, timeframe, buysell])

def pds(instrument, timeframe):
  subprocess.run(['jgtfxcli', '-i', instrument, '-t', timeframe, '--full'])

def cds(instrument, timeframe, use_fresh=False):
  old_or_fresh = '-old' if not use_fresh else '--fresh'
  subprocess.run(['jgtcli', '-i', instrument, '-t', timeframe, '--full', '-mfi', '-ba', '-ta', old_or_fresh])

def ocds(instrument, timeframe):
  subprocess.run(['jgtcli', '-i', instrument, '-t', timeframe, '--full', '-mfi', '-ba', '-ta', '-old'])

def ttf(instrument, timeframe):
  subprocess.run(['ptojgtmlttfprotocli', '-i', instrument, '-t', timeframe, '--full', '-fr'])

def mx(instrument, timeframe, use_fresh=False):
  old_or_fresh = '-old' if not use_fresh else '--fresh'
  subprocess.run(['jgtmlcli', '-i', instrument, '-t', timeframe, '-ba', '-ta', old_or_fresh])

def ttfmxwf(instrument, use_fresh=False):
  for t in ["M1", "W1", "D1", "H4"]:
    print(f"Processing {instrument} for timeframe {t}")
    print("  CDS....")
    cds(instrument, t, use_fresh)
    if t != "M1":
      print("  TTF....")
      ttf(instrument, t)
    if t != "M1" and t != "W1":
      print("  MX....")
      mx(instrument, t)
      
def ttfwf(instrument, use_fresh=False):
  for t in ["M1", "W1", "D1", "H4"]:
    print(f"Processing {instrument} for timeframe {t}")
    print("  CDS....")
    cds(instrument, t, use_fresh)
    if t != "M1":
      print("  TTF....")
      ttf(instrument, t)
        
def main():
  parser = argparse.ArgumentParser(description="CLI equivalent of bash functions")
  subparsers = parser.add_subparsers(dest='command')

  parser_tidealligator = subparsers.add_parser('tide', help='Run the pto tidealligator')
  parser_tidealligator.add_argument('-i','--instrument', help='Instrument')
  parser_tidealligator.add_argument('-t','--timeframe', help='Timeframe')
  parser_tidealligator.add_argument('buysell', help='Buy or Sell')

  parser_prep_pds_01 = subparsers.add_parser('pds', help='Refresh the PDS full for an instrument and timeframe')
  parser_prep_pds_01.add_argument('-i','--instrument', help='Instrument')
  parser_prep_pds_01.add_argument('-t','--timeframe', help='Timeframe')

  parser_prep_cds_05 = subparsers.add_parser('cds', help='Refresh the CDS')
  parser_prep_cds_05.add_argument('-i','--instrument', help='Instrument')
  parser_prep_cds_05.add_argument('-t','--timeframe', help='Timeframe')
  #--fresh flag to use the fresh data
  parser_prep_cds_05.add_argument('-new','--fresh', action='store_true', help='Use the fresh data')

  parser_prep_cds_06_old = subparsers.add_parser('ocds', help='Refresh the CDS from old PDS')
  parser_prep_cds_06_old.add_argument('-i','--instrument', help='Instrument')
  parser_prep_cds_06_old.add_argument('-t','--timeframe', help='Timeframe')
  
  
  parser_prep_ttf_10 = subparsers.add_parser('ttf', help='Refresh the TTF for an instrument and timeframe')
  parser_prep_ttf_10.add_argument('-i','--instrument', help='Instrument symbol')
  parser_prep_ttf_10.add_argument('-t','--timeframe', help='Timeframe')
  
  #ttfmxwf
  parser_post_ttfmxwf_14 = subparsers.add_parser('ttfmxwf', help='Refresh the TTF, MX and CDS for an instrument')
  parser_post_ttfmxwf_14.add_argument('-i','--instrument', help='Instrument symbol')
  parser_post_ttfmxwf_14.add_argument('-new','--fresh', action='store_true', help='Use the fresh data')

  parser_post_mx_15 = subparsers.add_parser('mx', help='Refresh the MX (using the TTF) for an instrument and timeframe')
  parser_post_mx_15.add_argument('-i','--instrument', help='Instrument symbol')
  parser_post_mx_15.add_argument('-t','--timeframe', help='Timeframe')

  parser_wf_ttf_prep_19 = subparsers.add_parser('ttfwf', help='Refresh TTF preparation for an instrument')
  parser_wf_ttf_prep_19.add_argument('-i','--instrument', help='Instrument symbol')
  parser_wf_ttf_prep_19.add_argument('-new','--fresh', action='store_true', help='Use the fresh data')

  args = parser.parse_args()
  #if no arguments are passed, print help
  if not vars(args).get('command'):
    parser.print_help()
    parser.exit()

  if args.command == 'tide':
    tide(args.instrument, args.timeframe, args.buysell)
  elif args.command == 'pds':
    pds(args.instrument, args.timeframe)
  elif args.command == 'cds':
    cds(args.instrument, args.timeframe, args.fresh)
  elif args.command == 'ocds':
    ocds(args.instrument, args.timeframe)
  elif args.command == 'ttf':
    ttf(args.instrument, args.timeframe)
  elif args.command == 'ttfmxwf':
    ttfmxwf(args.instrument, args.fresh)
  elif args.command == 'mx':
    mx(args.instrument, args.timeframe)
  elif args.command == 'ttfwf':
    ttfwf(args.instrument, args.fresh)

if __name__ == "__main__":
  main()