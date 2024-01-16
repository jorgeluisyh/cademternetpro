# -*- coding: utf-8 -*-

"""
Proceso que permite determinar los limites regionales
en funcion de los cuadrantes de 1km.
"""
from __future__ import print_function
import multiprocessing
from cademter_model import *
import sys
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as dt
import warnings
import traceback
import shutil
import uuid

# Desactiva advertencia de errores futuros
warnings.simplefilter(action='ignore', category=FutureWarning)


def clear_selection(feature_layer):
    arcpy.SelectLayerByAttribute_management(feature_layer, "CLEAR_SELECTION")


def get_cuadriculas_regionales(*args):
    """
    Permite determinar las cuadriculas regionales a un 90%
    :param args:
    :return:
    """
    arcpy.env.overwriteOutput = True
    from datetime import datetime, timedelta
    start = datetime.now()
    response = dict()
    response['label'] = os.path.basename(args[0])
    response['start'] = start.__str__()

    print(' ', response['label'])

    _ADMINISTRATION_PERCENTAGE = 0.5
    _SEARCH_DISTANCE = '10 METERS'
    _INTERCECT_DISTANCE = 4
    _FID_FIELD = 'FID'
    _foo = Suplies()
    _region = regiones()
    _DATUM = os.path.basename(os.path.dirname(args[0]))
    _OUTPUT_DIR = get_from_json(DIR_OUTPUT)
    _OUTPUT_SHP = os.path.join(_OUTPUT_DIR, _DATUM, os.path.basename(args[0]) + EXTENTION_SHP)

    cuadriculas_externas = list()

    # if arcpy.Exists(_OUTPUT_SHP):
    #     arcpy.Delete_management(_OUTPUT_SHP)

    # Ubicacion de archivos shapefile
    cuadriculas_path = os.path.join(args[0], _foo.quads + EXTENTION_SHP)
    marperuano_path = os.path.join(args[0], _foo.sea + EXTENTION_SHP)
    region_path = os.path.join(args[0], _foo.region + EXTENTION_SHP)
    cregiones_path = os.path.join(args[0], _foo.regions + EXTENTION_SHP)

    # FeatureLayers de shapefiles
    cuadriculas_mfl = arcpy.MakeFeatureLayer_management(cuadriculas_path, uuid.uuid4().hex)
    region_mfl = arcpy.MakeFeatureLayer_management(region_path, uuid.uuid4().hex)
    regiones_mfl = arcpy.MakeFeatureLayer_management(cregiones_path, uuid.uuid4().hex)

    # Obteniendo la geometria del FeatureLayer de region
    region_geom = [k[0] for k in arcpy.da.SearchCursor(region_mfl, ['SHAPE@'])][0]

    # Obteniendo el nombre de la region
    region_name = [k[0] for k in arcpy.da.SearchCursor(region_mfl, [_region.nm_depa.name])][0]

    # Obteniendo las cuadriculas que se intersectan con el mar como una lista
    arcpy.SelectLayerByLocation_management(cuadriculas_mfl, 'INTERSECT', marperuano_path, "#", 'NEW_SELECTION')
    cuadriculas_mar = [k[0] for k in arcpy.da.SearchCursor(cuadriculas_mfl, ['OID@'])]
    clear_selection(cuadriculas_mfl)

    # Obteniendo las cuadriculas que se cruzan unicamente con el borde de la region
    arcpy.SelectLayerByLocation_management(cuadriculas_mfl, 'CROSSED_BY_THE_OUTLINE_OF', region_mfl, "#",
                                           'NEW_SELECTION')

    for row in arcpy.da.SearchCursor(cuadriculas_mfl, ['SHAPE@', 'OID@']):
        if row[1] not in cuadriculas_mar:
            intersection = region_geom.intersect(row[0], _INTERCECT_DISTANCE)
            if intersection.area <= row[0].area * _ADMINISTRATION_PERCENTAGE:
                arcpy.SelectLayerByLocation_management(regiones_mfl, 'INTERSECT', row[0], _SEARCH_DISTANCE,
                                                       'NEW_SELECTION')
                if int(arcpy.GetCount_management(regiones_mfl).__str__()) > 2:
                    area, value = int(), str()
                    for k in arcpy.da.SearchCursor(regiones_mfl, ['SHAPE@', _region.nm_depa.name]):
                        region_intersection = k[0].intersect(row[0], _INTERCECT_DISTANCE).area
                        if region_intersection > area:
                            area, value = region_intersection, k[1]
                    if value != region_name:
                        cuadriculas_externas.append(str(row[1]))
                else:
                    cuadriculas_externas.append(str(row[1]))

    clear_selection(regiones_mfl)

    if len(cuadriculas_externas) > 0:
        query = "%s IN (%s)" % (_FID_FIELD, ", ".join(cuadriculas_externas))
        with arcpy.da.UpdateCursor(cuadriculas_path, ['OID@'], query) as cur:
            for row in cur:
                cur.deleteRow()
            del cur
        clear_selection(cuadriculas_mfl)

    arcpy.CopyFeatures_management(cuadriculas_path, _OUTPUT_SHP)

    response['end'] = datetime.now().__str__()
    time = datetime.now() - start
    response['time'] = str(timedelta(seconds=time.total_seconds()))
    return response


def filelog(*args):
    """
    Genera el archivo log de errores
    :param args: cadenas de errores generados
    :return: Despliega los errores en pantalla
    """
    pathfile = os.path.join(SCRATCH_DIR, uuid.uuid4().hex + EXTENTION_LOG)
    with open(pathfile, 'w') as f:
        f.write('Sucedio un error: \n')
        for k in args:
            f.write(k + '\n')
        f.close()
    del f
    os.startfile(pathfile)


def generar_grafico(response, datum):
    """
    Genera el grafico de seguimiento de procesamiento; construye un pandas.DataFrame a partir
    de una lista de diccionarios
    :param response: Lista de diccionarios con informacion de tiempos
    :return: Despliega el grafico en pantalla
    """
    _COLOR_VLINES = '#919190'
    _COLOR_HLINES = '#5959ff'
    _COLOR_SCATTER = '#5959ff'
    _LINESTYLE_VLINES = '--'
    _MARKER_SCATTER = 'o'

    pathgraph = os.path.join(SCRATCH_DIR, uuid.uuid4().hex + EXTENTION_PNG)
    df = pd.DataFrame(response)
    df.start = pd.to_datetime(df.start)
    df.end = pd.to_datetime(df.end)

    fig, ax = plt.subplots()

    plt.grid()

    yvaluesmin = list()
    yvaluesmax = list()
    xvalues = list()
    for i, v in df.iterrows():
        dato = df[df['start'] == v['end']]
        count = dato.shape[0]
        if count:
            yvaluesmin.append(i)
            yvaluesmax.append(dato.index.values[0])
            xvalues.append(dato.start.values[0])

    ax.vlines(x=xvalues, ymin=yvaluesmin, ymax=yvaluesmax, linestyle=_LINESTYLE_VLINES, color=_COLOR_VLINES)
    ax.hlines(y=[i for i, v in df.iterrows()], xmin=dt.date2num(df.start), xmax=dt.date2num(df.end), linewidth=2,
              color=_COLOR_HLINES)

    plt.yticks([i[0] for i in df.iterrows()], df.label.tolist())
    plt.scatter(df.end.tolist(), [i[0] for i in df.iterrows()], color=_COLOR_SCATTER, marker=_MARKER_SCATTER)

    for i, value in enumerate(df.time.tolist()):
        plt.text(df.end.tolist()[i], [k for k, v in df.iterrows()][i] + 0.2, value)

    plt.xlabel(msg.TITLE_AXIS_X_GRAPH)
    plt.ylabel(msg.TITLE_AXIS_Y_GRAPH)
    plt.title('%s - %s' % (msg.TITLE_GRAPH, datum.upper()), fontsize=16)
    fig.set_size_inches((35, 20), forward=False)
    fig.savefig(pathgraph, bbox_inches='tight')

    os.startfile(pathgraph)


def main(*args):
    """
    Funcion que permite realizar el multiprocesamiento
    :param args: el primer parametro esta referido a la cantidad de procesos
    en paralelo a ejecutar; el segundo parametro contiene la informacion a procesar
    :return: Genera un grafico del procesamiento y despliega automaticamente
    """
    p = multiprocessing.Pool(args[0])
    response = p.map(get_cuadriculas_regionales, args[1])
    p.close()
    p.join()
    generar_grafico(response, args[2])

def obtener_tamano_directorio(carpeta):
    total_tamano = 0
    for ruta, directorios, archivos in os.walk(carpeta):
        for archivo in archivos:
            ruta_completa = os.path.join(ruta, archivo)
            total_tamano += os.path.getsize(ruta_completa)
    return total_tamano


if __name__ == '__main__':
    try:
        datums = sys.argv[1].split(';')
        cores = int(sys.argv[2])
        work_dir = get_path_tmp()
        output_dir = get_from_json(DIR_OUTPUT)
        for datum in datums:
            print('DATUM: %s' % datum)
            path = os.path.join(output_dir, datum)
            if os.path.exists(path):
                shutil.rmtree(path)
            os.mkdir(path)
            datum_dir = os.path.join(work_dir, datum)
            folders = [os.path.join(datum_dir, i) for i in os.listdir(datum_dir)]
            elementos_con_tamanio = []

            # Recorre los elementos y obtén sus tamaños
            for elemento in folders:
                tamanio = obtener_tamano_directorio(elemento)
                elementos_con_tamanio.append((elemento, tamanio))

            # Ordena la lista de elementos por tamaño en orden ascendente
            sorted_folders = [x[0] for x in sorted(elementos_con_tamanio, key=lambda x: x[1] , reverse=True)]

            main(cores, sorted_folders, datum)
    except Exception as e:
        filelog(traceback.format_exc().__str__())
