import arcpy
import os

class Toolbox(object):
    def __init__(self):
        self.label = "BulkProcessing"
        self.alias = "BulkProcessing"
        self.tools = [DissolveToRepair, mergeSimilarLayers]

class DissolveToRepair(object):
    def __init__(self):
        self.label = "Dissolve to Repair"
        self.description = "Performs a pairwise dissolve on an input layer then performs both methods of Repair Geometry (ESRI and OGC)"
        self.canRunInBackground = False

    def getParameterInfo(self):
        input_layer = arcpy.Parameter(
            name="input_layer",
            displayName="Input Layer",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input"
        )
        
        output_geodatabase = arcpy.Parameter(
            name="output_geodatabase",
            displayName="Output Geodatabase",
            datatype="DEWorkspace",
            parameterType="Required",
            direction="Input"
        )
        
        parameters = [input_layer, output_geodatabase]
        return parameters

    def isLicensed(self):
        return True

    def updateParameters(self, parameters):
        return

    def updateMessages(self, parameters):
        return

    def execute(self, parameters, messages):

        # Set the outputMFlag environment to Disabled
        arcpy.env.outputMFlag = "Disabled"

        # Set the outputZFlag environment to Disabled
        arcpy.env.outputZFlag = "Disabled"

        input_layer = parameters[0].valueAsText
        output_geodatabase = parameters[1].valueAsText

        # Generate output feature class in the output geodatabase
        output_name = os.path.splitext(os.path.basename(input_layer))[0].lower()
        output_featureclass = os.path.join(output_geodatabase, output_name)

        arcpy.analysis.PairwiseDissolve(input_layer, output_featureclass)
        arcpy.AddMessage("Pairwise dissolve completed successfully on code {}".format(input_layer.upper()))

        # Repair geometry using Esri method
        arcpy.management.RepairGeometry(output_featureclass, "DELETE_NULL", "ESRI")
        arcpy.AddMessage("Geometry repaired using the Esri method.")

        # Repair geometry using OGC method
        arcpy.management.RepairGeometry(output_featureclass, "DELETE_NULL", "OGC")
        arcpy.AddMessage("Geometry repaired using the OGC method.")

class mergeSimilarLayers(object):
    def __init__(self):
        self.label = 'Merge Similar Layers'
        self.alias = 'Merge Similar Layers'
        self.canRunInBackground = False

    def getParameterInfo(self):
        output_geodatabase = arcpy.Parameter(
            name='output_geodatabase',
            displayName='Output Geodatabase',
            datatype="DEWorkspace",
            parameterType="Required",
            direction="Input"
        )
        
        input_layers = arcpy.Parameter(
            name='input_layers',
            displayName='Input Layers',
            datatype='GPFeatureLayer',
            parameterType='Required',
            direction='Input',
            multiValue=True
        )

        parameters = [output_geodatabase, input_layers]
        return parameters

    def execute(self, parameters, messages):
        output_geodatabase = parameters[0].valueAsText
        input_layers = parameters[1].values  # Get the list of input layers

        layers_dict = {}

        for layer in input_layers:
            fc = layer.name
            if fc.lower().startswith('code_'):
                fc_lower = fc.lower()[5:]  # Remove 'code_' prefix
            else:
                fc_lower = fc.lower()

            if fc_lower in layers_dict:
                layers_dict[fc_lower].append(fc)
            else:
                layers_dict[fc_lower] = [fc]

        for name, layers in layers_dict.items():
            if len(layers) >= 2:
                outfc = f"{output_geodatabase}/{name}"
                arcpy.Merge_management(layers, outfc)



