"""
@author: Sergey.Vinogradov@noaa.gov
"""
import sys, os, glob, shutil
import argparse
import csdllib
from csdllib.oper.sys import msg

#==============================================================================
def read_cmd_argv (argv):

    parser = argparse.ArgumentParser()
    
    parser.add_argument('-i','--iniFile',     required=True)
    parser.add_argument('-p','--paths',       required=True)
    
    args = parser.parse_args() 

    msg('i', 'autoval.validate.run.py is configured with :')
    print(args)
    return args

#==============================================================================
def setDir (path, flush=False):
    """
    Creates (or flushes) directories.
    """    
    if not os.path.exists(path):
        msg('w', 'Path='+path+' does not exist. Trying to mkdir.')
        try:
            os.makedirs(path)
        except:
            msg ('e', 'Cannot make path=' + path)
    elif flush:
        msg('w', 'Path='+path+' will be flushed.')
        shutil.rmtree(path)
        setDir (path)

#==============================================================================
def check_comout (comout):
    """
    Checks the validity of the specified model output directory.
    """
    if not os.path.exists(comout):
        msg('w','ofs path ' + comout + ' does not exist.')
        return 0
    elif len(glob.glob(os.path.join(comout,'*.nc'))) == 0:
        msg('w','No netCDF files in ofs path ' + comout + '.')
        return 0
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
    '''
    Need to collect :: expPaths (paths to experimental outputs)
                       expTags  (tags for experiments)
    '''
    cmd = read_cmd_argv (sys.argv[1:])   # Read command line aruments
    cfg = csdllib.oper.sys.config (cmd.iniFile) # Read config file
    
    # Set up validation execution paths, flush tmp directory
    _workDir = cfg['Analysis']['workdir']
    _dataDir = cfg['Analysis']['localdatadir']
    _tmpDir  = cfg['Analysis']['tmpdir']
    setDir (_workDir)
    setDir (_dataDir)
    setDir (_tmpDir, flush=True)

    # Find and validate path(s) to model output(s)
    expPaths = []                        # Define path(s) to experiment(s)
    if os.path.isdir(cmd.paths):  
        expPaths.append(cmd.paths)       # cmd line argument was a single path
    elif os.path.isfile(cmd.paths):      # check if this is a list file
        with open(cmd.paths) as f:       #  cmd line argument was a list 
            lines = f.readlines()        #   with possible path(s) to run(s)
            for line in lines:
                expPaths.append(line.strip())
    
    if len(expPaths) == 0:               # Nothing to do. Bye.
        msg('e','No valid model paths found. Exiting.')
        quit()
    
    for p in expPaths:                   # verify validity of paths
        if check_comout (p) == 0:
            msg('w', p + ' is invalid.')
            expPaths.remove (p)
    
    expTags = []                         # set up experiment tags
    msg('i','Detected valid directories:')
    for p in expPaths:
        folders = p.split('/')
        for f in folders:
            if f=='':
                folders.remove(f)
        tag = folders[-3] + '.' + folders[-2] + '.' + folders[-1]
        expTags.append(tag)
        msg (' ',p + ' tag=' + tag)
    
    
    diagVar = cfg['Analysis']['name']
    print (cfg['Analysis'])
    print (cfg[diagVar])


    # Get data

    # Run diagnostics - individual and across the experiments

    # Save/upload diagnostics reports

    # Plot graphics

    # Upload graphics
