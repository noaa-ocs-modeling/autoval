#!/bin/bash

#Script execution instructions

source /work/noaa/nosofs/aalipour/envs/autoval_env/bin/activate  #activate the virtual environment

# Set path to python3 
pyPath=/work/noaa/nosofs/aalipour/envs/autoval_env/bin/python

module load nco


datetimeLabel="202401101030" #$(date +\%Y\%m\%d\%H\%M)
currenttime="10:30" #$(date +%H:%M)
echo $currenttime
runDate="20240110" 


export USER=`whoami`

#Assign the directories
cwd=/work/noaa/nosofs/aalipour/STOFS_3D_Test/jobs/
inputDir=/work/noaa/nosofs/aalipour/STOFS_3D_Test/inputs/dynamic/
configDir=/work/noaa/nosofs/aalipour/STOFS_3D_Test/config/
procDir=/work/noaa/nosofs/aalipour/STOFS_3D_Test/outputs/www/
#saveOutDir=/work/noaa/nosofs/aalipour/STOFS_3D_Test/saveOutDir/ 
host=localhost
user=$USER

echo $cwd
echo $inputDir
echo $procDir
echo $saveOutDir
echo $host
echo $user

#Cleanup previous run
rm -rf $procDir{./img/*,index.htm,../work/*,../data/*,../tmp/*}

cd $cwd

fileMaxele="stofs_3d_atl.t12z.fields.cwl.maxele.nc"
filePoints="stofs_3d_atl.t12z.points.cwl.nc"

echo $runDate > maxele.recent.new.txt
echo $currenttime >> maxele.recent.new.txt
echo $fileMaxele >> maxele.recent.new.txt
echo $filePoints >> maxele.recent.new.txt

# Select points for skill assessment
#ncks -F -d station,1,833 $inputDir/stofs_2d_glo.t18z.points.cwl.nc $inputDir/stofs_2d_glo.t18z.points.autoval.cwl.nc
ncks $inputDir/stofs_3d_atl.t12z.points.cwl.nc $inputDir/stofs_3d_atl.t12z.points.autoval.cwl.nc

#Run the autovalidation script
#$cwd/drive.oper.estofs.glo.v6.cwl.bash $inputDir/ $configDir/oper.estofs-glo.v6.1.cwl.ini


# Set path to python executable
myCode="/work/noaa/nosofs/aalipour/STOFS_3D_Test/code/autoval/autoval/validate/run.py"

# Set PYTHONPATH to csdllib
PYTHONPATH="/work/noaa/nosofs/aalipour/STOFS_3D_Test/code/csdllib/"

# Specify the INI file
iniFile="/work/noaa/nosofs/aalipour/STOFS_3D_Test/config/test2_atl.ini"


PYTHONPATH=${PYTHONPATH} ${pyPath} -W ignore ${myCode} -p $inputDir/ -i ${iniFile}

