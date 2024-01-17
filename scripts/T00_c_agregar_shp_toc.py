import traceback
import os
import arcpy

if __name__ == '__main__':
    namepy = os.path.basename(__file__)
    state, message, response = 0, str(), str()
    try:
        response = arcpy.GetParameterAsText(0)
    except:
        message = traceback.print_exc().__str__()
    finally:
        arcpy.SetParameterAsText(1, response)

