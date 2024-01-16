# -*- coding: utf-8 -*-

from cademter_model import *
import cademter_model as model
from shutil import rmtree
import uuid

arcpy.env.overwriteOutput = True


class GeneradorInsumos(object):
    datums = arcpy.GetParameterAsText(0).split(';')
    new_folder = True if arcpy.GetParameterAsText(1) == 'true' else None
    if new_folder:
        write_on_json(NAME_DIR, uuid.uuid4().hex)
    _input_dir = get_from_json(DIR_INPUT)
    _model_region = regiones()
    _path_region = None
    _path_region_fc = None
    _model_zona_geografica = zonas_geograficas()
    _path_zona_geografica = None
    _dataset = FeatureDatasets()
    _work_dir = str()
    _datum_dir = str()
    _zones = range(17, 20)
    _cod_mar = get_from_json(CODE_MAR)
    _cod_frontera = get_from_json(CODE_FRONTERA)
    _name_mar = get_from_json(NAME_MAR)
    _name_frontera = get_from_json(NAME_FRONTERA)
    arcpy.AddMessage(dir(model))
    _insumos = Suplies()

    def agrupar_regiones_por_zona(self, datum):
        """
        Exporta el grupo de regiones que comparten la misma zona
        :return:
        """
        assert os.path.exists(self._path_zona_geografica), 'Can not find the specified file'

        _query = "%s not in ('%s', '%s')" % (self._model_region.nm_depa.name, self._name_frontera, self._name_mar)

        feature_layer_region = arcpy.MakeFeatureLayer_management(self._path_region, self._model_region.name, _query)

        # Verificar que las capas de zona geografica tengan el valor de zona en su tabla de atributos
        array = arcpy.da.SearchCursor(self._path_zona_geografica,
                                      ["SHAPE@", self._model_zona_geografica.zona.name])
        for i in array:
            self._dataset.zone = i[1]
            self._dataset.datum = datum
            path = os.path.join(self._dataset.path, self._model_region.name + datum + str(i[1]))
            oid = [str(m[0]) for m in
                   arcpy.da.SearchCursor(feature_layer_region, [self._model_region.cd_depa.name, 'SHAPE@']) if
                   m[1].overlaps(i[0]) or i[0].contains(m[1])]
            sql = "%s IN ('%s')" % (self._model_region.cd_depa.name, "', '".join(oid))
            arcpy.AddMessage('-------')
            arcpy.AddMessage(sql)
            arcpy.AddMessage(self._path_region)
            arcpy.AddMessage(path)
            arcpy.AddMessage('-*-*-*-*')
            flayer_filter = arcpy.MakeFeatureLayer_management(feature_layer_region, uuid.uuid4().hex[:8], sql)
            arcpy.CopyFeatures_management(flayer_filter, path)

    def crear_directorio_trabajo(self, datum):
        """
        Eliminando todos los archivos existentes dentro del directorio
        temporal, con el fin de evitar cualquier cruce de informacion.
        :return:
        """
        self._work_dir = get_path_tmp()

        if not os.path.exists(self._work_dir):
            os.mkdir(self._work_dir)

        self._datum_dir = os.path.join(self._work_dir, datum)

        if not os.path.exists(self._datum_dir):
            os.mkdir(self._datum_dir)
        else:
            rmtree(self._datum_dir)

        print('Directorio de trabajo %s' % self._work_dir)
        print('se eliminaron temporales')

    def contruir_directorio(self, name, zone):
        """
        Contruir los directorios de trabajo para cada region
        en funcion al nombre y la zona geografica
        :param name:
        :param zone:
        :return:
        """
        # Contruyendo ruta de directorio
        path = os.path.join(self._datum_dir, '%s%s' % (name, zone))
        # Generando el directorio
        os.makedirs(path)
        # Retorno la ubicacion del directorio
        return path

    def generar_feature_layer_region(self, name):
        """
        Funcion que permite obtener el feature layer de una region
        especificada por el parametro 'name' ( type: string )
        :param name:
        :return:
        """
        # Construyendo consulta en base al nombre
        query = "%s = '%s'" % (self._model_region.nm_depa.name, name)

        name = name.replace(" ", '')
        # Generando el feature layer
        res = arcpy.MakeFeatureLayer_management(self._path_region_fc, name, query)
        # Retorno de resultado
        return res

    def generar_feature_layer_cuadrantes(self, zone, datum):
        """
        Generar Fetures layer de los cuadrantes segun
        zona geografica
        :param zone:
        :param datum:
        :return:
        """
        # Instanciando el objeto Quads()
        # * Obteniendo el metodo path
        cuadrante = object()
        if int(zone) == 17:
            cuadrante = cuadriculas_17()
        elif int(zone) == 18:
            cuadrante = cuadriculas_18()
        elif int(zone) == 19:
            cuadrante = cuadriculas_19()

        path_cuadrante = os.path.join(self._input_dir, datum, cuadrante.name + EXTENTION_SHP)
        # Generando el feature layer de cuadrantes
        res = arcpy.MakeFeatureLayer_management(path_cuadrante, cuadrante.name)
        # Retorno de resultado
        return res

    def get_frontera_en_memoria(self, namefront):
        """

        :param namefront:
        :return:
        """
        # Se construye la consulta de la frontera que se necesita
        sql = "%s = '%s'" % (self._model_region.nm_depa.name, namefront)

        # Se genera un nombre unico
        name = 'm%s' % uuid.uuid4().hex

        # Se genera el feature layer de la frontera en funcion a la consulta necesaria
        response = arcpy.MakeFeatureLayer_management(self._path_region, name, sql)
        return response

    def get_frontera(self, namefront, flayer, directorio):
        """

        :param namefront:
        :param flayer:
        :param directorio:
        :return:
        """
        # Se obtiene el nombre del shapefile a exportar
        name = self._insumos.sea if namefront == self._name_mar else self._insumos.countries

        # Se construye la ruta donde se almacenara el archivo shapefile
        path = os.path.join(directorio, name)

        # Genera una copia del feature layer como shapefile en la ubicacion 'path'
        arcpy.CopyFeatures_management(flayer, path)

        return path

    @staticmethod
    def get_src(datum, zona):
        src = EPSG_WGS if datum.lower() == FOLDER_WGS else EPSG_PSAD
        src = src + zona
        return src

    @staticmethod
    def clear_seleccion(flayer):
        """
        Limpiar seleccion de cualquier feature layer
        :param flayer:
        :return:
        """
        arcpy.SelectLayerByAttribute_management(flayer, "CLEAR_SELECTION")

    def generar_insumos(self):
        """
        Funcion que permite generar los insumos necesarios para el
        procesamiento de los limites regionales de forma independiente
        :return:
        """

        for i in self.datums:
            self._path_region = os.path.join(self._input_dir, i.lower(), self._model_region.name + EXTENTION_SHP)
            self._path_zona_geografica = os.path.join(self._input_dir, i.lower(),
                                                      self._model_zona_geografica.name + EXTENTION_SHP)
            frontera = self.get_frontera_en_memoria(self._name_frontera)
            mar = self.get_frontera_en_memoria(self._name_mar)
            arcpy.AddMessage('\n DATUM: %s' % i)
            self.agrupar_regiones_por_zona(i)
            self.crear_directorio_trabajo(i)
            for zone in self._zones:
                self._dataset.zone = zone
                # Se construye la ruta de los feature class que contienen la regiones por zona
                self._path_region_fc = os.path.join(self._dataset.path, self._model_region.name + i + str(zone))
                cuadrante = self.generar_feature_layer_cuadrantes(zone, i)
                for name in arcpy.da.SearchCursor(self._path_region_fc, [self._model_region.nm_depa.name]):
                    arcpy.AddMessage('\tGenerando insumos de {0: <20}{1}'.format(name[0], zone))
                    namedir = name[0].replace(" ", '')
                    # Creando directorio para cada region
                    path = self.contruir_directorio(namedir, zone)
                    feature_layer_region = self.generar_feature_layer_region(name[0])
                    arcpy.SelectLayerByLocation_management(cuadrante, "INTERSECT", feature_layer_region, "#",
                                                           "NEW_SELECTION")

                    arcpy.env.outputCoordinateSystem = arcpy.SpatialReference(self.get_src(i, zone))
                    # Generando copia del litoral peruano
                    self.get_frontera(self._name_mar, mar, path)

                    # Generando copia de los paises fronterisos
                    self.get_frontera(self._name_frontera, frontera, path)

                    path_cuadrantes = os.path.join(path, self._insumos.quads)
                    arcpy.Erase_analysis(cuadrante, frontera, path_cuadrantes)

                    # Limpiando la seleccion
                    self.clear_seleccion(cuadrante)

                    # Generando copia de la region actual
                    arcpy.CopyFeatures_management(feature_layer_region, os.path.join(path, self._insumos.region))

                    # Generando la copia de las regiones ubicadas en la zona especificada
                    arcpy.CopyFeatures_management(self._path_region_fc, os.path.join(path, self._insumos.regions))

    def main(self):
        self.generar_insumos()


# Si se ejecuta el archivo actual
if __name__ == '__main__':
    poo = GeneradorInsumos()
    poo.main()
