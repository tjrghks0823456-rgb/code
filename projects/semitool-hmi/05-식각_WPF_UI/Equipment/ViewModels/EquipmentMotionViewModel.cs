using System.Windows.Media;
using etch_ui.Equipment.Helpers;
using etch_ui.Equipment.Models;
using etch_ui.ViewModels;

namespace etch_ui.Equipment.ViewModels;

/// <summary>장비 도식(TM·챔버·FOUP) 바인딩 — 16ms 보간은 EquipmentMotionAnimator가 갱신.</summary>
public sealed class EquipmentMotionViewModel : ViewModelBase
{
    private double _bladeAngleDegrees;
    private double _bladeExtension = 0.65;
    private bool _carryingWafer;
    private Brush _waferBrush = Brushes.Wheat;
    private string _tmRegionLabel = "TM";
    private string _servoHint = "시뮬/논리";
    private bool _isEfemRobotActive;

    private bool _loadLockDoorClosed = true;
    private bool _chamberADoorClosed = true;
    private bool _chamberBDoorClosed = true;
    private bool _chamberCDoorClosed = true;
    private bool _chamberDDoorClosed = true;
    private bool _foupAHasWafer;
    private bool _foupBHasWafer;
    private bool _foupCHasWafer;
    private bool _alignerHasWafer;
    private bool _sideStorageHasWafer;
    private bool _chamberAHasWafer;
    private bool _chamberBHasWafer;
    private bool _chamberCHasWafer;
    private bool _chamberDHasWafer;
    private Brush _chamberALampBrush = new SolidColorBrush(Color.FromRgb(230, 230, 235));
    private Brush _chamberBLampBrush = new SolidColorBrush(Color.FromRgb(230, 230, 235));
    private Brush _chamberCLampBrush = new SolidColorBrush(Color.FromRgb(230, 230, 235));
    private Brush _chamberDLampBrush = new SolidColorBrush(Color.FromRgb(230, 230, 235));

    public double BladeAngleDegrees
    {
        get => _bladeAngleDegrees;
        set => SetField(ref _bladeAngleDegrees, value);
    }

    public double BladeExtension
    {
        get => _bladeExtension;
        set => SetField(ref _bladeExtension, value);
    }

    public bool CarryingWafer
    {
        get => _carryingWafer;
        set => SetField(ref _carryingWafer, value);
    }

    public Brush WaferBrush
    {
        get => _waferBrush;
        set => SetField(ref _waferBrush, value);
    }

    public string TmRegionLabel
    {
        get => _tmRegionLabel;
        set => SetField(ref _tmRegionLabel, value);
    }

    public string ServoHint
    {
        get => _servoHint;
        set => SetField(ref _servoHint, value);
    }

    /// <summary>true면 도식에 EFEM 대기압 TM 표시, false면 진공 TM.</summary>
    public bool IsEfemRobotActive
    {
        get => _isEfemRobotActive;
        set => SetField(ref _isEfemRobotActive, value);
    }

    public bool LoadLockDoorClosed
    {
        get => _loadLockDoorClosed;
        set => SetField(ref _loadLockDoorClosed, value);
    }

    public bool ChamberADoorClosed { get => _chamberADoorClosed; set => SetField(ref _chamberADoorClosed, value); }
    public bool ChamberBDoorClosed { get => _chamberBDoorClosed; set => SetField(ref _chamberBDoorClosed, value); }
    public bool ChamberCDoorClosed { get => _chamberCDoorClosed; set => SetField(ref _chamberCDoorClosed, value); }
    public bool ChamberDDoorClosed { get => _chamberDDoorClosed; set => SetField(ref _chamberDDoorClosed, value); }

    public bool FoupAHasWafer { get => _foupAHasWafer; set => SetField(ref _foupAHasWafer, value); }
    public bool FoupBHasWafer { get => _foupBHasWafer; set => SetField(ref _foupBHasWafer, value); }
    public bool FoupCHasWafer { get => _foupCHasWafer; set => SetField(ref _foupCHasWafer, value); }
    public bool AlignerHasWafer { get => _alignerHasWafer; set => SetField(ref _alignerHasWafer, value); }
    public bool SideStorageHasWafer { get => _sideStorageHasWafer; set => SetField(ref _sideStorageHasWafer, value); }

    public bool ChamberAHasWafer { get => _chamberAHasWafer; set => SetField(ref _chamberAHasWafer, value); }
    public bool ChamberBHasWafer { get => _chamberBHasWafer; set => SetField(ref _chamberBHasWafer, value); }
    public bool ChamberCHasWafer { get => _chamberCHasWafer; set => SetField(ref _chamberCHasWafer, value); }
    public bool ChamberDHasWafer { get => _chamberDHasWafer; set => SetField(ref _chamberDHasWafer, value); }

    public Brush ChamberALampBrush { get => _chamberALampBrush; set => SetField(ref _chamberALampBrush, value); }
    public Brush ChamberBLampBrush { get => _chamberBLampBrush; set => SetField(ref _chamberBLampBrush, value); }
    public Brush ChamberCLampBrush { get => _chamberCLampBrush; set => SetField(ref _chamberCLampBrush, value); }
    public Brush ChamberDLampBrush { get => _chamberDLampBrush; set => SetField(ref _chamberDLampBrush, value); }

    /// <summary>목표값 설정(애니메이터가 현재값으로 보간).</summary>
    public void SetTargets(
        EquipmentRegion region,
        double extension,
        bool carrying,
        bool hardwareMode,
        TransferRobotKind robot)
    {
        TargetRegion = region;
        TargetExtension = extension;
        TargetCarrying = carrying;
        TargetRobot = robot;
        IsEfemRobotActive = robot == TransferRobotKind.EfemAtmospheric;
        TargetAngleDegrees = RegionAngleHelper.ToDegrees(region, robot, hardwareMode);
        TmRegionLabel = RegionAngleHelper.FormatLabel(region, robot);
    }

    internal EquipmentRegion TargetRegion { get; private set; } = EquipmentRegion.TM;
    internal TransferRobotKind TargetRobot { get; private set; } = TransferRobotKind.VacuumTm;
    internal double TargetAngleDegrees { get; private set; }
    internal double TargetExtension { get; private set; } = 0.65;
    internal bool TargetCarrying { get; private set; }

    internal void ApplyInterpolatedFrame(double angleDeg, double extension, bool carrying)
    {
        BladeAngleDegrees = angleDeg;
        BladeExtension = extension;
        CarryingWafer = carrying;
    }

    public void SetChamberLamp(int chamberIndex, ChamberLampVisual visual)
    {
        Brush brush = visual switch
        {
            ChamberLampVisual.Processing => Brushes.ForestGreen,
            ChamberLampVisual.CompletedBlinkOn => Brushes.ForestGreen,
            ChamberLampVisual.CompletedBlinkOff => new SolidColorBrush(Color.FromRgb(230, 230, 235)),
            _ => new SolidColorBrush(Color.FromRgb(230, 230, 235))
        };

        switch (chamberIndex)
        {
            case 0: ChamberALampBrush = brush; break;
            case 1: ChamberBLampBrush = brush; break;
            case 2: ChamberCLampBrush = brush; break;
            case 3: ChamberDLampBrush = brush; break;
        }
    }

    public ModulePanelVisual EfemPanel { get; } = new();
    public ModulePanelVisual EfemRobotPanel { get; } = new();
    public ModulePanelVisual AlignerPanel { get; } = new();
    public ModulePanelVisual SideStoragePanel { get; } = new();
    public ModulePanelVisual LoadPort1Panel { get; } = new();
    public ModulePanelVisual LoadPort2Panel { get; } = new();
    public ModulePanelVisual LoadPort3Panel { get; } = new();
    public ModulePanelVisual BufferPanel { get; } = new();
    public ModulePanelVisual TmPanel { get; } = new();
    public ModulePanelVisual Pm1Panel { get; } = new();
    public ModulePanelVisual Pm2Panel { get; } = new();
    public ModulePanelVisual Pm3Panel { get; } = new();
    public ModulePanelVisual Pm4Panel { get; } = new();

    public void ApplyModuleSnapshots(IReadOnlyList<ModuleStateSnapshot> snapshots)
    {
        foreach (ModuleStateSnapshot s in snapshots)
        {
            ModulePanelVisual? panel = s.ModuleId switch
            {
                EquipmentModuleId.Efem => EfemPanel,
                EquipmentModuleId.EfemRobot => EfemRobotPanel,
                EquipmentModuleId.Aligner => AlignerPanel,
                EquipmentModuleId.SideStorage => SideStoragePanel,
                EquipmentModuleId.LoadPort1 => LoadPort1Panel,
                EquipmentModuleId.LoadPort2 => LoadPort2Panel,
                EquipmentModuleId.LoadPort3 => LoadPort3Panel,
                EquipmentModuleId.BufferModule => BufferPanel,
                EquipmentModuleId.TransferModule => TmPanel,
                EquipmentModuleId.Pm1 => Pm1Panel,
                EquipmentModuleId.Pm2 => Pm2Panel,
                EquipmentModuleId.Pm3 => Pm3Panel,
                EquipmentModuleId.Pm4 => Pm4Panel,
                _ => null
            };
            if (panel != null)
            {
                panel.State = s.State;
            }
        }
    }
}
