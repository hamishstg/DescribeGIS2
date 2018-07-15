import arcpy
import csv
import os


class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Toolbox"
        self.alias = ""

        # List of tool classes associated with this toolbox
        self.tools = [DescribeGIS]


class DescribeGIS(object):
    
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "DescribeGIS"
        self.description = "A Tool to report on all GIS data that is located in a folder or SDE."
        self.canRunInBackground = False
        

    def getParameterInfo(self):

        param0 = arcpy.Parameter(
            displayName="Input Path",
            name="startpath",
            datatype="GPString",
            parameterType="Required",
            direction="Input")

        param1 = arcpy.Parameter(
            displayName="Output File",
            name="output_path",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        
        params = [param0,param1]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return


    def execute(self, parameters, messages):
        startpath = parameters[0].valueAsText
        outfile = parameters[1].valueAsText
        
        
        split = outfile.split("\\")
        splitpath = ""
        split[len(split) - 1] = "flat" + split[len(split)-1]
        for line in split:
            splitpath = splitpath + line + "\\"
        splitpath = splitpath[:-1]
        
        flatfile = open(splitpath,'w')
        file = open(outfile,'w')
        flatcsv = csv.writer(flatfile,csv.excel,lineterminator = '\n')
        csvfile = csv.writer(file,csv.excel,lineterminator = '\n')
        
        listing = main(csvfile,startpath,file,flatfile,flatcsv)
        
        arcpy.env.workspace = startpath

        flatfile.flush()
        file.flush()
        listing.listfolder(startpath)
        flatfile.close()
        file.close()


        return
    
    
    
class main():
    def __init__(self,csvfile,path,file,flatfile,flatcsv):
        self.csvfile = csvfile
        self.path = path
        self.file = file
        self.flatfile = flatfile
        self.flatcsv = flatcsv
    
    def listfolder(self,path):
        arcpy.env.workspace = path
        self.csvfile.writerow(["the Current workpath is " + path])
        self.csvfile.writerow([""])

        featureclass = arcpy.ListFeatureClasses()
        raster = arcpy.ListRasters()
        cadlist = arcpy.ListDatasets("*.dwg")
        workspace = arcpy.ListWorkspaces()
        mxd = arcpy.ListFiles("*.mxd")
    
    
        self.csvfile.writerow(["The shapefiles in this folder are Listed Below:"])
        for fc in featureclass:
            desc = arcpy.Describe(fc)
            try:
                self.csvfile.writerow([desc.name,"Shapefile",arcpy.env.workspace + "\\" + fc,desc.featureType + " " + desc.shapeType,desc.spatialreference.name,arcpy.GetCount_management(fc)])
                self.flatcsv.writerow([desc.name,"Shapefile",arcpy.env.workspace + "\\" + fc,desc.featureType + " " + desc.shapeType,desc.spatialreference.name,arcpy.GetCount_management(fc)])
                
            except:
                print(fc + " Did not seem to be able to be opened")
                continue

        self.csvfile.writerow([""])
        self.csvfile.writerow(["The CAD datasets within this folder are listed below:"])
        for cad in cadlist:
            try:
                desc = arcpy.Describe(cad)
                self.csvfile.writerow([desc.name,"CAD File",arcpy.env.workspace + "\\" + cad,desc.spatialreference.name])
                self.flatcsv.writerow([desc.name,"CAD File",arcpy.env.workspace + "\\" + cad,desc.spatialreference.name])
            except:
                print("Could not open cad data")
                continue



        self.csvfile.writerow([""])
        self.csvfile.writerow(["The rasters within this folder are listed below:"])
    
        for ras in raster:
            try:
                desc = arcpy.Describe(ras)
                self.csvfile.writerow([desc.name,desc.format,arcpy.env.workspace + "\\" + ras,desc.compressionType,desc.spatialreference.name])
                self.flatcsv.writerow([desc.name,desc.format,arcpy.env.workspace + "\\" + ras,desc.compressionType,desc.spatialreference.name])
            except:
                print (ras + " did not seem to be able to be opened")
                continue


        for maps in mxd:
            mxd = arcpy.mapping.MapDocument(arcpy.env.workspace + "\\" + maps)
            self.csvfile.writerow(["The Projections for " + maps + " dataframes are listed below"])
            for df in arcpy.mapping.ListDataFrames(mxd):
                self.csvfile.writerow([df.name, df.spatialReference.name])
                self.flatcsv.writerow([df.name, df.spatialReference.name])

            self.csvfile.writerow(["A list of the layers in " + maps])
            for lyr in arcpy.mapping.ListLayers(mxd):
                if lyr.supports("DATASOURCE"):
                    self.csvfile.writerow([lyr.datasetName,lyr.dataSource])
                    self.flatcsv.writerow([lyr.datasetName,lyr.dataSource])

        self.csvfile.writerow([""])
        self.csvfile.writerow([""])
        for work in workspace:
            print(work)
            if work.endswith(".gdb"):
                #print(work)
				self.listgeodatabase(work)
				#call list file geodatabase function
            elif os.path.isdir(work):
				#print(work)
				self.listfolder(work)

        self.file.flush()
        self.flatfile.flush()
    
    def listgeodatabase(self,path):
        arcpy.env.workspace = path
        self.csvfile.writerow(["The current file Geodatabase is " + path])
    
        featureclass = arcpy.ListFeatureClasses()
        raster = arcpy.ListRasters()
        tables = arcpy.ListTables()

        self.csvfile.writerow([""])
        self.csvfile.writerow(["The Feature Classes in " + path + " are listed below"])
        for fc in featureclass:
            desc = arcpy.Describe(fc)
            try:
                self.csvfile.writerow([desc.name,"Feature Class",arcpy.env.workspace + "\\" + fc,desc.featureType + " " + desc.shapeType,desc.spatialreference.name,arcpy.GetCount_management(fc)])
                self.flatcsv.writerow([desc.name,"Feature Class",arcpy.env.workspace + "\\" + fc,desc.featureType + " " + desc.shapeType,desc.spatialreference.name,arcpy.GetCount_management(fc)])
            except:
                print(fc + " did not seem to be able to be opened")
                continue

        self.csvfile.writerow([""])
        self.csvfile.writerow(["The Rasters in " + path + " are listed below"])
        for ras in raster:
        
            try:
                desc = arcpy.Describe(ras)
                self.csvfile.writerow([desc.name,desc.format,arcpy.env.workspace + "\\" + ras,desc.compressionType,desc.spatialreference.name])
                self.flatcsv.writerow([desc.name,desc.format,arcpy.env.workspace + "\\" + ras,desc.compressionType,desc.spatialreference.name])
            except:
                print(ras + " did not seem to be able to be opened")
                continue

        self.csvfile.writerow([""])
        self.csvfile.writerow(["The tables in " + path + " are listed below"])
    
        for table in tables:
            desc = arcpy.Describe(table)
            try:
                self.csvfile.writerow([desc.name,"Table"])
                self.flatcsv.writerow([desc.name,"Table"])
            except:
                print (table + " Did not seem to be able to be opened")


        self.csvfile.writerow([""])
        self.csvfile.writerow([""])
        
        self.file.flush()
        self.flatfile.flush()
