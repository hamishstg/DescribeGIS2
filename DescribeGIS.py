import arcpy
import os
import csv
import sys

def listgeodatabase(path):
    return ""


def listfolder(path):
    arcpy.env.workspace = path

    featureclass = arcpy.ListFeatureClasses()
    raster = arcpy.ListRasters()
    workspace = arcpy.ListWorkspaces()
    mxd = arcpy.ListFiles("*.mxd")

    csvfile.writerow(["hello world"])

    for fc in featureclass:
        desc = arcpy.Describe(fc)
        print ("there was a feature class")
        csvfile.writerow(["feature class goes here"])

    for ras in raster:
        desc = arcpy.Describe(ras)
        print ("there was a raster")
        csvfile.writerow(["raster data goes here"])

    for maps in mxd:
        desc = arcpy.Describe(maps)
        csvfile.writerow(["maps data will go here"])
        #need to do some other stuff before printing

    for work in workspace:
        if work.endswith(".gdb"):
            print(work + " is a file geodatabase will run function")
            #call list file geodatabase function
        elif os.path.isdir(work):
            print(work + " Is a folder will call again to run recursively")
            #make recursive call to funtion to start again :)
    file.flush()




file = open("C:\\Users\\Hamish St George\\Desktop\\test.csv",'w')
csvfile = csv.writer(file,delimiter = ',')

startpath = r'C:\Users\Hamish St George\Documents\ArcGIS\Projects\MyProject'
file.flush()
listfolder(startpath)
file.close()

