"""
@author: Sergey.Vinogradov@noaa.gov
"""
import csdllib
import os
import matplotlib.pyplot as plt

#==============================================================================
def pointSeries(cfg, obsVals, modVals, refDates, nosid, tag):
    
    xlim = cfg['WaterLevel']['PointXMin']
    ylim = cfg['WaterLevel']['PointYMin']
    datums      = 0
    floodlevels = 0

    fig, ax, ax2 = csdllib.plot.series.set(xlim, ylim, datums, floodlevels)
    ax = csdllib.plot.series.add(ax, refDates, obsVals, color='g',label='OBS',lw=2)
    ax = csdllib.plot.series.add(ax, refDates, modVals, color='b',label='MOD',lw=1)
    ax.set_ylabel ('WATER LEVELS, meters MSL')
    figFile = os.path.join( cfg['Analysis']['workdir'],     \
                            'ts.' + tag+ '.' + nosid + '.png')
    plt.savefig(figFile)
    plt.close()
    
    return
