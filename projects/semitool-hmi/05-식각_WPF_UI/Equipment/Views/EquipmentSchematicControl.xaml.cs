using System.Windows;
using System.Windows.Controls;
using System.Windows.Media;
using System.Windows.Shapes;
using etch_ui.Equipment.Layout;
using etch_ui.Equipment.ViewModels;

namespace etch_ui.Equipment.Views;

public partial class EquipmentSchematicControl : UserControl
{
    private const double TmBaseBlade = 50;
    private const double TmMaxBlade = 205;
    private const double EfemBaseBlade = 36;
    private const double EfemMaxBlade = 118;
    private EquipmentMotionViewModel? _bound;

    public EquipmentSchematicControl()
    {
        InitializeComponent();
        Loaded += OnLoaded;
        DataContextChanged += (_, _) => HookMotion();
    }

    private void OnLoaded(object sender, RoutedEventArgs e)
    {
        RepositionAll();
        DrawTracks();
        HookMotion();
    }

    private void HookMotion()
    {
        if (_bound != null)
        {
            _bound.PropertyChanged -= OnMotionPropertyChanged;
        }

        _bound = DataContext as EquipmentMotionViewModel;
        if (_bound != null)
        {
            _bound.PropertyChanged += OnMotionPropertyChanged;
            RefreshRobots();
        }
    }

    private void OnMotionPropertyChanged(object? sender, System.ComponentModel.PropertyChangedEventArgs e)
    {
        if (e.PropertyName is nameof(EquipmentMotionViewModel.BladeAngleDegrees)
            or nameof(EquipmentMotionViewModel.BladeExtension)
            or nameof(EquipmentMotionViewModel.CarryingWafer)
            or nameof(EquipmentMotionViewModel.IsEfemRobotActive))
        {
            RefreshRobots();
        }
    }

    private void RefreshRobots()
    {
        if (_bound == null)
        {
            return;
        }

        bool efem = _bound.IsEfemRobotActive;
        EfemRobotHost.Visibility = efem ? Visibility.Visible : Visibility.Collapsed;
        TmHost.Visibility = efem ? Visibility.Collapsed : Visibility.Visible;

        double norm = (_bound.BladeExtension - 0.4) / 1.2;
        norm = Math.Clamp(norm, 0, 1);

        if (efem)
        {
            EfemRotate.Angle = _bound.BladeAngleDegrees;
            double len = EfemBaseBlade + norm * (EfemMaxBlade - EfemBaseBlade);
            EfemBladeRect.Width = len;
            double pivot = EquipmentLayoutMetrics.EfemRobotPivot;
            WaferOnEfemBlade.Margin = new Thickness(pivot + len - 16, 0, 0, 0);
            WaferOnEfemBlade.Visibility = _bound.CarryingWafer ? Visibility.Visible : Visibility.Collapsed;
        }
        else
        {
            TmRotate.Angle = _bound.BladeAngleDegrees;
            double len = TmBaseBlade + norm * (TmMaxBlade - TmBaseBlade);
            BladeRect.Width = len;
            double pivot = EquipmentLayoutMetrics.TmPivot;
            WaferOnBlade.Margin = new Thickness(pivot + len - 22, 0, 0, 0);
            WaferOnBlade.Visibility = _bound.CarryingWafer ? Visibility.Visible : Visibility.Collapsed;
        }
    }

    private void RepositionAll()
    {
        Place(EfemBox, EquipmentLayoutMetrics.EfemPosition, EquipmentLayoutMetrics.EfemSize);
        Place(AlignerBox, EquipmentLayoutMetrics.AlignerPosition, EquipmentLayoutMetrics.AlignerSize);
        Place(SideStorageBox, EquipmentLayoutMetrics.SideStoragePosition, EquipmentLayoutMetrics.SideStorageSize);
        Place(LoadPort1Box, EquipmentLayoutMetrics.LoadPort1Position, EquipmentLayoutMetrics.LoadPortSize);
        Place(LoadPort2Box, EquipmentLayoutMetrics.LoadPort2Position, EquipmentLayoutMetrics.LoadPortSize);
        Place(LoadPort3Box, EquipmentLayoutMetrics.LoadPort3Position, EquipmentLayoutMetrics.LoadPortSize);
        Place(LoadLockBox, EquipmentLayoutMetrics.BufferPosition, EquipmentLayoutMetrics.BufferSize);
        Place(ChamberABox, EquipmentLayoutMetrics.Pm1Position, EquipmentLayoutMetrics.PmSize);
        Place(ChamberBBox, EquipmentLayoutMetrics.Pm2Position, EquipmentLayoutMetrics.PmSize);
        Place(ChamberCBox, EquipmentLayoutMetrics.Pm3Position, EquipmentLayoutMetrics.PmSize);
        Place(Pm4Box, EquipmentLayoutMetrics.Pm4Position, EquipmentLayoutMetrics.PmSize);

        Point efemTopLeft = EquipmentLayoutMetrics.EfemRobotHostTopLeft;
        Canvas.SetLeft(EfemRobotHost, efemTopLeft.X);
        Canvas.SetTop(EfemRobotHost, efemTopLeft.Y);

        Point tmTopLeft = EquipmentLayoutMetrics.TmHostTopLeft;
        Canvas.SetLeft(TmHost, tmTopLeft.X);
        Canvas.SetTop(TmHost, tmTopLeft.Y);
        Canvas.SetLeft(TmLabel, EquipmentLayoutMetrics.TmCenter.X - 48);
        Canvas.SetTop(TmLabel, EquipmentLayoutMetrics.TmCenter.Y + EquipmentLayoutMetrics.TmPivot + 8);
    }

    private static void Place(FrameworkElement el, Point pos, Size size)
    {
        el.Width = size.Width;
        el.Height = size.Height;
        Canvas.SetLeft(el, pos.X);
        Canvas.SetTop(el, pos.Y);
    }

    private void DrawTracks()
    {
        Point lp1 = EquipmentLayoutMetrics.GetPortCenter(Equipment.Models.EquipmentRegion.FoupA);
        Point efemPivot = EquipmentLayoutMetrics.EfemRobotCenter;
        Point bm = EquipmentLayoutMetrics.GetPortCenter(Equipment.Models.EquipmentRegion.LoadLock);
        Point tm = EquipmentLayoutMetrics.TmCenter;
        Point[] main = [lp1, efemPivot, bm, tm];
        MainTrack.Points = new PointCollection(main);
        MainTrackDash.Points = new PointCollection(main);

        PmSpokesLayer.Children.Clear();
        foreach (var region in new[]
                 {
                     Equipment.Models.EquipmentRegion.ChamberA,
                     Equipment.Models.EquipmentRegion.ChamberB,
                     Equipment.Models.EquipmentRegion.ChamberC,
                     Equipment.Models.EquipmentRegion.ChamberD
                 })
        {
            Point pm = EquipmentLayoutMetrics.GetPortCenter(region);
            PmSpokesLayer.Children.Add(new Line
            {
                X1 = tm.X,
                Y1 = tm.Y,
                X2 = pm.X,
                Y2 = pm.Y,
                Stroke = new SolidColorBrush(Color.FromArgb(90, 37, 99, 235)),
                StrokeThickness = 1.5,
                StrokeDashArray = new DoubleCollection { 4, 6 }
            });
        }
    }
}
