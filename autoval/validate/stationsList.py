import sys
import csdllib

#==============================================================================
if __name__ == "__main__":

    ncFile = sys.argv[1:]
    m = csdllib.models.adcirc.readTimeSeries (ncFile, ncVar = 'zeta', verbose=1)
    for n in range(len(m['lon'])):
        info = str(m['lon'][n]) + ' ' \
             + str(m['lat'][n]) + ' ' \
             + str(m['stations'][n])
        print ( info )
    

