# Mapping-US-Airquality
Center for Disease Control air quality data (1999-2013) mapped by US county

## Data Source
Air quality data are available from [Data.gov](https://data.cdc.gov/api/views/cjae-szjv/rows.json?accessType=DOWNLOAD). The json for these data is downloaded, parsed, and stored in a SQLite3 database using the Python Script AirQualGet.py. 

## Data Processing
Run the Python Script AirQualCleanAndMap.py to:

1. Query the air quality data from the SQLite3 database.

2. Download and parse a geojson file containing US county border data. 

* Note: These data may not be accurate in some cases (for example, IL and MI counties extend into great lakes). Check and replace with better coordinates data once found.

3. Clean both air quality and county border data and merge the two.

4. Assign a color scale to the range of air quality data, select the air quality measure of interest, and map air quality by county.

* Note: You must insert your own mapbox_access_token. Also, you can customize the resulting map with the parameters under data and layout. For more information, see the Plotly documentation on [choropleth maps in Python](https://plot.ly/python/choropleth-maps/).

## Results
The result will be a choropleth map of US counties for which data were found, colored to indicate the value of the air quality measure mapped. Three example plots are shown below, one for each air quality measure.

![test](https://github.com/dtelliott79/Mapping-US-Airquality/blob/master/example_1.jpeg)

![test](https://github.com/dtelliott79/Mapping-US-Airquality/blob/master/example_2.jpeg)

![test](https://github.com/dtelliott79/Mapping-US-Airquality/blob/master/example_3.jpeg)

Note: The original data files used in the analysis are also included in this repository. However, they are not required since the Python Scripts access the web data directly.