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
        
        flatfile = open(splitpath + ".csv",'w')
        file = open(outfile + ".md",'w')
        flatcsv = csv.writer(flatfile,csv.excel,lineterminator = '\n')
        
        listing = main(file,startpath,flatfile,flatcsv)
        
        arcpy.env.workspace = startpath

        flatfile.flush()
        file.flush()
        listing.listfolder(startpath)
        flatfile.close()
        file.close()


        return
    
    
    
class main():
    def __init__(self,file,path,flatfile,flatcsv):
        self.file = file
        self.path = path
        self.flatfile = flatfile
        self.flatcsv = flatcsv
    
    def listfolder(self,path):
        arcpy.env.workspace = path
        self.file.write("the Current workpath is: " + path + "\n")

        featureclass = arcpy.ListFeatureClasses()
        raster = arcpy.ListRasters()
        cadlist = arcpy.ListDatasets("*.dwg")
        workspace = arcpy.ListWorkspaces()
        mxd = arcpy.ListFiles("*.mxd")
    
    
        self.file.write("The shapefiles in this folder are Listed Below:\n\n")
        for fc in featureclass:
            desc = arcpy.Describe(fc)
            try:
                self.file.write("| " + desc.name + " | " + "Shapefile" + " | " + arcpy.env.workspace + "\\" + fc,desc.featureType + " " + desc.shapeType + " | " + desc.spatialreference.name + " | " + arcpy.GetCount_management(fc)+ " |  \n")
                self.flatcsv.writerow([desc.name,"Shapefile",arcpy.env.workspace + "\\" + fc,desc.featureType + " " + desc.shapeType,desc.spatialreference.name,arcpy.GetCount_management(fc)])
                
            except:
                print(fc + " Did not seem to be able to be opened")
                continue

        self.file.write("")
        self.file.write("The CAD datasets within this folder are listed below:\n\n")
        for cad in cadlist:
            try:
                desc = arcpy.Describe(cad)
                self.file.write("| " + desc.name + " | " + "CAD File" + " | " + arcpy.env.workspace + "\\" + cad + " | " + desc.spatialreference.name + " |  \n")
                self.flatcsv.writerow([desc.name,"CAD File",arcpy.env.workspace + "\\" + cad,"",desc.spatialreference.name])
            except:
                print("Could not open cad data")
                continue



        self.file.write("")
        self.file.write("The rasters within this folder are listed below:\n\n")
    
        for ras in raster:
            try:
                desc = arcpy.Describe(ras)
                self.file.write(" | " + desc.name + " | " + desc.format,arcpy.env.workspace + "\\" + ras,desc.compressionType + " | " + desc.spatialreference.name + " |  \n")
                self.flatcsv.writerow([desc.name,desc.format,arcpy.env.workspace + "\\" + ras,desc.compressionType,desc.spatialreference.name])
            except:
                print (ras + " did not seem to be able to be opened")
                continue


        for maps in mxd:
            mxd = arcpy.mapping.MapDocument(arcpy.env.workspace + "\\" + maps)
            self.file.write("The Projections for " + maps + " dataframes are listed below\n\n")
            for df in arcpy.mapping.ListDataFrames(mxd):
                self.file.write(" | " + df.name + " | " + "Maps" + " | " + arcpy.env.workspace + "\\" + maps + " | " + "" + " | " + df.spatialReference.name + " |  \n")
                self.flatcsv.writerow([df.name,"Maps",arcpy.emv.workspace + "\\" + maps,"",df.spatialReference.name])

            self.file.write("A list of the layers in " + maps + "\n\n")
            for lyr in arcpy.mapping.ListLayers(mxd):
                if lyr.supports("DATASOURCE"):
                    self.file.write(" | " + lyr.datasetName + " | " + lyr.dataSource)
                    self.flatcsv.writerow([lyr.datasetName,lyr.dataSource])

        self.file.write("")
        self.file.write("")
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
        self.file.write("The current file Geodatabase is " + path + "\n")
    
        featureclass = arcpy.ListFeatureClasses()
        raster = arcpy.ListRasters()
        tables = arcpy.ListTables()
        relclass = [c.name for c in arcpy.Describe(path).children if c.datatype == "RelationshipClass"]
        
        topologies = []
        gdb_objects = arcpy.ListDatasets(wild_card=None, feature_type='Feature')
        print "Feature datasets are: " + str(gdb_objects) #only feature datasets are here
        for obj in gdb_objects:
            fd_path = os.path.join(path,obj)
            arcpy.env.workspace = fd_path #get a new workspace pointed to the fd
            fd_objects = arcpy.ListDatasets(wild_card=None, feature_type='')

            for dataset in fd_objects: #iterate feature dataset objects
                desc_dataset = arcpy.Describe(dataset)
                if desc_dataset.datasetType == 'Topology': #finding out whether is topology
                    topologies.append(desc_dataset)
        

        self.file.write("")
        self.file.write("The Feature Classes in " + path + " are listed below\n\n")
        for fc in featureclass:
            desc = arcpy.Describe(fc)
            try:
                self.file.write("| " + desc.name + " | " + "Feature Class" + " | " + arcpy.env.workspace + "\\" + fc,desc.featureType + " " + desc.shapeType + " | " + desc.spatialreference.name + " | " + arcpy.GetCount_management(fc)+ " | \n")
                self.flatcsv.writerow([desc.name,"Feature Class",arcpy.env.workspace + "\\" + fc,desc.featureType + " " + desc.shapeType,desc.spatialreference.name,arcpy.GetCount_management(fc)])
            except:
                print(fc + " did not seem to be able to be opened")
                continue

        self.file.write("")
        self.file.write("The Rasters in " + path + " are listed below\n\n")
        for ras in raster:
        
            try:
                desc = arcpy.Describe(ras)
                self.file.write(" | " + desc.name + " | " + desc.format,arcpy.env.workspace + "\\" + ras,desc.compressionType + " | " + desc.spatialreference.name + " | \n")
                self.flatcsv.writerow([desc.name,desc.format,arcpy.env.workspace + "\\" + ras,desc.compressionType,desc.spatialreference.name])
            except:
                print(ras + " did not seem to be able to be opened")
                continue

        self.file.write("")
        self.file.write("The tables in " + path + " are listed below\n\n")
        for table in tables:
            desc = arcpy.Describe(table)
            try:
                self.file.write(" | " + desc.name + " | " + "Table" + " | " + arcpy.env.workspace + table + " | \n")
                self.flatcsv.writerow([desc.name,"Table",arcpy.env.workspace + table])
            except:
                print (table + " Did not seem to be able to be opened")

        self.file.write("")
        self.file.write("The relationships in " + path + " are listed below\n\n")
        for rel in relclass:
            desc = arcpy.Describe(rel)
            try:
                self.file.write(" | " + desc.name + " | " + "Relationship" + " | " + arcpy.env.workspace + "\\" + rel + " | \n")
                self.flatcsv.writerow([desc.name,"Relationship",arcpy.env.workspace + "\\" + rel])
            except:
                print(rel + " Looks like it could not be opened")
                continue
                
        self.file.write("") 
        self.file.write("The topologies in " + path + " are listed below")
        for top in topologies:
            desc = arcpy.Describe(top)
            try:
                self.file.write(" | " + desc.name + " | " + desc.featureClassNames + " | \n")
                self.flatcsv.writerow([desc.name,desc.featureClassNames])
            except:
                print(top + " does not seem like it could be opened")

        self.file.write("")
        self.file.write("")
        
        self.file.flush()
        self.flatfile.flush()
