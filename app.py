import geopandas as gpd
import rasterio
import numpy as np
import rasterio.mask
import fiona
from shapely.geometry import MultiPolygon
import math

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
output_gpkg = 'data\output_data\gadm_ppp_2020_1km_Aggregated.gpkg'

# list all layers in the GeoPackage
layers = fiona.listlayers(geopackage_path )

# exclude layers named ADM_0 and ADM_1
layers_to_process = [layer for layer in layers if layer not in ['ADM_0', 'ADM_3', 'ADM_4', 'ADM_5']]

# iterate over each layer in the geopackage
for layer in layers_to_process:
    layer_gdf = gpd.read_file(geopackage_path, layer=layer)
    pixel_sums = []
    for idx, row in layer_gdf.iterrows():
        geometry = row['geometry']
        if isinstance(geometry, MultiPolygon):
            # if the geometry is a MultiPolygon, sum pixels for each Polygon
            total_sum = 0
            for polygon in geometry.geoms:
                total_sum += sum_pixels(tiff_file, polygon)
            # print(total_sum)
            pixel_sums.append(total_sum)
        else:
            pixel_sum = sum_pixels(tiff_file, geometry)
            # print(pixel_sum)
            pixel_sums.append(pixel_sum)
    # add the pixel sums to the geodataframe
    layer_gdf['pixel_sum'] = pixel_sums
    # save the updated layer to the new geopackage
    layer_gdf.to_file(output_gpkg, layer=layer, driver="GPKG")

print(f"Results saved to {output_gpkg}")