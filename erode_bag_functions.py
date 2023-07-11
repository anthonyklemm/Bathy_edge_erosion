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
import h5py
import shutil

def bag_to_elevation_geotiff(input_bag, output_dir):
    dataset = gdal.Open(input_bag, gdal.GA_ReadOnly)
    gdal.Translate(output_dir +'/'+ 'full_elevation_tiff.tif', dataset, bandList=[1])
    full_elevation_tiff = output_dir +'/'+ 'full_elevation_tiff.tif'
    dataset = None
    return full_elevation_tiff

def bag_to_uncertainty_geotiff(input_bag, output_dir):
    dataset = gdal.Open(input_bag, gdal.GA_ReadOnly)
    gdal.Translate(output_dir +'/'+ 'full_uncertainty_tiff.tif', dataset, bandList=[2])
    full_uncertainty_tiff = output_dir +'/'+ 'full_uncertainty_tiff.tif'
    dataset = None
    return full_uncertainty_tiff

def erode_outer_edge_elevation(input_bag, output_dir, min_gap_size=6):
    full_elevation_tiff = bag_to_elevation_geotiff(input_bag, output_dir)
    dataset = gdal.Open(full_elevation_tiff)
    band = dataset.GetRasterBand(1)

    # Read the raster data as a NumPy array
    raster_data = band.ReadAsArray()

    # Create a binary mask based on the NoDataValue
    no_data_value = band.GetNoDataValue()
    binary_mask = np.where(raster_data != no_data_value, 1, 0).astype(np.uint8)

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

    # Dilate large gaps by 2 pixels
    dilated_large_gaps_mask = morphology.binary_dilation(large_gaps_mask, morphology.square(5))

    # Erode all edges, including gaps
    eroded_mask = morphology.binary_erosion(binary_mask, morphology.square(3))

    # Add back in data values from dilated large gaps mask and small gaps mask
    eroded_raster_data = np.where(eroded_mask == 1, raster_data, no_data_value)
    eroded_raster_data[~dilated_large_gaps_mask & (eroded_mask == 0)] = raster_data[~dilated_large_gaps_mask & (eroded_mask == 0)]
    eroded_raster_data[small_gaps_mask == 1] = raster_data[small_gaps_mask == 1]

    # Create a new GeoTIFF file for the eroded raster data
    driver = gdal.GetDriverByName('GTiff')
    eroded_elevation_tiff = driver.Create(output_dir +'/'+ 'eroded_elevation_tiff.tif', dataset.RasterXSize, dataset.RasterYSize, 1, band.DataType,
                                   options=["COMPRESS=LZW", "PREDICTOR=2"])

    # Copy the geotransform and projection from the input raster to the output raster
    eroded_elevation_tiff.SetGeoTransform(dataset.GetGeoTransform())
    eroded_elevation_tiff.SetProjection(dataset.GetProjection())

    # Write the eroded raster data to the output file
    output_band = eroded_elevation_tiff.GetRasterBand(1)
    output_band.WriteArray(eroded_raster_data)

    # Set the same NoDataValue in the output raster as in the input raster
    output_band.SetNoDataValue(no_data_value)

    # Close the datasets
    eroded_elevation_tiff.FlushCache()
    eroded_elevation_tiff = None
    dataset = None
    return output_dir +'/'+ 'eroded_elevation_tiff.tif'
    
def erode_outer_edge_uncertainty(input_bag, output_dir, min_gap_size=6):
    full_uncertainty_tiff = bag_to_uncertainty_geotiff(input_bag, output_dir)
    dataset = gdal.Open(full_uncertainty_tiff)
    band = dataset.GetRasterBand(1)

    # Read the raster data as a NumPy array
    raster_data = band.ReadAsArray()

    # Create a binary mask based on the NoDataValue
    no_data_value = band.GetNoDataValue()
    binary_mask = np.where(raster_data != no_data_value, 1, 0).astype(np.uint8)

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

    # Dilate large gaps by 2 pixels
    dilated_large_gaps_mask = morphology.binary_dilation(large_gaps_mask, morphology.square(5))

    # Erode all edges, including gaps
    eroded_mask = morphology.binary_erosion(binary_mask, morphology.square(3))

    # Add back in data values from dilated large gaps mask and small gaps mask
    eroded_raster_data = np.where(eroded_mask == 1, raster_data, no_data_value)
    eroded_raster_data[~dilated_large_gaps_mask & (eroded_mask == 0)] = raster_data[~dilated_large_gaps_mask & (eroded_mask == 0)]
    eroded_raster_data[small_gaps_mask == 1] = raster_data[small_gaps_mask == 1]

    # Create a new GeoTIFF file for the eroded raster data
    driver = gdal.GetDriverByName('GTiff')
    eroded_uncertainty_tiff = driver.Create(output_dir +'/'+ 'eroded_uncertainty_tiff.tif', dataset.RasterXSize, dataset.RasterYSize, 1, band.DataType,
                                   options=["COMPRESS=LZW", "PREDICTOR=2"])

    # Copy the geotransform and projection from the input raster to the output raster
    eroded_uncertainty_tiff.SetGeoTransform(dataset.GetGeoTransform())
    eroded_uncertainty_tiff.SetProjection(dataset.GetProjection())

    # Write the eroded raster data to the output file
    output_band = eroded_uncertainty_tiff.GetRasterBand(1)
    output_band.WriteArray(eroded_raster_data)

    # Set the same NoDataValue in the output raster as in the input raster
    output_band.SetNoDataValue(no_data_value)

    # Close the datasets
    eroded_uncertainty_tiff.FlushCache()
    eroded_uncertainty_tiff = None
    dataset = None
    return output_dir +'/'+ 'eroded_uncertainty_tiff.tif'

def replace_bag_bands(input_bag, output_dir, eroded_bag_file):
    # Copy the original BAG file to a new file with _eroded suffix
    shutil.copy2(input_bag, eroded_bag_file)

    # Open the eroded BAG file in read-write mode
    with h5py.File(eroded_bag_file, "r+") as bag:
        # Open the elevation and uncertainty GeoTIFF files
        eroded_elevation_tiff = erode_outer_edge_elevation(input_bag, output_dir)
        eroded_uncertainty_tiff = erode_outer_edge_uncertainty(input_bag, output_dir)
        elevation_ds = gdal.Open(eroded_elevation_tiff, gdal.GA_ReadOnly)
        uncertainty_ds = gdal.Open(eroded_uncertainty_tiff, gdal.GA_ReadOnly)

        # Read the elevation and uncertainty data as numpy arrays
        elevation = elevation_ds.GetRasterBand(1).ReadAsArray()
        uncertainty = uncertainty_ds.GetRasterBand(1).ReadAsArray()

        # Flip the elevation and uncertainty arrays along the vertical axis
        elevation = np.flipud(elevation)
        uncertainty = np.flipud(uncertainty)

        # Replace the elevation and uncertainty data in the BAG file
        bag["/BAG_root/elevation"][:] = elevation
        bag["/BAG_root/uncertainty"][:] = uncertainty

        # Close the elevation and uncertainty datasets
        elevation_ds = None
        uncertainty_ds = None

def remove_intermediate_files(output_dir):
    files_to_remove = ['full_elevation_tiff.tif', 'full_uncertainty_tiff.tif', 'eroded_elevation_tiff.tif', 'eroded_uncertainty_tiff.tif']

    for file in files_to_remove:
        file_path = os.path.join(output_dir, file)
        if os.path.exists(file_path):
            os.remove(file_path)

def process_bag(input_bag, output_dir, progress, root):
    eroded_bag_file = os.path.join(output_dir, os.path.splitext(os.path.basename(input_bag))[0] + "_eroded" + os.path.splitext(input_bag)[1])
    if progress is not None: progress["value"] = 25
    else: print("Progress: 25%")
    if root is not None: root.update_idletasks()
    bag_to_elevation_geotiff(input_bag, output_dir)
    if progress is not None: progress["value"] = 50
    else: print("Progress: 50%")
    if root is not None: root.update_idletasks()
    bag_to_uncertainty_geotiff(input_bag, output_dir)
    if progress is not None: progress["value"] = 75
    else: print("Progress: 75%")
    if root is not None: root.update_idletasks()
    replace_bag_bands(input_bag, output_dir, eroded_bag_file)
    remove_intermediate_files(output_dir)
    if progress is not None: progress["value"] = 100
    else: print("Progress: 100%")
    if root is not None: root.update_idletasks()
    return eroded_bag_file

    

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Process a BAG file to erode its outer edges.')
    parser.add_argument('input_bag', help='The path to the input BAG file.')
    parser.add_argument('output_dir', help='The directory to output the processed BAG file to.')
    
    args = parser.parse_args()
    
    # Call the process_bag function with the input arguments.
    process_bag(args.input_bag, args.output_dir, None, None)
