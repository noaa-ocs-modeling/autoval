"""
@author: Sergey.Vinogradov@noaa.gov
"""
import sys
import argparse
import csdllib

def read_cmd_argv (argv):

    parser = argparse.ArgumentParser()
    
    parser.add_argument('-i','--iniFile',        required=True)
    parser.add_argument('-p','--modelPath',      required=False)
    
    args = parser.parse_args()    
    csdllib.oper.sys.msg('i', 'autoval/validate/run.py is configured with :')
    print(args)
    return args
    
if __name__ == "__main__":
    cmd = read_cmd_argv ( sys.argv[1:] )
    cfg = csdllib.oper.sys.config (cmd.iniFile)
    print(cfg)

