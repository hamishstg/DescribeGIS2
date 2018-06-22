import arcpy
import os
import csv
import sys

def listgeodatabase(path):
    arcpy.env.workspace = path

    featureclass = arcpy.ListFeatureClasses()
    raster = arcpy.ListRasters()

    for fc in featureclass:
        desc = arcpy.Describe(fc)
        try:
            csvfile.writerow([desc.name,"Feature Class",arcpy.env.workspace + "\\" + fc,desc.featureType + " " + desc.shapeType,desc.spatialreference.name,arcpy.GetCount_management(fc)])
        except:
            print(fc + " did not seem to be able to be opened")
            continue

    for ras in raster:
        desc = arcpy.Describe(ras)
        try:
            csvfile.writerow([desc.name,desc.format,arcpy.env.workspace + "\\" + ras,desc.compressionType,desc.spatialreference.name])
        except:
            print(ras + " did not seem to be able to be opened")
            continue


def listfolder(path):
    arcpy.env.workspace = path

    featureclass = arcpy.ListFeatureClasses()
    raster = arcpy.ListRasters()
    workspace = arcpy.ListWorkspaces()
    mxd = arcpy.ListFiles("*.mxd")

    for fc in featureclass:

        desc = arcpy.Describe(fc)
        try:
            csvfile.writerow([desc.name,"Shapefile",arcpy.env.workspace + "\\" + fc,desc.featureType + " " + desc.shapeType,desc.spatialreference.name,arcpy.GetCount_management(fc)])
        except:
            print(fc + " Did not seem to be able to be opened")
            continue

    for ras in raster:
        try:
            desc = arcpy.Describe(ras)
            csvfile.writerow([desc.name,desc.format,arcpy.env.workspace + "\\" + ras,desc.compressionType,desc.spatialreference.name])
        except:
            print (ras + " did not seem to be able to be opened")
            continue


    for maps in mxd:
        desc = arcpy.Describe(maps)
        csvfile.writerow(["maps data will go here"])
        listgeodatabase(work)

    for work in workspace:
        if work.endswith(".gdb"):
            print(work)
            listgeodatabase(work)
            #call list file geodatabase function
        elif os.path.isdir(work):
            print(work)
            listfolder(work)
    file.flush()



import csv
file = open("C:\\Users\\hstgeorge\\Desktop\\test.csv",'w')
csvfile = csv.writer(file,csv.excel,lineterminator = '\n')

startpath = r'D:\Data for testing'
file.flush()
listfolder(startpath)
file.close()

