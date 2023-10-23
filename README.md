# Erode Raster Edges

This script processes bathymetry rasters created using the CUBE algorithm from Multibeam Echosounder (MBES) data to remove potential edge fliers. The algorithm erodes the edges of large interior gaps while preserving small gaps in the raster data. This is achieved by performing the following steps:

1. Read the input bathymetry raster (currently only supports BAG format, but support for CSAR is planned for future versions).
2. Identify the NoDataValue pixels.
3. Create a binary mask based on the NoDataValue pixels.
4. Label connected components in the inverted binary mask (using skimage.measure to distinguish between large and small gaps).
5. Create masks for small and large gaps based on the connected components.
6. Dilate the binary mask of large gaps.
7. Erode all edges, including gaps, of the binary mask.
8. Add back in data values from dilated large gaps mask and small gaps mask to the eroded binary mask (this allows for preservation of edge pixels in small gaps, but allows for the erosion of edges in larger gaps).
9. Save the modified raster data to a new BAG file with updated elevation and uncertainty bands.

## Customization

This script is designed to be easily customizable by adjusting parameters such as:

- Chunk height: The height of the chunks used for processing the raster in parts to optimize memory usage.
- Overlap factor: The percentage of overlap between chunks to ensure seamless processing at chunk boundaries.
- Minimum gap size: The threshold for distinguishing between small and large gaps.

The output raster will have the edges of large gaps eroded, while preserving the smaller gaps, thus reducing the potential for edge fliers in the bathymetry data.

## Usage

To use this script, you can run the `erode_bag_functions.py` file from the command line, providing the input BAG file and the output directory as arguments. Alternatively, you can use the `erode_bag_gui.py` file to run the script with a graphical user interface.

The script can be run from the command line with the following syntax:
python erode_bag_functions.py <input_bag> <output_dir>

Note: This script is designed to be easily customizable by adjusting parameters such as the minimum gap size. The output raster will have the edges of large gaps eroded by one pixel, while preserving the smaller gaps, thus reducing the potential for edge fliers in the bathymetry data.

In the image below, the white color is the eroded output raster, and the red raster is the original input raster. Notice how small interior gaps are not eroded in the output raster.

![raster erosion](https://user-images.githubusercontent.com/76973843/227607674-3b667641-2c5a-4adf-8c07-d16e6b72affa.jpg)
