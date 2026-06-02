using System.Text;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Data;
using System.Windows.Documents;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using System.Windows.Navigation;
using System.Windows.Shapes;

namespace 색_변화_버튼
{
    /// <summary>
    /// Interaction logic for MainWindow.xaml
    /// </summary>
    public partial class MainWindow : Window
    {
        public MainWindow()
        {
            InitializeComponent();
        }

        private void Button_Click(object sender, RoutedEventArgs e)
        {
            var bc = new BrushConverter();
            textBox.Background = (Brush)bc.ConvertFrom("#FF0000");
        }

        private void Button_Click_1(object sender, RoutedEventArgs e)
        {
            var bc = new BrushConverter();
            textBox.Background = (Brush)bc.ConvertFrom("#F1FF05");
        }

        private void Button_Click_2(object sender, RoutedEventArgs e)
        {
            var bc = new BrushConverter();
            textBox.Background = (Brush)bc.ConvertFrom("#070AFF");
        }

        private void Button_Click_3(object sender, RoutedEventArgs e)
        {
            var bc = new BrushConverter();
            textBox.Background = (Brush)bc.ConvertFrom("#29FF04");
        }

        private void Button_Click_4(object sender, RoutedEventArgs e)
        {
            var bc = new BrushConverter();
            textBox.Background = (Brush)bc.ConvertFrom("#FF9704");
        }

        private void Button_Click_5(object sender, RoutedEventArgs e)
        {
            var bc = new BrushConverter();
            textBox.Background = (Brush)bc.ConvertFrom("#6F00FF");
        }

        private void Button_Click_6(object sender, RoutedEventArgs e)
        {
            var bc = new BrushConverter();
            textBox.Background = (Brush)bc.ConvertFrom("#FF05E8");
        }

        private void Button_Click_7(object sender, RoutedEventArgs e)
        {
            var bc = new BrushConverter();
            textBox.Background = (Brush)bc.ConvertFrom("#000000");
        }
    }
}