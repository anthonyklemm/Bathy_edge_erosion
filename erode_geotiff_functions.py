
# -*- coding: utf-8 -*-
"""
Created on Tue May  2 15:40:29 2023

@author: Anthony.R.Klemm
"""
import os
import numpy as np
from osgeo import gdal
from skimage import morphology
from skimage.measure import label, regionprops


def prepare_geotiff(input_geotiff, output_dir):
    dataset = gdal.Open(input_geotiff, gdal.GA_ReadOnly)
    band = dataset.GetRasterBand(1)

    # Read raster data
    raster_data = band.ReadAsArray()

    # Get current NoData value
    current_nodata_value = band.GetNoDataValue()

    # Set the desired NoData value
    desired_nodata_value = 1000000

    # Replace current NoData value with desired NoData value
    if current_nodata_value is not None and not np.isnan(current_nodata_value):
        raster_data[raster_data == current_nodata_value] = desired_nodata_value

    # If current NoData value is 'nan', also replace 'nan' with desired NoData value
    if np.isnan(current_nodata_value):
        raster_data = np.nan_to_num(raster_data, nan=desired_nodata_value)

    # Check the data type of the raster data, convert to float32 if not already
    if raster_data.dtype != np.float32:
        raster_data = raster_data.astype(np.float32)

    # Create a new GeoTIFF file
    driver = gdal.GetDriverByName('GTiff')
    out_dataset = driver.Create(output_dir +'/'+ 'temp.tif', dataset.RasterXSize, dataset.RasterYSize, 1, gdal.GDT_Float32)
    out_dataset.SetGeoTransform(dataset.GetGeoTransform())
    out_dataset.SetProjection(dataset.GetProjection())

    # Write the processed data to the new file
    out_band = out_dataset.GetRasterBand(1)
    out_band.WriteArray(raster_data)
    out_band.SetNoDataValue(desired_nodata_value)

    # Clean up
    out_band.FlushCache()
    out_band = None
    out_dataset = None
    dataset = None

    full_elevation_tiff = output_dir +'/'+ 'temp.tif'
    return full_elevation_tiff


def erode_geotiff(input_geotiff, output_dir, chunk_height=1000, overlap_factor=0.1, min_gap_size=6):
    full_elevation_tiff = prepare_geotiff(input_geotiff, output_dir)
    dataset = gdal.Open(full_elevation_tiff)
    band = dataset.GetRasterBand(1)
    
    raster_width = dataset.RasterXSize
    raster_height = dataset.RasterYSize
    no_data_value = dataset.GetRasterBand(1).GetNoDataValue()
    
    
    # Resultant array to store the eroded data
    eroded_data = np.full((raster_height, raster_width), no_data_value)
    
    # Calculate the number of chunks
    overlap_pixels = int(chunk_height * overlap_factor)
    num_chunks = max(1, ((raster_height - overlap_pixels - 1) // (chunk_height - overlap_pixels)) + 1)
    print(f"Number of chunks: {num_chunks}")
    
    # Iterate over the raster in chunks
    for i, start_row in enumerate(range(0, raster_height, chunk_height - overlap_pixels)):
        if start_row >= raster_height:
            break
        end_row = min(start_row + chunk_height, raster_height)
        print(f"Processing chunk {i + 1} of {num_chunks}...")
        
        # Read the chunk data with buffer
        buffer_size = overlap_pixels
        buffer_start_row = max(0, start_row - buffer_size)
        buffer_end_row = min(raster_height, end_row + buffer_size)
        chunk_data = band.ReadAsArray(0, buffer_start_row, raster_width, buffer_end_row - buffer_start_row)
        
        # Create a binary mask based on the NoDataValue
        binary_mask = np.where(chunk_data != no_data_value, 1, 0).astype(np.uint8)

        # Invert binary mask to focus on gaps
        inverted_binary_mask = np.where(binary_mask == 0, 1, 0).astype(np.uint8)

        # Label connected components in the inverted binary mask
        labeled_mask = label(inverted_binary_mask)

        # Create masks for small and large gaps
        small_gaps_mask = np.zeros_like(binary_mask)
        large_gaps_mask = np.zeros_like(binary_mask)

        for region in regionprops(labeled_mask):
            region_mask = (labeled_mask == region.label)
            if region.area < min_gap_size:
                small_gaps_mask[region_mask] = 1
            else:
                large_gaps_mask[region_mask] = 1
        
        # Dilate large gaps
        dilated_large_gaps_mask = morphology.binary_dilation(large_gaps_mask, morphology.square(5))

        # Erode all edges, including gaps
        eroded_mask = morphology.binary_erosion(binary_mask, morphology.square(3))

        # Add back in data values from dilated large gaps mask and small gaps mask
        eroded_chunk = np.where(eroded_mask == 1, chunk_data, no_data_value)
        eroded_chunk[~dilated_large_gaps_mask & (eroded_mask == 0)] = chunk_data[~dilated_large_gaps_mask & (eroded_mask == 0)]
        eroded_chunk[small_gaps_mask == 1] = chunk_data[small_gaps_mask == 1]
        
        # Remove buffer
        buffer_rows_to_remove = buffer_size if start_row != 0 else 0
        final_eroded_chunk = eroded_chunk[buffer_rows_to_remove : buffer_rows_to_remove + (end_row - start_row), :]
        
        # Store the eroded chunk data in the resultant array
        eroded_data[start_row:end_row, :] = final_eroded_chunk
    
    # Save the eroded data as a TIFF (this can be modified based on requirements)
    driver = gdal.GetDriverByName('GTiff')
    options = ["COMPRESS=LZW"]
    eroded_dataset = driver.Create(
        os.path.join(output_dir, os.path.splitext(os.path.basename(input_geotiff))[0] + "_eroded" + os.path.splitext(input_geotiff)[1]),
        raster_width,
        raster_height,
        1,
        band.DataType,
        options=options
        )
    eroded_dataset.SetGeoTransform(dataset.GetGeoTransform())
    eroded_dataset.SetProjection(dataset.GetProjection())
    eroded_band = eroded_dataset.GetRasterBand(1)
    eroded_band.WriteArray(eroded_data)
    eroded_band.SetNoDataValue(no_data_value)
    eroded_band.FlushCache()

    # Cleanup
    dataset = None
    eroded_dataset = None
    print('***elevation band erosion complete***')
    return output_dir + '/eroded.tif'


def remove_intermediate_files(output_dir):
    print('***removing intermediate files***')
    full_elevation_tiff = output_dir +'/'+ 'temp.tif'
    os.remove(full_elevation_tiff)


def process_geotiff(input_geotiff, output_dir, progress, root):
    eroded_geotiff_file = os.path.join(output_dir, os.path.splitext(os.path.basename(input_geotiff))[0] + "_eroded" + os.path.splitext(input_geotiff)[1])
    prepare_geotiff(input_geotiff, output_dir)
    if progress is not None: progress["value"] = 25
    else: print("Progress: 25%")
    if root is not None: root.update_idletasks()
    erode_geotiff(input_geotiff, output_dir)
    if progress is not None: progress["value"] = 50
    else: print("Progress: 50%")
    if root is not None: root.update_idletasks()
    remove_intermediate_files(output_dir)
    if progress is not None: progress["value"] = 100
    else: print("Progress: 100%")
    if root is not None: root.update_idletasks()
    return eroded_geotiff_file


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Process a geotiff file to erode its outer edges.')
    parser.add_argument('input_geotiff', help='The path to the input geotiff file.')
    parser.add_argument('output_dir', help='The output directory of the processed geotiff file.')
    
    args = parser.parse_args()
    
    # Call the process_geotiff function with the input arguments.
    process_geotiff(args.input_geotiff, args.output_dir, None, None)

