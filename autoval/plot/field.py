"""
@author: Sergey.Vinogradov@noaa.gov
"""
import os
import csdllib
import matplotlib
matplotlib.use('Agg',warn=False)
import matplotlib.pyplot as plt
import numpy as np 

#==============================================================================
def map (cfg, grid, field, tag):
    '''
    Plots a map for a triangulated surface data.
    '''
    # Download / read map plot data
    # Get coastline
    coastlineFile = os.path.join(
        cfg['Analysis']['localdatadir'], 'coastline.dat')    
    if not os.path.exists(coastlineFile):
        csdllib.oper.transfer.download (cfg['PlotData']['coastlinefile'], coastlineFile)
    coast = csdllib.plot.map.readCoastline  (coastlineFile)

    # Check limits of the grid?
    lonlim = [ float(cfg['Analysis']['lonmin']), float(cfg['Analysis']['lonmax']) ]
    latlim = [ float(cfg['Analysis']['latmin']), float(cfg['Analysis']['latmax']) ]

    # Get clim
    diagVar = cfg['Analysis']['name'] 
    clim = [ float(cfg[diagVar]['maxfieldymin']), 
             float(cfg[diagVar]['maxfieldymax']) ]

    field[np.where(field<clim[0])] = np.nan
    field[np.where(field>clim[1])] = np.nan

    fig = csdllib.plot.map.set(lonlim, latlim, coast=coast)
    csdllib.plot.map.addField (grid, field, clim = clim, zorder=0, plotMax = True)
    plt.suptitle(tag + ' ', fontsize=8)    
    figFile = os.path.join( 
        cfg['Analysis']['workdir'], tag+'.map.max.png')
    plt.savefig(figFile)
    plt.close()

    #==============================================================================
    def movie (cfg, grid, field, tag):
        return