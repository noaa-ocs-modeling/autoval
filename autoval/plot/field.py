"""
@author: Sergey.Vinogradov@noaa.gov
"""
import os
import csdllib
import matplotlib
matplotlib.use('Agg',warn=False)
import matplotlib.pyplot as plt
import matplotlib.tri    as tri
import numpy as np 
from   matplotlib.colors import LinearSegmentedColormap

# The first couple of functions are borrowed and modified from csdllib
#==============================================================================
cdict = {'red': ((0.  , 1  , 1),
                 (0.05, 1  , 1),
                 (0.11, 0  , 0),
                 (0.66, 1, 1),
                 (0.89, 1, 1),
                 (1   , 0.5, 0.5)),
         'green': ((0., 1, 1),
                   (0.05, 1, 1),
                   (0.11, 0, 0),
                   (0.375, 1, 1),
                   (0.64, 1, 1),
                   (0.91, 0, 0),
                   (1, 0, 0)),
         'blue': ((0., 1, 1),
                  (0.05, 1, 1),
                  (0.11, 1, 1),
                  (0.34, 1, 1),
                  (0.65, 0, 0),
                  (1, 0, 0))}

jetMinWi = LinearSegmentedColormap('my_colormap',cdict,256)


#==============================================================================

def addField (grid, field, clim = [0,3], zorder=0, plotMax = False, lonlim=None, latlim=None):
    """
    Adds (unstructured) gridded field to the map
    """
    csdllib.oper.sys.msg('i','Plotting the surface.')
    
    lon       = grid['lon']
    lat       = grid['lat']
    triangles = grid['Elements']
    z         = field
    if len(z) != len(lon):
        csdllib.oper.sys.msg('e','Mesh and field sizes are not the same')
        csdllib.oper.sys.msg('e','   Field length is ' + str(len(z)))
        csdllib.oper.sys.msg('e','   Mesh  length is ' + str(len(lon)))
        return
    
    newTriangles = []
    nboundaryTriangles = 0
    for t in triangles-1:
        lons = []
        for n in range(len(t)):
            lons.append( lon[t[n]] )
        if np.ptp( np.asarray(lons) ) < 180.0:
            newTriangles.append (t)
            nboundaryTriangles += 1
    csdllib.oper.sys.msg('i','Number of found boundary elements: ' + 
        str(len(triangles)-nboundaryTriangles))
    
    #Tri  = tri.Triangulation(lon, lat, triangles=triangles-1)
    Tri  = tri.Triangulation(lon, lat, triangles=newTriangles) #-1)
   
    if hasattr(z,'mask'): 
        zmask = z.mask
    else:
        zmask = np.ones(len(z), dtype=bool)        
    # Set mask 
    # TODO : Optimize this following loop
    #
    
    mask = np.ones(len(Tri.triangles), dtype=bool)
    count = 0
    for t in Tri.triangles:
        count+=1
        ind = t
        if np.any(zmask[ind-1]):
            mask[count-1] = False    
    Tri.set_mask = mask
 
    myCmap = plt.cm.jet
    #print ('zmin/max = ' + str(np.nanmin(z)) + ' ' + str(np.nanmax(z)))
    #print ('clim = ' + str(clim[0]) + ' ' + str(clim[1]))
    #print('len(z)  =' + str(len(z)))

    
    
    plt.tripcolor(Tri, z, shading='gouraud',\
                          edgecolors='none', \
                          cmap=jetMinWi, \
                          vmin=clim[0], \
                          vmax=clim[1], zorder=zorder)
    #current_cmap = matplotlib.cm.get_cmap()
    #current_cmap.set_bad(color='gray')
    
    if plotMax:
        zmax = np.nanmax(z)
        imax = np.where (z == zmax)[0][0]
        
        
        if lonlim is not None and latlim is not None:
          
            zmax = np.nanmax(z[ (lonlim[0]  <= grid['lon']) & 
                            (grid['lon']<= lonlim[1])   &
                            (latlim[0]  <= grid['lat']) & 
                            (grid['lat']<= latlim[1] ) ])
            
            imax = np.where(z == zmax)[0][0]
            
        strzmax = str(np.round(zmax,1))
        
        plt.plot( lon[imax], lat[imax], 'ok', markerfacecolor='r',zorder=zorder+1)
        
        plt.text( lon[imax], lat[imax], strzmax,fontsize=6,zorder=zorder+2)  
    
    cbar = plt.colorbar()
    cbar.ax.tick_params(labelsize=8)     

#==============================================================================
def readCoastline (coastlineFile): 

    f = open(coastlineFile,'rb')
    xc = []
    yc = []
    for line in f:
        xc.append(float(line.split()[0]))
        yc.append(float(line.split()[1]))
    f.close()        

    return {'lon' : xc, 
            'lat' : yc}

#==============================================================================
def addCoastline (coast, col = 'gray', reverse_lon=False):
    """
    Adds coastline to the map
    """ 
       
    plt.plot(coast['lon'], coast['lat'],',',color=col,zorder=2)
    lon_values = coast['lon']

    if reverse_lon:  # if pacific domain
       lon_values = [-x for x in lon_values] 
    plt.plot( [360.-x for x in lon_values], coast['lat'],',',color=col,zorder=1)

#==============================================================================
def set(cfg, lonlim, latlim, coast=None, fig_w=8.0):
    """
    Sets the map according to configuration
    """
    minx, maxx = lonlim
    miny, maxy = latlim
    dx = float(maxx - minx)
    dy = float(maxy - miny)
    fig_h = np.round(fig_w*dy/dx, 2)
    csdllib.oper.sys.msg('i','Creating a figure with sizes :' \
                    + str(fig_w) + 'x' + str(fig_w))
    fig = plt.figure(figsize=[fig_w, fig_h])
    if coast is not None:
        if cfg['Analysis']['pacific'] == 1:
           addCoastline(coast, reverse_lon=True)
        else:
           addCoastline(coast)
    plt.xlim([minx, maxx])
    plt.ylim([miny, maxy])
    fig.tight_layout()

# Draw parallels
    if dx <= 10.:
        dx = 1.
    elif dx <= 20.:
        dx = 2.
    elif dx <= 50.:
        dx = 5.
    elif dx <= 100.:
        dx = 10.
    else:
        dx = 20.

    if dy <= 10.:
        dy = 1.
    elif dy <= 20.:
        dy = 2.
    elif dy <= 50.:
        dy = 5.
    elif dy <= 100.:
        dy = 10.
    else:
        dy = 20.

    meridians = np.arange(np.floor(minx/10.)*10.,np.ceil(maxx/10.)*10.,dx)
    parallels = np.arange(np.floor(miny/10.)*10.,np.ceil(maxy/10.)*10.,dy)
    
    for m in meridians:
        plt.plot([m,m],[miny,maxy],':',color='gray',linewidth=1,zorder=0)
    for p in parallels:
        plt.plot([minx,maxx],[p,p],':',color='gray',linewidth=1,zorder=0)
    plt.tick_params(labelsize=7)    
    plt.xlabel('LONGITUDE, deg E')
    plt.ylabel('LATITUDE, deg N')
    
    return fig

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
    #coast = csdllib.plot.map.readCoastline  (coastlineFile)
    coast = readCoastline  (coastlineFile)
    # Check limits of the grid?
    lonlim = [ float(cfg['Analysis']['lonmin']), float(cfg['Analysis']['lonmax']) ]
    latlim = [ float(cfg['Analysis']['latmin']), float(cfg['Analysis']['latmax']) ]
    print('Grid lon lim' + str(lonlim[0]) + ' ' + str(lonlim[1]) )
    print('Grid lat lim' + str(latlim[0]) + ' ' + str(latlim[1]) )

    # Get clim
    try:
        fmin = np.nanmin(field[ (lonlim[0]  <= grid['lon']) & 
                            (grid['lon']<= lonlim[1])   &
                            (latlim[0]  <= grid['lat']) & 
                            (grid['lat']<= latlim[1] ) ])

        fmax = np.nanmax(field[ (lonlim[0]  <= grid['lon']) & 
                            (grid['lon']<= lonlim[1])   &
                            (latlim[0]  <= grid['lat']) & 
                            (grid['lat']<= latlim[1] ) ])
    except:
        fmin = np.nanmin(field)
        fmax = np.nanmax(field)
    
    #field[np.where(field<clim[0])] = clim[0] #np.nan
    #field[np.where(field>clim[1])] = clim[1] #np.nan

    csdllib.oper.sys.msg('i','Field min/max=' + str(fmin) + '/' + str(fmax))
    
    fig = set(cfg, lonlim, latlim, coast=coast, fig_w=fig_w)
    
    addField (grid, field, clim = clim, zorder=0, plotMax = True, lonlim = lonlim, latlim = latlim)
    
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
    plt.close("all")
    
#==============================================================================
#def movie (cfg, grid, field, tag):
#    tmpDir = cfg['Analysis']['tmpdir']
