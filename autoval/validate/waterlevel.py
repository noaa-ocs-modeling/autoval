"""
@author: Sergey.Vinogradov@noaa.gov
"""
import glob
import csdllib

#==============================================================================
def timeSeriesStats (pointFile, cfg):
    """
    Reads model time series
    Downloads/reads CO-OPS data
    Computes time series stats on a specified datespan
    """
    stats = []
    model = \
        csdllib.models.adcirc.readTimeSeries (pointFile, ncVar = 'zeta', verbose=1)
    print (model)    
    return stats
    
#==============================================================================
def waterlevel (cfg, path):
    """
    Performs waterlevel validation of a single given run.
    Returns diagnostic fields (diagFields) for multirun analysis, if requested
    """
    pointStats = []
    # Point data (time series, hardwired to COOPS tide gauges)
    if cfg['Analysis']['pointdatastats']:
        fmask = cfg['WaterLevel']['pointfilemask']
        masks = fmask.split(',')
        pointFile = []
        for m in masks:
            f = glob.glob(path + m)
            if len(f):
                pointFile.append(f[0])
        if len(pointFile)>1:
            msg['w','Found more than 1 point output. Verify your mask!']
            for f in pointFile:
                print(f)
        pointFile = pointFile[0]
        
        pointStats = timeSeriesStats (pointFile, cfg)
        
    # 2. Parse cfg on what to do
    

    # 3. Call out validation, save
    # 4. Call out report generator
    # 5. Call out plotting

    return pointStats