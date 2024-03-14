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
                            'ts.' + str(nosid) + '.png')
#                            tag + '.ts.' + str(nosid) + '.png')
    mxpng = os.path.join(   cfg['Analysis']['imgdir'],
                            'skill.' + str(nosid) + '.png')
#                            tag + '.skill.' + str(nosid) + '.png')
    lcpng = os.path.join(   cfg['Analysis']['imgdir'],
                            'loc.' + str(nosid) + '.png')
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
    countries = []

   
    for i in info:
     
        ids.append(i['nosid'])
        names.append(i['name'])
        states.append(i['state'])
        countries.append(i['country'])
        
    # Filtering those states and countries that has observation

    states_with_Obs = []
    countries_with_Obs = []

    m=0
    for i in info:
        if not np.isnan( stats[m]['rmsd']):     
           states_with_Obs.append(i['state'])
           countries_with_Obs.append(i['country'])
        m=m+1

    states_list = set(filter(lambda state: state and state != "UN", states_with_Obs))
    countries_list = set(filter(lambda country: country, countries_with_Obs))


    # Filtering those states and countries that has no observation

    states_with_noObs = []
    countries_with_noObs = []

    m=0
    for i in info:
        if np.isnan( stats[m]['rmsd']):     
           states_with_noObs.append(i['state'])
           countries_with_noObs.append(i['country'])
        m=m+1

    states_list_noObs = set(filter(lambda state: state and state != "UN", states_with_noObs))
    countries_list_noObs = set(filter(lambda country: country, countries_with_noObs))

    
    

    reportDir = cfg['Analysis']['reportdir']
    diagVar   = cfg['Analysis']['name']
    expDescr  = cfg['Analysis']['experimentdescr']
    
# Try to upload
    try:
        host   = cfg['Upload']['host']
                       
        user   = cfg['Upload']['user']
                       
        remote_htm = cfg['Upload']['remote_htm']
                        
        remote_img = cfg['Upload']['remote_img']
                        
        remote_csv = cfg['Upload']['remote_csv']
                       
        # Upload pertinent tagged graphics
        imgPaths = os.path.join(reportDir + cfg['Analysis']['imgdir'], '*.png')
                        
        #imgPaths = os.path.join(reportDir + cfg['Analysis']['imgdir'], tag + '*.png')
        #csdllib.oper.transfer.upload(imgPaths, user+'@'+host, remote_img)
                        
        # Upload pertinent untagged graphics
        #imgPaths = os.path.join(reportDir + cfg['Analysis']['imgdir'], 'loc*.png')
                       
        #csdllib.oper.transfer.upload(imgPaths, user+'@'+host, remote_img)
                        
    except:
        csdllib.oper.sys.msg('w','Report has not been uploaded')
                        
    outFile   = os.path.join( reportDir, 'index.htm')
    #outFile   = os.path.join( reportDir, tag + '.htm')
                    
    csdllib.oper.sys.msg('i','Creating report in ' + outFile)
    print("this is report")
    print(reportDir)

    local = os.path.join(cfg['Analysis']['tmpdir'],'template.htm')
    csdllib.oper.transfer.download (cfg[diagVar]['pointtemplate'], local) 

    fod = open(outFile, 'w')
    print("this is created report")

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
                    'map.max.png')
                #    tag + '.map.max.png')
                lines = mainMap(imgPath)
                for l in lines:
                    fod.write(l)

            elif '<!--InsertZoomMaps-->' in line:
                
                c = 0
                for zoom in range(1,5):
                    imgPath = os.path.join(cfg['Analysis']['imgdir'],
                        'map.max.' + str(zoom) +'.png')
                    #    tag + '.map.max.' + str(zoom) +'.png')
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
                                'mapskill.' + key + '.png')
                    #            tag + '.mapskill.' + key + '.png')
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
                
                # State initials to full name mapping
                state_initials_to_full = {
                'AL': 'Alabama',
                'AK': 'Alaska',
                'AZ': 'Arizona',
                'AR': 'Arkansas',
                'CA': 'California',
                'CO': 'Colorado',
                'CT': 'Connecticut',
                'DE': 'Delaware',
                'FL': 'Florida',
                'GA': 'Georgia',
                'HI': 'Hawaii',
                'ID': 'Idaho',
                'IL': 'Illinois',
                'IN': 'Indiana',
                'IA': 'Iowa',
                'KS': 'Kansas',
                'KY': 'Kentucky',
                'LA': 'Louisiana',
                'ME': 'Maine',
                'MD': 'Maryland',
                'MA': 'Massachusetts',
                'MI': 'Michigan',
                'MN': 'Minnesota',
                'MS': 'Mississippi',
                'MO': 'Missouri',
                'MT': 'Montana',
                'NE': 'Nebraska',
                'NV': 'Nevada',
                'NH': 'New Hampshire',
                'NJ': 'New Jersey',
                'NM': 'New Mexico',
                'NY': 'New York',
                'NC': 'North Carolina',
                'ND': 'North Dakota',
                'OH': 'Ohio',
                'OK': 'Oklahoma',
                'OR': 'Oregon',
                'PA': 'Pennsylvania',
                'RI': 'Rhode Island',
                'SC': 'South Carolina',
                'SD': 'South Dakota',
                'TN': 'Tennessee',
                'TX': 'Texas',
                'UT': 'Utah',
                'VT': 'Vermont',
                'VA': 'Virginia',
                'WA': 'Washington',
                'WV': 'West Virginia',
                'WI': 'Wisconsin',
                'WY': 'Wyoming'}


                fod.write("<div id='list'><h2 style='font-size: 16px;'>Jump to</h2></div>")
                
                # Check if states_list is not empty
                if states_list:
                   fod.write("<h3 style='font-size: 15px;'>NOS Stations:</h3>")
                   state_links = []
                   island_links = []
    
                   for state_initial in states_list:
                       if state_initial in state_initials_to_full:
                          full_state_name = state_initials_to_full[state_initial]
                          state_links.append(f"<a href='#{full_state_name}'>{state_initial}</a>")
                       else:
                          island_links.append(state_initial)
    
                   # Add Islands category if there are islands
                   if island_links:
                       state_links.append("<a href='#Islands'>Islands</a>")
    
                   fod.write(', '.join(state_links))
                   fod.write('<br>')

                   # Write Islands section
                   #if island_links:
                       #fod.write(', '.join(island_links))
                       #fod.write('<br>') 


                # Check if country_list is not empty
                if countries_list:
                   fod.write("<h3 style='font-size: 15px;'>IOC Stations:</h3>")
                   country_links = []
                   for country in countries_list:
                       country_links.append(f"<a href='#{country}'>{country}</a>")
                   fod.write(', '.join(country_links))
                   fod.write('<br>')

                # Check if states_list_noObs is not empty
                if states_list_noObs:
                   fod.write("<h3 style='font-size: 15px;'>NOS Stations (without Observation):</h3>")
                   state_links_noObs = []
                   island_links_noObs = []
    
                   for state_initial in states_list_noObs:
                       if state_initial in state_initials_to_full:
                          full_state_name = state_initials_to_full[state_initial]
                          state_links_noObs.append(f"<a href='#{full_state_name}_noObs'>{state_initial}</a>")
                       else:
                          island_links_noObs.append(state_initial)
    
                   # Add Islands category if there are islands
                   if island_links_noObs:
                       state_links_noObs.append("<a href='#Islands_noObs'>Islands</a>")
    
                   fod.write(', '.join(state_links_noObs))
                   fod.write('<br>')

                   # Write Islands section
                   #if island_links_noObs:
                       #fod.write(', '.join(island_links_noObs))
                       #fod.write('<br>') 

                # Check if country_list_noObs is not empty
                if countries_list_noObs:
                   fod.write("<h3 style='font-size: 15px;'>IOC Stations:</h3>")
                   country_links_noObs = []
                   for country in countries_list_noObs:
                       country_links_noObs.append(f"<a href='#{country}_noObs'>{country}</a>")
                   fod.write(', '.join(country_links_noObs))
                   fod.write('<br>')
              
                # Check if there exists a station meeting the conditions
                station_exists = any(np.isnan(stats[n]['rmsd']) and states[n] == 'UN' and countries[n] is None for n in range(len(ids)))

                # Use the 'station_exists' variable as needed
                if station_exists:
                   fod.write("<h3 style='font-size: 15px;'><a href='#Others'>Other Stations without Observation</a></h3>")
                fod.write('<hr>\n')
                   

                ###########Add the tables and timeseries
                

                for states_name in states_list:  
                    if states_name in state_initials_to_full:               

                       # Get indices of entries with the current state
                       indices = [index for index, value in enumerate(states) if value == states_name]
                    
                       # Get the full state name from the mapping
                       full_state_name = state_initials_to_full.get(states_name,states_name)
                  

                       # Write heading for the state

                       heading = f"<h2 id='{full_state_name}' style='background-color: #e0e0e0; padding: 5px; font-size: 14px;'>{full_state_name} <a href='#list' style='float: right;'>top</a></h2>"
                       fod.write(heading)

                       for n in range(len(indices)):
                           if not np.isnan( stats[indices[n]]['rmsd']): #True: 
                               #fod.write('<br>\n')
                               nosid = ids[indices[n]]
                               name  = names[indices[n]]
                               state = states[indices[n]]
                               timeSeriesPanel (fod, cfg, tag, nosid, name, state)

                               csv2html (fod, stats[indices[n]])
                               fod.write('<hr>\n')
                
                # Process 'Islands' category
                if states_list: 
                   if island_links:
                      fod.write("<h2 id='Islands' style='background-color: #e0e0e0; padding: 5px; font-size: 14px;'>Islands <a href='#list' style='float: right;'>top</a></h2>")
  
                for states_name in states_list:  
                    if states_name not in state_initials_to_full:               

                       # Get indices of entries with the current state
                       indices = [index for index, value in enumerate(states) if value == states_name]

                       for n in range(len(indices)):
                           if not np.isnan( stats[indices[n]]['rmsd']): #True: 
                               #fod.write('<br>\n')
                               nosid = ids[indices[n]]
                               name  = names[indices[n]]
                               state = states[indices[n]]
                               timeSeriesPanel (fod, cfg, tag, nosid, name, state)

                               csv2html (fod, stats[indices[n]])
                               fod.write('<hr>\n')
  
              
                for country_name in countries_list:
                    #if True: #not np.isnan( stats[n]['rmsd']):
                    #if not np.isnan( stats[n]['rmsd']):
                      # Get indices of entries with the current state
                      indices = [index for index, value in enumerate(countries) if value == country_name]

                      # Write heading for the state
                      #heading = f"<h2 style='background-color: #e0e0e0; padding: 5px; font-size: 14px;'>{full_state_name}</h2>"
                      heading = f"<h2 id='{country_name}' style='background-color: #e0e0e0; padding: 5px; font-size: 14px;'>{country_name} <a href='#list' style='float: right;'>top</a></h2>"

                      fod.write(heading)

                      for n in range(len(indices)):
                          if not np.isnan( stats[indices[n]]['rmsd']): #True:
                              #fod.write('<br>\n')
                              nosid = ids[indices[n]]
                              name  = names[indices[n]]
                              state = states[indices[n]]
                              timeSeriesPanel (fod, cfg, tag, nosid, name, state)

                              csv2html (fod, stats[indices[n]])
                              fod.write('<hr>\n')
                
                #add sations witout observation
                
                for states_name in states_list_noObs:
                    
                    if states_name in state_initials_to_full:  

                       # Get indices of entries with the current state
                       indices = [index for index, value in enumerate(states) if value == states_name]
                     
                       # Get the full state name from the mapping
                       full_state_name = state_initials_to_full.get(states_name,states_name)
                  
                       # Write heading for the state

                       heading = f"<h2 id='{full_state_name}_noObs' style='background-color: #e0e0e0; padding: 5px; font-size: 14px;'>{full_state_name} <a href='#list' style='float: right;'>top</a></h2>"
                       fod.write(heading)

                       for n in range(len(indices)):
                           if np.isnan( stats[indices[n]]['rmsd']): #True: 
                               #fod.write('<br>\n')
                               nosid = ids[indices[n]]
                               name  = names[indices[n]]
                               state = states[indices[n]]
                               timeSeriesPanel (fod, cfg, tag, nosid, name, state)

                               csv2html (fod, stats[indices[n]])
                               fod.write('<hr>\n')
                
                # Process 'Islands' category
                if states_list_noObs:
                   if island_links_noObs:
                      fod.write("<h2 id='Islands_noObs' style='background-color: #e0e0e0; padding: 5px; font-size: 14px;'>Islands <a href='#list' style='float: right;'>top</a></h2>")

                for states_name in states_list_noObs:  
                    if states_name not in state_initials_to_full:               

                       # Get indices of entries with the current state
                       indices = [index for index, value in enumerate(states) if value == states_name]

                       for n in range(len(indices)):
                           if np.isnan( stats[indices[n]]['rmsd']): #True: 
                               #fod.write('<br>\n')
                               nosid = ids[indices[n]]
                               name  = names[indices[n]]
                               state = states[indices[n]]
                               timeSeriesPanel (fod, cfg, tag, nosid, name, state)

                               csv2html (fod, stats[indices[n]])
                               fod.write('<hr>\n')

                for country_name in countries_list_noObs:
                    #if True: #not np.isnan( stats[n]['rmsd']):
                    #if not np.isnan( stats[n]['rmsd']):
                      # Get indices of entries with the current state
                      indices = [index for index, value in enumerate(countries) if value == country_name]

                      # Write heading for the state
                      #heading = f"<h2 style='background-color: #e0e0e0; padding: 5px; font-size: 14px;'>{full_state_name}</h2>"
                      heading = f"<h2 id='{country_name}_noObs' style='background-color: #e0e0e0; padding: 5px; font-size: 14px;'>{country_name} <a href='#list' style='float: right;'>top</a></h2>"

                      fod.write(heading)

                      for n in range(len(indices)):
                          if np.isnan( stats[indices[n]]['rmsd']): #True:
                              #fod.write('<br>\n')
                              nosid = ids[indices[n]]
                              name  = names[indices[n]]
                              state = states[indices[n]]
                              timeSeriesPanel (fod, cfg, tag, nosid, name, state)

                              csv2html (fod, stats[indices[n]])
                              fod.write('<hr>\n')
                
                #add other stations
                if station_exists:
                   heading = f"<h2 id='Others' style='background-color: #e0e0e0; padding: 5px; font-size: 14px;'>Other Stations without Observation <a href='#list' style='float: right;'>top</a></h2>"
                   fod.write(heading)
                for n in range(len(ids)):
                    if (np.isnan(stats[n]['rmsd']) and states[n] == 'UN' and countries[n] == None): #True: 
                          #fod.write('<br>\n')
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
        fid.close()
    fod.close()

    # Upload htm file
    try:
        remotefile = cfg['Upload']['remotefile']
        csdllib.oper.transfer.upload(outFile, user+'@'+host, remotefile)
    except:
        csdllib.oper.transfer.upload(outFile, user+'@'+host, remote_htm)

    try:
        # Upload pertinent csv file
        csvPaths = os.path.join(cfg['Analysis']['workdir'], cfg[diagVar]['globalstatfile'])
        csdllib.oper.transfer.upload(csvPaths, user+'@'+host, remote_csv )
    except:
        pass
