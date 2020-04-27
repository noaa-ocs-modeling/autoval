"""
@author: Sergey.Vinogradov@noaa.gov
"""
import os
import csdllib
import re

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
def singleReport (cfg, tag, stats, ids, avgStats):

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
            if '<!--InsertTabLink-->' in line:
                for key in avgStats:
                    print (key)
                    isDefault = False
                    n = 0
                    if n==0:
                        isDefault = True
                        n =+ 1
                    lines = tabLink(key, isDefault)
                    fod.write(lines+'\n')
            elif '<!--InsertTabContent-->' in line:
                for key in avgStats:
                    imgPath = os.path.join(
                                cfg['Analysis']['workdir'],
                                tag + '.mapskill.' + key + '.png')
                    lines = tabContent(key, str(key), imgPath)
                    for l in lines:
                        fod.write(l)
            else:
                line = re.sub('__expname__', tag, line)
                line = re.sub('__expdesc__', cfg['Analysis']['experimentdescr'], line)
                fod.write(line)
    fod.close()

    # read time series, create state anchors, generate rows = ts + panel

