# MODIS_burned_areas_index_values_identification
This script gets best index values for MODIS burned areas identification.

Path to folder with clean MODIS imagery (no clouds, good pixel quality) has to be identified in the script.
MODIS imagery has to be organized in subfolder by protected areas and all subfolders have to be stored in one main folder.
The output is a numpy array with many bands: each band stores indexes (NBR, dNBR, RdNBR and Band 5 ratio) and before/after event dates when a burned area event has been detected.
