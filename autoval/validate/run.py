"""
@author: Sergey.Vinogradov@noaa.gov
"""
import sys, os
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
    if not os.path.exists(comout):
        msg('e','ofs path ' + comout + ' does not exist. Exiting')
        return 0
    else:
        return 1   
#==============================================================================
def singlerun (cfg):

    # 1. Check model Path
    comout = cfg['Experiment']['path']
    if not check_comout (comout):
        pass # exit here
    
    # 2. Parse cfg on what to do

    # 3. Call out validation, save
    # 4. Call out report generator
    # 5. Call out plotting

#==============================================================================
if __name__ == "__main__":

    cmd = read_cmd_argv          (sys.argv[1:])
    cfg = csdllib.oper.sys.config (cmd.iniFile)
    if cfg['Mode']['multirun']:
        # Assemble multirun setup here
        pass
    else:
        singlerun (cfg)
