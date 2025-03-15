#!/bin/bash

# Script execution instructions

# Get the path to python3 from the active conda environment
pyPath=$(which python)

# Check if python3 is found
if [[ -z "$pyPath" ]]; then
  echo "Error: python not found in the active conda environment."
  exit 1
fi

# Install nco via conda if it is not found.
if ! command -v ncks &> /dev/null
then
    echo "ncks not found. Installing via conda..."
    conda install -y -c conda-forge nco
    if [ $? -ne 0 ]; then
        echo "Error: Failed to install nco."
        exit 1
    fi
fi

datetimeLabel="202307171030"
currenttime="10:30"
echo "$currenttime"
runDate="20230717"

export USER=$(whoami)

cwd="/c/autoval_gsoc/autoval_package/jobs"
inputDir="/c/autoval_gsoc/autoval_package/inputs/dynamic"
configDir="/c/autoval_gsoc/autoval_package/config"
procDir="/c/autoval_gsoc/autoval_package/outputs/www"
host="localhost"
user="$USER"

echo "$cwd"
echo "$inputDir"
echo "$procDir"
echo "$host"
echo "$user"

rm -rf "$procDir"{/img/*,index.htm,/../work/*,/../data/*,/../tmp/*}

cd "$cwd"

fileMaxele="stofs_2d_glo.t06z.fields.cwl.maxele.nc"
filePoints="stofs_2d_glo.t06z.points.cwl.nc"

echo "$runDate" > maxele.recent.new.txt
echo "$currenttime" >> maxele.recent.new.txt
echo "$fileMaxele" >> maxele.recent.new.txt
echo "$filePoints" >> maxele.recent.new.txt

# Select points for skill assessment
ncks -F -d station,1,10 "$inputDir/stofs_2d_glo.t18z.points.cwl.nc" "$inputDir/stofs_2d_glo.t06z.points.autoval.cwl.nc"

# Check if ncks command was successful.
if [ $? -ne 0 ]; then
    echo "ncks command failed."
    exit 1
fi

myCode="/c/autoval_gsoc/autoval_package/code/autoval/autoval/validate/run.py"
PYTHONPATH="/c/autoval_gsoc/autoval_package/code/csdllib"
iniFile="/c/autoval_gsoc/autoval_package/config/test1_global.ini"

/c/Users/siddh/anaconda3/envs/autoval_env/python -W ignore "$myCode" -p "$inputDir/" -i "$iniFile"

if [ $? -ne 0 ]; then
    echo "Python script failed."
    exit 1
fi

echo "Script completed successfully."