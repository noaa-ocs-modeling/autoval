
#==============================================================================
def waterlevel (field):

    description = ''
    if 'rmsd' in field:
        description = 'Root Mean Square Difference, meters.'
    elif 'bias' in field:
        description = 'Model Bias, meters.'
    elif 'peak' in field:
        description = 'Model Peak, meters.'
    elif 'plag' in field:
        description = 'Model Peak Lag, minutes.'
    elif 'rval' in field:
        description = 'R-Value, unitless.'
    elif 'skil' in field:
        description = 'Statistical Skill, unitless.'
    elif 'vexp' in field:
        description = 'Variance Explained, %.'
    elif 'npts' in field:
        description = 'Number of points in the analysis.'
    return description