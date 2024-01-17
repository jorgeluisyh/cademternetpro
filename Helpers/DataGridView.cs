using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace cademternetPro.Helpers
{
    internal class DataGridView
    {
    }

    // Hereda de INotifyPropertyChanged para poder mostrar los cambios de la clase en el Ui y viceversa
    class FolderRow: INotifyPropertyChanged
    {
        private bool _turn;
        public string Id { get; set; }
        public string Path { get; set; }
        public bool Turn
        {
            get => _turn;
            set
            {
                if (_turn != value)
                {
                    _turn = value;
                    OnPropertyChanged(nameof(Turn));
                }
            }
        }
        public string Del { get; set; }

        public event PropertyChangedEventHandler PropertyChanged;

        protected virtual void OnPropertyChanged(string propertyName)
        {
            PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
        }
    }

    // Hereda de INotifyPropertyChanged para poder mostrar los cambios de la clase en el Ui y viceversa
    class ShapefileRow : INotifyPropertyChanged
    {
        private bool _turn;
        public string Parent { get; set; }
        public string ShapeFile { get; set; }
        public bool Turn
        {
            get => _turn;
            set
            {
                if (_turn != value)
                {
                    _turn = value;
                    OnPropertyChanged(nameof(Turn));
                }
            }
        }
        public string Del { get; set; }

        public event PropertyChangedEventHandler PropertyChanged;

        protected virtual void OnPropertyChanged(string propertyName)
        {
            PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
        }
    }
}
