from cademter_messages import *
from T00_config import *

if __name__ == '__main__':
    response = dict()
    response['status'] = 1
    response['message'] = 'success'
    msg = Messages()
    try:
        folder = arcpy.GetParameterAsText(0)
        folder = str(folder).replace(' ', '')
        arcpy.env.workspace = folder
        shapefiles = arcpy.ListFeatureClasses()
        shapefiles = [i for i in os.listdir(folder) if i.lower().endswith(".shp")]
        if len(shapefiles) == 0:
            raise RuntimeError(msg.LIST_SHAPEFILES_ERROR_LEN)
        respuesta = ','.join(shapefiles)
        response["response"] = respuesta
    except Exception as e:
        response['status'] = 0
        response['message'] = e.message
    finally:
        response = json.dumps(response, ensure_ascii=False).encode('windows-1252')
        arcpy.SetParameterAsText(1, response)