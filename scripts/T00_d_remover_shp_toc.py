import traceback
import os
import arcpy

if __name__ == '__main__':
    namepy = os.path.basename(__file__)
    message = 'success'
    try:
        layer_name = arcpy.GetParameterAsText(0)
        layer_name = layer_name.split('.')[0]

        # mxd = arcpy.mapping.MapDocument('CURRENT')
        # for df in arcpy.mapping.ListDataFrames(mxd):
        #     for lyr in arcpy.mapping.ListLayers(mxd, layer_name, df):
        #         arcpy.mapping.RemoveLayer(df, lyr)
        
        project = arcpy.mp.ArcGISProject("CURRENT")
        map = project.activeMap
        layersborrar = map.listLayers(layer_name)
        for lyr in layersborrar:
            map.removeLayer(lyr)

    except:
        message = traceback.print_exc().__str__()
    finally:
        arcpy.SetParameterAsText(1, message)
