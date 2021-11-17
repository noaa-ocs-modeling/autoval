"""
@author: Sergey.Vinogradov@noaa.gov
"""
import csdllib
import os
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
import matplotlib.dates as mdates
import numpy as np
#import bokeh
from bokeh.plotting import ColumnDataSource, figure
from bokeh.models import HoverTool
from bokeh.embed import components
from bokeh.models.annotations import Label
from bokeh.models import LinearAxis, Range1d
from bokeh.models import DatetimeTickFormatter
from csdllib.oper.sys import stampToTime, timeToStamp, msg

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
    coast = csdllib.plot.map.readCoastline  (coastlineFile)

    fig = csdllib.plot.map.set([xo-dx, xo+dx], [yo-dy, yo+dy], fig_w=3.0, coast=coast)
    plt.suptitle(info['name'] + ' ' + info['state'], fontsize=8)

    plt.scatter(xo, yo, c='r', marker = 'o', edgecolors='k', s=30,zorder=2)
    plt.text(xo+0.01*dx, yo+0.01*dy, str(info['nosid']), color='darkblue', fontsize=7, weight='bold',zorder=2)

    plt.savefig(figFile)
    plt.close(fig)
    plt.close()

#==============================================================================
def pointSeriesInteractive(cfg, obsVals, modVals, refDates, nosid, info, tag, 
                forecastDates = None, forecast = None):
    '''
    Plots one station.
    '''
    imgDir  = os.path.join( cfg['Analysis']['reportdir'], 
                            cfg['Analysis']['imgdir'])

    xlim = [min(refDates), max(refDates)]
    ylim = [cfg['WaterLevel']['pointymin'],cfg['WaterLevel']['pointymax']]
    datums      = 0
    floodlevels = 0
    if forecastDates is not None:
        xlim[1] = forecastDates[-1]
    
    plotTitle = tag + ' ' + nosid + ' ' + info['name'] + ', ' + info['state']
    plot = figure(width=778, height=250, #, tools=[hover, 'wheel_zoom','save'], #tooltips=TOOLTIPS,
                  title=plotTitle)
    plot.xaxis.formatter = DatetimeTickFormatter(hours=["%m/%d\n%H:%M"],
                                                 days=["%m/%d\n%H:%M"],
                                                 months=["%m/%d\n%H:%M"],
                                                 years=["%m/%d\n%H:%M"]
                                                 )
    plot.title.text_font_size = "8px"
    plot.title.align = 'center'
    plot.yaxis.axis_label='WATER LEVELS, meters MSL'
    plot.xaxis.axis_label='DATE/TIME UTC'
    plot.x_range=Range1d(xlim[0], xlim[1])
    plot.y_range=Range1d(ylim[0], ylim[1])

    #For the axis in feet
    plot.extra_y_ranges={ "y_column2_range": Range1d(start=ylim[0]*3.28084, end=ylim[1]*3.28084)}
    plot.add_layout(LinearAxis(y_range_name="y_column2_range", axis_label="WATER LEVELS, feet MSL"), "right")
    
    if obsVals is not None:
        dataSource = ColumnDataSource(data={
            'x':refDates,
            'modVals':modVals,
            'obsVals':obsVals,
        })
        plot.line(name="obsLine", x='x', y='obsVals', color="lime", source=dataSource, legend_label="OBS", line_width=2)
        obsToolTips = [
            ("Date","@x{%m/%d %H:%M}"),
            ("Observation", "@obsVals{1.2f}m")
        ]

        obsHover = HoverTool(names=["obsLine"], tooltips=obsToolTips,
                             formatters={"@x":"datetime", "obsVals":"printf"}
        )
        plot.add_tools(obsHover)
    else:
        dataSource = ColumnDataSource(data={
            'x':refDates,
            'modVals':modVals
        })
    lenModVals = len(modVals)
    
    plot.line(name="modLine", x='x', y='modVals', color="blue",  source=dataSource, legend_label="MOD", line_width=2)
    modToolTips = [
        ("Date","@x{%m/%d %H:%M}"),
        ("Model", "@modVals{1.2f}m")
    ]

    modHover = HoverTool(names=["modLine"], tooltips=modToolTips,
                         formatters={"@x":"datetime", "modVals":"printf"}
    )
    plot.add_tools(modHover)

    if forecast is not None:
        dataSourceForecast = ColumnDataSource(data={
            'xf':forecastDates[lenModVals:],
            'forVals':forecast[lenModVals:],
        })
        
        forLine = plot.line(name="forLine",x='xf', y='forVals', color="blue",  source=dataSourceForecast, line_width=1)
        forToolTips = [
            ("Date","@xf{%m/%d %H:%M}"),
            ("Forecast", "@forVals{1.2f}m")
        ]
        
        forHover = HoverTool(names=["forLine"], tooltips=forToolTips,
                             formatters={"@xf":"datetime", "forVals":"printf"}
        )
        plot.add_tools(forHover)
        
    label = Label(x=xlim[0], y=ylim[1], x_offset=0, y_offset=0.05, text="NOAA / OCEAN SERVICE", text_font_size="8pt")

    plot.legend.label_text_font_size = '8px'
    plot.legend.glyph_height = 4
    
    plot.legend.label_height = 4
    plot.legend.location = "bottom_right"
    plot.legend.orientation = "horizontal" 

    # Implementing label in our plot
    plot.add_layout(label, 'above')

    return plot
    
#==============================================================================
def pointSeries(cfg, obsVals, modVals, refDates, nosid, info, tag, 
                forecastDates = None, forecast = None):
    '''
    Plots one station.
    '''
    imgDir  = os.path.join( cfg['Analysis']['reportdir'], 
                            cfg['Analysis']['imgdir'])

    xlim = [min(refDates), max(refDates)]
    ylim = [cfg['WaterLevel']['pointymin'],cfg['WaterLevel']['pointymax']]
    datums      = 0
    floodlevels = 0
    if forecastDates is not None:
            xlim[1] = forecastDates[-1]

    fig, ax, ax2 = csdllib.plot.series.set(xlim, ylim, datums, floodlevels)
    if obsVals is not None:
        ax = csdllib.plot.series.add(ax, refDates, obsVals, color='lime',label='OBS',lw=2)
    ax = csdllib.plot.series.add(ax, refDates, modVals, color='b',label='MOD',lw=2)
    ax.legend(bbox_to_anchor=(0.8, 0.82), loc='center left',prop={'size':6})
    if forecast is not None:
        ax = csdllib.plot.series.add(ax, forecastDates, forecast, 
             color='b',label='FCST',lw=1)
        
    ax.text(xlim[0],ylim[1]+0.05,'NOAA / OCEAN SERVICE')
    ax.set_ylabel ('WATER LEVELS, meters MSL')
    ax2.set_ylabel('WATER LEVELS, feet MSL')
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
