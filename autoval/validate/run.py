"""
@author: Sergey.Vinogradov@noaa.gov
"""
import sys, os, glob
import argparse
import csdllib
from csdllib.oper.sys import msg

#==============================================================================
def read_cmd_argv (argv):

    parser = argparse.ArgumentParser()
    
    parser.add_argument('-i','--iniFile',        required=True)
    parser.add_argument('-p','--modelPath',      required=False)
    
    args = parser.parse_args() 

    msg('i', 'autoval.validate.run.py is configured with :')
    print(args)
    return args
#==============================================================================
def check_comout (comout):
    """
    Checks the validity of the specified model output directory.
    """
    if not os.path.exists(comout):
        msg('e','ofs path ' + comout + ' does not exist. Exiting')
        exit
    elif len(glob.glob(os.path.join(comout,'*.nc'))) == 0:
        msg('e','No netCDF files in ofs path ' + comout + '. Exiting')
        exit
    return 1

#==============================================================================
def singleRun (cfg):
    """
    Performs validation of a single given run.
    Returns diagnostic fields (diagFields) for multirun analysis, if requested
    """
    grid       = []
    diagFields = []

    # 1. Check model Path
    comout = cfg['Experiment']['path']
    check_comout (comout)
    
    # 2. Parse cfg on what to do
    

    # 3. Call out validation, save
    # 4. Call out report generator
    # 5. Call out plotting

    return grid, diagFields 

#==============================================================================
if __name__ == "__main__":

    cmd = read_cmd_argv          (sys.argv[1:])
    cfg = csdllib.oper.sys.config (cmd.iniFile)
    if cmd.modelPath:              # Command line is priority over ini file
        cfg['Experiment']['path'] = cmd.modelPath

    print (cfg) 

    if cfg['Mode']['multirun']:
        # Assemble multirun setup here
        experiments = []
        # Call singlerun for each experiment, collect diagFields
        for exp in experiments:
            grid, diagFields = singleRun (cfg)
        # Perform multirun diagnostics here

    else:
        singleRun (cfg)
