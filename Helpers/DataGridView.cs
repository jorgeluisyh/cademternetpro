using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace cademternetPro.Helpers
{
    internal class DataGridView
    {
    }

    class FolderRow
    {
        public string Id { get; set; }
        public string Path { get; set; }
        public bool Turn { get; set; }
        public string Del { get; set; }
    }

    class ShapefileRow
    {
        public string Parent { get; set; }
        public string ShapeFile { get; set; }
        public bool Turn { get; set; }
        public string Del { get; set; }
    }
}
