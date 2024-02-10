# AUTOVAL
Autoval is a library designed for model skill assessment, with a focus on large-scale water level data.

## Supported Models
Autoval currently supports the output of the following models: 

- [STOFS-2D_Global](https://noaa-gestofs-pds.s3.amazonaws.com/README.html)

- [STOFS-3D-Atlantic](https://noaa-nos-stofs3d-pds.s3.amazonaws.com/README.html) 

- [STOFS-3D-Pacific](https://ocean.weather.gov/estofs/estofs_pacific_surge_info.php)

## Development Team
The package is developed by Sergey.Vinogradov@noaa.gov and later updated by:

- georgios.britzolakis@noaa.gov
- atieh.alipour@noaa.gov
- saeed.moghimi@noaa.gov
- soroosh.mani@noaa.gov
- l.shi@noaa.gov
- zizang.yang@noaa.gov
- gregory.seroka@noaa.gov
- yuji.funakoshi@noaa.gov

## Disclaimer
The United States Department of Commerce (DOC) GitHub project code is provided on an 'as is' basis and the user assumes responsibility for its use. DOC has relinquished control of the information and no longer has responsibility to protect the integrity, confidentiality, or availability of the information. Any claims against the Department of Commerce stemming from the use of its GitHub project will be governed by all applicable Federal law. Any reference to specific commercial products, processes, or services by service mark, trademark, manufacturer, or otherwise, does not constitute or imply their endorsement, recommendation or favoring by the Department of Commerce. The Department of Commerce seal and logo, or the seal and logo of a DOC bureau, shall not be used in any manner to imply endorsement of any commercial product or activity by DOC or the United States Government.

## Download
To download the Autoval package, follow these steps:
1. **Choose a Location with Sufficient Space:**

   Create a folder in a space where you have approximately 20GB of free space available.

2. **Clone the Repository:**
   
   Use the following command to clone the repository:
   ```
   git clone -b v3.0.0 https://github.com/noaa-ocs-modeling/autoval.git
   ```
## Installation
To install the Autoval package, follow these steps:

1. **Setup Python Environment:**
   
   - We recommend setting up a Conda virtual environment to manage dependencies. If you haven't already, install Conda by following the instructions [here](https://docs.anaconda.com/free/miniconda/).

   - Once Conda is installed, create a new virtual environment for autoval. Run the following command:
   
   ```
   conda create --name autoval_env
   ```
   Replace autoval_env with your desired environment name.

   - Activate the newly created virtual environment using the following command:
   ```
   conda activate autoval_env
   ```
    
   - Navigate to the directory where you downloaded the Autoval package.

   - With the virtual environment activated, install the required dependencies using the requirements.txt file:
   
   ```
   pip install -r requirements.txt
   ```

## Package Description
- Currently, Autoval is specifically designed to read and plot ADCIRC model output (the base model used for STOFS-2D-global). For STOFS-3D model outputs (based on the SCHISM model), we use converted model outputs available in the same location.

- The package reads model outputs and compares predicted water levels with data from the Intergovernmental Oceanographic Commission (IOC) and NOAA NOS Center for Operational Oceanographic Products and Services (CO-OPS).

- The `csdlib` package is fully integrated into the Autoval package. Autoval uses `csdllib` to read predicted water levels, calculate performance metrics, and report relevant notifications. It is recommended that users download and save the `csdllib` package in the same directory as the Autoval package.

- It is also recommended to use a bash file (available in the tests folder) to run the package. These bash files include the directory of configuration and `csdllib` packages and call the `run.py` code to execute Autoval.

- The recommended bash scripts use a main configuration file to execute the Autoval code. Example configuration files are available in the tests folder. Users should modify the directories and parameters according to their working area.

- Autoval is currently being used for STOFS skill assessment. An example of the Autoval report output can be found [here](https://polar.ncep.noaa.gov/estofs/autoval/estofs.glo/index.htm).

- The package generates both spatial maps of the maximum water levels and time series of model-predicted and observed water levels.

- Autoval uses different performance metrics to assess the model's skill at any specific location. The performance metrics are listed below:

    - RMSE (meters): Root Mean Square Error between the model and the observations.
    - PEAK (meters): Under/overestimation of the maximal water level.
    - PLAG (minutes): Time lag between the modeled and the observed peak in water level.
    - BIAS (meters): Linear bias in the modeled water level.
    - VEXP (%): Variance explained, a measure of coherence between the model and the observations.
    - SKIL (unitless): Statistical Skill of the model against the observations.
    - RVAL (unitless): R-Value of the model against the observations.
    - NPTS (unitless): The number of 6-minute model/data pairs at the location that went into computing the above metrics.

For more information, please refer to this [link](https://polar.ncep.noaa.gov/estofs/glo.htm).

Below are a few examples of setting up and running Autoval.

   
   

   

   







