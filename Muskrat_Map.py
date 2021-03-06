############################################
# A tool to add muskrat lodge monitoring data to a map
# Osanna Drake
############################################

# import the modules we need to run the code
import arcpy
import xlrd
import os


# defining the workspace (change this to the folder where you keep the monitoring files
folder = arcpy.GetParameterAsText(0)  # for me this is r"C:\Users\osanna\Downloads" #change this to the path to the folder where the file is kept on your computer

# set the work environment to the workspace folder we defined earlier, and allow overwriting the output
arcpy.env.workspace = folder
arcpy.env.overwriteOutput = True
# Spatial reference set to GCS_WGS_1984 (if your GPS uses something else input it here)
spatial_reference = arcpy.SpatialReference(4326)

# define what file within the workspace folder we want to use (the one with muskrat data)
input_excel_file = "Muskrat Monitoring Data.xlsx"  # if you rename the excel file you'll be able to select it dynamically
master_sheet = "Muskrat Master Spreadsheet"  # if you rename the master sheet, change this to match it
muskrat_table = "Muskrat_Table.dbf"  # this is the new geodatabase table we'll create to hold the excel data
muskrat_shapefile = "Muskrat_Lodge_Map.shp"  # you can rename this here if you'd like

# convert from the master sheet in the muskrat excel file into a geodatabase format ArcMap can read
arcpy.ExcelToTable_conversion(input_excel_file, muskrat_table, master_sheet)

# make an empty shapefile to populate with the data from our table
arcpy.CreateFeatureclass_management(folder, muskrat_shapefile, "POINT")

# list the fields in our geodatabase
fields = arcpy.ListFields(muskrat_table)

# modify the fieldnames list for what fields you're interested in (but they need to match what's in the table)
fieldnames = ['Date', 'Zone', 'Flag_ID_', 'Latitude', 'Longitude', 'Dome_appro', 'Water_Dept', 'Activity_L', 'Type',
              'Dominant_L', 'Dominant_C']

# add fields to our new shapefile
for field in fields:
    if field.name in fieldnames:
        arcpy.AddField_management(muskrat_shapefile, field.name, field.type)

# delete the autogenerated field
arcpy.DeleteField_management(muskrat_shapefile, "Id")

# make a search cursor to loop through lodge records
muskrat_search = arcpy.da.SearchCursor(muskrat_table, fieldnames)

# make an insert cursor to add fields to the new shapefile
muskrat_insert = arcpy.da.InsertCursor(muskrat_shapefile, fieldnames)

# loop through search cursor (table) and add rows to the lodge list
for row in muskrat_search:
    if row[3]:
        newlodge = []
        for i in range(len(fieldnames)):
            newlodge.append(row[i])
        muskrat_insert.insertRow(newlodge)

# delete finished cursors
del row
del muskrat_search
del muskrat_insert

# make an update cursor to change the geometry to point
muskrat_update = arcpy.da.UpdateCursor(muskrat_shapefile, ['Latitude', 'Longitude', 'SHAPE@'])

# project into the coordinate system we defined at the top
arcpy.DefineProjection_management(muskrat_shapefile, spatial_reference)

# loop through the update cursor to turn rows into points using lat and long
for row in muskrat_update:
    if row[0]:
        row[2] = arcpy.Point(row[1], row[0])
        muskrat_update.updateRow(row)

    # delete finished cursors
del muskrat_update
del row
