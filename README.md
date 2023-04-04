# Bathy_edge_erosion
Erodes one grid cell on all edges, but retains small interior gaps - say goodbye to any edge fliers in your CUBE-generated bathymetric grid. 

This script processes bathymetry rasters created using the CUBE algorithm from Multibeam Echosounder (MBES) data to remove potential edge fliers. The algorithm erodes the edges of large interior gaps while preserving small gaps in the raster data. This is achieved by performing the following steps:

1. Read the input bathymetry raster (at this point, it only works with geotiffs), identifying the NoDataValue pixels.

2. Create a binary mask based on the NoDataValue pixels.

3. Dilate the binary mask and subtract it from the original binary mask, leaving only the eroded edges.

4. Fill all gaps in the binary mask and compute the area of each gap.

5. Identify large gaps (those with an area larger than the specified minimum gap size) and create a separate mask for them.

6. Erode the edges of the large gaps mask.

7. Combine the eroded large gaps mask with the eroded edges mask to create a combined mask.

8. Apply the combined mask to the input raster data, replacing the eroded edges with NoDataValue pixels.

9. Save the modified raster data to a new GeoTIFF file with LZW compression.

Note: This script is designed to be easily customizable by adjusting parameters such as the minimum gap size. The output raster will have the edges of large gaps eroded by one pixel, while preserving the smaller gaps, thus reducing the potential for edge fliers in the bathymetry data.

In the image below, the white color is the eroded output raster, and the red raster is the original input raster. Notice how small interior gaps are not eroded in the output raster.

![raster erosion](https://user-images.githubusercontent.com/76973843/227607674-3b667641-2c5a-4adf-8c07-d16e6b72affa.jpg)
