import arcpy
import os
import csv

def readSDE(path):
    arcpy.env.workspace = path
    csvfile.writerow(["The current file Geodatabase is " + path])

    featureclass = arcpy.ListFeatureClasses()
    print(featureclass)
    raster = arcpy.ListRasters()
    print(raster)
    tables = arcpy.ListTables()
    print(tables)

    csvfile.writerow([""])
    csvfile.writerow(["The Feature Classes in " + path + " are listed below"])
    for fc in featureclass:
        desc = arcpy.Describe(fc)
        try:
            csvfile.writerow(
                [desc.name, "Feature Class", arcpy.env.workspace + "\\" + fc, desc.featureType + " " + desc.shapeType,
                 desc.spatialreference.name, arcpy.GetCount_management(fc)])
        except:
            print(fc + " did not seem to be able to be opened")
            continue

    csvfile.writerow([""])
    csvfile.writerow(["The Rasters in " + path + " are listed below"])
    for ras in raster:

        try:
            desc = arcpy.Describe(ras)
            csvfile.writerow([desc.name, desc.format, arcpy.env.workspace + "\\" + ras, desc.compressionType,
                              desc.spatialreference.name])
        except:
            print(ras + " did not seem to be able to be opened")
            continue

    csvfile.writerow([""])
    csvfile.writerow(["The tables in " + path + " are listed below"])
    for table in tables:
        desc = arcpy.Describe(table)
        try:
            csvfile.writerow([desc.name, "Table"])
        except:
            print (table + " Did not seem to be able to be opened")

    csvfile.writerow([""])
    csvfile.writerow([""])



file = open("C:\\Users\\hstgeorge\\Desktop\\testsde.csv",'w')
csvfile = csv.writer(file,csv.excel,lineterminator = '\n')


startpath = r'C:\Users\hstgeorge\AppData\Roaming\ESRI\Desktop10.6\ArcCatalog\Connection to LEA-304752 (2).sde'
arcpy.env.workspace = startpath


file.flush()
readSDE(startpath)
file.close()