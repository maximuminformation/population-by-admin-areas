import geopandas as gpd
import rasterio
import numpy as np
import rasterio.mask
import fiona
from shapely.geometry import MultiPolygon
import math
from constants import countries, NAME_1_exclusion

# function to calculate the sum of all pixels (negative values counted as zero)
def sum_pixels(tiff_file, geometry):
    with rasterio.open(tiff_file) as src:
        # mask the raster with the geometry
        out_image, out_transform = rasterio.mask.mask(src, [geometry], crop=True)
        # set negative values to zero
        out_image[out_image < 0] = 0
        # sum all pixel values and round to its nearest integer
        return math.ceil(np.sum(out_image))

# read the geopackage
geopackage_path = 'data\gadm_410-levels\gadm_410-levels.gpkg'

# path to the tiff file
tiff_file = 'data\ppp_2020_1km_Aggregated.tif'

# create a new GeoPackage to save the results
output_gpkg = 'data\output_data\gadm_ppp_2020_1km_Aggregated_light'

# list all layers in the GeoPackage
layers = fiona.listlayers(geopackage_path)

# keep only layers named ADM_1 and ADM_2
layers_to_process = [layer for layer in layers if layer not in ['ADM_0', 'ADM_3', 'ADM_4', 'ADM_5']]

# iterate over each layer in the geopackage
for layer in layers_to_process:
    layer_gdf = gpd.read_file(geopackage_path, layer=layer)
    # filter by country in the list
    filtered_layer_gdf_country = layer_gdf[layer_gdf['GID_0'].isin(countries)].copy()
    # filter by area name not in the list
    filtered_layer_gdf_name_1 = filtered_layer_gdf_country[filtered_layer_gdf_country['NAME_1'].isin(NAME_1_exclusion) == False].copy()
    pixel_sums = []
    for idx, row in filtered_layer_gdf_name_1.iterrows():
        geometry = row['geometry']
        if isinstance(geometry, MultiPolygon):
            # if the geometry is a MultiPolygon, sum pixels for each Polygon
            total_sum = 0
            for polygon in geometry.geoms:
                total_sum += sum_pixels(tiff_file, polygon)
            print(total_sum)
            pixel_sums.append(total_sum)
        else:
            pixel_sum = sum_pixels(tiff_file, geometry)
            print(pixel_sum)
            pixel_sums.append(pixel_sum)
    # add the pixel sums to the geodataframe
    filtered_layer_gdf_name_1['POPULATION'] = pixel_sums
    # save the updated layer to a new geopackage
    out_file = output_gpkg + ".gpkg"
    filtered_layer_gdf_name_1.to_file(out_file, layer=layer, driver="GPKG")
    # save the updated layer to a new shapefile
    out_file = output_gpkg + f"_{layer}.shp"
    filtered_layer_gdf_name_1.to_file(out_file, layer=layer)

print(f"Results saved to {output_gpkg}")