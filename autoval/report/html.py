"""
@author: Sergey.Vinogradov@noaa.gov
"""
import os
import csdllib
import re
import numpy as np
from .metricsDescription import waterlevel 

#==============================================================================
def tabLink (tabName, isDefault=False):
    string = '<button class=\"tablinks\" onclick=\"openMap(event, \'__skill__\')\">__skill__</button>'
    if isDefault:
        string = '<button class=\"tablinks\" onclick=\"openMap(event, \'__skill__\')\" id=\"defaultOpen\">__skill__</button>'
    string = re.sub('__skill__', tabName, string)
    return string

#==============================================================================
def tabContent(tabName, tabDescription, imgPath):
    lines = []
    line1 = '<div id=\"__skill__\" class=\"tabcontent\">'
    lines.append( re.sub('__skill__', tabName, line1) )
    line2 = '  <h3>__skill__</h3>'
    lines.append( re.sub('__skill__', tabName, line2) )
    line3 = '  <p>__skill__</p>'
    lines.append( re.sub('__skill__', tabDescription, line3) )
    line4 = '  <a href=\"_map.png_\"><img src=\"_map.png_\" alt=\"\" width=\"400\" border=\"0\"></a>'
    lines.append( re.sub('_map.png_',imgPath, line4) )
    lines.append( '</div>' )
    return lines

#==============================================================================
def mainMap (imgPath):
    lines = []
    line = '  <a href=\"_map.png_\"><img src=\"_map.png_\" alt=\"\" width=\"800\" border=\"0\"></a>'
    lines.append( re.sub('_map.png_',imgPath, line) )
    return lines

#==============================================================================
def auxMap (imgPath):
    lines = []
    line = '  <a href=\"_map.png_\"><img src=\"_map.png_\" alt=\"\" width=\"400\" border=\"0\"></a>'
    lines.append( re.sub('_map.png_',imgPath, line) )
    return lines

#==============================================================================
def csv2html (fod, avgStats):
    fod.write('<table width=\"800\" cellspacing=\"2\" cellpadding=\"2\" border=\"0\">\n')
    fod.write('<tr>\n')
    for key in avgStats:
        fod.write('<td bgcolor=\"#ccccff\">\n')
        fod.write(key+'\n')
        fod.write('</td>\n')
    fod.write('</tr>\n<tr>\n')
    for key in avgStats:
        fod.write('<td>\n')
        fod.write( str(np.round(avgStats[key],2)) + '\n')
        fod.write('</td>\n')
    fod.write('</tr>') 
    fod.write('</table>\n')

#==============================================================================
def timeSeriesPanel (fod, cfg, tag, nosid, name, state):

    tspng = os.path.join(   cfg['Analysis']['imgdir'],
                            tag + '.ts.' + str(nosid) + '.png')
    mxpng = os.path.join(   cfg['Analysis']['imgdir'],
                            tag + '.skill.' + str(nosid) + '.png')
    lcpng = os.path.join(   cfg['Analysis']['imgdir'],
                            tag + '.loc.' + str(nosid) + '.png')

    fod.write('<table width=\"700\" cellspacing=\"2\" cellpadding=\"2\" border=\"0\">\n')
    fod.write('<tr>\n')
    fod.write('<td colspan = \"3\">' + str(nosid)+': ' + name + ' ' + state +  '</td>\n')
    fod.write('</tr>\n')
    fod.write('<tr>\n')
    fod.write('<td>\n')
    fod.write('<a href=\"' + 
                tspng + '\"><img src=\"' + tspng + 
                '\" alt=\"\" height=\"250\" border=\"0\"></a>\n')
    fod.write('</td>\n')

    fod.write('<td>\n')
    fod.write('<a href=\"' + 
                lcpng + '\"><img src=\"' + lcpng + 
                '\" alt=\"\" height=\"250\" border=\"0\"></a>\n')
    fod.write('</td>\n')

    fod.write('<td>\n')
    fod.write('<a href=\"' + 
                mxpng + '\"><img src=\"' + mxpng + 
                '\" alt=\"\" height=\"250\" border=\"0\"></a>\n')
    fod.write('</td>\n')
    fod.write('</tr>') 
    fod.write('</table>\n')

#==============================================================================
def singleReport (cfg, tag, info, datespan, stats, avgStats):
    '''
    singleReport (cfg, tag, info, datespan, stats, avgStats)
    '''
    ids    = []
    names  = []
    states = []
    for i in info:
        ids.append(i['nosid'])
        names.append(i['name'])
        states.append(i['state'])

    reportDir = cfg['Analysis']['reportdir']
    diagVar   = cfg['Analysis']['name']
    expDescr  = cfg['Analysis']['experimentdescr']
    
    outFile   = os.path.join( reportDir, tag + '.htm')
    csdllib.oper.sys.msg('i','Creating report in ' + outFile)

    local = os.path.join(cfg['Analysis']['tmpdir'],'template.htm')
    csdllib.oper.transfer.download (cfg[diagVar]['pointtemplate'], local) 

    fod = open(outFile, 'w')
    with open(local,"r") as fid:
        for line in fid:
            if '<!--InsertDate-->' in line:
                fod.write(expDescr + '<br>\n')
                fod.write('Generated: ' +csdllib.oper.sys.timeStamp() + '<br>\n')

            elif '<!--InsertDateSpan-->' in line:
                fod.write('<br>Date span for analysis:<br>\n')
                fod.write('' + 
                    csdllib.oper.sys.timeToStamp (datespan[0]) + ' ... ' + 
                    csdllib.oper.sys.timeToStamp (datespan[-1]) + '<br>\n')

            elif '<!--InsertBBox-->' in line:
                fod.write('<br>BBox:<br>\n')
                fod.write('Longitudes: [' + str(cfg['Analysis']['lonmin']) + ' ... ' + 
                                str(cfg['Analysis']['lonmax']) + ']<br>\n')
                fod.write('Latitudes : [' + str(cfg['Analysis']['latmin']) + ' ... ' + 
                                str(cfg['Analysis']['latmax']) + ']<br>\n')

            
            elif '<!--InsertMainFieldMap-->' in line:
                imgPath = os.path.join(cfg['Analysis']['imgdir'],
                    tag + '.map.max.png')
                lines = mainMap(imgPath)
                for l in lines:
                    fod.write(l)

            elif '<!--InsertZoomMaps-->' in line:
                
                c = 0
                for zoom in range(1,5):
                    imgPath = os.path.join(cfg['Analysis']['imgdir'],
                        tag + '.map.max.' + str(zoom) +'.png')
                    c += 1
                    fod.write('<td>\n')
                    fod.write( '<a href=\"' + imgPath + '\"><img src=\"' + imgPath + '\" alt=\"\" width=\"400\" border=\"0\"></a>'+'\n')
                    fod.write('</td>\n')
                    if np.mod(c,2) == 0:
                        fod.write('</tr>\n<tr>\n')
                fod.write('</tr>') 
                fod.write('</table>\n')

            elif '<!--InsertSkillMaps-->' in line:
                fod.write('<table style=\"width:800\">\n')
                fod.write('<tr>\n')
                c = 0
                for key in avgStats:
                    c += 1
                    fod.write('<td>\n')
                    fod.write(key+'<br>\n')
                    imgPath = os.path.join(
                                cfg['Analysis']['imgdir'],
                                tag + '.mapskill.' + key + '.png')
                    fod.write( '<a href=\"' + imgPath + '\"><img src=\"' + imgPath + '\" alt=\"\" width=\"400\" border=\"0\"></a>'+'\n')
                    fod.write('</td>\n')
                    if np.mod(c,2) == 0:
                        fod.write('</tr>\n<tr>\n')
                fod.write('</tr>\n<hr>\n')

            elif '<!--InsertAvgStatsTable-->' in line:
                fod.write('Average time-series statistics:\n')
                csv2html (fod, avgStats)

            elif '<!--InsertTimeSeries-->' in line:
                fod.write('Individual time-series statistics:\n')
                fod.write('<hr>\n')
                for n in range(len(ids)):
                    if not np.isnan( stats[n]['rmsd']):
                        fod.write('<br>\n')
                        nosid = ids[n]
                        name  = names[n]
                        state = states[n]
                        timeSeriesPanel (fod, cfg, tag, nosid, name, state)
                        csv2html (fod, stats[n])
                        fod.write('<hr>\n')
            else:
                line = re.sub('__expname__', tag, line)
                line = re.sub('__expdesc__', cfg['Analysis']['experimentdescr'], line)
                fod.write(line)
    fod.close()

    # read time series, create state anchors, generate rows = ts + panel

