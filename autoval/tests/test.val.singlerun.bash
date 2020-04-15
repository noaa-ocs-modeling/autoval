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
iniFile=${mount}"/GitHub/autoval/autoval/tests/singlerun.al182012.hsofs.ini"

# Execute
PYTHONPATH=${PYTHONPATH} ${pyPath} -W ignore ${myCode} -i ${iniFile} -p $1

