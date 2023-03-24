# -*- coding: utf-8 -*-
"""
Created on Fri Mar 24 13:06:42 2023

@author: Anthony.R.Klemm
"""
import numpy as np
from osgeo import gdal
from skimage import morphology
from skimage.measure import label, regionprops

def erode_outer_edge(raster_file, output_file, min_gap_size=6):
    # Open the raster file
    dataset = gdal.Open(raster_file)
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
    output_dataset = driver.Create(output_file, dataset.RasterXSize, dataset.RasterYSize, 1, band.DataType,
                                   options=["COMPRESS=LZW", "PREDICTOR=2"])

    # Copy the geotransform and projection from the input raster to the output raster
    output_dataset.SetGeoTransform(dataset.GetGeoTransform())
    output_dataset.SetProjection(dataset.GetProjection())

    # Write the eroded raster data to the output file
    output_band = output_dataset.GetRasterBand(1)
    output_band.WriteArray(eroded_raster_data)

    # Set the same NoDataValue in the output raster as in the input raster
    output_band.SetNoDataValue(no_data_value)

    # Close the datasets
    output_band.FlushCache()
    output_dataset = None
    dataset = None

if __name__ == "__main__":
    input_raster_file = r"C:\Users\Anthony.R.Klemm\Documents\CARIS\extract_1m.tiff"
    output_raster_file = r"C:\Users\Anthony.R.Klemm\Documents\CARIS\extract_1m_eroded11.tiff"

    erode_outer_edge(input_raster_file, output_raster_file)
