#!/bin/bash

#Script execution instructions

source /work/noaa/nosofs/aalipour/envs/autoval_env/bin/activate  #activate the virtual environment


# Set path to python3 
pyPath=/work/noaa/nosofs/aalipour/envs/autoval_env/bin/python

module load nco


datetimeLabel="202403101030" #$(date +\%Y\%m\%d\%H\%M)
currenttime="10:30" #$(date +%H:%M)
echo $currenttime
runDate="20240310" 


export USER=`whoami`

#Assign the directories
cwd=/work/noaa/nosofs/aalipour/test_bias/jobs/
inputDir=/work/noaa/nosofs/aalipour/test_bias/inputs/dynamic/stofs_2d_glo.$runDate/
configDir=/work/noaa/nosofs/aalipour/test_bias/config/
procDir=/work/noaa/nosofs/aalipour/test_bias/outputs/www/
parentinputDir=/work/noaa/nosofs/aalipour/test_bias/inputs/dynamic
#saveOutDir=/work/noaa/nosofs/aalipour/STOFS_2D_Test/saveOutDir/ 
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

fileMaxele="stofs_2d_glo.t06z.fields.cwl.maxele.nc"
filePoints="stofs_2d_glo.t06z.points.cwl.nc"

echo $runDate > maxele.recent.new.txt
echo $currenttime >> maxele.recent.new.txt
echo $fileMaxele >> maxele.recent.new.txt
echo $filePoints >> maxele.recent.new.txt

# Select points for skill assessment
#ncks -F -$inputDir/stofs_2d_glo.t06z.points.cwl.nc $inputDir/stofs_2d_glo.t06z.points.autoval.cwl.nc
ncks -F -d station,1,20 $inputDir/stofs_2d_glo.t06z.points.cwl.nc $inputDir/stofs_2d_glo.t06z.points.autoval.cwl.nc

NowcastPeriod=120 # hours

# Loop through each day
for (( i=0; i<=$NowcastPeriod; i+=24 )); do
    # Calculate the date for the current iteration
    NowcastDate=$(date -d "$runDate - $i hours" +"%Y%m%d") # number of hours
    echo $NowcastDate
    # Loop through each hour of the day
    for hour in 00 06 12 18; do

        # Perform operations with the current date and hour
        ncks -F -d station,1,20 "$parentinputDir/stofs_2d_glo.$NowcastDate/stofs_2d_glo.t${hour}z.points.cwl.nc" \
            "$parentinputDir/stofs_2d_glo.$NowcastDate/stofs_2d_glo.t${hour}z.points.autoval.cwl.nc"
    done
done


## If BiasCorrection is 1 activate this part
# Loop through each day
for (( i=0; i<=$NowcastPeriod; i+=24 )); do
    # Calculate the date for the current iteration
    NowcastDate=$(date -d "$runDate - $i hours" +"%Y%m%d") # number of hours
    echo $NowcastDate
    # Loop through each hour of the day
    for hour in 00 06 12 18; do

        # Perform operations with the current date and hour
        ncks -F -d station,1,20 "$parentinputDir/stofs_2d_glo.$NowcastDate/stofs_2d_glo.t${hour}z.points.cwl.noanomaly.nc" \
            "$parentinputDir/stofs_2d_glo.$NowcastDate/stofs_2d_glo.t${hour}z.points.autoval.cwl.noanomaly.nc"
    done
done


# Set path to python executable
myCode="/work/noaa/nosofs/aalipour/test_bias/code/autoval/autoval/validate/run.py"

# Set PYTHONPATH to csdllib
PYTHONPATH="/work/noaa/nosofs/aalipour/test_bias/code/csdllib/"

# Specify the INI file
iniFile="/work/noaa/nosofs/aalipour/test_bias/config/test1_global.ini"


PYTHONPATH=${PYTHONPATH} ${pyPath} -W ignore ${myCode} -p $inputDir/ -i ${iniFile}

