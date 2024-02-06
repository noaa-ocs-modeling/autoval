"""
@author: Sergey.Vinogradov@noaa.gov
"""
import os, glob, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))    
import plot as plt
import csdllib
from csdllib.oper.sys import stampToTime, timeToStamp, msg
from datetime import datetime, timedelta
import numpy as np
import copy
import multiprocessing
import gc
from searvey import coops 
from searvey import ioc
from searvey import uhslc


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
            print(fil)
            outputFile.append(fil)
    if len(outputFile)>1:
        msg('w','Found more than 1 output detected. Verify your mask!')
        for f in outputFile:
            print(f)
        outputFile.sort(key=os.path.getmtime)
    print (outputFile)
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
    if cfg['Analysis']['fielddataplots'] == 1: # Plot maxele
        fmask = cfg[diagVar]['fieldfilemask']
        fieldFile, tag = selectOutputFile (cfg, path, tag, fmask)
        model    = csdllib.models.adcirc.readSurfaceField (fieldFile, 
                            cfg[diagVar]['fieldfilevariable'])
        maxele  = csdllib.models.adcirc.computeMax (model['value'])
        lons  = model['lon']
        print('maxele lonlim = ' + str(np.min(lons)) + ' ' + str(np.max(lons)))
        clim = [ float(cfg[diagVar]['maxfieldymin']), 
                 float(cfg[diagVar]['maxfieldymax']) ]
        
        if diagVar.lower() == 'waterlevel':
            plt.field.map (cfg, grid, maxele, clim, tag, 'Maximal Elevation')
            figFile = os.path.join(imgDir, 'map.max.png')

        if diagVar.lower() == 'windvelocity':
            maxele = 1.94384*maxele  # mps to knots
            plt.field.map (cfg, grid, maxele, clim, tag, 'Maximal Wind Velocity')
            figFile = os.path.join(imgDir, 'map.maxwvel.png')

        plt.field.save (figFile)
        
    
    if cfg['Analysis']['maxfieldplots'] == 1:   
        fmask = cfg[diagVar]['maxfieldfilemask']
        fieldFile, tag = selectOutputFile (cfg, path, tag, fmask)
        model    = csdllib.models.adcirc.readSurfaceField (fieldFile, 
                            cfg[diagVar]['maxfieldvariable'])
        maxele  = model['value']

        lons  = model['lon']
        clim = [ float(cfg[diagVar]['maxfieldymin']), 
                 float(cfg[diagVar]['maxfieldymax']) ]
        if diagVar.lower() == 'waterlevel':
            plt.field.map (cfg, grid, maxele, clim, tag, 'Maximal Elevation')
            figFile = os.path.join(imgDir, 'map.max.png')
        if diagVar.lower() == 'windvelocity':
            maxele = 1.94384*maxele  # mps to knots
            plt.field.map (cfg, grid, maxele, clim, tag, 'Maximal Wind Velocity')
            figFile = os.path.join(imgDir, 'map.maxwvel.png')
        plt.field.save (figFile)
         
    #Zoom levels, 1 to 4
    
    if cfg['Analysis']['maxfieldplots'] == 1 or cfg['Analysis']['fielddataplots'] == 1:   
        
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
                if diagVar.lower() == 'waterlevel':
                    
                    plt.field.map (cfgzoom, grid, maxele, clim, tag, 
                               'Maximal Elevation', fig_w=5.0)
                    figFile = os.path.join(imgDir, 'map.max.'+ str(zoom)+'.png')
                    
                if diagVar.lower() == 'windvelocity':
                    plt.field.map (cfgzoom, grid, maxele, clim, tag, 
                               'Maximal Wind Velocity', fig_w=5.0)
                    figFile = os.path.join(imgDir, 'map.maxwvel.'+ str(zoom)+'.png')
       
                plt.field.save (figFile)
                
            except:
                pass
        
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
    
    return tag

    

#=======================================
# def getData 
def getData(nosid, datespan): 

   try:

      # Retrieve water level infromation for the specified date range             
      station_info = coops.COOPS_Query(int(nosid),product='water_level', start_date=datespan[0], end_date=datespan[1],interval = None, datum = 'MSL',)

      # Perform necessary cleanup                   
      station_df = station_info.data.drop(columns = ['q','s','f'])
      new2_station_df = station_df.reset_index()
      new2_station_df.rename(columns={'t':'dates','v':'values'}, inplace=True)

      # Format the date and time in the DataFrame
      new2_station_df['dates'] =  new2_station_df['dates'].apply(lambda d: datetime(d.year, d.month, d.day, d.hour, d.minute))

      # Extract dates and values as lists
      dates_list = new2_station_df['dates'].tolist() 
      values_list = new2_station_df['values'].apply(lambda v: round(v, 3)).tolist()

      return {'dates' : dates_list, 'values' : values_list} 

   except ValueError as ve: 
      
      # Handle the ValueError exception (station not found)
      print(f"Error: {ve}. Skipping data retrieval for station {nosid}.")
      return {'dates' : [], 'values' : []}


#=======================================

# def getUHSLCID

def getUHSLCID(string):

    """
    Parses 3-digit UHSLC ID from the string
    """
    uhslcid = None
    try:
        uhslcid_full_id = string[2:5]
        uhslcid  = str(int(uhslcid_full_id))
        
        if string[:2] != 'UH':
            uhslcid = None
    except:
        pass
    return uhslcid

#=======================================

# Function to remove outliers from IOC data based on IOC website
def remove_outliers(data, window_size):
    median_values = data.median()
    percentile90 = data.quantile(0.9)
    tolerance = 3 * np.abs(percentile90 - median_values)

    # Hide values where abs(X - median) > tolerance
    outliers_mask = np.abs(data - median_values) > tolerance
    data[outliers_mask] = np.nan

    # Spike removal using median of a window with size 3
    data = data.rolling(window=window_size, center=True, min_periods=1).median()

    return data



#=======================================

# def get_IOC_country

def getIOC_Country(uhslcid,datespan):
    ioc_country = None

    try:

       # get uhslc id , this needs to be changed
       all_UHSLC_stations = uhslc.get_uhslc_data(start_date = datespan[0]-timedelta(days=1095),end_date=datespan[1]-timedelta(days=1085),)   #get data from 3 years ago, UHSLC is not updated
       all_UHSLC_stations = all_UHSLC_stations.set_index('uhslc_id')
       stationn=int(uhslcid)
   
       
       # Get IOC country name for plotting
       ioc_stations_c = all_UHSLC_stations['station_country'][stationn]
       ioc_stations_c_new = ioc_stations_c.reset_index()
       ioc_country = ioc_stations_c_new['station_country'][0]
       return ioc_country

    except:
       return ioc_country
    


#=======================================

# def get_IOC_Data 

# later I should this function that dode not use UHSLC id

def getIOCData(uhslcid,datespan): 

   try:
       # Get IOC Id using uhslc id 
       all_UHSLC_stations = uhslc.get_uhslc_data(start_date = datespan[0]-timedelta(days=1095),end_date=datespan[1]-timedelta(days=1085),)   #get data from 3 years ago, UHSLC is not updated
     
       all_UHSLC_stations = all_UHSLC_stations.set_index('uhslc_id')
       stationn=int(uhslcid)

       ioc_stations = all_UHSLC_stations['ssc_id'][stationn]
       ioc_stations_new = ioc_stations.reset_index()
       ioc_id = ioc_stations_new['ssc_id'][0]
       
         
       # download data using ioc function in searvey
       station_df = ioc.get_ioc_station_data(ioc_code = ioc_id,endtime=datespan[1], )


       # Filter the DataFrame based on the time range
       filtered_df = station_df[(station_df['time'] >= datespan[0]) & (station_df['time'] <= datespan[1])]

       # take data every six minutes
       filtered_df.set_index('time', inplace=True)
       station_df_resampled = filtered_df.resample('6T').first()
       station_df_resampled.reset_index(inplace=True)   
   
       #In some stations we have the report of multiple sensores, here we first calculate the relative water level
       # similar to the IOC website and then we average the value of different sensors

       # Check for the existence of columns 'prs', 'rad', 'ras', and etc.
       columns_to_check = ['pr2', 'rad', 'ras','ra2','bub','flt','pwl','wls']
       existing_columns = [col for col in columns_to_check if col in station_df_resampled.columns]

       if existing_columns:
          # Calculate medians of existing columns
          median_values = station_df_resampled[existing_columns].median()

          # Subtract medians from respective columns
          station_df_resampled[existing_columns] -= median_values

          # Remove outliers and spikes for existing columns
          for col in existing_columns:
             window_size = 3  # Adjust the window size as needed
             station_df_resampled[col] = remove_outliers(station_df_resampled[col], window_size)

          # Detect flat sensors
          flat_sensors = station_df_resampled.columns[station_df_resampled.nunique().eq(1)]

          # drop flat sensors
          station_df_resampled.drop(columns = flat_sensors)
      
          # update the sensor list
          selected_columns = [col for col in columns_to_check if col in station_df_resampled.columns]

          # Calculate the average value considering NaN values
          station_df_resampled['values'] = station_df_resampled[selected_columns].mean(axis=1, skipna=True)

          
          # drop the columns
          station_df_resampled.drop(columns = ['ioc_code'])
          station_df_resampled.drop(columns = selected_columns)
       
       # rename the column
       station_df_resampled.rename(columns={'time':'dates'}, inplace=True)

       # Format the date and time in the DataFrame
       station_df_resampled['dates'] =  station_df_resampled['dates'].apply(lambda d: datetime(d.year, d.month, d.day, d.hour, d.minute))


       # Extract dates and values as lists
       dates_list = station_df_resampled['dates'].tolist()
       values_list = station_df_resampled['values'].apply(lambda v: round(v, 3)).tolist()
       return {'dates' : dates_list, 'values' : values_list}

   except:
       return {'dates' : [], 'values' : []}


#==============================================================================
#def stationValidation(cfg, path, tag, lonMin, lonMax, latMin, latMax, n, stations, model, tmpDir, datespan, pointSkill):
def stationValidation(args):
    (cfg, path, tag, lonMin, lonMax, latMin, latMax, stations, model, tmpDir, datespan), n = args
    msg('i', 'Working on station : ' + str(n).zfill(5) + 
                                   ' ' + stations[n].strip())
    myPointData = dict () 
    isVirtual   = False  # 'virtual' station has no obs counterpart

    forecast = model['zeta'][:,n]
    forecast[np.where(forecast<-100.)] = np.nan  # _fillvalue doesnt work
    

    # Try to obtain NOS ID
    nosid       = csdllib.data.coops.getNOSID ( stations[n].strip() )
  

    # Try to obtaion UHSLC ID
    uhslcid = getUHSLCID ( stations[n].strip() )
    

    # Getting stations' info
    if nosid is None and uhslcid is None:  
        isVirtual = True # add attempts to get UH or GLOSS ids here
   
    elif nosid is None and uhslcid is not None: # Is a IOC station
        info          = dict()
        info['nosid'] = 'UH'+uhslcid.zfill(3)
        info['lon']   =  model['lon'][n]
        info['lat']   =  model['lat'][n]
        info['name']  =  model['stations'][n]
        info['state'] = 'UN'
        info['country'] = getIOC_Country(uhslcid,datespan)
        msg('w','Station is uhslc gauge. Using id=' + info['nosid'])

    else:

        # Try to get stations' info, save locally as info.nos.XXXXXXX.dat
        localFile = os.path.join(cfg['Analysis']['localdatadir'], 'info.nos.'+nosid+'.dat')
        if not os.path.exists(localFile) and uhslcid is None:  # Is not IOC station
            info = csdllib.data.coops.getStationInfo (nosid, 
                                                      verbose=1, tmpDir=tmpDir)
            
            #print(info)
          
            if info is None:
                msg('w','No info found for station ' + nosid)
                isVirtual = True
              
            else:
                csdllib.data.coops.writeStationInfo (info, localFile)
                info['country'] = None
        else:
        
            info = csdllib.data.coops.readStationInfo (localFile)
            info['country'] = None     
    

    if isVirtual:

        info          = dict()
        info['nosid'] = 'UN'+str(n).zfill(5)
        info['lon']   =  model['lon'][n]
        info['lat']   =  model['lat'][n]
        info['name']  =  model['stations'][n]
        info['state'] = 'UN'
        info['country'] = None
        msg('w','Station is not NOAA gauge. Using id=' + info['nosid'])
     

    # Check lon/lats  
  
    
    if info['lon'] < -180 and lonMax - lonMin > 359.:
        info['lon'] = 360.+info['lon']  
        
    if cfg['Analysis']['pacific'] == 1 and info['lon'] < -30: 
        info['lon'] = 360.+info['lon']

    
    if  lonMin <= info['lon'] and info['lon'] <= lonMax and     \
        latMin <= info['lat'] and info['lat'] <= latMax:
       
        # plot time series
        if cfg['Analysis']['pointdataplots']:
        
            #Plot IOS stations
        
            if not isVirtual and uhslcid is not None: # changed this for ioc
                
                localFile = os.path.join(
                        cfg['Analysis']['localdatadir'], 
                        'cwl.uhslc.' + info['nosid'] + '.' + \
                        timeToStamp(datespan[0]) + '-' + \
                        timeToStamp(datespan[1]) + '.dat')
                      
                if not os.path.exists(localFile):
                   
                    obs = getIOCData(uhslcid, datespan)
                    #obs = csdllib.data.coops.getData(nosid, datespan, tmpDir=tmpDir) 
                    csdllib.data.coops.writeData    (obs,  localFile)
                else:
                    
                    obs = csdllib.data.coops.readData ( localFile )
       
              
                refDates = np.nan
                obsVals  = np.nan
                modVals  = np.nan

                if len(obs['values']) == 0 or all(value != value for value in obs['values']):  # check if we do not have observation
                    msg('w','No obs found for station ' + uhslcid + ', skipping.')
                    isVirtual = True
                    
                elif len(forecast) == 0 or np.sum(~np.isnan(forecast)) == 0:
                    msg('w','No forecast found for station ' + uhslcid + ', skipping.')
                   
                else:
                    # Unify model and data series 
                    refDates, obsVals, modVals =            \
                    csdllib.methods.interp.retime  (    \
                    obs ['dates'], obs['values'],   \
                    model['time'], forecast, refStepMinutes=6)
                
           
                # Compute statistics    
                M = csdllib.methods.statistics.metrics (obsVals, modVals, refDates)

                myPointData['id']      = info['nosid']            
                myPointData['info']    = info
                myPointData['metrics'] = M
                

                #pointSkill.append ( myPointData )
 
                try:
                    plt.waterlevel.pointSeries(cfg,
                        obsVals, modVals, refDates, info['nosid'], info, tag,
                        model['time'], forecast)

                    
                except:
                    isVirtual = True
                    
                pass
       
            #Plot NOS stations
 
            if not isVirtual and uhslcid is None:

                # Get station's water levels for this timespan, save locally
                localFile = os.path.join(
                        cfg['Analysis']['localdatadir'], 
                        'cwl.nos.' + nosid + '.' + \
                        timeToStamp(datespan[0]) + '-' + \
                        timeToStamp(datespan[1]) + '.dat')  
 
                          

                if not os.path.exists(localFile):
                    obs = getData(nosid, datespan)
                    #obs = csdllib.data.coops.getData(nosid, datespan, tmpDir=tmpDir) 
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
                

                #pointSkill.append ( myPointData )

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
                 #pointSkill.append ( myPointData )
                
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
      
        
        # Plot dashpanels for IOC stations
        if cfg['Analysis']['pointskillpanel'] and not isVirtual and uhslcid is not None: 
            plt.skill.panel(cfg, M, refDates, info['nosid'], info, tag)
     
        # Plot dashpanels
        if cfg['Analysis']['pointskillpanel'] and not isVirtual and uhslcid is None: 
            plt.skill.panel(cfg, M, refDates, nosid, info, tag)

    else:
        msg('i','Station ' + info['nosid'] + ' is not within the domain. Skipping')
        

    return myPointData
#==============================================================================
def pointValidation (cfg, path, tag):
    '''
    Works on point data
    '''
    pointSkill   = []
    
    tmpDir     = cfg['Analysis']['tmpdir']
    
    diagVar    = cfg['Analysis']['name']
    
    nProcessors = int(cfg['Analysis']['numberofprocessors'])
    
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

    num_stations = len(stations)
    #num_stations = 239
    tupleArgs = []
    for i in range(num_stations):
        tupleArgs.append((cfg, path, tag, lonMin, lonMax, latMin, latMax, stations, model, tmpDir, datespan))

 
    input = zip(tupleArgs, range(num_stations))
  
    pool = multiprocessing.Pool(processes=nProcessors)
    for item in pool.map(stationValidation, input):
        pointSkill.append(item)

    # # # Done running on stations list
    return pointSkill, datespan, tag

#==============================================================================
def waterLevel (cfg, path, tag):
    '''
    Performs waterlevel validation of a single given run.
    '''
    mtx      = []
    info     = []
    datespan = []

    # Field data analysis
    if cfg['Analysis']['fielddataplots'] or cfg['Analysis']['maxfieldplots']:
        # Get the grid
        gridFile = os.path.join(
            cfg['Analysis']['localdatadir'], 'fort.14')    
        csdllib.oper.transfer.refresh (cfg['Analysis']['gridfile'], gridFile)
        grid = csdllib.models.adcirc.readGrid  (gridFile)
        tag = fieldValidation (cfg, path, tag, grid)

    del(grid)
    gc.collect()
    # Point data (time series)
    if cfg['Analysis']['pointdatastats']:
        pointSkill, datespan, tag = pointValidation (cfg, path, tag)
        lon  = []
        lat  = []
        for point in pointSkill:
            lon.append ( point['info']['lon'] )
            lat.append ( point['info']['lat'] )
            info.append ( point['info'])
            mtx.append ( point['metrics'] )

        del(pointSkill)
        gc.collect()
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
