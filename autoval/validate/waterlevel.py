"""
@author: Sergey.Vinogradov@noaa.gov
"""
import os, glob, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))    
import plot as plt
import csdllib
from csdllib.oper.sys import stampToTime, timeToStamp, msg
from datetime import datetime
import numpy as np


#==============================================================================
def pointValidation (cfg, path, tag):
    '''
    Works on point data
    '''
    pointData  = []
    tmpDir     = cfg['Analysis']['tmpdir']
    
    # Choose the model output file
    fmask = cfg['WaterLevel']['pointfilemask']
    masks = fmask.split(',')
    pointsFile = []
    for m in masks:
        f = glob.glob(path + m)
        if len(f):
            pointsFile.append(f[0])
    if len(pointsFile)>1:
        msg['w','Found more than 1 point output. Verify your mask!']
        for f in pointsFile:
            print(f)
    pointsFile = pointsFile[-1] # Taking the latest cycle (estofs)
        
    # Read list of stations out of model file
    model    = csdllib.models.adcirc.readTimeSeries (pointsFile)
    stations = model['stations']
    if len(stations) == 0:
        msg('w','No stations found')
        
    # Set datespan
    dates = model['time']
    datespan = [dates[0], dates[-1]] 
    try:
        datespan[0] = stampToTime (cfg['WaterLevel'].get('pointdatesstart'))
    except:
        pass
    try:
        datespan[1] = stampToTime (cfg['WaterLevel'].get('pointdatesend'))
    except:
        pass
    msg ( 'i','Datespan for analysis is set to: ' \
            + timeToStamp(datespan[0]) + ' ' + timeToStamp(datespan[1]) )
        
    # # # Running on stations list
    # Download / read COOPS stations data
    for n in range(len(stations)):

        singlePointData = dict ()
        forecast        = model['zeta'][:,n]
        nosid           = stations[n].strip()
            
        # Get stations' info, save locally as info.nos.XXXXXXX.dat
        localFile = os.path.join(
                    cfg['Analysis']['localdatadir'], 
                        'info.nos.' + nosid + '.dat')    
        if not os.path.exists(localFile):
            info = csdllib.data.coops.getStationInfo (nosid, 
                                        verbose=1, tmpDir=tmpDir)
            csdllib.data.coops.writeStationInfo (info, localFile)
        else:
            info = csdllib.data.coops.readStationInfo (localFile)            

        msg('i','Working on station ' + nosid + ' ' + info['name'])
            
        # Get station's water levels for this timespan, save locally
        localFile = os.path.join(
                    cfg['Analysis']['localdatadir'], 
                    'cwl.nos.' + nosid + '.' + \
                    timeToStamp(datespan[0]) + '-' + \
                    timeToStamp(datespan[1]) + '.dat')    
        if not os.path.exists(localFile):
            obs = csdllib.data.coops.getData(nosid, datespan, tmpDir=tmpDir)
            csdllib.data.coops.writeData    (obs,  localFile)
        else:
            obs = csdllib.data.coops.readData ( localFile )

        refDates = np.nan
        obsVals  = np.nan
        modVals  = np.nan

        if len(obs['values']) == 0:
            msg('w','No obs found for station ' + nosid + ', skipping.')
        elif len(forecast) == 0:
            msg('w','No forecast found for station ' + nosid + ', skipping.')
        else:
            # Unify model and data series 
            refDates, obsVals, modVals =            \
                csdllib.methods.interp.retime  (    \
                    obs ['dates'], obs['values'],   \
                    model['time'], forecast, refStepMinutes=6)
        # Compute statistics    
        M = csdllib.methods.statistics.metrics (obsVals, modVals, refDates)

        singlePointData['id']      = nosid            
        singlePointData['info']    = info
        singlePointData['metrics'] = M

        pointData.append ( singlePointData )
        # Plot time series
        if cfg['Analysis']['pointdataplots']: 
            validPoint = True
            try:
                plt.waterlevel.pointSeries(cfg, 
                            obsVals, modVals, refDates, nosid, info, tag)
            except:
                validPoint = False
                pass

        # Plot dashpanels
        if cfg['Analysis']['pointskillpanel'] and validPoint: 
            plt.skill.panel(cfg, M, refDates, nosid, info, tag)
    
    # # # Done running on stations list
    return pointData

#==============================================================================
def waterlevel (cfg, path, tag):
    '''
    Performs waterlevel validation of a single given run.
    '''

    # Point data (time series, hardwired to COOPS tide gauges)
    if cfg['Analysis']['pointdatastats']:
        pointData = pointValidation (cfg, path, tag)
        lon = []
        lat = []
        ids = []
        mtx = []
        for point in pointData:
            lon.append ( point['info']['lon'] )
            lat.append ( point['info']['lat'] )
            ids.append ( point['info']['nosid'])
            mtx.append ( point['metrics'] )

        # Plot stats on the map
        if cfg['Analysis']['pointskillmap']:
            plt.skill.map (cfg, lon, lat, mtx, 'rmsd', [0., 1.],  [0.,0.2],tag)
            plt.skill.map (cfg, lon, lat, mtx, 'bias', [-1., 1.], [-0.2, 0.2], tag)
            plt.skill.map (cfg, lon, lat, mtx, 'peak', [-1., 1.], [-0.2, 0.2], tag)
            plt.skill.map (cfg, lon, lat, mtx, 'plag', [-180., 180.], [-30., 30.], tag)
            plt.skill.map (cfg, lon, lat, mtx, 'skil', [0., 1.], [0.8, 1.], tag)
            plt.skill.map (cfg, lon, lat, mtx, 'rval', [0., 1.], [0.8, 1.], tag)
            plt.skill.map (cfg, lon, lat, mtx, 'vexp', [0., 100.], [80., 100.], tag)

    return mtx, ids