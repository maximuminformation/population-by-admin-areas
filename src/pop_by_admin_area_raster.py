import rasterio
from rasterio.enums import Compression
from rasterio.transform import from_origin
from rasterio.features import rasterize
import geopandas as gpd
import numpy as np

# Load the population raster file
pop_raster = 'data/ppp_2020_1km_Aggregated.tif'
with rasterio.open(pop_raster) as src:
    transform = src.transform
    crs = src.crs
    width = src.width
    height = src.height
    original_nodata = src.nodata

# Define a new NoData value for int32
new_nodata = 0

# Load the geopackage layers from which you want to pickup the area code
gadm_gpkg = 'data\gadm_410-levels\gadm_ppp_2020_1km_aggregated_light__adm_2_slim.gpkg'
adm2 = gpd.read_file(gadm_gpkg) #, layer='ADM_2')
print(adm2)

# Create empty arrays for the new bands
# np.int32 has been used instead of np.float32 to approximate the population estimate to a whole number and to keep file size to a minimum
band2 = np.full((height, width), new_nodata, dtype=np.int32)

# Rasterize the entire GeoDataFrame at once
shapes = ((geom, value) for geom, value in zip(adm2.geometry, adm2.ID))
band2 = rasterize(
    shapes,
    out_shape=(height, width),
    transform=transform,
    fill=new_nodata,
    dtype=np.int32
)

# Process the raster data in 100x100 chunks to avoid memory problems
square_size = 100
new_raster = 'compressed_population_with_names.tif'

with rasterio.open(
    new_raster,
    'w',
    driver='GTiff',
    height=height,
    width=width,
    count=2,
    dtype=np.int32,
    crs=crs,
    transform=transform,
    compress='lzw',
    nodata=new_nodata
) as dst:
    total_chunks = (height // square_size + 1) * (width // square_size + 1)
    chunk_count = 0
    
    for i in range(0, height, square_size):
        for j in range(0, width, square_size):
            # Ensure the window does not exceed the raster bounds
            window_height = min(square_size, height - i)
            window_width = min(square_size, width - j)
            window = rasterio.windows.Window(j, i, window_width, window_height)
            
            with rasterio.open(pop_raster) as src:
                pop_data = src.read(1, window=window)
                pop_data = np.where(pop_data == original_nodata, new_nodata, pop_data).astype(np.float32)
                # np.ceil() has been chosen instead of np.round() to avoid counting as 0 sparcely populated areas
                pop_data = np.ceil(pop_data).astype(np.int32)
            
            # Write the processed data back to the new raster
            dst.write(pop_data, 1, window=window)
            dst.write(band2[i:i+window_height, j:j+window_width], 2, window=window)
            
            # Update and print progress
            chunk_count += 1
            print(f"Processed chunk {chunk_count}/{total_chunks} ({(chunk_count/total_chunks)*100:.2f}%)")

print(f"Compressed 2-band raster file created: {new_raster}")