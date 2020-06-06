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
def map (cfg, grid, field, clim, tag, title=None, fig_w=8.0):
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
    print('Grid lon lim' + str(lonlim[0]) + ' ' + str(lonlim[1]) )
    # Get clim

    #fmin = np.nanmin(field)
    #fmax = np.nanmax(field)
    fmin = np.nanmin(field[ (lonlim[0]  <= grid['lon']) & 
                            (grid['lon']<= lonlim[1])   &
                            (latlim[0]  <= grid['lat']) & 
                            (grid['lat']<= latlim[1] ) ])

    fmax = np.nanmax(field[ (lonlim[0]  <= grid['lon']) & 
                            (grid['lon']<= lonlim[1])   &
                            (latlim[0]  <= grid['lat']) & 
                            (grid['lat']<= latlim[1] ) ])
        
    #field[np.where(field<clim[0])] = clim[0] #np.nan
    #field[np.where(field>clim[1])] = clim[1] #np.nan

    csdllib.oper.sys.msg('i','Field min/max=' + str(fmin) + '/' + str(fmax))

    fig = csdllib.plot.map.set(lonlim, latlim, coast=coast, fig_w=fig_w)
    csdllib.plot.map.addField (grid, field, clim = clim, zorder=0, plotMax = True)
    plt.suptitle(tag + ' ', fontsize=8)    
    if title:
        plt.title(title)
    
#==============================================================================
def contour (cfg, grid, field, clim):
    #levels = np.arange(-10,10,1)
    csdllib.plot.map.addContour (grid, field, clim)

#==============================================================================
def save (figFile):
    plt.savefig(figFile)
    csdllib.oper.sys.msg ('i','Saving figure ' + figFile)    
    plt.close()
    
#==============================================================================
#def movie (cfg, grid, field, tag):
#    tmpDir = cfg['Analysis']['tmpdir']
