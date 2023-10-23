# Erode Raster

A Python script that erodes one grid cell on all edges but retains small interior gaps. This is particularly useful for removing edge fliers in bathymetric grids generated using the CUBE algorithm from Multibeam Echosounder (MBES) data.

## How it Works

The algorithm performs the following steps to process the bathymetry rasters:

1. Read the input bathymetry raster (currently supports BAG files).
2. Identify the NoDataValue pixels in the raster.
3. Create a binary mask based on the NoDataValue pixels.
4. Perform morphological dilation on the binary mask and subtract it from the original binary mask, leaving only the eroded edges.
5. Fill all gaps in the binary mask and compute the area of each gap.
6. Identify large gaps (those with an area larger than the specified minimum gap size) and create a separate mask for them.
7. Erode the edges of the large gaps mask.
8. Combine the eroded large gaps mask with the eroded edges mask to create a combined mask.
9. Apply the combined mask to the input raster data, replacing the eroded edges with NoDataValue pixels.
10. Save the modified raster data to a new BAG file with LZW compression.

## Customization

The script is designed to be user-friendly and easily customizable by adjusting parameters such as the minimum gap size. The output raster will have the edges of large gaps eroded by one pixel, while preserving the smaller gaps, thus reducing the potential for edge fliers in the bathymetry data.

## Usage

The script can be run from the command line with the following syntax:
python erode_bag_functions.py <input_bag> <output_dir>

Note: This script is designed to be easily customizable by adjusting parameters such as the minimum gap size. The output raster will have the edges of large gaps eroded by one pixel, while preserving the smaller gaps, thus reducing the potential for edge fliers in the bathymetry data.

In the image below, the white color is the eroded output raster, and the red raster is the original input raster. Notice how small interior gaps are not eroded in the output raster.

![raster erosion](https://user-images.githubusercontent.com/76973843/227607674-3b667641-2c5a-4adf-8c07-d16e6b72affa.jpg)
