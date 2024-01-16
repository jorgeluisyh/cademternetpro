import os 
import json
import arcpy

SCRIPTS_DIR = os.path.dirname(__file__)
PROJECT_DIR = os.path.dirname(SCRIPTS_DIR)
STATICS_DIR = os.path.join(PROJECT_DIR, 'statics')
ABOUT_FORM = os.path.join(STATICS_DIR, 'forms\\presentacion_cademter.exe')
LOADER_FORM = os.path.join(STATICS_DIR, 'forms\\loader_cademter.exe')
REPORT_CHECK_STRUCTURE_HTML = os.path.join(STATICS_DIR, 'reports\\report_check_structure.html')
STRUCTURE_DIR = os.path.join(STATICS_DIR, 'structure')
FILE_GDB = os.path.join(STATICS_DIR, 'insumos.gdb')
REQUIREMENTS_DIR = os.path.join(STATICS_DIR, 'requirements')
SCRATCH_DIR = arcpy.env.scratchFolder
# @Enviroment variables
SET_ENV_DIRS = 'SET_ENVIROMENT_DIRS_CADEMTER'

# @Extentions
EXTENTION_SHP = '.shp'
EXTENTION_TXT = '.txt'
EXTENTION_HTML = '.html'
EXTENTION_LOG = '.log'
EXTENTION_CSV = '.csv'
EXTENTION_PNG = '.png'

# @Name folder datum
FOLDER_PSAD = 'psad56'
FOLDER_WGS = 'wgs84'

EPSG_PSAD = 24860
EPSG_WGS = 32700


config_json = os.path.join(STATICS_DIR, 'config.json')

# variables estaticas
DIR_INPUT = 'dir_input'
NAME_MAR = 'name_mar'
CODE_MAR = 'code_mar'
NAME_FRONTERA = 'name_frontera'
CODE_FRONTERA = 'code_frontera'
DIR_OUTPUT = 'dir_output'
DIR_TEMP = 'dir_temp'
NAME_DIR = 'name_dir'


# file = open(config_json, 'r')

def write_on_json(key, value):
    f = open(config_json, 'r')
    diccionary=json.load(f)
    if key in diccionary.keys():
        diccionary[key]=value
    else:
        print(u"No se encontró la clave")
    f.close()
    f = open(config_json, 'w')
    json.dump(diccionary, f)
    f.close()

def get_from_json(key):
    f = open(config_json, 'r')
    diccionary = json.load(f)
    response = diccionary.get(key)    
    f.close()
    return response

def get_path_tmp():
    path = os.path.join(get_from_json(DIR_TEMP) , f'preparacion_insumos_{get_from_json(NAME_DIR)}' )
    return path

# @Suplies (insumos)
class Suplies(object):
    sea = 'mar'
    countries = 'paises'
    region = 'region'
    regions = 'regiones'
    quads = 'cuadrantes'


