#!/bin/bash

# Set path to python3 
pyPath=/usrx/local/dev/python/3.6.3/bin/python

# Set path to python executable
myCode="/gpfs/hps3/nos/noscrub/nwprod/autoval/autoval/validate/stationsList.py"

# Set PYTHONPATH to csdllib
PYTHONPATH="/gpfs/hps3/nos/noscrub/nwprod/csdllib"

PYTHONPATH=${PYTHONPATH} ${pyPath} -W ignore ${myCode} ${1}
