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
        
        if (outfile.endswith(".csv")):
            file = open(outfile,'w')
            csvfile = csv.writer(file,csv.excel,lineterminator = '\n')
        elif "." not in outfile:
            arcpy.AddMessage("hello")
            file = open(outfile + ".csv",'w')
            csvfile = csv.writer(file,csv.excel,lineterminator = '\n')
        else:
            raise ValueError('Please enter an output path that ends with .csv or the filename')
        
        listing = main(file,startpath,csvfile)
        
        arcpy.env.workspace = startpath
        
        file.flush()
        if (startpath.endswith(".sde")):
            listing.listgeodatabase(startpath)
        else:
            listing.listfolder(startpath)
        file.close()


        return
    
    
    
class main():
    def __init__(self,file,path,flatcsv):
        self.file = file
        self.path = path
        self.flatcsv = flatcsv
    
    def listfolder(self,path):
        arcpy.env.workspace = path

        featureclass = arcpy.ListFeatureClasses()
        raster = arcpy.ListRasters()
        cadlist = arcpy.ListDatasets("*.dwg")
        workspace = arcpy.ListWorkspaces()
        mxd = arcpy.ListFiles("*.mxd")
        
        for fc in featureclass:
            try:
                desc = arcpy.Describe(fc)
                self.flatcsv.writerow([desc.name,"Shapefile",arcpy.env.workspace + "\\" + fc,desc.featureType + " " + desc.shapeType,desc.spatialreference.name,arcpy.GetCount_management(fc)])  
            except:
                arcpy.AddMessage(fc + " Did not seem to be able to be opened")
                continue

        for cad in cadlist:
            try:
                desc = arcpy.Describe(cad)
                self.flatcsv.writerow([desc.name,"CAD File",arcpy.env.workspace + "\\" + cad,"",desc.spatialreference.name])
            except:
                print("Could not open cad data")
                continue


        for ras in raster:
            try:
                desc = arcpy.Describe(ras)
                self.flatcsv.writerow([desc.name,desc.format,arcpy.env.workspace + "\\" + ras,desc.compressionType,desc.spatialreference.name])
            except:
                arcpy.AddMessage(ras + " did not seem to be able to be opened")
                continue


        for maps in mxd:
            mxd = arcpy.mapping.MapDocument(arcpy.env.workspace + "\\" + maps)
            for df in arcpy.mapping.ListDataFrames(mxd):
                self.flatcsv.writerow([df.name,"Maps",arcpy.emv.workspace + "\\" + maps,"",df.spatialReference.name])

            for lyr in arcpy.mapping.ListLayers(mxd):
                if lyr.supports("DATASOURCE"):
                    self.flatcsv.writerow([lyr.datasetName,lyr.dataSource])

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
    
    def listgeodatabase(self,path):
        arcpy.env.workspace = path
    
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
        

        for fc in featureclass:
            try:
                desc = arcpy.Describe(fc)
                self.flatcsv.writerow([desc.name,"Feature Class",arcpy.env.workspace + "\\" + fc,desc.featureType + " " + desc.shapeType,desc.spatialreference.name,arcpy.GetCount_management(fc)])
            except:
                print(fc + " did not seem to be able to be opened")
                continue

        for ras in raster:
        
            try:
                desc = arcpy.Describe(ras)
                self.flatcsv.writerow([desc.name,desc.format,arcpy.env.workspace + "\\" + ras,desc.compressionType,desc.spatialreference.name])
            except:
                print(ras + " did not seem to be able to be opened")
                continue

        for table in tables:
    
            try:
                desc = arcpy.Describe(table)
                self.flatcsv.writerow([desc.name,"Table",arcpy.env.workspace + table])
            except:
                print (table + " Did not seem to be able to be opened")

        for rel in relclass:
            try:
                desc = arcpy.Describe(rel)
                self.flatcsv.writerow([desc.name,"Relationship",arcpy.env.workspace + "\\" + rel])
            except:
                print(rel + " Looks like it could not be opened")
                continue
                
        for top in topologies:
            desc = arcpy.Describe(top)
            try:
                self.flatcsv.writerow([desc.name,desc.featureClassNames])
            except:
                print(top + " does not seem like it could be opened")
        
        self.file.flush()