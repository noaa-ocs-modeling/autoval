#!/bin/bash

# Set path to python3 
pyPath=/usrx/local/dev/python/3.6.3/bin/python

# Set path to python executable
myCode="/gpfs/hps3/nos/noscrub/nwprod/autoval/autoval/validate/run.py"

# Set PYTHONPATH to csdllib
PYTHONPATH="/gpfs/hps3/nos/noscrub/nwprod/csdllib"

# Specify the INI file
iniFile="/gpfs/hps3/nos/noscrub/nwprod/autoval/autoval/tests/oper.estofs-glo.v4.cwl.ini"

# Execute
if test -z $1 
then
    echo "Please specify a path to experiment folder"
    echo "Or a path to a file with folders paths for multirun analysis"
elif test -z $2
then
    PYTHONPATH=${PYTHONPATH} ${pyPath} -W ignore ${myCode} -p $1 -i ${iniFile}
else    
    PYTHONPATH=${PYTHONPATH} ${pyPath} -W ignore ${myCode} -p $1 -i $2
fi
