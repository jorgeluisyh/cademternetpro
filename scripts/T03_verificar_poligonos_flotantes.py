from cademter_model import *
import uuid

arcpy.env.overwriteOutput = True

_COD_FUERA_PERU = get_from_json(CODE_FRONTERA)
_NAME_MAR = get_from_json(NAME_MAR)
_NAME_FRONTERA = get_from_json(NAME_FRONTERA)
_OUTPUT = 'in_memory\errores_poligonos_flotantes'
_CLAUSE = "%s = '%s' AND %s = '%s'"

REGIONES_SHP = regiones()

input_folder = get_from_json(DIR_INPUT)

def check_invalid_geometries(area, datum):
    """

    :param area:
    :return:
    """
    datum = int(datum)
    name = uuid.uuid4().hex + EXTENTION_SHP
    mfl = arcpy.MakeFeatureLayer_management(path_regiones, name)
    mts = arcpy.MultipartToSinglepart_management(mfl)
    mts_copy = arcpy.CopyFeatures_management(mts, os.path.join(SCRATCH_DIR, 'mts_copy'))
    mts_mfl = arcpy.MakeFeatureLayer_management(mts_copy, name)
    rows = ", ".join(
        [str(i[0]) for i in arcpy.da.SearchCursor(mts_mfl, ["OID@", "SHAPE@AREA"], None, arcpy.SpatialReference(datum))
         if i[1] <= float(area) * 10000])
    if rows == "":
        return
    sql = "FID IN (%s)" % rows
    arcpy.SelectLayerByAttribute_management(mts_mfl, "NEW_SELECTION", sql)
    response = arcpy.MinimumBoundingGeometry_management(mts_mfl, _OUTPUT, 'ENVELOPE')
    arcpy.SelectLayerByAttribute_management(mts_mfl, "CLEAR_SELECTION")
    return response

def get_fronteras(name):
    """

    :param name:
    :return:
    """
    query = _CLAUSE % (REGIONES_SHP.cd_depa.name, _COD_FUERA_PERU, REGIONES_SHP.nm_depa.name, name)
    response = arcpy.MakeFeatureLayer_management(path_regiones, name, query)
    return response


if __name__ == '__main__':
    try:
        param = arcpy.GetParameterAsText(0)
        datum = arcpy.GetParameterAsText(1)
        epsg = 24878 if datum == 'PSAD56' else 32718
        print(epsg)
        path_regiones = os.path.join(input_folder, datum.lower(), REGIONES_SHP.name + EXTENTION_SHP)
        mar = get_fronteras(_NAME_MAR)
        frontera = get_fronteras(_NAME_FRONTERA)
        errors = check_invalid_geometries(param, epsg)
        arcpy.SetParameterAsText(2, frontera)
        arcpy.SetParameterAsText(3, mar)
        arcpy.SetParameterAsText(4, path_regiones)
        if errors:
            arcpy.SetParameterAsText(5, errors)
    except Exception as e:
        arcpy.AddError('Error: %s' % e.message.__str__())