using Microsoft.Win32;
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
using ArcGIS.Desktop.Catalog;
using ArcGIS.Desktop.Core;
using Newtonsoft.Json;
using System.Collections.ObjectModel;
using cademternetPro.Helpers;
using ArcGIS.Core.Data;
using ActiproSoftware.Windows.Extensions;

namespace cademternetPro.Pages
{
    /// <summary>
    /// Lógica de interacción para UCMain.xaml
    /// </summary>
    public partial class UCMain : UserControl
    {
        private ContentControl _parentForm;
        private ObservableCollection<ShapefileRow> _shapefilerows = new ObservableCollection<ShapefileRow>();
        private ObservableCollection<FolderRow> _folderrows = new ObservableCollection<FolderRow>();
        public UCMain()
        {
            InitializeComponent();
        }

        public UCMain(ContentControl parentForm)
        {
            _parentForm = parentForm;
            InitializeComponent();
        }

        private void btnSalir_Click(object sender, RoutedEventArgs e)
        {
            var Result = MessageBox.Show("¿Desea Salir de CademterNet?", "Salir", MessageBoxButton.YesNo, MessageBoxImage.Question);
            if (Result == MessageBoxResult.Yes)
            {
                _parentForm.Content = new UCLogin(_parentForm);

            }

        }

        private void image01Config_MouseLeftButtonUp(object sender, MouseButtonEventArgs e)
        {
            GPToolDialog(_tool_01_configurarentorno);
        }

        private void image02Structure_MouseLeftButtonUp(object sender, MouseButtonEventArgs e)
        {
            GPToolDialog(_tool_02_verificarestructura);
        }

        private void image03FloatPol_MouseLeftButtonUp(object sender, MouseButtonEventArgs e)
        {
            GPToolDialog(_tool_03_verificarpoligonosflotantes);
        }

        private void image04Cuad_MouseLeftButtonUp(object sender, MouseButtonEventArgs e)
        {
            GPToolDialog(_tool_04_tratamientoinsumos);
        }

        private void image05ProcInfo_MouseLeftButtonUp(object sender, MouseButtonEventArgs e)
        {
            GPToolDialog(_tool_05_cuadriculasregionales);
        }

        private void image06CorrectCuad_MouseLeftButtonUp(object sender, MouseButtonEventArgs e)
        {
            GPToolDialog(_tool_06_validacioncuadriculas);
        }

        private async void openFolder_Click(object sender, RoutedEventArgs e)
        {
            OpenItemDialog openItemDialog = new OpenItemDialog
            {
                Title = "Seleccione la carpeta",
                MultiSelect = false,
                BrowseFilter = BrowseProjectFilter.GetFilter(ArcGIS.Desktop.Catalog.ItemFilters.Folders)
            };
            bool? ok = openItemDialog.ShowDialog();
            
            if (!ok.HasValue || openItemDialog.Items.Count() == 0)
                return;   //nothing selected

            var item = openItemDialog.Items.First();
            string path = item.Path;
            int ident = dgFolders.Items.Count +1;
            _folderrows.Add(new FolderRow { Id= ident.ToString(), Path= path, Turn=false });
            //foreach(FolderRow row in folderrows)
            //{
            //    dgFolders.Items.Add(row);   
            //}
            dgFolders.ItemsSource = _folderrows;


            parameters.Clear();
            parameters.Add(path);
            var response = await ExecuteGP(_tool_00_b_listarshapefiles, parameters, _toolboxPath);
            string[] rowsResponse = response.Split(',');
            foreach( string  row in rowsResponse)
            {
                _shapefilerows.Add(new ShapefileRow{ Parent=ident.ToString(),  ShapeFile =row, Turn=false });
            }
            dgShapeFiles.ItemsSource = _shapefilerows;

        }

        private void Button_Click(object sender, RoutedEventArgs e)
        {
            var button = sender as Button;
            var rowData = button.DataContext as FolderRow;

            if (rowData != null)
            {
                _folderrows.Remove(rowData);
            }
            _shapefilerows.RemoveAll(row => row.Parent == rowData.Id);
        }

        private void Button_Click_1(object sender, RoutedEventArgs e)
        {
            var button = sender as Button;
            var rowData = button.DataContext as ShapefileRow;
            
            if (rowData != null)
            {
                _shapefilerows.Remove(rowData);
            }
        }
        void ShpOnChecked(object sender, RoutedEventArgs e)
        {
            MessageBox.Show("Checked");
        }
        void ShpOnUnchecked(object sender, RoutedEventArgs e)
        {
            MessageBox.Show("Unchecked");
        }
        
    }
}

