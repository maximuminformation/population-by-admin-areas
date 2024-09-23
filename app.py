import geopandas as gpd
import rasterio
import numpy as np
import rasterio.mask
import fiona
from shapely.geometry import MultiPolygon
import math

# Function to calculate the sum of all pixels (negative values counted as zero)
def sum_pixels(tiff_file, geometry):
    with rasterio.open(tiff_file) as src:
        # Mask the raster with the geometry
        out_image, out_transform = rasterio.mask.mask(src, [geometry], crop=True)
        # Set negative values to zero
        out_image[out_image < 0] = 0
        # Sum all pixel values
        return math.ceil(np.sum(out_image))

# Read the geopackage
geopackage_path = 'data\gadm_410-levels\gadm_410-levels.gpkg'

# Path to the tiff file
tiff_file = 'data\ppp_2020_1km_Aggregated.tif'

# Create a new GeoPackage to save the results
output_gpkg = 'data\output_data\gadm_ppp_2020_1km_Aggregated.gpkg'

# List all layers in the GeoPackage
layers = fiona.listlayers(geopackage_path )

# Exclude layers named ADM_0 and ADM_1
layers_to_process = [layer for layer in layers if layer not in ['ADM_0', 'ADM_3', 'ADM_4', 'ADM_5']]

# Iterate over each layer in the geopackage
for layer in layers_to_process:
    layer_gdf = gpd.read_file(geopackage_path, layer=layer)
    # Initialize a list to store pixel sums for each feature
    pixel_sums = []
    # Iterate over each feature in the layer
    for idx, row in layer_gdf.iterrows():
        geometry = row['geometry']
        if isinstance(geometry, MultiPolygon):
            # If the geometry is a MultiPolygon, sum pixels for each Polygon
            total_sum = 0
            for polygon in geometry.geoms:
                total_sum += sum_pixels(tiff_file, polygon)
            print(total_sum)
            pixel_sums.append(total_sum)
        else:
            pixel_sum = sum_pixels(tiff_file, geometry)
            print(pixel_sum)
            pixel_sums.append(pixel_sum)
    # Add the pixel sums to the GeoDataFrame
    layer_gdf['pixel_sum'] = pixel_sums
    # Save the updated layer to the new GeoPackage
    layer_gdf.to_file(output_gpkg, layer=layer, driver="GPKG")

print(f"Results saved to {output_gpkg}")