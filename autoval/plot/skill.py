"""
@author: Sergey.Vinogradov@noaa.gov
"""
import os
import csdllib
import matplotlib
matplotlib.use('Agg',warn=False)
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

#==============================================================================
def subplot (ax, val, name, plotRange, goodRange):

    ax.set_xlim([-1, 2])
    ax.set_ylim(plotRange)
    ax.set_xticklabels([])
    #ax.set_yticklabels([])
    ax.tick_params(axis="y",direction="in", pad=-22, labelsize=6)
    ax.set_xlabel (name)
    ax.grid(True,axis='y')   
    p = patches.Rectangle((-1, goodRange[0]), 
        3, goodRange[1]-goodRange[0], color='lime',alpha=0.15)
    ax.add_patch(p)

    ax.plot ([-1,2], [0,0], c='r', lw=2)
    ax.plot ([0,0], [0,val], c='r', lw=4)
    ax.plot ( 0,val, 'o', markerfacecolor = 'r', markeredgecolor = 'r')

    ytxt = val+0.02*(plotRange[1]-plotRange[0])
    if val<0:
        ytxt = val-0.04*(plotRange[1]-plotRange[0])
    ax.text ( -0.65, ytxt, str( round(val,2)),
                color='r', fontsize=10, weight='bold' )

    return ax

#==============================================================================
def subplot_blank (ax):
    ax.set_xlim([-1, 1])
    ax.set_ylim([-1, 1])
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    ax.axis('off')
    return ax

#==============================================================================
def panel (cfg, metrics, refDates, nosid, info, tag):
    '''
    Plots a panel with vital metrics values, 
    along with typical and acceptable ranges.
    '''

    fig, axs = plt.subplots(1,10,figsize=(5.5, 4.5))
    plt.style.use('seaborn-white')
    plt.suptitle(tag + ' ' + nosid + ' ' + info['name'] + ', ' + info['state'], fontsize=8)

    #rmse
    pos = 0
    axs[pos] = subplot(axs[pos],metrics['rmsd'],'RMSD',[0,1.0], [0,0.2])
    axs[pos].set_ylabel ('meters')
    #bias
    pos = 1
    axs[pos] = subplot(axs[pos],metrics['bias'],'BIAS',[-1.0,1.0], [-0.2,0.2])
    #peak
    pos = 2
    axs[pos] = subplot(axs[pos],metrics['peak'],'PEAK',[-1.0,1.0], [-0.2,0.2])
    #blank
    pos = 3
    axs[pos] = subplot_blank(axs[pos])
    #plag
    pos = 4
    axs[pos] = subplot(axs[pos],metrics['plag'],'PLAG',[-180., 180], [-30,30])
    axs[pos].set_ylabel ('minutes')
    #blank
    pos = 5
    axs[pos] = subplot_blank(axs[pos])
    #skil
    pos = 6
    axs[pos] = subplot(axs[pos],metrics['skil'],'SKILL',[0, 1], [0.8,1])
    axs[pos].set_ylabel ('unitless')
    #rval
    pos = 7
    axs[pos] = subplot(axs[pos],metrics['rval'],'R-VAL',[0, 1], [0.8,1])
    #blank
    pos = 8
    axs[pos] = subplot_blank(axs[pos])
    #varexp
    pos = 9
    axs[pos] = subplot(axs[pos],metrics['vexp'],'VAREXP',[0, 100], [80,100])
    axs[pos].set_ylabel ('%')
    
    figFile = os.path.join( cfg['Analysis']['workdir'],     \
                            'skill.' + tag+ '.' + nosid + '.png')
    plt.savefig(figFile)
    plt.close()

#==============================================================================
def map (cfg, pointData, tag):
    '''
    Plots a map for a specified data
    '''
    # Download / read map plot data
    # Get coastline
    coastlineFile = os.path.join(
        cfg['Analysis']['localdatadir'], 'coastline.dat')    
    if not os.path.exists(coastlineFile):
        csdllib.oper.transfer.refresh (cfg['PlotData']['coastlinefile'], coastlineFile)
    coast = csdllib.plot.map.readCoastline  (coastlineFile)

    lonlim = [-98, -54]
    latlim = [  5,  47]

    # rmse
    fig = csdllib.plot.map.set(lonlim, latlim, coast)
    plt.suptitle(tag + ' ' + name, fontsize=8)
    figFile = os.path.join( cfg['Analysis']['workdir'], 'mapskill.rmse' + tag+ '.png')
    plt.savefig(figFile)
    plt.close()
