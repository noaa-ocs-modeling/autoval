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
import copy

#==============================================================================
def detectCycle (tag):
    cycle = ''
    masks = ['t00z', 't06z', 't12z', 't18z']
    for mask in masks:
        if mask in tag:
            cycle = mask
    return cycle

#==============================================================================
def selectOutputFile (cfg, path, tag, fmasks):
    '''
    Selects the file to read, and updates experiment tag if needed
    '''
    masks = fmasks.split(',')
    cycle = ''
    try:
        cycle = cfg['Forecast']['cycle']
    except:
        pass 
    if cycle == '':   
        cycle = detectCycle (tag)
    print ('tag=' + tag)
    print ('cycle=' + cycle)
    outputFile = []
    for m in masks:
        f = glob.glob(path + '*' + cycle + '*' + m + '*')
        for fil in f:
            outputFile.append(fil)
    if len(outputFile)>1:
        msg('w','Found more than 1 output detected. Verify your mask!')
        for f in outputFile:
            print(f)
        outputFile.sort(key=os.path.getmtime)
    outputFile = outputFile[-1] # Taking the latest cycle (estofs)
    # Update tag with the detected OFS cycle
    if cycle == '':
        for cycle in ['t00z','t06z','t12z','t18z']:
            if cycle in outputFile:
                tag = tag + '.' + cycle
                msg('i','Tag updated: ' + tag)

    return outputFile, tag

#==============================================================================
def multi_plot (cfg, tag, grid, model, clim, n):
    '''
    Possible multiprocessing execution. 
    '''
    figFile = os.path.join( 
                    cfg['Analysis']['tmpdir'], 
                    tag+'.mov.'+ str(n).zfill(3) + '.png')

    plt.field.map( cfg, grid, model['value'][n,:], 
                              clim, tag, title=
                               str(n).zfill(3) + ' ' + 
                               timeToStamp(model['time'][n]),
                               fig_w = 8.0)
    plt.field.save(figFile)

#==============================================================================
def fieldValidation (cfg, path, tag, grid):
    '''
    Works on point data
    '''
    imgDir  = os.path.join( cfg['Analysis']['reportdir'], 
                            cfg['Analysis']['imgdir'])
    tmpDir  = cfg['Analysis']['tmpdir']

    fieldVal = []
    diagVar  = cfg['Analysis']['name']

    # Choose the model output file
    fmask = cfg[diagVar]['fieldfilemask']
    fieldFile, tag = selectOutputFile (cfg, path, tag, fmask)
    model    = csdllib.models.adcirc.readSurfaceField (fieldFile, 
                            cfg[diagVar]['fieldfilevariable'])
    
    if True: # Plot maxele
        maxele  = csdllib.models.adcirc.computeMax (model['value'])
        lons  = model['lon']
        print('maxele lonlim = ' + str(np.min(lons)) + ' ' + str(np.max(lons)))
        clim = [ float(cfg[diagVar]['maxfieldymin']), 
                 float(cfg[diagVar]['maxfieldymax']) ]
        
        if diagVar == 'waterlevel':
            plt.field.map (cfg, grid, maxele, clim, tag, 'Maximal Elevation')
            figFile = os.path.join(imgDir, 'map.max.png')

        if diagVar == 'windvelocity':
            plt.field.map (cfg, grid, maxele, clim, tag, 'Maximal Wind Velocity')
            figFile = os.path.join(imgDir, 'map.maxwvel.png')

        plt.field.save (figFile)

        #Zoom levels, 1 to 4
        for zoom in range(1,5):
            print('Working on zoom ' + str(zoom))
            try:
                iniFile = cfg['Zoom'+str(zoom)]['domainfile']
                lonlim, latlim = csdllib.plot.map.ini(iniFile, 
                             local=os.path.join(tmpDir, 'mapfile.ini'))
                cfgzoom = copy.deepcopy(cfg)
                cfgzoom['Analysis']['lonmin'] = lonlim[0]
                cfgzoom['Analysis']['lonmax'] = lonlim[1]
                cfgzoom['Analysis']['latmin'] = latlim[0]
                cfgzoom['Analysis']['latmax'] = latlim[1]
                #figFile = os.path.join(imgDir, tag+'.map.max.'+ str(zoom)+'.png')
                if diagVar == 'waterlevel':
                    plt.field.map (cfgzoom, grid, maxele, clim, tag, 
                               'Maximal Elevation', fig_w=5.0)
                    figFile = os.path.join(imgDir, 'map.max.'+ str(zoom)+'.png')
                
                if diagVar == 'windVelocity':
                    plt.field.map (cfgzoom, grid, maxele, clim, tag, 
                               'Maximal Wind Velocity', fig_w=5.0)
                    figFile = os.path.join(imgDir, 'map.maxwvel.'+ str(zoom)+'.png')
       
                plt.field.save (figFile)
            except:
                pass
        
        #maxele  = csdllib.models.adcirc.read   (model['value'])
        #lons  = model['lon']
        #print('maxele lonlim = ' + str(np.min(lons)) + ' ' + str(np.max(lons)))
        #clim = [ float(cfg[diagVar]['maxfieldymin']), 
        #         float(cfg[diagVar]['maxfieldymax']) ]
        #plt.field.map (cfg, grid, maxele, clim, tag, 'Maximal Elevation')
        #figFile = os.path.join(imgDir, 'map.max.png')
        #plt.field.save (figFile)

    if cfg['Analysis']['fieldevolution']: # Do the movie
        if os.system('which convert') == 0:
            clim = [ float(cfg[diagVar]['fieldymin']), 
                     float(cfg[diagVar]['fieldymax']) ]
            
            for n in range(len(model['time'])):
                msg('i','Working on ' + str(n))
                multi_plot(cfg, tag, grid, model, clim, n)

            gifFile = os.path.join( imgDir, tag + '.gif')
            cmd = "convert -delay 20 -loop 1 " + \
                   os.path.join(cfg['Analysis']['tmpdir'], tag+'*.mov*.png') + \
                   " " + gifFile
            os.system(cmd)

        else:
            msg('e','You need Convert installed on your system.')

    return fieldVal, grid, tag

#==============================================================================
def pointValidation (cfg, path, tag):
    '''
    Works on point data
    '''
    pointSkill   = []
    tmpDir     = cfg['Analysis']['tmpdir']
    diagVar    = cfg['Analysis']['name']

    # Choose the model output file
    fmask = cfg[diagVar]['pointfilemask']
    outputFile, tag = selectOutputFile (cfg, path, tag, fmask)

    # Read list of stations out of model file
    model    = csdllib.models.adcirc.readTimeSeries (outputFile)
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
        datespan[0] = stampToTime (cfg[diagVar].get('pointdatesstart'))
    except:
        pass
    try:
        datespan[1] = stampToTime (cfg[diagVar].get('pointdatesend'))
    except:
        pass
    msg ( 'i','Datespan for analysis is set to: ' \
            + timeToStamp(datespan[0]) + ' ' + timeToStamp(datespan[1]) )
    
    for n in range(len(stations)):
        
        msg('i', 'Working on station : ' + str(n).zfill(5) + 
                                     ' ' + stations[n].strip())
        
        myPointData = dict () 
        isVirtual   = False  # 'virtual' station has no obs counterpart

        forecast = model['zeta'][:,n]
        forecast[np.where(forecast<-100.)] = np.nan  # _fillvalue doesnt work

        # Try to obtain NOS ID
        nosid       = csdllib.data.coops.getNOSID ( stations[n].strip() )

        if nosid is None:
            isVirtual = True # add attempts to get UH or GLOSS ids here
        else:

            # Try to get stations' info, save locally as info.nos.XXXXXXX.dat
            localFile = os.path.join(
                    cfg['Analysis']['localdatadir'], 'info.nos.'+nosid+'.dat')
            if not os.path.exists(localFile):
                info = csdllib.data.coops.getStationInfo (nosid, 
                                    verbose=1, tmpDir=tmpDir)
                if info is None:
                    msg('w','No info found for station ' + nosid)
                    isVirtual = True
                else:
                    csdllib.data.coops.writeStationInfo (info, localFile)
            else:
                info = csdllib.data.coops.readStationInfo (localFile)   

        if isVirtual:
            info          = dict()
            info['nosid'] = 'UN'+str(n).zfill(5)
            info['lon']   =  model['lon'][n]
            info['lat']   =  model['lat'][n]
            info['name']  =  model['stations'][n]
            info['state'] = 'UN'
            msg('w','Station is not NOAA gauge. Using id=' + info['nosid'])

        # Check lon/lats
        print(str(info['lon']))
        if  lonMin <= info['lon'] and info['lon'] <= lonMax and     \
            latMin <= info['lat'] and info['lat'] <= latMax:
    
            # plot time series
            if cfg['Analysis']['pointdataplots']: 

                if not isVirtual:
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
                        isVirtual = True
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

                    myPointData['id']      = nosid            
                    myPointData['info']    = info
                    myPointData['metrics'] = M

                    pointSkill.append ( myPointData )

                    try:
                        plt.waterlevel.pointSeries(cfg, 
                            obsVals, modVals, refDates, nosid, info, tag, 
                            model['time'], forecast)
                    except:
                        isVirtual = True
                    pass

                if isVirtual:
                    # Compute statistics    
                    M = csdllib.methods.statistics.metrics (np.nan, np.nan, np.nan)
                    myPointData['id']      = nosid            
                    myPointData['info']    = info
                    myPointData['metrics'] = M
                    pointSkill.append ( myPointData )

                    try:
                        plt.waterlevel.pointSeries(cfg, 
                            None, forecast, model['time'], 
                            info['nosid'], info, tag, 
                            model['time'], forecast)                    
                    except:
                        msg('w','Virtual station ' + nosid + ' was not plotted.')
                        pass

            # plot station map
            if cfg['Analysis']['pointlocationmap']: 
                plt.waterlevel.stationMap(cfg, info['nosid'], info, tag)

            # Plot dashpanels
            if cfg['Analysis']['pointskillpanel'] and not isVirtual: 
                plt.skill.panel(cfg, M, refDates, nosid, info, tag)

        else:
            msg('i','Station ' + info['nosid'] + ' is not within the domain. Skipping')

    # # # Done running on stations list
    return pointSkill, datespan, tag

#==============================================================================
def waterLevel (cfg, path, tag):
    '''
    Performs waterlevel validation of a single given run.
    '''

    # Field data analysis
    if cfg['Analysis']['fielddataplots']:
        # Get the grid
        gridFile = os.path.join(
            cfg['Analysis']['localdatadir'], 'fort.14')    
        csdllib.oper.transfer.refresh (cfg['Analysis']['gridfile'], gridFile)
        grid = csdllib.models.adcirc.readGrid  (gridFile)
        fieldVal, grid, tag = fieldValidation (cfg, path, tag, grid)

    # Point data (time series)
    if cfg['Analysis']['pointdatastats']:
        pointSkill, datespan, tag = pointValidation (cfg, path, tag)
        lon  = []
        lat  = []
        info = []
        mtx = []
        for point in pointSkill:
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