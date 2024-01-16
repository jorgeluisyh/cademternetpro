
from cademter_model import *
import uuid


class Validation:
    def __init__(self, datum):
        self.datum = datum.lower()
        self._input_dir = get_from_json(DIR_INPUT)
        self._output_dir = get_from_json(DIR_OUTPUT)
        self._region = regiones()
        self._region_path = os.path.join(self._input_dir, datum.lower(), self._region.name + EXTENTION_SHP)
        self.reg = None
        self._regiones_adyacentes = list()
        self._zones = range(17, 20)
        # self.g_insumos = GeneradorInsumos()

    def get_region_en_memoria(self):
        """
        Metodo que permite la generacion del feature layer de regiones del Peru
        :return:
        """
        _name = 'regiones'
        query = "%s NOT IN ('%s', '%s')" % (self._region.nm_depa.name, get_from_json(NAME_MAR), get_from_json(NAME_FRONTERA))
        response = arcpy.MakeFeatureLayer_management(self._region_path, _name, query)
        return response

    def get_regiones(self):
        """
        Metodo que permite obtener las regiones como una lista, donde cada region esta representada por su
        nombre y geometria
        :return:
        """
        # @get_relacion_adyacencia_entre_regiones
        self.reg = self.get_region_en_memoria()
        response = [m for m in arcpy.da.SearchCursor(self.reg, ["SHAPE@", self._region.nm_depa.name])]
        return response

    def get_relacion_adyacencia_entre_regiones(self):
        """
        Obtener la relacion de adyacencia necesaria entre regiones
        1. Obtiene la lista que contiene la geometria y el nombre de cada region ['SHAPE@', NM_DEPA] array_regiones,
           se le asigna a self.reg el feature layer del feature class regiones (esto se hace en la funcion
           self.get_regiones()
        2. Itera el array_regiones.
        3. Se realiza la seleccion por ubicacion para determinar las regiones adyacentes a la region evaluada
        4. Se iteran las regiones seleccionadas teniendo en cuenta el nombre de la region
        5. Se genera un item de tipo lista que contiene los nombres de las regiones evaluadas y se ordenan de forma
           ascendente
        6. Se verifica que este item no existe en el atributo self._regiones_adyacentes y a su vez que no se evalue
        entre la misma region
        7. Agrega el item al atributo
        :return: 
        """
        array_regiones = self.get_regiones()
        for i in array_regiones:
            arcpy.SelectLayerByLocation_management(self.reg, "INTERSECT", i[0], "#", "NEW_SELECTION")
            for n in arcpy.da.SearchCursor(self.reg, [self._region.nm_depa.name]):
                item = sorted([i[1], n[0]])
                if item not in self._regiones_adyacentes and n[0] != i[1]:
                    self._regiones_adyacentes.append(item)
            arcpy.SelectLayerByAttribute_management(self.reg, 'CLEAR_SELECTION')
        
        # Se agrega esto para poder evaluar en ambos sentidos
        lista_reversa = [[x[1],x[0]]for x in self._regiones_adyacentes]
        self._regiones_adyacentes = self._regiones_adyacentes + lista_reversa

    def realizar_validacion(self):
        """
        Ejecutar Validacion
        :return:
        """
        
        for i in self._regiones_adyacentes:
            arcpy.AddMessage('  Evaluacion entre: %s' % ' - '.join(i))
            for zone in self._zones:
                # quitamos el espacio entre nombres
                namecapa_0 = i[0].replace(' ','') 
                namecapa_1 = i[1].replace(' ','') 
                cuadriculas_ini = os.path.join(self._output_dir, self.datum, namecapa_0 + str(zone) + EXTENTION_SHP)
                cuadriculas_fin = os.path.join(self._output_dir, self.datum, namecapa_1 + str(zone) + EXTENTION_SHP)
                controller = map(os.path.exists, [cuadriculas_ini, cuadriculas_fin])
                if controller == [True] * 2:
                    self.procesamiento(path_ini=cuadriculas_ini, path_fin=cuadriculas_fin, array=i, zone=zone)

    def get_geometria_region_by_zona(self, region_name, zona):
        """
        1. Determina el codigo EPSG para la zona segun el sistema de referencia
        2. Genera el objeto que define el sistema de referencia
        3. Construye el filtro para la seleccion de la region a utilizar
        4. Obtiene la geometria de la region mediante un SearchCursor
        :param region_name:
        :param zona:
        :return:
        """
        epsg = EPSG_WGS if self.datum == FOLDER_WGS else EPSG_PSAD
        src = arcpy.SpatialReference(epsg + zona)
        query = "%s = '%s'" % (self._region.nm_depa.name, region_name)
        response = [x[0] for x in arcpy.da.SearchCursor(self._region_path, ["SHAPE@"], query, src)][0]
        return response

    def procesamiento(self, **kwargs):
        """
        Ejecuta el proceso para la identificacion y correcion de posibles errores.
        Los parametros aceptados son:
            path_ini: Ruta de los cuadrantes de la region a
            paths_fin: Ruta de los cuadrantes de la region b
            array: Lista de nombres de ambas regiones
            zone: Zona geografica (17, 18, 19)
        :param kwargs: {path_ini, paths_fin, array, zone}
        :return:
        """
        # Feature layer de las cuadriculas de cada region a evaluar
        flayer_ini = arcpy.MakeFeatureLayer_management(kwargs['path_ini'], uuid.uuid4().hex)
        flayer_fin = arcpy.MakeFeatureLayer_management(kwargs['path_fin'], uuid.uuid4().hex)

        # Identificar las cuadriculas identicas entre los dos feature layer de cuadriculas regiones
        arcpy.SelectLayerByLocation_management(flayer_ini, "ARE_IDENTICAL_TO", flayer_fin, "#", "NEW_SELECTION")
        arcpy.AddMessage(kwargs['path_ini'])
        arcpy.AddMessage("nro de registros : {}".format(str(arcpy.GetCount_management(flayer_ini)[0])))
        # Se obtiene la geometria (geom) de las regiones inicial
        region_ini = self.get_geometria_region_by_zona(kwargs['array'][0], kwargs['zone'])
        region_fin = self.get_geometria_region_by_zona(kwargs['array'][1], kwargs['zone'])

        # Esta operacion realiza la asignacion correcta entre los cuadrantes identicos de las
        # las regiones evaluadas, por tanto es necesario determinar el area de mayor incidencia del cuadrante sobre 
        # las regiones
        with arcpy.da.UpdateCursor(flayer_ini, ["SHAPE@", "OID@","CD_CUAD"]) as cursorUC:
            for row in cursorUC:
                geom = row[0]
                intsc = geom.intersect(region_ini, 4)
                fintsc = geom.intersect(region_fin, 4)
                # Si se cumple esta condicion, quiere decir que el cuadrante esta asignado incorrectamente a 
                # la region, por tanto debe ser eliminado
                # if row[2] == '25-I_429':
                #     arcpy.AddMessage(intsc.area)
                #     arcpy.AddMessage(geom.area)
                #     arcpy.AddMessage(intsc.area/ geom.area)
                if intsc.area < fintsc.area:
                    arcpy.AddMessage('\t Se detecto una inconsistencia en el registro %s' % row[1])
                    # Eliminando el registro
                    cursorUC.deleteRow()
                    arcpy.AddMessage('\t Corregido!')
        # Eliminando el cursor
        del cursorUC
       


        arcpy.SelectLayerByAttribute_management(flayer_ini, "CLEAR_SELECTION")

        # Como ya se ha corregido la primera region en lineas ateriores se vuelve a identificar los cuadrantes
        # identicos restantes entre las regiones. Por defecto si aun persisten cuadrantes identicos esto quiere
        # decir que no le corresponden a la segunda region.
        arcpy.SelectLayerByLocation_management(flayer_fin, "ARE_IDENTICAL_TO", flayer_ini, "#", "NEW_SELECTION")

        # Eliminando las coincidencias encontradas
        arcpy.DeleteRows_management(flayer_fin)

        arcpy.SelectLayerByAttribute_management(flayer_fin, "CLEAR_SELECTION")

    def main(self):
        """
        Metodo principal que ejecuta el procesamiento
        :return:
        """
        self.get_relacion_adyacencia_entre_regiones()
        self.realizar_validacion()


if __name__ == '__main__':
    datums = arcpy.GetParameterAsText(0).split(';')
    for i in datums:
        arcpy.AddMessage(' DATUM: %s' % i)
        poo = Validation(i)
        poo.main()
