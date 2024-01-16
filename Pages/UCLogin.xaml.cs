using ArcGIS.Desktop.Core;
using ArcGIS.Desktop.Framework.Threading.Tasks;
using ArcGIS.Desktop.Internal.Mapping;
using ArcGIS.Desktop.Mapping;
using ArcGIS.Core.Events;
using ArcGIS.Desktop.Mapping.Events;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Data;
using System.Windows.Documents;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using System.Windows.Navigation;
using System.Windows.Shapes;
using static cademternetPro.Toolbox;


namespace cademternetPro.Pages
{
    /// <summary>
    /// Lógica de interacción para UCLogin.xaml
    /// </summary>
    public partial class UCLogin : UserControl
    {
        private ContentControl _parentForm;        

        public UCLogin()
        {
            InitializeComponent();
        }
        public UCLogin(ContentControl parentForm)
        {
            _parentForm = parentForm;
            InitializeComponent();
        }
        public async Task AddMapToProject()
        {
            Project aprx = Project.Current;

            if (aprx.GetMaps().Count() > 0)
            {
                await QueuedTask.Run(() =>
                {
                    Map map = aprx.GetItems<MapProjectItem>().FirstOrDefault().GetMap();
                    ProApp.Panes.CreateMapPaneAsync(map);
                });
            }
            else
            {
                await QueuedTask.Run(() =>
                {
                    var map = MapFactory.Instance.CreateMap("Actualizar Demarcación", basemap: Basemap.ProjectDefault);
                    ProApp.Panes.CreateMapPaneAsync(map);
                });
            }
            parameters.Clear();
            await ExecuteGP(_tool_00_a_habilitarValidator, parameters, _toolboxPath,false);
        }        


        private async void btnLogin_Click(object sender, RoutedEventArgs e)
        {
            imageGif.Visibility = Visibility.Visible;
            //await Task.Delay(2500);
            await AddMapToProject();
            _parentForm.Content = new Pages.UCMain(_parentForm);
            
        }
    }
}
