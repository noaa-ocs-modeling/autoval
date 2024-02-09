#!/bin/bash

#Set mount point
mount="/gpfs/dell2/nos/noscrub/Georgios.Britzolakis/CMMB/test07_20_2020"

# Set path to python3 
pyPath="/usrx/local/prod/packages/python/3.6.3/bin/python"

# Set path to python executable
myCode="/gpfs/dell2/nos/noscrub/Georgios.Britzolakis/CMMB/test07_20_2020/autoval/autoval/validate/run.py"

# Set PYTHONPATH to csdllib
PYTHONPATH="/gpfs/dell2/nos/noscrub/Georgios.Britzolakis/CMMB/test07_20_2020/csdllib"

# Specify the INI file
iniFile="/gpfs/dell2/nos/noscrub/Georgios.Britzolakis/CMMB/test07_20_2020/autoval/autoval/tests/test.estofs-glo.v6.cwl.ini"

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
