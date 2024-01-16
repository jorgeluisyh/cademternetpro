from T00_config import *
from cademter_messages import Messages as msg
class column(object):
    def __init__(self, **kwargs):
        self.name = kwargs.get('name')
        self.type = kwargs.get('type')

    @property
    def to_dict(self):
        return self.__dict__


class FeatureDatasets(object):
    def __init__(self, zone=None, datum=None):
        self.zone = zone
        self.datum = datum

    @property
    def name(self):
        return 'insumos_{}_{}'.format(self.zone, self.datum)

    @property
    def path(self):
        return os.path.join(FILE_GDB, self.name)


class tb_cademter_control(object):
    def __init__(self):
        self.usuario = column(name='USUARIO')
        self.mac = column(name='MAC')
        self.path = column(name='PATH')
        self.path_input = column(name='PATH_INPUT')
        self.path_output = column(name='PATH_OUTPUT')
        self.path_tmp = column(name='PATH_TMP')
        self.name_dir = column(name='NAME_DIR')
        self.cod_mar = column(name='COD_MAR')
        self.name_mar = column(name='NAME_MAR')
        self.cod_front = column(name='COD_FRONT')
        self.name_front = column(name='NAME_FRONT')

    @property
    def name(self):
        return 'DAGU1883.TB_CADEMTER_CONTROL'

    def __str__(self):
        return self.name


class regiones(object):
    def __init__(self):
        # self.pc_depa = column(name='PC_DEPA', type='String')
        self.cd_depa = column(name='CD_DEPA', type='String')
        self.nm_depa = column(name='NM_DEPA', type='String')
        self.cap_depa = column(name='CAP_DEPA', type='String')

    @property
    def name(self):
        return self.__class__.__name__

    def __str__(self):
        return self.name


class zonas_geograficas(object):
    def __init__(self):
        self.zona = column(name='ZONA', type='Integer')

    @property
    def name(self):
        return self.__class__.__name__

    def __str__(self):
        return self.name


class cuadriculas_17(object):
    def __init__(self):
        self.cd_cuad = column(name='CD_CUAD', type='String')
        self.zona = column(name='ZONA', type='String')
        self.norte_min = column(name='NORTE_MIN', type='Double')
        self.norte_max = column(name='NORTE_MAX', type='Double')
        self.este_min = column(name='ESTE_MIN', type='Double')
        self.este_max = column(name='ESTE_MAX', type='Double')
        self.has = column(name='HAS', type='Double')

    @property
    def name(self):
        return self.__class__.__name__

    def __str__(self):
        return self.name


class cuadriculas_18(cuadriculas_17):
    def __init__(self):
        super(self.__class__, self).__init__()


class cuadriculas_19(cuadriculas_17):
    def __init__(self):
        super(self.__class__, self).__init__()


class distritos(object):
    def __init__(self):
        self.cd_dist = column(name='CD_DIST', type='String')
        self.zona = int()
        self.datum = str()

    @property
    def name(self):
        return 'dist{}c'.format(self.zona)

    @property
    def path(self):
        return os.path.join(get_from_json(DIR_INPUT), self.datum, self.name + EXTENTION_SHP)
