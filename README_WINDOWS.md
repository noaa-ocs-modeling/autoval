# WINDOWS BASED SYSTEMS

## Setup Python Environment

   -Download and Install Anaconda on Windows System.

   -After installation, search for Anaconda PowerShell Prompt in the Start menu.

   -In the Anaconda PowerShell, run the following command to create a new environment named autoval_env (any name can be given) with Python 3.9
    ```   
    conda create --name autoval_env python=3.9
    ```

   -Once the environment is created, activate it by running:
    ```
    conda activate autoval_env
    ```

   -Install the required packages using the following commands:
    ```
    conda install -c conda-forge nco=5.2.4
    conda install anaconda::git
    conda install anaconda::pycosat
    conda install matplotlib=3.3.4 seaborn=0.11.0
    ```
   -Install additional Python dependencies from requirements_windows.txt:
    ```
    pip install -r requirements_windows.txt
    ```
### STOFS-2D-Global:

1. **Recommended Directory Structure:**

   - There are multiple components of inputs (some static and some dynamically change over each run), code scripts, Autoval different outputs, configuration, and bash scripts. Here is the recommended directory structure for the Autoval package:
   
   ![Directory Structure](https://github.com/noaa-ocs-modeling/autoval/assets/148251584/b30b8d44-5a64-4177-afcc-a22fe8cd6f6b)

2. **Setup:**

   - Create `code`, `inputs`, `outputs`, `jobs`, and `config` directories in a root directory where you have enough storage (~20 GB).
   
   - Go to the code directory and download the Autoval package using the following command:

     ```
     git clone -b v3.0.0 https://github.com/noaa-ocs-modeling/autoval.git
     ```

   - In the same code directory, download the `csdllib` package:

     ```
     git clone https://github.com/noaa-ocs-modeling/csdllib.git
     ```

   - Go to the `inputs` directory and create two directories: `static` and `dynamic`.

   - Inside the `dynamic` folder, download STOFS-2D-Global outputs using the following commands:
    
    ```
     curl -O https://noaa-nos-stofs2d-pds.s3.amazonaws.com/stofs_2d_glo.20230717/stofs_2d_glo.t06z.points.cwl.nc
     curl -O https://noaa-nos-stofs2d-pds.s3.amazonaws.com/stofs_2d_glo.20230717/stofs_2d_glo.t06z.fields.cwl.maxele.nc
     ```
   - Inside the `static` folder, download grid data and coastline data:
    
    ```
     curl -O ftp://ocsftp.ncd.noaa.gov/svinogra/GESTOFS/glo6/GESTOFS_vPT_V2_w_weir_island.14
     curl -O ftp://ocsftp.ncd.noaa.gov/estofs/data/noaa_coastline_world.dat
    ```
   - To run Autoval, we need a main config file and up to five config files specifying the spatial extent of the maximum water level plots.

   - For the extent of the domain, copy `config.map.estofs.glo.ini`, `config.map.estofs.atl.ini`, `config.map.estofs.pac.ini`, `config.map.puertorico.ini` from the cfg.domains folder to the config folder. You can also follow the same format and generate any domain.ini file that you would like. Just note that STOFS-2D-Global model outputs are associated with -180 to 180 longitude coordinates.

   - Copy the `test1_global.ini` file from the tests folder into your config folder. This will serve as your main configuration file. Update the directories inside the file to correspond to your paths.

   - Copy the `test1_global.bash` file from the tests directory to your jobs directory. Ensure you have set up the environment as per the **Setup Python Environment** section. Update the file locations inside the bash script to point to the appropriate files.

3. **Run:**

   - Submit the bash file to the computing node or simply run it interactively:

     ```
     bash test1_global.bash
     ```

### STOFS-2D-Global (Using bias corrected data):
Here we explain how to use Autoval for STOFS-2D-Global on bias corrected data. For that we need to read additional data from previous cycles to calculate bias. Follow steps 1 explained for STOFS-2D-Global to create directories. Follow step 2 to download the csdllib and Autoval packages in the code directory.

Go to the `inputs` directory and create two directories: `static` and `dynamic`.

   - Inside the 'dynamic' folder, download STOFS-2D-Global outputs for five to six days. Create six folders using the dates of data you are interested in; for example:
     
     ```
     mkdir stofs_2d_glo.202403{05..10} 
     ```
   - To download all the available cycles in each folder, copy the url files available in the 'tests' folder to the corresponding directory and download data for all the available cycles for that date using the following commands:
     ```
     FOR POWERSHELL:
     $dates = "20240310", "20240309", "20240308", "20240307", "20240306", "20240305"
     foreach ($date in $dates) 
     {Set-Location "./stofs_2d_glo.$date"
     Get-Content "urls_$date.txt" | ForEach-Object { curl -O $_ }
     Set-Location ".."}
     ```
   - Inside the static folder, download grid data and coastline data:
    ```
     curl -O ftp://ocsftp.ncd.noaa.gov/estofs/data/GSTOFSv5.6.5_BT_DMW.14
     curl -O ftp://ocsftp.ncd.noaa.gov/estofs/data/noaa_coastline_world.dat
     curl -O ftp://ocsftp.ncd.noaa.gov/estofs/data/noaa_coastline_world.dat
    ```

- In the csdllib plot/map, plot/series, and plot/scatter scripts, replace the line:
    ```
     matplotlib.use('Agg', warn=False)
     with
     matplotlib.use('Agg')
    ```

- To run Autoval, we need a main config file and up to five config files specifying the spatial extent of the maximum water level plots.

- For the extent of the domain, copy `config.map.estofs.glo.ini`, `config.map.estofs.atl.ini`, `config.map.estofs.pac.ini`, `config.map.puertorico.ini` from the cfg.domains folder to the config folder. You can also follow the same format and generate any domain.ini file that you would like. Just note that STOFS-2D-Global model outputs are associated with -180 to 180 longitude coordinates.

- Copy the test4_global.ini file from the tests folder into your config folder. This will serve as your main configuration file. Update the directories inside the file to correspond to your paths.

- Copy the test4_global.bash file from the tests directory to your jobs directory. Ensure you have set up the environment as per the Setup Python Environment section. Update the file locations inside the bash script to point to the appropriate files.

- Submit the bash file to the computing node or simply run it interactively:

     ```
     bash test4_global.bash
     ```


### STOFS-3D-Atlantic:
The steps to use Autoval for STOFS-3D-Atlantic are very similar to those for STOFS-2D-Global. Follow steps 1 and 2 to create directories. Follow step 2 to download the csdllib and Autoval packages in the code directory.

- Inside the `dynamic` folder, download STOFS-3D-Atlantic outputs using the following commands:
    ```
     curl -O https://noaa-gestofs-pds.s3.amazonaws.com/stofs_2d_glo.20250109/stofs_2d_glo.t18z.points.cwl.nc
     curl -O https://noaa-gestofs-pds.s3.amazonaws.com/stofs_2d_glo.20250109/stofs_2d_glo.t18z.fields.cwl.maxele.nc
    ```

- Inside the `static` folder, download grid data and coastline data:
    ```
     curl -O ftp://ocsftp.ncd.noaa.gov/estofs/data/GSTOFSv5.6.5_BT_DMW.14
     curl -O ftp://ocsftp.ncd.noaa.gov/estofs/data/noaa_coastline_world.dat
    ```
- In the csdllib plot/map, plot/series, and plot/scatter scripts, replace the line:
    ```
     matplotlib.use('Agg', warn=False)
     with
     matplotlib.use('Agg')
    ```
- To run Autoval, we need a main config file and up to five config files specifying the spatial extent of the maximum water level plots.

  - For the extent of the domain, copy `config.map.estofs.glo.ini`, `config.map.estofs.atl.ini`, `config.map.puertorico.ini` from the `cfg.domains` folder to the config folder. You can also follow the same format and generate any `domain.ini` file that you would like. Just note that STOFS-3D-Atlantic model outputs are associated with -180 to 180 longitude coordinates.

  - Copy the `test2_atl.ini` file from the tests folder into your config folder. This will serve as your main configuration file. Update the directories inside the file to correspond to your paths.

  - Copy the `test2_atl.bash` file from the tests directory to your jobs directory. Ensure you have set up the environment as per the Setup Python Environment section. Update the file locations inside the bash script to point to the appropriate files.

  - Submit the bash file to the computing node or simply run it interactively:

     ```
     bash test2_atl.bash
     ```

### STOFS-3D-Pacific:
The steps to use Autoval for STOFS-3D-Pacific are very similar to those for STOFS-2D-Global. Follow steps 1 and 2 to create directories. Follow step 2 to download the csdllib and Autoval packages in the code directory.

- Inside the `dynamic` folder, download STOFS-3D-Pacific outputs using the following commands:
    ```
     curl -O https://noaa-nos-stofs3d-pds.s3.amazonaws.com/STOFS-3D-Pac/para/stofs_3d_pac.20240126/stofs_3d_pac.t12z.points.cwl.nc
     curl -O https://noaa-nos-stofs3d-pds.s3.amazonaws.com/STOFS-3D-Pac/para/stofs_3d_pac.20240126/stofs_3d_pac.t12z.fields.cwl.maxele.nc
    ```

- Inside the `static` folder, download grid data and coastline data:
    ```
     curl -O https://noaa-nos-stofs3d-pds.s3.amazonaws.com/STOFS-3D-Pac/para/stofs_3d_pac.20240101/rerun/hgrid_split.gr3
     curl -O https://noaa-nos-stofs3d-pds.s3.amazonaws.com/STOFS-3D-Pac/para/stofs_3d_pac.20240101/rerun/coastline.dat
    ```

- In the csdllib plot/map, plot/series, and plot/scatter scripts, replace the line:
    ```
     matplotlib.use('Agg', warn=False)
     with
     matplotlib.use('Agg')
    ```

- To run Autoval, we need a main config file and up to five config files specifying the spatial extent of the maximum water level plots.

- For the extent of the domain, copy `config.map.estofs.glo_pac.ini`, `config.map.estofs.pac.pac.ini`, `config.map.west.ini`, `config.map.Alaska.ini`, `config.map.hawaii_pac.ini` from the `cfg.domains` folder to the config folder. You can also follow the same format and generate any `domain.ini` file that you would like. Just note that STOFS-3D-Pacific model outputs are associated with -30 to 330 longitude coordinates.

- Copy the `test3_pac.ini` file from the tests folder into your config folder. This will serve as your main configuration file. Update the directories inside the file to correspond to your paths.

- Copy the `test3_pac.bash` file from the tests directory to your jobs directory. Ensure you have set up the environment as per the Setup Python Environment section. Update the file locations inside the bash script to point to the appropriate files.

- Submit the bash file to the computing node or simply run it interactively:

     ```
     bash test3_pac.bash
     ```
