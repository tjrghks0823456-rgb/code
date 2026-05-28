using System;
using System.Collections.Generic;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Media;
using System.Windows.Threading;

namespace etch_ui.PresentationMotion;

public partial class DemoEquipmentMotionWindow : Window
{
    private const double WaferSize = 36;
    private const double RobotCenterX = 583;
    private const double RobotCenterY = 323;
    private const double RobotArmLength = 131;
    private const double ModuleProgressWidth = 126;

    private readonly DispatcherTimer _motionTimer;
    private readonly List<MotionStep> _steps;

    private int _stepIndex;
    private DateTime _stepStartedAt;
    private bool _isRunning;
    private bool _isPaused;
    private bool _isError;
    private bool _waitingForLoop;
    private DateTime _loopWaitStartedAt;

    private Point _currentWaferCenter;
    private Point _fromWaferCenter;
    private Point _toWaferCenter;
    private double _fromRobotAngle;
    private double _toRobotAngle;

    public DemoEquipmentMotionWindow()
    {
        InitializeComponent();

        _steps = BuildDemoSteps();
        _currentWaferCenter = DemoPoints.FoupA;
        _fromWaferCenter = DemoPoints.FoupA;
        _toWaferCenter = DemoPoints.FoupA;
        _fromRobotAngle = 180;
        _toRobotAngle = 180;

        _motionTimer = new DispatcherTimer
        {
            Interval = TimeSpan.FromMilliseconds(33)
        };
        _motionTimer.Tick += MotionTimer_Tick;

        ResetVisualState();
        AddLog("Demo screen ready - no PLC, EtherCAT, Flask, or DB connection is used.");
    }

    private void StartDemo_Click(object sender, RoutedEventArgs e)
    {
        if (_isError)
        {
            AddLog("Cannot start while ERROR is active. Press Clear Error first.");
            return;
        }

        if (_isPaused)
        {
            _isPaused = false;
            AddLog("Demo resumed");
            _motionTimer.Start();
            return;
        }

        if (!_isRunning)
        {
            StartCycle();
        }
    }

    private void Pause_Click(object sender, RoutedEventArgs e)
    {
        if (!_isRunning || _isError)
        {
            return;
        }

        _isPaused = !_isPaused;
        RobotStatusText.Text = _isPaused ? "Paused" : "Motion resumed";
        CurrentStepText.Text = _isPaused ? $"PAUSED - {CurrentStepText.Text}" : _steps[_stepIndex].StepName;
        AddLog(_isPaused ? "Demo paused" : "Demo resumed");

        if (_isPaused)
        {
            _motionTimer.Stop();
        }
        else
        {
            // Restart the current visual step from the current position.
            BeginStep(_stepIndex, useCurrentPosition: true);
        }
    }

    private void Reset_Click(object sender, RoutedEventArgs e)
    {
        _motionTimer.Stop();
        _isRunning = false;
        _isPaused = false;
        _isError = false;
        _waitingForLoop = false;
        _stepIndex = 0;

        ResetVisualState();
        AddLog("Demo reset");
    }

    private void InjectError_Click(object sender, RoutedEventArgs e)
    {
        _isError = true;
        _isRunning = false;
        _isPaused = false;
        _waitingForLoop = false;
        _motionTimer.Stop();

        EquipmentStateText.Text = "ERROR";
        EquipmentStateText.Foreground = BrushFrom("#FF5A6A");
        CurrentStepText.Text = "Manual demo error injected";
        ActiveModuleText.Text = "Safety Display";
        RobotStatusText.Text = "Stopped";
        InterlockStatusText.Text = "DISPLAY ONLY - INTERLOCK FAULT SIMULATED";
        InterlockStatusText.Foreground = BrushFrom("#FF5A6A");

        SetModuleFill("ALL", "#3B1822");
        AddLog("ERROR injected by presenter");
    }

    private void ClearError_Click(object sender, RoutedEventArgs e)
    {
        _isError = false;
        ResetVisualState();
        AddLog("Error cleared - demo ready");
    }

    private void StartCycle()
    {
        _isRunning = true;
        _isPaused = false;
        _waitingForLoop = false;
        _stepIndex = 0;
        EventLogList.Items.Clear();
        ResetVisualState(clearLog: false);
        AddLog("Demo cycle started");
        BeginStep(_stepIndex);
        _motionTimer.Start();
    }

    private void BeginStep(int index, bool useCurrentPosition = false)
    {
        if (index < 0 || index >= _steps.Count)
        {
            return;
        }

        MotionStep step = _steps[index];
        _stepStartedAt = DateTime.Now;
        _fromWaferCenter = useCurrentPosition ? _currentWaferCenter : _currentWaferCenter;
        _toWaferCenter = step.TargetWaferCenter;
        _fromRobotAngle = RobotArmRotateTransform.Angle;
        _toRobotAngle = step.RobotAngle;

        EquipmentStateText.Text = step.ProcessingModule is null ? "RUNNING" : "PROCESSING";
        EquipmentStateText.Foreground = step.ProcessingModule is null ? BrushFrom("#39D9FF") : BrushFrom("#FFC857");
        CurrentStepText.Text = step.StepName;
        WaferLocationText.Text = step.WaferLocation;
        ActiveModuleText.Text = step.ActiveModule;
        RobotStatusText.Text = step.RobotStatus;
        ChamberProgressBar.Value = 0;
        ChamberProgressText.Text = "0%";
        ClockText.Text = DateTime.Now.ToString("HH:mm:ss");

        SetDoorOpen(step.LoadLockDoorOpen);
        ResetModuleHighlights();

        if (step.ProcessingModule is not null)
        {
            SetModuleFill(step.ProcessingModule, "#5C4A19");
        }
        else
        {
            SetModuleFill(step.ActiveModule, "#203F52");
        }

        AddLog(step.StartLog);
    }

    private void MotionTimer_Tick(object? sender, EventArgs e)
    {
        ClockText.Text = DateTime.Now.ToString("HH:mm:ss");

        if (_isError || _isPaused)
        {
            return;
        }

        if (_waitingForLoop)
        {
            if ((DateTime.Now - _loopWaitStartedAt).TotalMilliseconds >= 1700)
            {
                _waitingForLoop = false;
                _stepIndex = 0;
                ResetVisualState(clearLog: false);
                AddLog("Next wafer cycle auto-start");
                BeginStep(_stepIndex);
            }

            return;
        }

        MotionStep step = _steps[_stepIndex];
        double elapsed = (DateTime.Now - _stepStartedAt).TotalMilliseconds;
        double progress = Math.Clamp(elapsed / step.DurationMs, 0, 1);
        double eased = EaseInOut(progress);

        Point waferPoint = Lerp(_fromWaferCenter, _toWaferCenter, eased);
        double robotAngle = Lerp(_fromRobotAngle, _toRobotAngle, eased);

        MoveWaferTo(waferPoint);
        SetRobotAngle(robotAngle);

        if (step.ProcessingModule is not null)
        {
            SetChamberProgress(step.ProcessingModule, progress * 100);
        }
        else
        {
            SetChamberProgress(null, 0);
        }

        if (progress >= 1)
        {
            FinishStep(step);
        }
    }

    private void FinishStep(MotionStep step)
    {
        _currentWaferCenter = step.TargetWaferCenter;
        SetRobotAngle(step.RobotAngle);
        MoveWaferTo(_currentWaferCenter);

        if (step.ProcessingModule is not null)
        {
            SetChamberProgress(step.ProcessingModule, 100);
        }

        if (!string.IsNullOrWhiteSpace(step.CompleteLog))
        {
            AddLog(step.CompleteLog);
        }

        _stepIndex++;

        if (_stepIndex >= _steps.Count)
        {
            EquipmentStateText.Text = "COMPLETE";
            EquipmentStateText.Foreground = BrushFrom("#4FE38A");
            CurrentStepText.Text = "Cycle complete";
            ActiveModuleText.Text = "FOUP Return";
            RobotStatusText.Text = "Standby";
            ChamberProgressBar.Value = 100;
            ChamberProgressText.Text = "100%";
            AddLog("Demo cycle complete");

            _waitingForLoop = true;
            _loopWaitStartedAt = DateTime.Now;
            return;
        }

        BeginStep(_stepIndex);
    }

    private List<MotionStep> BuildDemoSteps()
    {
        return new List<MotionStep>
        {
            new(
                StepName: "FOUP A wafer pickup",
                StartLog: "FOUP A wafer pickup",
                CompleteLog: null,
                WaferLocation: "FOUP A",
                ActiveModule: "FOUP A",
                RobotStatus: "EFEM pickup ready",
                TargetWaferCenter: DemoPoints.FoupA,
                RobotAngle: 180,
                DurationMs: 700,
                ProcessingModule: null,
                LoadLockDoorOpen: false),

            new(
                StepName: "Move wafer to aligner",
                StartLog: "EFEM moving wafer to aligner",
                CompleteLog: "Aligner position reached",
                WaferLocation: "Aligner",
                ActiveModule: "Aligner",
                RobotStatus: "EFEM transfer",
                TargetWaferCenter: DemoPoints.Aligner,
                RobotAngle: 180,
                DurationMs: 1300,
                ProcessingModule: null,
                LoadLockDoorOpen: false),

            new(
                StepName: "Load Lock door open",
                StartLog: "Load Lock door open",
                CompleteLog: null,
                WaferLocation: "Aligner",
                ActiveModule: "Load Lock",
                RobotStatus: "Waiting for LL open",
                TargetWaferCenter: DemoPoints.Aligner,
                RobotAngle: 180,
                DurationMs: 700,
                ProcessingModule: null,
                LoadLockDoorOpen: true),

            new(
                StepName: "Wafer entered Load Lock",
                StartLog: "Wafer entered Load Lock",
                CompleteLog: null,
                WaferLocation: "Load Lock",
                ActiveModule: "Load Lock",
                RobotStatus: "EFEM handoff complete",
                TargetWaferCenter: DemoPoints.LoadLock,
                RobotAngle: 180,
                DurationMs: 1150,
                ProcessingModule: null,
                LoadLockDoorOpen: true),

            new(
                StepName: "Transfer Robot moving to PM2",
                StartLog: "Transfer Robot moving to PM2",
                CompleteLog: null,
                WaferLocation: "PM2",
                ActiveModule: "PM2 Etch",
                RobotStatus: "Robot arm rotating to PM2",
                TargetWaferCenter: DemoPoints.Pm2,
                RobotAngle: -58,
                DurationMs: 1550,
                ProcessingModule: null,
                LoadLockDoorOpen: false),

            new(
                StepName: "PM2 Etch processing",
                StartLog: "PM2 Etch processing start",
                CompleteLog: "PM2 process complete",
                WaferLocation: "PM2",
                ActiveModule: "PM2 Etch",
                RobotStatus: "Wafer seated in PM2",
                TargetWaferCenter: DemoPoints.Pm2,
                RobotAngle: -58,
                DurationMs: 2400,
                ProcessingModule: "PM2",
                LoadLockDoorOpen: false),

            new(
                StepName: "Transfer Robot moving to PM3",
                StartLog: "Transfer Robot moving to PM3",
                CompleteLog: null,
                WaferLocation: "PM3",
                ActiveModule: "PM3 Etch",
                RobotStatus: "Robot arm rotating to PM3",
                TargetWaferCenter: DemoPoints.Pm3,
                RobotAngle: -5,
                DurationMs: 1400,
                ProcessingModule: null,
                LoadLockDoorOpen: false),

            new(
                StepName: "PM3 process",
                StartLog: "PM3 process start",
                CompleteLog: "PM3 process complete",
                WaferLocation: "PM3",
                ActiveModule: "PM3 Etch",
                RobotStatus: "Wafer seated in PM3",
                TargetWaferCenter: DemoPoints.Pm3,
                RobotAngle: -5,
                DurationMs: 2100,
                ProcessingModule: "PM3",
                LoadLockDoorOpen: false),

            new(
                StepName: "Transfer Robot moving to PM4",
                StartLog: "Transfer Robot moving to PM4",
                CompleteLog: null,
                WaferLocation: "PM4",
                ActiveModule: "PM4 Etch",
                RobotStatus: "Robot arm rotating to PM4",
                TargetWaferCenter: DemoPoints.Pm4,
                RobotAngle: 58,
                DurationMs: 1400,
                ProcessingModule: null,
                LoadLockDoorOpen: false),

            new(
                StepName: "PM4 process",
                StartLog: "PM4 process start",
                CompleteLog: "PM4 process complete",
                WaferLocation: "PM4",
                ActiveModule: "PM4 Etch",
                RobotStatus: "Wafer seated in PM4",
                TargetWaferCenter: DemoPoints.Pm4,
                RobotAngle: 58,
                DurationMs: 2100,
                ProcessingModule: "PM4",
                LoadLockDoorOpen: false),

            new(
                StepName: "Transfer Robot moving to PM1",
                StartLog: "Transfer Robot moving to PM1",
                CompleteLog: null,
                WaferLocation: "PM1",
                ActiveModule: "PM1 Strip",
                RobotStatus: "Robot arm rotating to PM1",
                TargetWaferCenter: DemoPoints.Pm1,
                RobotAngle: -118,
                DurationMs: 1600,
                ProcessingModule: null,
                LoadLockDoorOpen: false),

            new(
                StepName: "PM1 Strip process",
                StartLog: "PM1 Strip processing start",
                CompleteLog: "PM1 Strip process complete",
                WaferLocation: "PM1",
                ActiveModule: "PM1 Strip",
                RobotStatus: "Wafer seated in PM1",
                TargetWaferCenter: DemoPoints.Pm1,
                RobotAngle: -118,
                DurationMs: 2300,
                ProcessingModule: "PM1",
                LoadLockDoorOpen: false),

            new(
                StepName: "Load Lock return",
                StartLog: "Transfer Robot returning wafer to Load Lock",
                CompleteLog: "Load Lock door open",
                WaferLocation: "Load Lock",
                ActiveModule: "Load Lock",
                RobotStatus: "Robot arm returning",
                TargetWaferCenter: DemoPoints.LoadLock,
                RobotAngle: 180,
                DurationMs: 1500,
                ProcessingModule: null,
                LoadLockDoorOpen: true),

            new(
                StepName: "FOUP Return",
                StartLog: "Wafer returned to FOUP",
                CompleteLog: null,
                WaferLocation: "FOUP Return",
                ActiveModule: "Unload / FOUP Return",
                RobotStatus: "EFEM unload complete",
                TargetWaferCenter: DemoPoints.FoupReturn,
                RobotAngle: 180,
                DurationMs: 1400,
                ProcessingModule: null,
                LoadLockDoorOpen: true),
        };
    }

    private void ResetVisualState(bool clearLog = false)
    {
        _currentWaferCenter = DemoPoints.FoupA;
        _fromWaferCenter = DemoPoints.FoupA;
        _toWaferCenter = DemoPoints.FoupA;
        _fromRobotAngle = 180;
        _toRobotAngle = 180;

        EquipmentStateText.Text = "IDLE";
        EquipmentStateText.Foreground = BrushFrom("#EAF6FF");
        CurrentStepText.Text = "Ready";
        WaferLocationText.Text = "FOUP A";
        ActiveModuleText.Text = "None";
        RobotStatusText.Text = "Standby";
        InterlockStatusText.Text = "DISPLAY ONLY - ALL CONDITIONS OK";
        InterlockStatusText.Foreground = BrushFrom("#4FE38A");
        ChamberProgressBar.Value = 0;
        ChamberProgressText.Text = "0%";
        ClockText.Text = DateTime.Now.ToString("HH:mm:ss");

        MoveWaferTo(DemoPoints.FoupA);
        SetRobotAngle(180);
        SetDoorOpen(false);
        ResetModuleHighlights();
        SetChamberProgress(null, 0);

        if (clearLog)
        {
            EventLogList.Items.Clear();
        }
    }

    private void ResetModuleHighlights()
    {
        SetModuleFill("FOUP A", "#162C3C");
        SetModuleFill("FOUP Return", "#162C3C");
        SetModuleFill("Aligner", "#162C3C");
        SetModuleFill("Load Lock", "#182F3D");
        SetModuleFill("PM1", "#152B3A");
        SetModuleFill("PM2", "#152B3A");
        SetModuleFill("PM3", "#152B3A");
        SetModuleFill("PM4", "#152B3A");
        SetModuleFill("Side Storage", "#162C3C");

        PM1ProgressFill.Width = 0;
        PM2ProgressFill.Width = 0;
        PM3ProgressFill.Width = 0;
        PM4ProgressFill.Width = 0;
    }

    private void MoveWaferTo(Point center)
    {
        _currentWaferCenter = center;
        Canvas.SetLeft(WaferEllipse, center.X - WaferSize / 2);
        Canvas.SetTop(WaferEllipse, center.Y - WaferSize / 2);
    }

    private void SetRobotAngle(double angle)
    {
        RobotArmRotateTransform.Angle = angle;

        double radians = angle * Math.PI / 180.0;
        double carrierCenterX = RobotCenterX + Math.Cos(radians) * RobotArmLength;
        double carrierCenterY = RobotCenterY + Math.Sin(radians) * RobotArmLength;

        Canvas.SetLeft(RobotCarrierGlow, carrierCenterX - RobotCarrierGlow.Width / 2);
        Canvas.SetTop(RobotCarrierGlow, carrierCenterY - RobotCarrierGlow.Height / 2);
    }

    private void SetDoorOpen(bool isOpen)
    {
        LoadLockDoor.Fill = isOpen ? BrushFrom("#4FE38A") : BrushFrom("#FF5A6A");
        DoorStatusText.Text = isOpen ? "DOOR OPEN" : "DOOR CLOSED";
        DoorStatusText.Foreground = isOpen ? BrushFrom("#4FE38A") : BrushFrom("#FF8A96");
        Canvas.SetLeft(LoadLockDoor, isOpen ? 380 : 392);
    }

    private void SetChamberProgress(string? module, double percent)
    {
        double clamped = Math.Clamp(percent, 0, 100);
        ChamberProgressBar.Value = clamped;
        ChamberProgressText.Text = $"{clamped:0}%";

        double width = ModuleProgressWidth * (clamped / 100.0);

        if (module == "PM1")
        {
            PM1ProgressFill.Width = width;
        }
        else if (module == "PM2")
        {
            PM2ProgressFill.Width = width;
        }
        else if (module == "PM3")
        {
            PM3ProgressFill.Width = width;
        }
        else if (module == "PM4")
        {
            PM4ProgressFill.Width = width;
        }
    }

    private void SetModuleFill(string module, string color)
    {
        Brush brush = BrushFrom(color);

        if (module == "ALL")
        {
            FoupAModule.Fill = brush;
            FoupReturnModule.Fill = brush;
            AlignerModule.Fill = brush;
            LoadLockModule.Fill = brush;
            PM1Module.Fill = brush;
            PM2Module.Fill = brush;
            PM3Module.Fill = brush;
            PM4Module.Fill = brush;
            SideStorageModule.Fill = brush;
            return;
        }

        switch (module)
        {
            case "FOUP A":
                FoupAModule.Fill = brush;
                break;
            case "FOUP Return":
            case "Unload / FOUP Return":
                FoupReturnModule.Fill = brush;
                break;
            case "Aligner":
                AlignerModule.Fill = brush;
                break;
            case "Load Lock":
                LoadLockModule.Fill = brush;
                break;
            case "PM1":
            case "PM1 Strip":
                PM1Module.Fill = brush;
                break;
            case "PM2":
            case "PM2 Etch":
                PM2Module.Fill = brush;
                break;
            case "PM3":
            case "PM3 Etch":
                PM3Module.Fill = brush;
                break;
            case "PM4":
            case "PM4 Etch":
                PM4Module.Fill = brush;
                break;
            case "Side Storage":
                SideStorageModule.Fill = brush;
                break;
        }
    }

    private void AddLog(string? message)
    {
        if (string.IsNullOrWhiteSpace(message))
        {
            return;
        }

        EventLogList.Items.Add($"[{DateTime.Now:HH:mm:ss}] {message}");
        EventLogList.ScrollIntoView(EventLogList.Items[^1]);
    }

    private static Point Lerp(Point a, Point b, double t)
    {
        return new Point(Lerp(a.X, b.X, t), Lerp(a.Y, b.Y, t));
    }

    private static double Lerp(double a, double b, double t)
    {
        return a + (b - a) * t;
    }

    private static double EaseInOut(double t)
    {
        // Smoothstep easing keeps the visual movement presentation-friendly.
        return t * t * (3 - 2 * t);
    }

    private static SolidColorBrush BrushFrom(string hex)
    {
        return new SolidColorBrush((Color)ColorConverter.ConvertFromString(hex));
    }

    private sealed record MotionStep(
        string StepName,
        string StartLog,
        string? CompleteLog,
        string WaferLocation,
        string ActiveModule,
        string RobotStatus,
        Point TargetWaferCenter,
        double RobotAngle,
        double DurationMs,
        string? ProcessingModule,
        bool LoadLockDoorOpen);

    private static class DemoPoints
    {
        public static readonly Point FoupA = new(117, 279);
        public static readonly Point Aligner = new(284, 300);
        public static readonly Point LoadLock = new(468, 300);
        public static readonly Point Pm2 = new(704, 142);
        public static readonly Point Pm3 = new(870, 304);
        public static readonly Point Pm4 = new(704, 484);
        public static readonly Point Pm1 = new(500, 142);
        public static readonly Point FoupReturn = new(117, 445);
    }
}
