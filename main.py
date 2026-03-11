## Organizing thoughts to create a script that does the following:

# User inputs their information for the EPA API
# User inputs their GEE information -> If possible, I want the user to only make an account, they should be able to upload their shapefile locally
# User Inputs shapfile after account information is verified
# User selects a pollutant offered by the EPA API (ozone, no2, pm2.5, etc.)
# User enters a date range for the data they want to download (e.g. 2018-2024)
# User selects hourly, daily, or monthly data
# User declares whether they want to save the data or simply view it
# Program runs epa_api_aqnow.py to download and clean the data. This will be saved as a csv file in the data folder. The program will also return a list of the monitoring stations that were downloaded, which will be used in the next step.
# Program should display a map with 3 layers: the downloaded monitors, the inputted shapefile, and base Esri layers.
# Below the map, program should display pollutant over time for each monitor with a main line depicting the mean of all monitors for the AOI.
# User selects raster layers from a list of supplied layers (temperature, humidity, wind speed, etc.). -> Add recomendation that the user is familiar with the processes that drives the pollutant
# User selects a model, the best one is recommened based on the data they have and the pollutant they are modeling. The user can select a different model if they want, but the program will explain why the recommended model is best.
# User defines a resolution for the final model output (e.g. 1km x 1km grid, 5km x 5km grid, etc.)
# Program runs gee_data.py to gather and extract raster data to points
# Program runs models.py to train the model and make predictions
# Program runs surface_plot.py to make a surface plot of the predictions
# Program displays map with the predicted pollutant concentrations, the inputted shapefile, and base Esri layers. The user can use a slider option to change the raster being viewed, and toggle between the monitor data and the predicted data to compare them.

# The user should be able to download the github, open a terminal in the folder, run main.py, and a GUI allows the user to input all of the above information and get the outputs. The user should not have to change any code, they should just be able to run the program and follow the prompts.