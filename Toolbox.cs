using ArcGIS.Core.Internal.CIM;
using ArcGIS.Desktop.Core.Geoprocessing;
using ArcGIS.Desktop.Framework.Dialogs;
using ArcGIS.Desktop.Framework.Threading.Tasks;
using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using static cademternetPro.General;

namespace cademternetPro
{
    class Toolbox
    {
        //1. Variables globales
        // _toolboxPath: Construye la ruta donde se encuentra el archivo *.tbx
        public static string _toolboxPath = _path + @"\scripts\cademter.atbx";

        // Tools GPTools
        public static string _tool_01_configurarentorno = "configurarentorno";
        public static string _tool_02_verificarestructura = "verificarestructura";
        public static string _tool_03_verificarpoligonosflotantes = "verificarpoligonosflotantes";
        public static string _tool_04_tratamientoinsumos = "tratamientoinsumos";
        public static string _tool_05_cuadriculasregionales = "cuadriculasregionales";
        public static string _tool_06_validacioncuadriculas = "validacioncuadriculas";


        //Tools ExecuteGP
        public static string _tool_00_a_habilitarValidator = "habilitarValidator";
        public static string _tool_00_b_listarshapefiles = "listarshapefiles";
        public static string _tool_00_c_agregarshapefiletoc = "agregarshapefiletoc";
        public static string _tool_00_d_removershapefiletoc = "removershapefiletoc";


        public static List<object> parameters = new List<object>();
        public static string GPToolDialog(string tool, bool modal = false, string tbxpath = null)
        {
            string success = "1";
            try
            {
                // Si no se especificó la ruta del tbx
                if (tbxpath == null)
                {
                    tbxpath = _toolboxPath;
                }

                string toolpath = tbxpath + @"\"+tool;
                Geoprocessing.OpenToolDialog(toolpath, null);

            }
            catch (Exception ex)
            {
                MessageBox.Show(ex.Message);
                success = "0";
            }
            return success;

        }

        public static async Task<string> ExecuteGP(string toolName, List<object> parameters, string tbxpath = null, bool getResult = true)
        {
            string response = "";
            try
            {
                // Si no se especificó la ruta del tbx
                if (string.IsNullOrEmpty(tbxpath))
                {
                    tbxpath = _toolboxPath;
                }

                string toolPath = tbxpath + @"\" + toolName;

                // Preparar parámetros para la ejecución
                var args = Geoprocessing.MakeValueArray(parameters.ToArray());

                if (getResult)
                {
                    // Ejecutar la herramienta y obtener resultados
                    var result = await QueuedTask.Run(() => Geoprocessing.ExecuteToolAsync(toolPath, args));
                    response = result.ReturnValue;
                    var responseJson = JsonConvert.DeserializeObject<Dictionary<string, object>>(response);
                    if (responseJson["status"].ToString() == "0")
                    {
                        MessageBox.Show((string)responseJson["message"]);
                        response = "Failed";
                    }
                    else response = responseJson["response"].ToString();

                }
                else
                {
                    // Ejecutar la herramienta sin obtener resultados
                    await QueuedTask.Run(() => Geoprocessing.ExecuteToolAsync(toolPath, args, null, null, null,
                        GPExecuteToolFlags.AddOutputsToMap));
                    response = "Success";
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show(ex.Message);
                response = "Failed";
            }

            return response;
        }

    }
}
