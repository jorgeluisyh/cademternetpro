using System;
using System.Collections.Generic;
using System.Linq;
using System.Runtime.CompilerServices;
using System.Text;
using System.Threading.Tasks;

namespace cademternetPro
{
    class General
    {
        //Metadata
        public static string __title__ = "Cademternet Pro 2024";
        public static string __author__ = "Jorge Luis Yupanqui Herrera";
        public static string __copyright__ = "INGEMMET";
        public static string __credits__ = "Jorge Yupanqui H.";
        public static string __version__ = "1.0";
        public static string __maintainer = "Jorge Yupanqui H.";
        public static string __mail__ = "jyupanqui@ingemmet.gob.pe";
        public static string __status__ = "Development";

        // Variables globales estáticas
        public static string _path = __file__();
        public static string _scripts_path = _path + @"\scripts";

        static string message_runtime_error = "¡Ocurrió un error inesperado!" + Environment.NewLine + "Por favor, contacte al administrador del sistema.";


        public static string __file__()
        {
            //string codeBase = System.Reflection.Assembly.GetExecutingAssembly().CodeBase;
            string codeBase = System.Reflection.Assembly.GetExecutingAssembly().Location;
            UriBuilder uriBuilder = new UriBuilder(codeBase);
            string path = Uri.UnescapeDataString(uriBuilder.Path);
            return System.IO.Path.GetDirectoryName(path);
        }

    }
}
