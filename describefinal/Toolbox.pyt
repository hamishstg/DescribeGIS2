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
            datatype="DEWorkspace",
            parameterType="Required",
            direction="Input")

        param1 = arcpy.Parameter(
            displayName="Output File",
            name="output_path",
            datatype="DEFile",
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
        # read in parameters
        startpath = parameters[0].valueAsText
        outfile = parameters[1].valueAsText
        
        # Check if the output file is written with .csv in it else throw an error. 
        if (outfile.endswith(".csv")):
            file = open(outfile,'w')
            csvfile = csv.writer(file,csv.excel,lineterminator = '\n')
        elif "." not in outfile:
            file = open(outfile + ".csv",'w')
            csvfile = csv.writer(file,csv.excel,lineterminator = '\n')
        else:
            raise ValueError('Please enter an output path that ends with .csv or the filename')
        
        #create new class for dataa
        listing = main(file,startpath,csvfile)
        
        #set workspace
        arcpy.env.workspace = startpath
        
        #check if path is an sde or if it is a csv run script and then close file
        file.flush()
        if (startpath.endswith(".sde")):
            listing.listgeodatabase(startpath)
        else:
            listing.listfolder(startpath)
        file.close()


        return
    
    
""" This is the main class within this module. Within this class there are two main functions.
listfolders will recursively run through folders and find all raster, shapefiles and CAD data and map documents and print out there
associated data with the main types being name, type, path, spatialreference
listgeodatabase will search within a geodatabase for all rasters, tables, feature classes, reltationship and topologies and print out
there respective values. The main values being name, type, path and spatial reference"""    
class main():
    #pass in all parameters that are needed being the csv file, and starting path to search
    def __init__(self,file,path,flatcsv):
        self.file = file
        self.path = path
        self.flatcsv = flatcsv
    
    #See above in main for description of functions the paramters passed in are the path to be searched. 
    def listfolder(self,path):
        arcpy.env.workspace = path

        #list all available data
        featureclass = arcpy.ListFeatureClasses()
        raster = arcpy.ListRasters()
        cadlist = arcpy.ListDatasets("*.dwg")
        workspace = arcpy.ListWorkspaces()
        mxd = arcpy.ListFiles("*.mxd")
        
        #For each shapefile print the values to the csv
        for fc in featureclass:
            try:
                desc = arcpy.Describe(fc)
                self.flatcsv.writerow([desc.name,"Shapefile",arcpy.env.workspace + "\\" + fc,desc.featureType + " " + desc.shapeType,desc.spatialreference.name,arcpy.GetCount_management(fc)])  
            except:
                arcpy.AddMessage(fc + " Did not seem to be able to be opened")
                continue

        #For each cad dataset print the values to the csv
        for cad in cadlist:
            try:
                desc = arcpy.Describe(cad)
                self.flatcsv.writerow([desc.name,"CAD File",arcpy.env.workspace + "\\" + cad,"",desc.spatialreference.name])
            except:
                arcpy.AddMessage("Could not open cad data")
                continue

        #For each raster in the folder print the values to a csv.        
        for ras in raster:
            try:
                desc = arcpy.Describe(ras)
                self.flatcsv.writerow([desc.name,"Raster",arcpy.env.workspace + "\\" + ras,desc.format,desc.spatialreference.name])
            except:
                arcpy.AddMessage(ras + " did not seem to be able to be opened")
                continue

        #For each mxd within the folder
        for maps in mxd:
            try:
                mxd = arcpy.mapping.MapDocument(arcpy.env.workspace + "\\" + maps)
                #list all dataframes an write there spatial reference to a csv
                for df in arcpy.mapping.ListDataFrames(mxd):
                    try:
                        self.flatcsv.writerow([df.name,"Data frames",arcpy.env.workspace + "\\" + maps,"",df.spatialReference.name])
                    except:
                        continue

                #For each layer in the mxd print to a csv file
                for lyr in arcpy.mapping.ListLayers(mxd):
                    if lyr.supports("DATASOURCE"):
                        try:
                            self.flatcsv.writerow([lyr.datasetName,"Layer",lyr.dataSource])
                        except:
                            arcpy.AddMessage('Broken data link in ' + maps)
                            continue
            except:
                arcpy.message(maps + "did not seem to be able to be opened")
        
        #Recursively search all of the folders in a depth first search check whether to run listgeodatabase or listfolder
        for work in workspace:
            if work.endswith(".gdb"):
                self.listgeodatabase(work)
                
            #call list file geodatabase function
            elif os.path.isdir(work):
                self.listfolder(work)

        self.file.flush()
        
        
    def listfeaturedataset(self,path):
        arcpy.env.workspace = path
        arcpy.AddMessage(path)
        
        featureclass = arcpy.ListFeatureClasses()
        
        for fc in featureclass:
            try:
                desc = arcpy.Describe(fc)
                self.flatcsv.writerow([desc.name,"Feature Class",arcpy.env.workspace + "\\" + fc,desc.featureType + " " + desc.shapeType,desc.spatialreference.name,arcpy.GetCount_management(fc)])  
            except:
                arcpy.AddMessage(fc + " Did not seem to be able to be opened")
                continue
            
        
    # See main class comment for comments the one parameter is the path to the geodatabasse
    def listgeodatabase(self,path):
        arcpy.env.workspace = path
    
        #list all available data
        featureclass = arcpy.ListFeatureClasses()
        raster = arcpy.ListRasters()
        tables = arcpy.ListTables()
        featuredatasets = arcpy.ListDatasets(feature_type = "Feature")
        mosaics = arcpy.ListDatasets(feature_type="Mosaic")
        
            # can print out topologies and relationshipclasses if needed please uncomment this line to do so and lines 246-262
        #relclass = [c.name for c in arcpy.Describe(path).children if c.datatype == "RelationshipClass"]
        #list topoligies will likely be commented out
        #topologies = []
        #gdb_objects = arcpy.ListDatasets(wild_card=None, feature_type='Feature')
        #print "Feature datasets are: " + str(gdb_objects) #only feature datasets are here
        #for obj in gdb_objects:
        #    fd_path = os.path.join(path,obj)
        #    arcpy.env.workspace = fd_path #get a new workspace pointed to the fd
        #    fd_objects = arcpy.ListDatasets(wild_card=None, feature_type='')

        #for dataset in fd_objects: #iterate feature dataset objects
        #        desc_dataset = arcpy.Describe(dataset)
        #        if desc_dataset.datasetType == 'Topology': #finding out whether is topology
        #            topologies.append(desc_dataset)
                    
        
        
        #For each feature class in the geodatabase print the values to a csv
        for fc in featureclass:
            try:
                desc = arcpy.Describe(fc)
                self.flatcsv.writerow([desc.name,"Feature Class",arcpy.env.workspace + "\\" + fc,desc.featureType + " " + desc.shapeType,desc.spatialreference.name,arcpy.GetCount_management(fc)])
            except:
                arcpy.AddMessage(fc + " did not seem to be able to be opened")
                continue
                
        #For each raster in the geodatabse print the values in a csv
        for ras in raster:
            try:
                desc = arcpy.Describe(ras)
                self.flatcsv.writerow([desc.name,"Raster",arcpy.env.workspace + "\\" + ras,desc.format,desc.spatialreference.name])
            except:
                arcpy.AddMessage(ras + " did not seem to be able to be opened")
                continue

        #For each tbale in the geodatabase print the values to a csv 
        for table in tables:
            try:
                desc = arcpy.Describe(table)
                self.flatcsv.writerow([desc.name,"Table",arcpy.env.workspace + "\\" + table])
            except:
                arcpy.AddMessage(table + " Did not seem to be able to be opened")
                continue
                
        for fd in featuredatasets:
            temp = arcpy.env.workspace
            try:
                desc = arcpy.Describe(fd)
                self.flatcsv.writerow([desc.name,"Feature Dataset",arcpy.env.workspace + "\\" + fd,"",desc.spatialreference.name])
                self.listfeaturedataset(os.path.join(arcpy.env.workspace,fd))
                arcpy.env.workspace = temp
            except:
                arcpy.AddMessage(fd + " Did not seem to be able to be opened")
                continue

        for mos in mosaics:
            try:
                desc = arcpy.Describe(mos)
                self.flatcsv.writerow([desc.name,"Mosaic Dataset",arcpy.env.workspace + "\\" + mos,"",desc.spatialreference.name])
            except:
                arcpy.AddMessage(mos + "Did not seem to be able to be opened")
                
        #for each relationship in the geodatabase print the values to a csv
        #for rel in relclass:
        #    try:
        #        desc = arcpy.Describe(rel)
        #        self.flatcsv.writerow([desc.name,"Relationship",arcpy.env.workspace + "\\" + rel])
        #    except:
        #       arcpy.AddMessage(rel + " Looks like it could not be opened")
        #        continue
                
        #For each topolgy in the geodabase print the values to a csv        
        #for top in topologies:
        #    desc = arcpy.Describe(top)
        #    try:
        #        self.flatcsv.writerow([desc.name,desc.featureClassNames])
        #    except:
        #        arcpy.AddMessage(top + " does not seem like it could be opened")
                
        self.file.flush()