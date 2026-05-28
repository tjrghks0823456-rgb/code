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
    private const double RobotCenterX = 885;
    private const double RobotCenterY = 355;
    private const double RobotArmLength = 180;
    private const double ModuleProgressWidth = 142;

    private readonly DispatcherTimer _motionTimer;
    private readonly List<MotionStep> _steps;

    private int _stepIndex;
    private int _cycleSlot = 1;
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

        _motionTimer = new DispatcherTimer { Interval = TimeSpan.FromMilliseconds(33) };
        _motionTimer.Tick += MotionTimer_Tick;

        ResetVisualState();
        AddLog("Demo ready - visual scheduler only, no PLC or EtherCAT connection.");
    }

    private void StartDemo_Click(object sender, RoutedEventArgs e)
    {
        if (_isError)
        {
            AddLog("Start blocked: simulated ERROR is active.");
            return;
        }

        if (_isPaused)
        {
            _isPaused = false;
            AddLog("Demo resumed");
            BeginStep(_stepIndex, useCurrentPosition: true);
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
        AddLog(_isPaused ? "Demo paused" : "Demo resumed");

        if (_isPaused)
        {
            _motionTimer.Stop();
        }
        else
        {
            BeginStep(_stepIndex, useCurrentPosition: true);
            _motionTimer.Start();
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
        _cycleSlot = 1;
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
        SchedulerDecisionText.Text = "Scheduler hold: fault active";
        DispatcherStatusText.Text = "Dispatcher stopped";
        ResourceLockText.Text = "RobotArm = LOCKED\nLoadLockDoor = LOCKED\nVacuumPath = LOCKED";
        SetSignalState(isDoorOpen: false, isFault: true);
        SetModuleFill("ALL", "#3B1822");
        AddLog("ERROR injected by presenter");
    }

    private void ClearError_Click(object sender, RoutedEventArgs e)
    {
        _isError = false;
        ResetVisualState(clearLog: false);
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
        AddLog($"Cycle start: FOUP A Slot {_cycleSlot:00}");
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
        SetSignalState(isDoorOpen: step.LoadLockDoorOpen, isFault: false);
        ResetModuleHighlights();

        if (step.ProcessingModule is not null)
        {
            SetModuleFill(step.ProcessingModule, "#5C4A19");
        }
        else
        {
            SetModuleFill(step.ActiveModule, "#203F52");
        }

        UpdatePipelinePanel(step, 0);
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
            if ((DateTime.Now - _loopWaitStartedAt).TotalMilliseconds >= 1600)
            {
                _waitingForLoop = false;
                _stepIndex = 0;
                _cycleSlot = _cycleSlot >= 5 ? 1 : _cycleSlot + 1;
                ResetVisualState(clearLog: false);
                AddLog($"Next wafer reserved: FOUP A Slot {_cycleSlot:00}");
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

        UpdatePipelinePanel(step, progress);

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
            SchedulerDecisionText.Text = "Scheduler: next slot pre-reserved";
            DispatcherStatusText.Text = "Dispatcher: cycle complete";
            ResourceLockText.Text = "RobotArm = FREE\nChamber = FREE\nLoadLockDoor = CLOSED";
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
            new("FOUP A wafer pickup", "FOUP A wafer pickup", null, "FOUP A Slot 01", "FOUP A", "EFEM pickup ready", DemoPoints.FoupA, 180, 700, null, false, "Reserve next FOUP slot"),
            new("Aligner transfer", "EFEM moving wafer to aligner", "Aligner position reached", "Aligner / Buffer", "Aligner", "EFEM transfer", DemoPoints.Aligner, 180, 1300, null, false, "Dispatch align job"),
            new("Load Lock door open", "Load Lock door open", null, "Aligner / Buffer", "Load Lock", "Waiting for LL open", DemoPoints.Aligner, 180, 700, null, true, "Check atmosphere side interlock"),
            new("Wafer entered Load Lock", "Wafer entered Load Lock", null, "Load Lock", "Load Lock", "EFEM handoff complete", DemoPoints.LoadLock, 180, 1150, null, true, "Lock Load Lock resource"),
            new("Robot moving to PM2", "Transfer Robot moving to PM2", null, "PM2", "PM2 Etch", "Robot arm rotating to PM2", DemoPoints.Pm2, -52, 1550, null, false, "Dispatch robot move"),
            new("PM2 Etch processing", "PM2 Etch processing start", "PM2 process complete", "PM2", "PM2 Etch", "Wafer seated in PM2", DemoPoints.Pm2, -52, 2400, "PM2", false, "Pre-stage next wafer while PM2 runs"),
            new("Robot moving to PM3", "Transfer Robot moving to PM3", null, "PM3", "PM3 Etch", "Robot arm rotating to PM3", DemoPoints.Pm3, -2, 1400, null, false, "Select available chamber"),
            new("PM3 process", "PM3 process start", "PM3 process complete", "PM3", "PM3 Etch", "Wafer seated in PM3", DemoPoints.Pm3, -2, 2100, "PM3", false, "Keep robot free during chamber process"),
            new("Robot moving to PM4", "Transfer Robot moving to PM4", null, "PM4", "PM4 Etch", "Robot arm rotating to PM4", DemoPoints.Pm4, 55, 1400, null, false, "Avoid arm/chamber collision"),
            new("PM4 process", "PM4 process start", "PM4 process complete", "PM4", "PM4 Etch", "Wafer seated in PM4", DemoPoints.Pm4, 55, 2100, "PM4", false, "Queue downstream unload"),
            new("Robot moving to PM1", "Transfer Robot moving to PM1", null, "PM1", "PM1 Strip", "Robot arm rotating to PM1", DemoPoints.Pm1, -126, 1600, null, false, "Route final strip step"),
            new("PM1 Strip process", "PM1 Strip processing start", "PM1 Strip process complete", "PM1", "PM1 Strip", "Wafer seated in PM1", DemoPoints.Pm1, -126, 2300, "PM1", false, "Reserve Load Lock return path"),
            new("Load Lock return", "Transfer Robot returning wafer to Load Lock", "Load Lock door open", "Load Lock", "Load Lock", "Robot arm returning", DemoPoints.LoadLock, 180, 1500, null, true, "Release chamber and lock LL"),
            new("FOUP Return", "Wafer returned to FOUP", null, "FOUP Return", "Unload / FOUP Return", "EFEM unload complete", DemoPoints.FoupReturn, 180, 1400, null, true, "Complete wafer and dispatch next slot"),
        };
    }

    private void ResetVisualState(bool clearLog = true)
    {
        _currentWaferCenter = DemoPoints.FoupA;
        _fromWaferCenter = DemoPoints.FoupA;
        _toWaferCenter = DemoPoints.FoupA;
        _fromRobotAngle = 180;
        _toRobotAngle = 180;

        EquipmentStateText.Text = "IDLE";
        EquipmentStateText.Foreground = BrushFrom("#EAF6FF");
        CurrentStepText.Text = "Ready";
        WaferLocationText.Text = $"FOUP A Slot {_cycleSlot:00}";
        ActiveModuleText.Text = "None";
        RobotStatusText.Text = "Standby";
        InterlockStatusText.Text = "DISPLAY ONLY - VAC / DOOR / ROBOT OK";
        InterlockStatusText.Foreground = BrushFrom("#4FE38A");
        ChamberProgressBar.Value = 0;
        ChamberProgressText.Text = "0%";
        ClockText.Text = DateTime.Now.ToString("HH:mm:ss");

        MoveWaferTo(DemoPoints.FoupA);
        SetRobotAngle(180);
        SetDoorOpen(false);
        SetSignalState(isDoorOpen: false, isFault: false);
        ResetModuleHighlights();
        SetChamberProgress(null, 0);
        UpdatePipelinePanel(null, 0);

        if (clearLog)
        {
            EventLogList.Items.Clear();
        }
    }

    private void UpdatePipelinePanel(MotionStep? step, double progress)
    {
        int nextSlot = _cycleSlot >= 5 ? 1 : _cycleSlot + 1;
        SlotQueueText.Text =
            $"Active : Slot {_cycleSlot:00}\n" +
            $"Next   : Slot {nextSlot:00} reserved\n" +
            "Rule   : bottom slot first\n" +
            "Buffer : 1 wafer pre-stage";

        SchedulerDecisionText.Text = step?.SchedulerNote ?? "Scheduler: wait for Start Demo";
        DispatcherStatusText.Text = step is null
            ? "Dispatcher: idle"
            : $"Dispatcher: {step.ActiveModule} command issued";

        string robotLock = step is null ? "FREE" : "LOCKED";
        string chamberLock = step?.ProcessingModule is null ? "FREE" : $"{step.ProcessingModule} BUSY";
        string loadLock = step?.ActiveModule.Contains("Load Lock", StringComparison.OrdinalIgnoreCase) == true ? "LOCKED" : "READY";
        ResourceLockText.Text =
            $"RobotArm    = {robotLock}\n" +
            $"Chamber     = {chamberLock}\n" +
            $"LoadLock    = {loadLock}\n" +
            $"VacuumPath  = {(step?.LoadLockDoorOpen == true ? "ATM GATE" : "VAC READY")}";

        RecipeStatusText.Text = step?.ProcessingModule is null
            ? "Recipe: transfer / handling step"
            : $"Recipe: {step.ProcessingModule} active ({progress * 100:0}%)";

        VacuumStatusText.Text = step?.LoadLockDoorOpen == true
            ? "Vacuum interlock display: atmosphere side door open"
            : "Vacuum interlock display: vacuum transfer path sealed";

        ModuleStateList.Items.Clear();
        AddModuleState("EFEM", step?.ActiveModule is "FOUP A" or "Aligner" or "Unload / FOUP Return" ? "BUSY" : "READY");
        AddModuleState("Align/Buffer", step?.ActiveModule == "Aligner" ? "BUSY" : "READY");
        AddModuleState("LoadLock", step?.ActiveModule == "Load Lock" ? "BUSY" : "READY");
        AddModuleState("Robot", step?.RobotStatus.Contains("rotating", StringComparison.OrdinalIgnoreCase) == true ? "BUSY" : "READY");
        AddModuleState("PM1", step?.ProcessingModule == "PM1" ? "BUSY" : "READY");
        AddModuleState("PM2", step?.ProcessingModule == "PM2" ? "BUSY" : "READY");
        AddModuleState("PM3", step?.ProcessingModule == "PM3" ? "BUSY" : "READY");
        AddModuleState("PM4", step?.ProcessingModule == "PM4" ? "BUSY" : "READY");
    }

    private void AddModuleState(string module, string state)
    {
        ModuleStateList.Items.Add($"{module,-13} {state}");
    }

    private void ResetModuleHighlights()
    {
        SetModuleFill("FOUP A", "#162C3C");
        SetModuleFill("FOUP Return", "#162C3C");
        SetModuleFill("Aligner", "#162C3C");
        SetModuleFill("Buffer Stage", "#142838");
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
        Canvas.SetLeft(LoadLockDoor, isOpen ? 508 : 524);
    }

    private void SetSignalState(bool isDoorOpen, bool isFault)
    {
        SignalDoorLamp.Fill = isDoorOpen ? BrushFrom("#4FE38A") : BrushFrom("#FF5A6A");
        SignalDoorText.Text = isDoorOpen ? "ON" : "OFF";
        SignalDoorText.Foreground = isDoorOpen ? BrushFrom("#4FE38A") : BrushFrom("#FF8A96");

        SignalFaultLamp.Fill = isFault ? BrushFrom("#FF5A6A") : BrushFrom("#315064");
        SignalFaultText.Text = isFault ? "ON" : "OFF";
        SignalFaultText.Foreground = isFault ? BrushFrom("#FF5A6A") : BrushFrom("#86A7BA");

        SignalRobotReadyLamp.Fill = isFault ? BrushFrom("#315064") : BrushFrom("#4FE38A");
        SignalRobotReadyText.Text = isFault ? "OFF" : "ON";
        SignalRobotReadyText.Foreground = isFault ? BrushFrom("#86A7BA") : BrushFrom("#4FE38A");

        SignalVacuumLamp.Fill = isDoorOpen || isFault ? BrushFrom("#FFC857") : BrushFrom("#4FE38A");
        SignalVacuumText.Text = isDoorOpen ? "ATM" : isFault ? "HOLD" : "ON";
        SignalVacuumText.Foreground = isDoorOpen || isFault ? BrushFrom("#FFC857") : BrushFrom("#4FE38A");

        SignalWaferLamp.Fill = isFault ? BrushFrom("#315064") : BrushFrom("#4FE38A");
        SignalWaferText.Text = isFault ? "HOLD" : "ON";
        SignalWaferText.Foreground = isFault ? BrushFrom("#86A7BA") : BrushFrom("#4FE38A");
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
            BufferModule.Fill = brush;
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
            case "Buffer Stage":
                BufferModule.Fill = brush;
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
        bool LoadLockDoorOpen,
        string SchedulerNote);

    private static class DemoPoints
    {
        public static readonly Point FoupA = new(143, 268);
        public static readonly Point Aligner = new(374, 278);
        public static readonly Point LoadLock = new(624, 362);
        public static readonly Point Pm2 = new(1043, 138);
        public static readonly Point Pm3 = new(1279, 349);
        public static readonly Point Pm4 = new(1043, 612);
        public static readonly Point Pm1 = new(773, 138);
        public static readonly Point FoupReturn = new(143, 554);
    }
}
