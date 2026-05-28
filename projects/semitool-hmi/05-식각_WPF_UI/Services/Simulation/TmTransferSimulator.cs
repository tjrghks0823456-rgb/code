using etch_ui.Equipment.Helpers;
using etch_ui.Equipment.Models;

namespace etch_ui.Services.Simulation;

/// <summary>
/// 가상 웨이퍼 이송 — MODULE_역할_정의.md 표준 루트.
/// EFEM·TM(대기압): LP→Aligner→BM / 진공 TM: BM↔PM / EFEM·TM: BM→Side Stg→LP.
/// </summary>
public sealed class TmTransferSimulator
{
    public enum SimPhase
    {
        Idle,
        MoveToPickup,
        WaitDoorPickupOpen,
        PickupExtend,
        PickupRetract,
        WaitDoorPickupClose,
        MoveToDropoff,
        WaitDoorDropoffOpen,
        DropoffExtend,
        DropoffRetract,
        WaitDoorDropoffClose
    }

    private readonly Queue<(EquipmentRegion Pickup, EquipmentRegion Dropoff)> _queue = new();
    private (EquipmentRegion Pickup, EquipmentRegion Dropoff)? _current;
    private SimPhase _phase = SimPhase.Idle;
    private int _ticksLeft;
    private bool _running;

    private readonly HashSet<EquipmentRegion> _waferAt = new();
    private EquipmentRegion _originLoadPort = EquipmentRegion.FoupA;

    public bool IsActive => _running && _current.HasValue;
    public SimPhase Phase => _phase;
    public EquipmentRegion TmRegion { get; private set; } = EquipmentRegion.TM;
    public TransferRobotKind ActiveRobot { get; private set; } = TransferRobotKind.VacuumTm;
    public double BladeExtension { get; private set; } = 0.65;
    public bool CarryingWafer { get; private set; }
    public string PhaseHint { get; private set; } = "가상 이송 · 대기";

    public void StartDemoLoop()
    {
        Stop();
        _running = true;
        _originLoadPort = EquipmentRegion.FoupA;
        BuildStandardCycle();
        TryStartNext();
    }

    public void Stop()
    {
        _running = false;
        _queue.Clear();
        _current = null;
        _phase = SimPhase.Idle;
        _ticksLeft = 0;
        TmRegion = EquipmentRegion.TM;
        ActiveRobot = TransferRobotKind.VacuumTm;
        BladeExtension = 0.65;
        CarryingWafer = false;
        PhaseHint = "가상 이송 · 정지";
        _waferAt.Clear();
    }

    public void Tick()
    {
        if (!_running || !_current.HasValue)
        {
            return;
        }

        if (_ticksLeft > 0)
        {
            _ticksLeft--;
            if (_ticksLeft > 0)
            {
                return;
            }
        }

        AdvancePhase();
    }

    public bool IsVirtualDoorClosed(EquipmentRegion region)
    {
        if (!_current.HasValue)
        {
            return true;
        }

        var (pickup, dropoff) = _current.Value;
        if (_phase is SimPhase.WaitDoorPickupOpen && region == pickup)
        {
            return false;
        }

        if (_phase is SimPhase.WaitDoorDropoffOpen && region == dropoff)
        {
            return false;
        }

        return true;
    }

    public bool HasWaferAt(EquipmentRegion region) => _waferAt.Contains(region);

    private void Enqueue(EquipmentRegion pickup, EquipmentRegion dropoff) =>
        _queue.Enqueue((pickup, dropoff));

    /// <summary>MODULE_역할_정의.md §7 — 1매 사이클.</summary>
    private void BuildStandardCycle()
    {
        _waferAt.Clear();
        _waferAt.Add(_originLoadPort);

        // EFEM (대기압)
        Enqueue(_originLoadPort, EquipmentRegion.Aligner);
        Enqueue(EquipmentRegion.Aligner, EquipmentRegion.LoadLock);
        // TM (진공) — 식각 PM2→PM3→PM4 후 Strip PM1
        Enqueue(EquipmentRegion.LoadLock, EquipmentRegion.ChamberB);
        Enqueue(EquipmentRegion.ChamberB, EquipmentRegion.ChamberC);
        Enqueue(EquipmentRegion.ChamberC, EquipmentRegion.ChamberD);
        Enqueue(EquipmentRegion.ChamberD, EquipmentRegion.ChamberA);
        Enqueue(EquipmentRegion.ChamberA, EquipmentRegion.LoadLock);
        // 복귀 — Fume 제거 후 원 FOUP
        Enqueue(EquipmentRegion.LoadLock, EquipmentRegion.SideStorage);
        Enqueue(EquipmentRegion.SideStorage, _originLoadPort);
    }

    private void TryStartNext()
    {
        if (_queue.Count == 0)
        {
            BuildStandardCycle();
        }

        if (_queue.Count == 0)
        {
            _current = null;
            _phase = SimPhase.Idle;
            PhaseHint = "가상 이송 · 큐 없음";
            return;
        }

        _current = _queue.Dequeue();
        Enter(SimPhase.MoveToPickup, 2, _current.Value.Pickup, 0.65, false, "픽업 위치 이동");
    }

    private void AdvancePhase()
    {
        if (!_current.HasValue)
        {
            return;
        }

        var (pickup, dropoff) = _current.Value;

        switch (_phase)
        {
            case SimPhase.MoveToPickup:
                Enter(SimPhase.WaitDoorPickupOpen, 1, pickup, 0.65, false, $"{Label(pickup)} 도어 열림(가상)");
                break;
            case SimPhase.WaitDoorPickupOpen:
                Enter(SimPhase.PickupExtend, 2, pickup, 1.15, true, $"{Label(pickup)} 픽업");
                break;
            case SimPhase.PickupExtend:
                _waferAt.Remove(pickup);
                Enter(SimPhase.PickupRetract, 1, pickup, 0.65, true, "픽업 후퇴");
                break;
            case SimPhase.PickupRetract:
                Enter(SimPhase.WaitDoorPickupClose, 1, pickup, 0.65, true, $"{Label(pickup)} 도어 닫힘(가상)");
                break;
            case SimPhase.WaitDoorPickupClose:
                Enter(SimPhase.MoveToDropoff, 2, dropoff, 0.65, true, "드롭 위치 이동");
                break;
            case SimPhase.MoveToDropoff:
                Enter(SimPhase.WaitDoorDropoffOpen, 1, dropoff, 0.65, true, $"{Label(dropoff)} 도어 열림(가상)");
                break;
            case SimPhase.WaitDoorDropoffOpen:
                Enter(SimPhase.DropoffExtend, 2, dropoff, 1.15, true, $"{Label(dropoff)} 드롭");
                break;
            case SimPhase.DropoffExtend:
                CarryingWafer = false;
                _waferAt.Add(dropoff);
                Enter(SimPhase.DropoffRetract, 1, dropoff, 0.65, false, "드롭 후퇴");
                break;
            case SimPhase.DropoffRetract:
                Enter(SimPhase.WaitDoorDropoffClose, 1, dropoff, 0.65, false, $"{Label(dropoff)} 도어 닫힘(가상)");
                break;
            case SimPhase.WaitDoorDropoffClose:
                _current = null;
                _phase = SimPhase.Idle;
                TryStartNext();
                break;
            default:
                TryStartNext();
                break;
        }
    }

    private void Enter(SimPhase phase, int ticks, EquipmentRegion region, double ext, bool carrying, string hint)
    {
        _phase = phase;
        _ticksLeft = ticks;
        TmRegion = region;
        if (_current.HasValue)
        {
            ActiveRobot = TransferLegClassifier.RobotForLeg(_current.Value.Pickup, _current.Value.Dropoff);
        }

        BladeExtension = ext;
        CarryingWafer = carrying;
        string robotTag = ActiveRobot == TransferRobotKind.EfemAtmospheric ? "EFEM·TM" : "TM";
        PhaseHint = $"{robotTag}: {hint}";
    }

    private static string Label(EquipmentRegion r) => r switch
    {
        EquipmentRegion.FoupA => "LP1",
        EquipmentRegion.FoupB => "LP2",
        EquipmentRegion.FoupC => "LP3",
        EquipmentRegion.Aligner => "Aligner",
        EquipmentRegion.SideStorage => "Side Stg",
        EquipmentRegion.LoadLock => "BM",
        EquipmentRegion.ChamberA => "PM1 Strip",
        EquipmentRegion.ChamberB => "PM2 Etch",
        EquipmentRegion.ChamberC => "PM3 Etch",
        EquipmentRegion.ChamberD => "PM4 Etch",
        _ => r.ToString()
    };
}
