# Bathy_edge_erosion
Erodes one grid cell on all edges, but retains small interior gaps - say goodbye to any edge fliers in your CUBE-generated bathymetric grid. 

This script processes bathymetry rasters created using the CUBE algorithm from Multibeam Echosounder (MBES) data to remove potential edge fliers. The algorithm erodes the edges of large interior gaps while preserving small gaps in the raster data. This is achieved by performing the following steps:

Read the input bathymetry raster (at this point, it only works with geotiffs), identifying the NoDataValue pixels.
Create a binary mask based on the NoDataValue pixels, where 255 represents valid data and 0 represents NoDataValue pixels.
Dilate the binary mask and subtract it from the original binary mask, leaving only the eroded edges.
Fill all gaps in the binary mask and compute the area of each gap.
Identify large gaps (those with an area larger than the specified minimum gap size) and create a separate mask for them.
Erode the edges of the large gaps mask.
Combine the eroded large gaps mask with the eroded edges mask to create a combined mask.
Apply the combined mask to the input raster data, replacing the eroded edges with NoDataValue pixels.
Save the modified raster data to a new GeoTIFF file with LZW compression.
This script is designed to be easily customizable by adjusting parameters such as the minimum gap size. The output raster will have the edges of large gaps eroded by one pixel, while preserving the smaller gaps, thus reducing the potential for edge fliers in the bathymetry data.

https://user-images.githubusercontent.com/76973843/227607393-d4475faa-3ac1-4d71-9602-fc9ca31d4f77.jpg
