from cademter_model import *
from cademter_messages import Messages as msg
import uuid
import subprocess
import arcpy
import re


_SUCCESS = 'success'
_NAME = 'name'
_TYPE = 'type'
_FORMAT_MSG = '%s: %s'

STATE = 1

REGIONES_SHP = regiones()
ZONAS_SHP = zonas_geograficas()
CUADRICULAS_17_SHP = cuadriculas_17()
CUADRICULAS_18_SHP = cuadriculas_18()
CUADRICULAS_19_SHP = cuadriculas_19()

# input_folder = get_from_json(DIR_INPUT)
input_folder = arcpy.GetParameterAsText(0)

container = list()

def validate_decorator(func):
    def decorator(dirpath, shape):
        path_shape = os.path.join(dirpath, shape.name + EXTENTION_SHP)
        relative_path = os.path.relpath(path_shape, os.path.dirname(input_folder))
        validation = msg.VALIDATE_SHP_MSG + shape.name

        if not os.path.exists(path_shape):
            create_row_html(validation, 0, _FORMAT_MSG % (relative_path, msg.ERROR_SHP_NOT_EXIST_MSG))
        else:
            create_row_html(validation, 1, _FORMAT_MSG % (relative_path, _SUCCESS))
            func(path_shape, shape)

    return decorator

def create_row_html(validation, state, reason=_SUCCESS):
    global container
    global STATE
    if not state:
        STATE = 0
    state = "success" if state else "danger"
    template = '<tr><td>%s</td><td class="table-%s"></td><td class="text-%s">%s</td></tr>'
    response = template % (validation, state, state, reason)
    container.append(response)

@validate_decorator
def validate_shapefiles(path_shape, shape):
    validation = msg.VALIDATE_FIELDS_MSG + shape.name
    desc = arcpy.Describe(path_shape)
    fields_shape = {i.name.lower(): {_NAME: i.name, _TYPE: i.type} for i in desc.fields}
    fields_model = {k: v.to_dict for k, v in shape.__dict__.items()}
    for k, v in fields_model.items():
        item = fields_shape.get(k)
        if not item:
            create_row_html(validation, 0, _FORMAT_MSG % (k.upper(), msg.ERROR_FIELD_NO_EXISTS_MSG))
            continue
        try:
            assert item[_NAME].lower() == v[_NAME].lower(), msg.ERROR_FIELD_NAME_NO_EXISTS_MSG
            assert item[_TYPE].lower() == v[_TYPE].lower(), msg.ERROR_FIELD_TYPE_NO_EXISTS_MSG
            create_row_html(validation, 1, _FORMAT_MSG % (k.upper(), _SUCCESS))
        except Exception as e:
            create_row_html(validation, 0, _FORMAT_MSG % (k.upper(), e.message.__str__()))

def get_structure(path):
    tree = os.path.join(SCRATCH_DIR, uuid.uuid4().hex + EXTENTION_TXT)
    subprocess.call('tree /f /a %s > %s' % (path, tree), shell=True)


    response = open(tree, "r").read()
    # patron = r"n.{0,3}mero"
    # reemplazo = "numero"
    # response = re.sub(patron, reemplazo, response)

    return response

def open_html_template():
    tag = '${content}'
    tag_structure_standar = '${structure_standar}'
    # tag_structure_valued = '${structure_evaluated}'

    path = os.path.join(SCRATCH_DIR, uuid.uuid4().hex + EXTENTION_HTML)
    rows = ''.join(container)
    txt = open(REPORT_CHECK_STRUCTURE_HTML).read()
    txt = txt.replace(tag, rows)

    structure_standar = get_structure(STRUCTURE_DIR)
    # structure_valuated = str()
    # if os.path.exists(input_folder):
    #     structure_valuated = get_structure(input_folder)

    txt = txt.replace(tag_structure_standar, structure_standar)
    # txt = txt.replace(tag_structure_valued, structure_valuated)

    with open(path, 'w') as f:
        f.write(txt)
        f.close()
    del f
    os.startfile(path)
    arcpy.SetParameter(1, STATE)


if __name__ == '__main__':
    # verify existence of main directories
    try:
        assert input_folder, msg.ERROR_NOT_SPECIFIED_MSG
        assert os.path.exists(input_folder), msg.ERROR_DIR_NOT_EXIST_MSG
        create_row_html(msg.VALIDATE_INPUT_DIR_MSG, 1)
    except Exception as e:
        create_row_html(msg.VALIDATE_INPUT_DIR_MSG, 0, e.message.__str__())
        open_html_template()

    # verify existence directory psad56
    try:
        path_psad = os.path.join(input_folder, FOLDER_PSAD)
        assert os.path.exists(path_psad), msg.ERROR_DIR_NOT_EXIST_MSG
        create_row_html(msg.VALIDATE_DIR_PSAD_MSG, 1)

        # Validate shapefiles
        validate_shapefiles(path_psad, REGIONES_SHP)
        validate_shapefiles(path_psad, ZONAS_SHP)

        validate_shapefiles(path_psad, CUADRICULAS_17_SHP)
        validate_shapefiles(path_psad, CUADRICULAS_18_SHP)
        validate_shapefiles(path_psad, CUADRICULAS_19_SHP)

    except Exception as e:
        create_row_html(msg.VALIDATE_DIR_PSAD_MSG, 0, e.message.__str__())

    # verify existence directory wgs84
    try:
        path_wgs = os.path.join(input_folder, FOLDER_WGS)
        assert os.path.exists(path_wgs), msg.ERROR_DIR_NOT_EXIST_MSG
        create_row_html(msg.VALIDATE_DIR_WGS_MSG, 1)

        # Validate shapefiles
        validate_shapefiles(path_wgs, REGIONES_SHP)
        validate_shapefiles(path_wgs, ZONAS_SHP)

        validate_shapefiles(path_wgs, CUADRICULAS_17_SHP)
        validate_shapefiles(path_wgs, CUADRICULAS_18_SHP)
        validate_shapefiles(path_wgs, CUADRICULAS_19_SHP)

    except Exception as e:
        create_row_html(msg.VALIDATE_DIR_WGS_MSG, 0, e.message.__str__())

    open_html_template()