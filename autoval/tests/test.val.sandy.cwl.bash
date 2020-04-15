#!/bin/bash

#Set mount point
mount="/Users/svinogra"

# Set path to python3 
pyPath=${mount}"/anaconda3/bin/python"

# Set path to python executable
myCode=${mount}"/GitHub/autoval/autoval/validate/run.py"

# Set PYTHONPATH to csdllib
PYTHONPATH=${mount}"/GitHub/csdllib"

# Specify the INI file
iniFile=${mount}"/GitHub/autoval/autoval/tests/al182012.cwl.ini"

# Execute
if test -z $1 
then
    echo "Please specify a path to experiment folder"
    echo "Or a path to a file with folders paths for multirun analysis"
else
    PYTHONPATH=${PYTHONPATH} ${pyPath} -W ignore ${myCode} -i ${iniFile} -p $1
fi
