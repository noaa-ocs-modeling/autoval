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
def fieldValidation (cfg, path, tag):
    '''
    Works on point data
    '''
    fieldVal = []
    msg('e','Not Yet Implemented.')
    return fieldVal

#==============================================================================
def pointValidation (cfg, path, tag):
    '''
    Works on point data
    '''
    pointVal   = []
    tmpDir     = cfg['Analysis']['tmpdir']
    
    # Choose the model output file
    fmask = cfg['WaterLevel']['pointfilemask']
    masks = fmask.split(',')
    cycle = ''
    try:
        cycle = cfg['Forecast']['cycle']
    except:
        pass
    pointsFile = []
    for m in masks:
        f = glob.glob(path + '*' + cycle + '*' + m + '*')
        for fil in f:
            pointsFile.append(fil)
    if len(pointsFile)>1:
        msg('w','Found more than 1 point output. Verify your mask!')
        for f in pointsFile:
            print(f)
        pointsFile.sort(key=os.path.getmtime)
    pointsFile = pointsFile[-1] # Taking the latest cycle (estofs)
    # Update tag with the detected OFS cycle
    if cycle == '':
        for cycle in ['t00z','t06z','t12z','t18z']:
            if cycle in pointsFile:
                tag = tag + '.' + cycle
                msg('i','Tag updated: ' + tag)

    # Read list of stations out of model file
    model    = csdllib.models.adcirc.readTimeSeries (pointsFile)
    stations = model['stations']
    if len(stations) == 0:
        msg('w','No stations found')
        
    # Set/get bbox
    lonMin = float( cfg['Analysis']['lonmin'])
    lonMax = float( cfg['Analysis']['lonmax'])
    latMin = float( cfg['Analysis']['latmin'])
    latMax = float( cfg['Analysis']['latmax'])

    # Set/get datespan
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

        validStation    = True
        singlePointData = dict ()
        forecast        = model['zeta'][:,n]
        forecast[np.where(forecast<-100.)] = np.nan  # _fillvalue doesnt work
        nosid           = csdllib.data.coops.getNOSID(stations[n].strip())
        if nosid is None:
            validStation = False
        
        if validStation:    
            # Get stations' info, save locally as info.nos.XXXXXXX.dat
            localFile = os.path.join(
                cfg['Analysis']['localdatadir'], 'info.nos.'+nosid+'.dat')
            if not os.path.exists(localFile):
                info = csdllib.data.coops.getStationInfo (nosid, 
                                        verbose=1, tmpDir=tmpDir)
                
                if info is None:
                    msg('w','No info found for station ' + nosid)
                    validStation = False

                if validStation:
                    csdllib.data.coops.writeStationInfo (info, localFile)
            else:
                if validStation:
                    info = csdllib.data.coops.readStationInfo (localFile)   

            if validStation:
                lon = float(info['lon'])
                lat = float(info['lat'])

            if validStation and                         \
                lonMin <= lon and lon <= lonMax and     \
                latMin <= lat and lat <= latMax:

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
                elif len(forecast) == 0 or np.sum(~np.isnan(forecast)) == 0:
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

                pointVal.append ( singlePointData )
                # Plot time series
                if cfg['Analysis']['pointdataplots']: 
                    
                    try:
                        plt.waterlevel.pointSeries(cfg, 
                            obsVals, modVals, refDates, nosid, info, tag, 
                            model['time'], forecast)
                    except:
                        validStation = False
                    pass

                # Plot dashpanels
                if cfg['Analysis']['pointskillpanel'] and validStation: 
                    plt.skill.panel(cfg, M, refDates, nosid, info, tag)

                # Plot submaps of station locations
                if cfg['Analysis']['pointlocationmap'] and validStation: 
                    plt.waterlevel.stationMap(cfg, nosid, info, tag)

            else:
                msg('i','Station ' + nosid + ' is not within the domain. Skipping')


    # # # Done running on stations list
    return pointVal, datespan, tag

#==============================================================================
def waterLevel (cfg, path, tag):
    '''
    Performs waterlevel validation of a single given run.
    '''

    # Field data analysis
    if cfg['Analysis']['fielddataplots']:
        fieldVal = fieldValidation (cfg, path, tag)

    # Point data (time series, hardwired to COOPS tide gauges)
    if cfg['Analysis']['pointdatastats']:
        pointVal, datespan, tag = pointValidation (cfg, path, tag)
        lon  = []
        lat  = []
        info = []
        mtx = []
        for point in pointVal:
            lon.append ( point['info']['lon'] )
            lat.append ( point['info']['lat'] )
            info.append ( point['info'])
            mtx.append ( point['metrics'] )

        # Plot stats on the map
        if cfg['Analysis']['pointskillmap']:
            plt.skill.map (cfg, lon, lat, mtx, 'rmsd', [0., 1.],      [0.,0.2],tag)
            plt.skill.map (cfg, lon, lat, mtx, 'bias', [-1., 1.],     [-0.2, 0.2], tag)
            plt.skill.map (cfg, lon, lat, mtx, 'peak', [-1., 1.],     [-0.2, 0.2], tag)
            plt.skill.map (cfg, lon, lat, mtx, 'plag', [-360., 360.], [-30., 30.], tag)
            plt.skill.map (cfg, lon, lat, mtx, 'skil', [0., 1.],      [0.8, 1.], tag)
            plt.skill.map (cfg, lon, lat, mtx, 'rval', [0., 1.],      [0.8, 1.], tag)
            plt.skill.map (cfg, lon, lat, mtx, 'vexp', [0., 100.],    [80., 100.], tag)
            plt.skill.map (cfg, lon, lat, mtx, 'npts', [0., 1000.],   [240.,1000.], tag)
    return mtx, info, datespan, tag