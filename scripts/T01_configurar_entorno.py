from T00_config import *
from cademter_messages import Messages as msg
import os
import arcpy
import sys
import uuid

sys.path.append(SCRIPTS_DIR)

if __name__ == '__main__':
    namepy = os.path.basename(__file__)
    dir_input = arcpy.GetParameterAsText(0)
    name_mar = arcpy.GetParameterAsText(1)
    code_mar = arcpy.GetParameterAsText(2)
    name_frontera = arcpy.GetParameterAsText(3)
    code_frontera = arcpy.GetParameterAsText(4)
    dir_output = arcpy.GetParameterAsText(5)
    dir_temp = arcpy.GetParameterAsText(6)

    try:
        write_on_json(DIR_INPUT, dir_input)
        write_on_json(NAME_MAR, name_mar)
        write_on_json(CODE_MAR, code_mar)
        write_on_json(NAME_FRONTERA, name_frontera)
        write_on_json(CODE_FRONTERA, code_frontera)
        write_on_json(DIR_OUTPUT, dir_output)
        write_on_json(DIR_TEMP, dir_temp)
        write_on_json(NAME_DIR, uuid.uuid4().hex)
        arcpy.AddMessage(msg.LOAD_SUCCESS_FOLDER_MSG)
        os.environ[SET_ENV_DIRS] = ''
    except Exception as e:
        arcpy.AddError(e.message.__str__())
