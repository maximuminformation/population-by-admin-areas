# Attributing population data to administrative areas
This Python attributes gridded population data to polygon amministrative areas.

## Data sources
### Population data
    - 2020 1KM unconstrained population count
      format: .tif
      link: https://hub.worldpop.org/geodata/summary?id=24777
      citation: WorldPop (www.worldpop.org - School of Geography and Environmental Science, University of Southampton; Department of Geography and Geosciences, University of Louisville; Departement de Geographie, Universite de Namur) and Center for International Earth Science Information Network (CIESIN), Columbia University (2018). Global High Resolution Population Denominators Project - Funded by The Bill and Melinda Gates Foundation (OPP1134076). https://dx.doi.org/10.5258/SOTON/WP00647
      license: © 2024 WorldPop datasets are licensed under the Creative Commons Attribution 4.0 International https://creativecommons.org/licenses/by/4.0/

### Administrative areas data
    - GDAM v4.1
      format: .gpkg
      link: https://gadm.org/download_world.html
      citation: none found.
      license: The data are freely available for academic use and other non-commercial use. Redistribution or commercial use is not allowed without prior permission.
      Using the data to create maps for publishing of academic research articles is allowed. Thus you can use the maps you made with GADM data for figures in articles published by PLoS, Springer Nature, Elsevier, MDPI, etc. You are allowed (but not required) to publish these articles (and the maps they contain) under an open license such as CC-BY as is the case with PLoS journals and may be the case with other open access articles. Data for the following countries is covered by a a different license Austria: Creative Commons Attribution-ShareAlike 2.0 (source: Government of Ausria) 

## What does this code do?
The code accepts two inputs, the file paths of a single band tif file containing the population values at 1Km resolution and a geopackage file containing the administrative areas for every county in the World.

The .gpkg contains 6 layers for 6 different administrative levels, however the code will only process ```ADM_1``` and ```ADM_2``` levels.

The code will iterate through each polygon for each amministrative area in each layer and calculate the total population falling within the ```.tif``` file and save the results in a new geopackage and shape files.