"""
@author: Sergey.Vinogradov@noaa.gov
"""
import csdllib
import os
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
import matplotlib.dates as mdates
import numpy as np
from .field import set
from .field import readCoastline
from csdllib.methods.convert import ft2meters
import matplotlib
matplotlib.use('Agg',warn=False)
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from datetime import timedelta as dt


#==============================================================================
def pset (xlim, ylim, datums, floodlevels, zero='MSL',width=14, height=4.5):
    """
    stages the hydrograph plot with vertical datums and flood levels.
    Returns figure and axis handles.
    """
        
    fig, ax = plt.subplots(sharex=True, figsize=(width, height))
    ax2 = ax.twinx()
    ax.plot([],[])

    """
    TODO: Extract the below to addDatums() and addLevels()
    """
    if datums:

        datum_mhhw_ft = datums['datum_mhhw_ft']
        datum_mllw_ft = datums['datum_mllw_ft']
        datum_msl_ft  = datums['datum_msl_ft']
        datum_hat_ft  = datums['datum_hat_ft']

        shift = 0.
        datum_msl_m = 0
        if zero is 'MLLW':
            shift =  - datum_mllw_ft + datum_msl_ft
            datum_msl_m = ft2meters( datum_msl_ft )
    
    if floodlevels:

        fl_major_ft   = floodlevels['fl_major_ft']
        fl_moder_ft   = floodlevels['fl_moder_ft']
        fl_minor_ft   = floodlevels['fl_minor_ft']

        # Compute and plot minor flood level
        fl_minor_m = ft2meters( datum_mhhw_ft+fl_minor_ft-datum_msl_ft+shift ) 
        if not np.isnan(fl_minor_m) and fl_minor_m < ylim[1]:
            ax.plot(xlim[0], fl_minor_m, 'dr', markerfacecolor='r')
            ax.text(xlim[0], fl_minor_m,\
                    'Minor Flood: ' + str(np.round(fl_minor_m,2)),color='k',fontsize=7)
            p = patches.Rectangle((mdates.date2num(xlim[0]), fl_minor_m), \
                                mdates.date2num(xlim[1])-mdates.date2num(xlim[0]), \
                                ylim[1]-fl_minor_m, \
                                color='r',alpha=0.15)
            ax.add_patch(p)
                
        # Compute and plot moderate flood level
        fl_moder_m = ft2meters( datum_mhhw_ft+fl_moder_ft-datum_msl_ft+shift ) 
        if not np.isnan(fl_moder_m) and fl_moder_m < ylim[1]:
            ax.plot(xlim[0], fl_moder_m, 'dr', markerfacecolor='r')
            ax.text(xlim[0], fl_moder_m,\
                    'Moderate Flood: '+ str(np.round(fl_moder_m,2)),color='k',fontsize=7)
            p = patches.Rectangle((mdates.date2num(xlim[0]), fl_moder_m), \
                                mdates.date2num(xlim[1])-mdates.date2num(xlim[0]), \
                                ylim[1]-fl_moder_m, \
                                color='r',alpha=0.15)
            ax.add_patch(p)

        # Compute and plot major flood level
        fl_major_m = ft2meters( datum_mhhw_ft+fl_major_ft-datum_msl_ft+shift ) 
        if not np.isnan(fl_major_m) and fl_major_m < ylim[1]:
            ax.plot(xlim[0], fl_major_m, 'dr', markerfacecolor='r')
            ax.text(xlim[0], fl_major_m,\
                    'Major Flood: ' + str(np.round(fl_major_m,2)),color='k',fontsize=7)
            p = patches.Rectangle((mdates.date2num(xlim[0]), fl_major_m), \
                                mdates.date2num(xlim[1])-mdates.date2num(xlim[0]), \
                                ylim[1]-fl_major_m, \
                                color='r',alpha=0.15)
            ax.add_patch(p)

        # Compute and plot MHHW datum
        datum_mhhw_m = ft2meters( datum_mhhw_ft-datum_msl_ft+shift ) 
        if not np.isnan(datum_mhhw_m) and datum_mhhw_m < ylim[1]:
            ax.plot(xlim, [datum_mhhw_m, datum_mhhw_m], color='c')
            ax.plot(xlim[1], datum_mhhw_m, 'dc', markerfacecolor='c')
            ax.text(xlim[1] - dt(hours=6), 
                    datum_mhhw_m + 0.05, 'MHHW',color='c',fontsize=7)

        # Compute and plot MLLW datum
        datum_mllw_m = ft2meters( datum_mllw_ft-datum_msl_ft+shift ) 
        if not np.isnan(datum_mllw_m) and datum_mllw_m > ylim[0] and datum_mllw_m < ylim[1]:
            ax.plot(xlim, [datum_mllw_m, datum_mllw_m], color='c')
            ax.plot(xlim[1], datum_mllw_m, 'dc', markerfacecolor='c')
            ax.text(xlim[1] - dt(hours=6), 
                    datum_mllw_m + 0.05, 'MLLW',color='c',fontsize=7)

        # Compute and plot HAT datum
        datum_hat_m  = ft2meters( datum_hat_ft-datum_msl_ft+shift ) 
        if not np.isnan(datum_hat_m) and datum_hat_m < ylim[1]:
            ax.plot(xlim, [datum_hat_m, datum_hat_m], color='y')
            ax.plot(xlim[1], datum_hat_m, 'dy', markerfacecolor='y')
            ax.text(xlim[1] - dt(hours=6), 
                    datum_hat_m  + 0.05, 'HAT',color='y',fontsize=7)

        # Plot LMSL datum
        if not np.isnan(shift):
            ax.plot(xlim, [ft2meters(shift), ft2meters(shift)], color='k')
            ax.plot(xlim[1], ft2meters(shift), 'dk',color='k')
            ax.text(xlim[1] - dt(hours=6), 0.05+ft2meters(shift), 'LMSL',color='k',fontsize=7)

        # Plot 'now' line
        #ax.plot( [now, now], ylim, 'k',linewidth=1)
        #ax.text(  now + dt(hours=1),  ylim[1]-0.4,'N O W', color='k',fontsize=6, 
        #          rotation='vertical', style='italic')
    
    return fig, ax, ax2

#==============================================================================
def add (ax, dates, values, color='k',label='',lw=2):
    """
    Adds time series and its paraphernalia to the axis
    """
    ax.plot(dates, values, color=color, label=label,linewidth=lw)
    return ax

#==============================================================================
def addDatums(ax):
    """
    Adds vertical datums to the axis
    """
    cs.oper.sys.msg('e','function is not yet implemented')
    return ax

#==============================================================================
def addLevels(ax):
    """
    Adds (flood) levels to the plot
    """
    cs.oper.sys.msg('e','function is not yet implemented')
    return ax


#==============================================================================
def stationMap(cfg, nosid, info, tag):
    '''  
    Plots one stations map 
    '''
    imgDir  = os.path.join( cfg['Analysis']['reportdir'], 
                            cfg['Analysis']['imgdir'])

    figFile = os.path.join( \
        imgDir, 'loc.'+nosid+'.png')
    if os.path.exists(figFile):
        return

    xo = info['lon']
    yo = info['lat']
    dx = 1.8
    dy = 1.8

    coastlineFile = os.path.join(
        cfg['Analysis']['localdatadir'], 'coastline.dat')    
    if not os.path.exists(coastlineFile):
        csdllib.oper.transfer.download (cfg['PlotData']['coastlinefile'], coastlineFile)
    coast = readCoastline  (coastlineFile)

    fig = set(cfg, [xo-dx, xo+dx], [yo-dy, yo+dy], fig_w=3.0, coast=coast)
    plt.suptitle(info['name'] + ' ' + info['state'], fontsize=8)

    plt.scatter(xo, yo, c='r', marker = 'o', edgecolors='k', s=30,zorder=2)
    plt.text(xo+0.01*dx, yo+0.01*dy, str(info['nosid']), color='darkblue', fontsize=7, weight='bold',zorder=2)

    plt.savefig(figFile)
    plt.close(fig)
    plt.close()
#==============================================================================
def pointSeries(cfg, obsVals, modVals, refDates, nosid, info, tag, 
                forecastDates = None, forecast = None, nowcast_biased = None):
    '''
    Plots one station.
    '''

    imgDir  = os.path.join( cfg['Analysis']['reportdir'], 
                            cfg['Analysis']['imgdir'])

    xlim = [min(refDates), max(refDates)]

    ylim = [cfg['WaterLevel']['pointymin'],cfg['WaterLevel']['pointymax']]

    datums      = 0
    floodlevels = 0

    if cfg['Analysis']['nowcast'] == 1: 
       num_intervals_per_hour = int(60 / 6)  # 6 minutes interval
       num_intervals_hours = num_intervals_per_hour * cfg['Analysis']['nowcastperiodineachfile']

    if forecastDates is not None:
            xlim[1] = forecastDates[-1]

    #fig, ax, ax2 = csdllib.plot.series.set(xlim, ylim, datums, floodlevels)
    fig, ax, ax2 = pset(xlim, ylim, datums, floodlevels)

    if obsVals is not None:
       ax.plot(refDates, obsVals, color='lime', linestyle='-',label='OBS', lw=2)
       #ax.legend(bbox_to_anchor=(0.8, 0.82), loc='center left',prop={'size':6})

    if forecast is not None:
       if cfg['Analysis']['nowcast'] == 1:
           #ax = csdllib.plot.series.add(ax, forecastDates, forecast, 
             #color='b',label='FCST',lw=1)
           #ax = add(ax, forecastDates, forecast,color='b',label='FCST',lw=1)
           idx = np.where(refDates < forecastDates[int(num_intervals_hours)])[0][-1]
           ax.plot(refDates[:idx], modVals[:idx], color='b', linestyle='--', label='MOD Nowcast', lw=2)
           ax.plot(refDates[idx:], modVals[idx:], color='b', linestyle='-',label='MOD', lw=2)
       else:
           ax.plot(refDates, modVals, color='b', linestyle='-', label='MOD', lw=2)
            
    ax.legend(bbox_to_anchor=(0.8, 0.82), loc='center left',prop={'size':6})

    ax.text(xlim[0],ylim[1]+0.05,'NOAA / OCEAN SERVICE')
    ax.set_ylabel ('WATER LEVELS, meters')
    ax2.set_ylabel('WATER LEVELS, feet')
    ax.set_xlabel('DATE/TIME UTC')
    ax.grid(True,which='both')
    if obsVals is not None:
        peak_obs_val = np.nanmax(obsVals)
        peak_obs_dat = refDates[np.argmax(obsVals)]
    peak_mod_val = np.nanmax(modVals)
    peak_mod_dat = refDates[np.argmax(modVals)]
    if forecast is not None:
        peak_fst_val = np.nanmax(forecast)
        peak_fst_dat = forecastDates[np.argmax(forecast)]
        if ylim[0] <= peak_fst_val and peak_fst_val <= ylim[1]:
            ax.plot(peak_fst_dat, peak_fst_val, 'o',
                markerfacecolor='b', markeredgecolor='b')
            ax.plot([peak_fst_dat, peak_fst_dat],[ylim[0],peak_fst_val], 
                '--',c='b')
            ax.text(peak_fst_dat, 1.06*peak_fst_val, 
                str(np.round(peak_fst_val,1)) + "m",
                color='darkblue', fontsize=7, weight='bold')
    if ylim[0] <= peak_mod_val and peak_mod_val <= ylim[1]:
        ax.plot(peak_mod_dat, peak_mod_val, 'o',
                markerfacecolor='b', markeredgecolor='k')
        ax.plot([peak_mod_dat, peak_mod_dat],[ylim[0],peak_mod_val], 
                '--',c='b')
    if cfg['Analysis']['nowcast'] == 1: 
       #num_intervals_per_hour = int(60 / 6)  # 6 minutes interval
       #num_intervals_hours = num_intervals_per_hour * cfg['Analysis']['nowcastperiodineachfile']
       # Add a dashed vertical line at start of forecast
       ax.axvline(x=forecastDates[int(num_intervals_hours)], color='r', linestyle='--')
       if cfg['Analysis']['biascorrection'] == 1 and obsVals is not None:
          bias = np.nanmean(nowcast_biased[:idx])-np.nanmean(obsVals[:idx])
          ax.text(xlim[0]+0.05*(xlim[1]-xlim[0]), ylim[0]+0.1*(ylim[1]-ylim[0]), 'Adjusted Bias {:.2f}m'.format(bias), fontsize=8, color='red', ha='left', va='bottom')

    if obsVals is not None and ylim[0] <= peak_obs_val and peak_obs_val <= ylim[1]:
        ax.plot(peak_obs_dat, peak_obs_val, 'o',
                markerfacecolor='limegreen', markeredgecolor='k')
        ax.plot([peak_obs_dat, peak_obs_dat],[ylim[0],peak_obs_val], 
                '--',c='limegreen')
        ax.text(peak_obs_dat, 1.06*peak_obs_val, 
                str(np.round(peak_obs_val,1)) + "m (" + 
                str(np.round(3.28084*peak_obs_val,1)) +"ft)",
                color='forestgreen', fontsize=7, weight='bold')
 
    ax.xaxis.set_major_locator(mdates.DayLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d\n00:00'))
    ax.xaxis.set_minor_locator(MultipleLocator(0.5))

    ax.set_xlim (        xlim)
    ax.set_ylim (        ylim)
    ax2.set_ylim(3.28084*ylim[0], 3.28084*ylim[1])
    ax2.plot([],[])

    plt.suptitle(tag + ' ' + nosid + ' ' + info['name'] + ', ' + info['state'], fontsize=8)
    plt.tight_layout()
    
    figFile = os.path.join( \
        imgDir, 'ts.'+nosid+'.png')
#        imgDir, tag+ '.ts.'+nosid+'.png')
    plt.savefig(figFile)
    plt.close(fig)
    plt.close()
    
    return
