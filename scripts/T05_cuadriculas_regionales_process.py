import subprocess
import os
import arcpy

_PROCESS = os.path.join(os.path.dirname(__file__), 'cuadriculas_regionales.py')

datums = arcpy.GetParameterAsText(0)
cores = arcpy.GetParameterAsText(1)

# datums = 'WGS84'
# cores = 5


if __name__ == '__main__':
    p1 = subprocess.Popen(r"C:\Users\jyupanqui\AppData\Local\ESRI\conda\envs\arcgispro-py3-clone\python.exe %s %s %s" % (_PROCESS, datums, cores))
    p1.wait()