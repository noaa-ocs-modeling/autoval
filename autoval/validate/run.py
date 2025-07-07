"""
@author: Sergey.Vinogradov@noaa.gov
"""
import sys, os, glob, shutil
import argparse
import datetime
from waterlevel import waterLevel
from report.html import singleReport
import csdllib
from csdllib.oper.sys import msg
import numpy as np
from searvey import coops


#==============================================================================
def read_cmd_argv (argv):
    ''' Parse command line arguments '''
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
def writeLocalStats(cfg, tag, pointStats, info):
    pointIDs = []
    for n in range(len(info)):
        pointIDs.append( info[n]['nosid'])
    outFile = os.path.join(         \
        cfg['Analysis']['workdir'], \
        tag+'.' + cfg[cfg['Analysis']['name']]['localstatfile'])
    
    with open(outFile,'w') as f:
        keys = pointStats[0].keys()
        header = 'pointID,'
        for key in keys:
            header = header + key + ','
        f.write(header + '\n')
        for n in range(len(pointIDs)):
            line = pointIDs[n] + ','
            for key in keys:
                line = line + str(pointStats[n][key]) + ','
            f.write(line + '\n')
        f.close()

#==============================================================================
def appendGlobalStats(cfg, tag, avgStats):

    outFile = os.path.join(         \
        cfg['Analysis']['workdir'], \
        cfg[cfg['Analysis']['name']]['globalstatfile'])

    keys = avgStats.keys()
    if not os.path.exists(outFile):
        with open(outFile,'a+') as f:
            header = 'experiment, date,'
            for key in keys:
                header = header + key + ','
            f.write(header + '\n')
            f.close()
    with open(outFile,'a+') as f:
        line = tag + ',' + csdllib.oper.sys.timeStamp() + ','
        for key in keys:
            line = line + str(avgStats[key]) + ','
        f.write(line + '\n')    
        f.close()

#==============================================================================
def computeAvgStats(pointStats):

    keys = pointStats[0].keys()
    avgStats = {key: None for key in keys}

    for key in keys:
        stats    = np.empty(len(pointStats))
        for n in range(len(pointStats)):
            stats[n] = pointStats[n][key]
        avgStats[key] = np.nanmean(stats)

    return avgStats
            
#==============================================================================
def setDomainLimits(cfg):
    '''
     Set/get bbox
    '''
    lonMin =  -89.99
    lonMax =   89.99
    latMin = -179.99
    latMax =  179.99
    try:
        lonMin = float( cfg['Analysis']['lonmin'])
    except: 
        pass
    try:
        lonMax = float( cfg['Analysis']['lonmax'])
    except: 
        pass
    try:
        latMin = float( cfg['Analysis']['latmin'])
    except: 
        pass
    try:
        latMax = float( cfg['Analysis']['latmax'])
    except: 
        pass
    try:
        domainFile = os.path.join(cfg['Analysis']['localdatadir'], 'domain.ini')
        csdllib.oper.transfer.refresh( cfg['Analysis']['domainfile'], domainFile)
        dom = csdllib.oper.sys.config (domainFile)
        lonMin = float(dom['Limits']['lonmin'])
        lonMax = float(dom['Limits']['lonmax'])
        latMin = float(dom['Limits']['latmin'])
        latMax = float(dom['Limits']['latmax'])
        msg('i','Domain is read from ' + cfg['Analysis']['domainfile'])
    except:
        pass
    msg('i','Domain limits are '+ str(lonMin) + ', ' + str(lonMax) + 
                           ', ' + str(latMin) + ', ' + str(latMax))

    cfg['Analysis']['lonmin'] = lonMin
    cfg['Analysis']['lonmax'] = lonMax
    cfg['Analysis']['latmin'] = latMin
    cfg['Analysis']['latmax'] = latMax

    return cfg

#==============================================================================
if __name__ == "__main__":
    '''
    Generic Validation Driver 
    '''
    msg('time', str(datetime.datetime.utcnow()) + ' UTC')
    cmd = read_cmd_argv (sys.argv[1:])   # Read command line aruments
    cfg = csdllib.oper.sys.config (cmd.iniFile) # Read config file   
    cycle = ''                                  # OFS cycle
    
    try:
        cycle = cfg['Forecast']['cycle']            
    except:
        pass
    # Set up validation execution paths, flush tmp directory
    workDir = cfg['Analysis']['workdir']
    dataDir = cfg['Analysis']['localdatadir']
    tmpDir  = cfg['Analysis']['tmpdir']
    wwwDir  = cfg['Analysis']['reportdir']
    RemoteDir = cfg['Upload']['remote_htm']
    RemotecsvDir = cfg['Upload']['remote_csv']    
    RemoteimgDir = cfg['Upload']['remote_img']
    #imgDir  = os.path.join(wwwDir, cfg['Analysis']['imgdir'])
    imgDir  = os.path.join(wwwDir, cfg['Analysis']['imgdir'])
    setDir (workDir)
    setDir (dataDir)
    setDir (wwwDir, flush=True)
    setDir (imgDir)
    setDir (tmpDir, flush=True)
    setDir (imgDir)
    setDir (RemoteDir)
    setDir (RemotecsvDir)
    setDir (RemoteimgDir)
    cfg = setDomainLimits(cfg)                  # Set domain limits 

    
    # Find and validate path(s) to model output(s)
    expPaths = []                        # Define path(s) to experiment(s)
    if os.path.isdir(cmd.paths):   # cmd line argument was a single path.
        expPaths.append(os.path.join(cmd.paths,'')) 
    elif os.path.isfile(cmd.paths):      # check if this is a list file.
        with open(cmd.paths) as f:       # cmd line argument was a list 
            lines = f.readlines()        #  with possible path(s) to run(s)
            f.close()
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
    mainTag = ''
    try:
        mainTag = cfg['Analysis']['tag']
    except:
        pass
    
    for p in expPaths:
        folders = p.split('/')           # beware of reverse slashes!
        for f in folders:
            if f=='':
                folders.remove(f)
        tag = folders[-3] + '.' + folders[-2] + '.' + folders[-1]

        if len(mainTag):
            if not folders[-1]:
                tag = folders[-3] + '.' + folders[-2] + '.' + mainTag
            else:
                tag = folders[-3] + '.' + folders[-2] + '.' + folders[-1]+'.'+ mainTag
 
        if len(cycle):
            tag = folders[-3] + '.' + folders[-2] + '.' + folders[-1]+'.'+cycle

            if len(mainTag):
                tag = folders[-3] + '.' + folders[-2] + '.' + folders[-1]+'.'+ mainTag+'.' + cycle


        expTags.append(tag)
        msg (' ',p + ' tag=' + tag)
    
    diagVar = cfg['Analysis']['name'].lower() 
    msg ('i', 'Working on variable=' + diagVar)
    
    # Run diagnostics - individual and across the experiments
    expStats = []
    for n in range(len(expPaths)):
        
        tag  = expTags[n]
        path = expPaths[n] 

        stats, info, datespan, tag = waterLevel (cfg, path, tag)
        expTags[n] = tag # in case if OFS cycle was detected
        
        expStats.append( stats )
        avgStats = []
        if cfg['Analysis']['pointdatastats']:            
                writeLocalStats(cfg, tag, stats, info)
                avgStats    = computeAvgStats (stats)
                appendGlobalStats(cfg, tag, avgStats)

        # Save/upload diagnostics reports
        
        singleReport (cfg, tag, info, datespan, stats, avgStats)
        
        
