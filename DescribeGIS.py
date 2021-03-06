import arcpy
import os
import csv
import sys

def listgeodatabase(path):

    arcpy.env.workspace = path
    csvfile.writerow(["The current file Geodatabase is " + path])

    featureclass = arcpy.ListFeatureClasses()
    raster = arcpy.ListRasters()
    tables = arcpy.ListTables()


    print len(featureclass)
    csvfile.writerow([""])
    csvfile.writerow(["The Feature Classes in " + path + " are listed below"])
    for fc in featureclass:
        desc = arcpy.Describe(fc)
        try:
            csvfile.writerow([desc.name,"Feature Class",arcpy.env.workspace + "\\" + fc,desc.featureType + " " + desc.shapeType,desc.spatialreference.name,arcpy.GetCount_management(fc)])
        except:
            print(fc + " did not seem to be able to be opened")
            continue

    csvfile.writerow([""])
    csvfile.writerow(["The Rasters in " + path + " are listed below"])
    for ras in raster:

        try:
            desc = arcpy.Describe(ras)
            csvfile.writerow([desc.name,desc.format,arcpy.env.workspace + "\\" + ras,desc.compressionType,desc.spatialreference.name])
        except:
            print(ras + " did not seem to be able to be opened")
            continue

    csvfile.writerow([""])
    csvfile.writerow(["The tables in " + path + " are listed below"])
    for table in tables:
        desc = arcpy.Describe(table)
        try:
            csvfile.writerow([desc.name,"Table"])
        except:
            print (table + " Did not seem to be able to be opened")


    csvfile.writerow([""])
    csvfile.writerow([""])



def listfolder(path):
    arcpy.env.workspace = path


    featureclass = arcpy.ListFeatureClasses()
    raster = arcpy.ListRasters()
    workspace = arcpy.ListWorkspaces()
    mxd = arcpy.ListFiles("*.mxd")

    featureclass = arcpy.ListFeatureClasses()
    raster = arcpy.ListRasters()
    cadlist = arcpy.ListDatasets("*.dwg")
    workspace = arcpy.ListWorkspaces()
    mxd = arcpy.ListFiles("*.mxd")

    print(len(featureclass))
    csvfile.writerow(["The shapefiles in this folder are Listed Below:"])
    for fc in featureclass:
        desc = arcpy.Describe(fc)
        try:
            csvfile.writerow([desc.name,"Shapefile",arcpy.env.workspace + "\\" + fc,desc.featureType + " " + desc.shapeType,desc.spatialreference.name,arcpy.GetCount_management(fc)])
        except:
            print(fc + " Did not seem to be able to be opened")
            continue

    csvfile.writerow([""])
    csvfile.writerow(["The CAD datasets within this folder are listed below:"])
    print(len(cadlist))
    for cad in cadlist:
        try:
            desc = arcpy.Describe(cad)
            csvfile.writerow([desc.name,"CAD File",arcpy.env.workspace + "\\" + cad,desc.spatialreference.name])
        except:
            print("Could not open cad data")
            continue



    csvfile.writerow([""])
    csvfile.writerow(["The rasters within this folder are listed below:"])
    for ras in raster:
        try:
            desc = arcpy.Describe(ras)
            csvfile.writerow([desc.name,desc.format,arcpy.env.workspace + "\\" + ras,desc.compressionType,desc.spatialreference.name])
        except:
            print (ras + " did not seem to be able to be opened")
            continue


    for maps in mxd:
        mxd = arcpy.mapping.MapDocument(arcpy.env.workspace + "\\" + maps)
        csvfile.writerow(["The Projections for " + maps + " dataframes are listed below"])
        for df in arcpy.mapping.ListDataFrames(mxd):
            csvfile.writerow([df.name, df.spatialReference.name])

        csvfile.writerow(["A list of the layers in " + maps])
        for lyr in arcpy.mapping.ListLayers(mxd):
            if lyr.supports("DATASOURCE"):
                csvfile.writerow([lyr.datasetName,lyr.dataSource])
        csvfile.writerow([""])

    csvfile.writerow([""])
    csvfile.writerow([""])
    for work in workspace:
        print(work)
        if work.endswith(".gdb"):
            #print(work)
            listgeodatabase(work)
            #call list file geodatabase function
        elif os.path.isdir(work):
            #print(work)
            listfolder(work)

    file.flush()






file = open("C:\Users\hstgeorge\Desktop\\test.csv",'w')
csvfile = csv.writer(file,csv.excel,lineterminator = '\n')


startpath = r'D:\Data for testing'
arcpy.env.workspace = startpath


file.flush()
listfolder(startpath)
file.close()

