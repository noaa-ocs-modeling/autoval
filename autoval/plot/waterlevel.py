"""
@author: Sergey.Vinogradov@noaa.gov
"""
import csdllib
import os
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
import matplotlib.dates as mdates
import numpy as np

#==============================================================================
def pointSeries(cfg, obsVals, modVals, refDates, nosid, info, tag):
    '''
    Plots one station.
    '''
    xlim = [min(refDates), max(refDates)]
    ylim = [cfg['WaterLevel']['pointymin'],cfg['WaterLevel']['pointymax']]
    datums      = 0
    floodlevels = 0

    fig, ax, ax2 = csdllib.plot.series.set(xlim, ylim, datums, floodlevels)
    ax = csdllib.plot.series.add(ax, refDates, obsVals, color='lime',label='OBS',lw=2)
    ax = csdllib.plot.series.add(ax, refDates, modVals, color='b',label='MOD',lw=1)
    
    ax.legend(bbox_to_anchor=(0.8, 0.82), loc='center left',prop={'size':6})
    ax.text(xlim[0],ylim[1]+0.05,'NOAA / OCEAN SERVICE')
    ax.set_ylabel ('WATER LEVELS, meters MSL')
    ax2.set_ylabel('WATER LEVELS, feet MSL')
    ax.set_xlabel('DATE/TIME UTC')
    ax.grid(True,which='both')

    peak_obs_val = np.nanmax(obsVals)
    peak_obs_dat = refDates[np.argmax(obsVals)]
    peak_mod_val = np.nanmax(modVals)
    peak_mod_dat = refDates[np.argmax(modVals)]
  
    if ylim[0] <= peak_mod_val and peak_mod_val <= ylim[1]:
        ax.plot(peak_mod_dat, peak_mod_val, 'o',
                markerfacecolor='b', markeredgecolor='k')
        ax.plot([peak_mod_dat, peak_mod_dat],[ylim[0],peak_mod_val], 
                '--',c='b')
    
    if ylim[0] <= peak_obs_val and peak_obs_val <= ylim[1]:
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
        cfg['Analysis']['workdir'], tag+ '.ts.'+nosid+'.png')
    plt.savefig(figFile)
    plt.close()
    
    return
