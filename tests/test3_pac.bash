#!/bin/bash

#Script execution instructions

source /work/noaa/nosofs/aalipour/envs/autoval_env/bin/activate  #activate the virtual environment

# Set path to python3 
pyPath=/work/noaa/nosofs/aalipour/envs/autoval_env/bin/python

module load nco


datetimeLabel="20240126_1030" #$(date +\%Y\%m\%d\%H\%M)
currenttime="10:30" #$(date +%H:%M)
echo $currenttime
runDate="20240126" 


export USER=`whoami`

#Assign the directories
cwd=/work/noaa/nosofs/aalipour/STOFS_3D_Pac_Test/jobs/
inputDir=/work/noaa/nosofs/aalipour/STOFS_3D_Pac_Test/inputs/dynamic/
configDir=/work/noaa/nosofs/aalipour/STOFS_3D_Pac_Test/config/
procDir=/work/noaa/nosofs/aalipour/STOFS_3D_Pac_Test/outputs/www/
#saveOutDir=/work/noaa/nosofs/aalipour/STOFS_3D_Pac_Test/saveOutDir/ 
host=localhost
user=$USER

echo $cwd
echo $inputDir
echo $procDir
#echo $saveOutDir
echo $host
echo $user

#Cleanup previous run
rm -rf $procDir{./img/*,index.htm,../work/*,../data/*,../tmp/*}

cd $cwd

fileMaxele="stofs_3d_pac.t12z.fields.cwl.maxele.nc"
filePoints="stofs_3d_pac.t12z.points.cwl.nc"

echo $runDate > maxele.recent.new.txt
echo $currenttime >> maxele.recent.new.txt
echo $fileMaxele >> maxele.recent.new.txt
echo $filePoints >> maxele.recent.new.txt

# Select stations for skill assessment

ncks -F -d station,1,30 $inputDir/stofs_3d_pac.t12z.points.cwl.nc $inputDir/stofs_3d_pac.t12z.points.autoval.cwl.nc


# Set path to python executable
myCode="/work/noaa/nosofs/aalipour/STOFS_3D_Pac_Test/code/autoval/autoval/validate/run.py"

# Set PYTHONPATH to csdllib
PYTHONPATH="/work/noaa/nosofs/aalipour/STOFS_3D_Pac_Test/code/csdllib/"

# Specify the INI file
iniFile="/work/noaa/nosofs/aalipour/STOFS_3D_Pac_Test/config/test3_pac.ini"


PYTHONPATH=${PYTHONPATH} ${pyPath} -W ignore ${myCode} -p $inputDir/ -i ${iniFile}

