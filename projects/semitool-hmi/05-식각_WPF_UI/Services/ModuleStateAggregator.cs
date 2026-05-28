using etch_ui.Equipment.Models;
using etch_ui.Services.Simulation;

namespace etch_ui.Services;

/// <summary>
/// 장비 전역 상태 + 가상 이송 + Load Lock 접촉 → 모듈별 상태 배열.
/// </summary>
public static class ModuleStateAggregator
{
    public sealed class Context
    {
        public required string EquipmentState { get; init; }
        public bool MaintenanceMode { get; init; }
        public bool HasLiveSensorData { get; init; }
        public bool InterlockOk { get; init; }
        public bool BenchMode { get; init; }
        public bool AccessSafe { get; init; }
        public bool AccessInputValid { get; init; }
        public string? AlarmCode { get; init; }
        public TmTransferSimulator? Transfer { get; init; }
    }

    public static IReadOnlyList<ModuleStateSnapshot> Build(Context ctx)
    {
        bool globalMaint = ctx.MaintenanceMode;
        bool globalAlarm = ctx.EquipmentState.Equals("ALARM", StringComparison.OrdinalIgnoreCase);
        bool globalWarning = ctx.EquipmentState.Equals("WARNING", StringComparison.OrdinalIgnoreCase);
        bool globalRunning = ctx.EquipmentState.Equals("RUNNING", StringComparison.OrdinalIgnoreCase);
        bool globalReady = ctx.EquipmentState.Equals("READY", StringComparison.OrdinalIgnoreCase);
        bool transferActive = ctx.Transfer is { IsActive: true };

        var list = new List<ModuleStateSnapshot>(13);

        // Load ports: FOUP A → LP1, LP2 spare, FOUP B → LP3
        list.Add(BuildLoadPort(EquipmentModuleId.LoadPort1, EquipmentRegion.FoupA, ctx, globalMaint, globalAlarm, transferActive));
        list.Add(BuildLoadPort(EquipmentModuleId.LoadPort2, EquipmentRegion.FoupB, ctx, globalMaint, globalAlarm, transferActive));
        list.Add(BuildLoadPort(EquipmentModuleId.LoadPort3, EquipmentRegion.FoupC, ctx, globalMaint, globalAlarm, transferActive));

        list.Add(BuildBufferModule(ctx, globalMaint, globalAlarm, globalRunning, transferActive));
        list.Add(BuildEfemRobot(ctx, globalMaint, globalAlarm, transferActive));
        list.Add(BuildTransferModule(ctx, globalMaint, globalAlarm, globalRunning, transferActive));
        list.Add(BuildPm(EquipmentModuleId.Pm1, EquipmentRegion.ChamberA, ctx, globalMaint, globalAlarm, globalWarning, globalRunning, transferActive));
        list.Add(BuildPm(EquipmentModuleId.Pm2, EquipmentRegion.ChamberB, ctx, globalMaint, globalAlarm, globalWarning, globalRunning, transferActive));
        list.Add(BuildPm(EquipmentModuleId.Pm3, EquipmentRegion.ChamberC, ctx, globalMaint, globalAlarm, globalWarning, globalRunning, transferActive));
        list.Add(BuildPm(EquipmentModuleId.Pm4, EquipmentRegion.ChamberD, ctx, globalMaint, globalAlarm, globalWarning, globalRunning, transferActive));

        list.Add(BuildEfem(ctx, globalMaint, globalAlarm, globalRunning, transferActive));
        list.Add(BuildAligner(ctx, globalMaint, globalAlarm, transferActive));
        list.Add(BuildSideStorage(ctx, globalMaint, globalAlarm, transferActive));

        return list;
    }

    private static ModuleStateSnapshot BuildLoadPort(
        EquipmentModuleId id,
        EquipmentRegion region,
        Context ctx,
        bool globalMaint,
        bool globalAlarm,
        bool transferActive,
        bool forceEmpty = false)
    {
        if (globalMaint)
        {
            return Snap(id, ModuleOperationalState.Maintenance, detail: "유지보수");
        }

        if (!transferActive && forceEmpty)
        {
            return Snap(id, ModuleOperationalState.Idle, hasWafer: false, detail: "대기");
        }

        bool hasWafer = !forceEmpty && ctx.Transfer is not null && ctx.Transfer.HasWaferAt(region);
        bool pickupOpen = ctx.Transfer is not null
                          && !ctx.Transfer.IsVirtualDoorClosed(region)
                          && ctx.Transfer.IsActive;

        ModuleOperationalState st = globalAlarm ? ModuleOperationalState.Alarm
            : pickupOpen ? ModuleOperationalState.Running
            : hasWafer ? ModuleOperationalState.Standby
            : ModuleOperationalState.Idle;

        return Snap(id, st, hasWafer: hasWafer, detail: pickupOpen ? "도어 열림(가상)" : null);
    }

    private static ModuleStateSnapshot BuildBufferModule(
        Context ctx,
        bool globalMaint,
        bool globalAlarm,
        bool globalRunning,
        bool transferActive)
    {
        if (globalMaint)
        {
            return Snap(EquipmentModuleId.BufferModule, ModuleOperationalState.Maintenance, detail: "유지보수");
        }

        if (ctx.BenchMode)
        {
            return Snap(EquipmentModuleId.BufferModule, ModuleOperationalState.Standby,
                doorClosed: true, detail: "데모(시뮬 접촉)");
        }

        if (!ctx.HasLiveSensorData)
        {
            return Snap(EquipmentModuleId.BufferModule, ModuleOperationalState.Offline,
                doorClosed: null, detail: "접촉 미측정");
        }

        bool doorClosed = ctx.AccessInputValid && ctx.AccessSafe;
        ModuleOperationalState st = globalAlarm ? ModuleOperationalState.Alarm
            : !ctx.AccessSafe ? ModuleOperationalState.Alarm
            : globalRunning || transferActive ? ModuleOperationalState.Running
            : ModuleOperationalState.Standby;

        return Snap(EquipmentModuleId.BufferModule, st,
            doorClosed: doorClosed,
            detail: ctx.AccessInputValid ? (ctx.AccessSafe ? "접촉 닫힘(실측)" : "접촉 열림(실측)") : "접촉 미측정");
    }

    private static ModuleStateSnapshot BuildEfemRobot(
        Context ctx,
        bool globalMaint,
        bool globalAlarm,
        bool transferActive)
    {
        if (globalMaint)
        {
            return Snap(EquipmentModuleId.EfemRobot, ModuleOperationalState.Maintenance, detail: "유지보수");
        }

        if (transferActive && ctx.Transfer is not null
            && ctx.Transfer.ActiveRobot == TransferRobotKind.EfemAtmospheric)
        {
            return Snap(EquipmentModuleId.EfemRobot, ModuleOperationalState.Running,
                hasWafer: ctx.Transfer.CarryingWafer,
                detail: "대기압 TM · LP/BM");
        }

        if (globalAlarm)
        {
            return Snap(EquipmentModuleId.EfemRobot, ModuleOperationalState.Alarm, detail: ctx.AlarmCode);
        }

        return Snap(EquipmentModuleId.EfemRobot, ModuleOperationalState.Standby, detail: "EFEM TM 대기");
    }

    private static ModuleStateSnapshot BuildTransferModule(
        Context ctx,
        bool globalMaint,
        bool globalAlarm,
        bool globalRunning,
        bool transferActive)
    {
        if (globalMaint)
        {
            return Snap(EquipmentModuleId.TransferModule, ModuleOperationalState.Maintenance);
        }

        if (transferActive && ctx.Transfer is not null
            && ctx.Transfer.ActiveRobot == TransferRobotKind.VacuumTm)
        {
            bool carrying = ctx.Transfer.CarryingWafer;
            return Snap(EquipmentModuleId.TransferModule, ModuleOperationalState.Running,
                hasWafer: carrying, detail: "진공 TM · BM/PM");
        }

        if (globalAlarm)
        {
            return Snap(EquipmentModuleId.TransferModule, ModuleOperationalState.Alarm, detail: ctx.AlarmCode);
        }

        if (globalRunning)
        {
            return Snap(EquipmentModuleId.TransferModule, ModuleOperationalState.Standby, detail: "이송 대기");
        }

        return Snap(EquipmentModuleId.TransferModule, ModuleOperationalState.Idle);
    }

    private static ModuleStateSnapshot BuildPm(
        EquipmentModuleId pmId,
        EquipmentRegion region,
        Context ctx,
        bool globalMaint,
        bool globalAlarm,
        bool globalWarning,
        bool globalRunning,
        bool transferActive,
        bool virtualOnly = false)
    {
        if (globalMaint)
        {
            return Snap(pmId, ModuleOperationalState.Maintenance);
        }

        if (virtualOnly)
        {
            return Snap(pmId, ModuleOperationalState.Idle, detail: "미사용(표시만)");
        }

        bool hasWafer = ctx.Transfer is not null && ctx.Transfer.HasWaferAt(region);
        bool doorClosed = ctx.Transfer is null || ctx.Transfer.IsVirtualDoorClosed(region);
        bool doorPhase = transferActive && !doorClosed;

        ModuleOperationalState st;
        if (globalAlarm)
        {
            st = ModuleOperationalState.Alarm;
        }
        else if (globalWarning && region == EquipmentRegion.ChamberA)
        {
            st = ModuleOperationalState.Warning;
        }
        else if (doorPhase)
        {
            st = ModuleOperationalState.Running;
        }
        else if (hasWafer && globalRunning)
        {
            st = ModuleOperationalState.Processing;
        }
        else if (hasWafer)
        {
            st = ModuleOperationalState.Standby;
        }
        else
        {
            st = ModuleOperationalState.Idle;
        }

        string label = pmId switch
        {
            EquipmentModuleId.Pm1 => "Strip (PR)",
            EquipmentModuleId.Pm2 => "Etch",
            EquipmentModuleId.Pm3 => "Etch",
            EquipmentModuleId.Pm4 => "Etch",
            _ => "Etch"
        };

        return Snap(pmId, st, doorClosed: doorClosed, hasWafer: hasWafer,
            detail: doorPhase ? "슬릿 열림(가상)" : hasWafer ? label : null);
    }

    private static ModuleStateSnapshot BuildEfem(
        Context ctx,
        bool globalMaint,
        bool globalAlarm,
        bool globalRunning,
        bool transferActive)
    {
        if (globalMaint)
        {
            return Snap(EquipmentModuleId.Efem, ModuleOperationalState.Maintenance);
        }

        ModuleOperationalState st = globalAlarm ? ModuleOperationalState.Alarm
            : transferActive || globalRunning ? ModuleOperationalState.Standby
            : ModuleOperationalState.Idle;

        return Snap(EquipmentModuleId.Efem, st, detail: "EFEM (대기압 구역)");
    }

    private static ModuleStateSnapshot BuildAligner(Context ctx, bool globalMaint, bool globalAlarm, bool transferActive)
    {
        if (globalMaint)
        {
            return Snap(EquipmentModuleId.Aligner, ModuleOperationalState.Maintenance);
        }

        bool atAligner = ctx.Transfer is not null && ctx.Transfer.HasWaferAt(EquipmentRegion.Aligner);
        bool alignPhase = transferActive && ctx.Transfer is not null
            && (ctx.Transfer.TmRegion == EquipmentRegion.Aligner || atAligner);

        ModuleOperationalState st = globalAlarm ? ModuleOperationalState.Alarm
            : alignPhase ? ModuleOperationalState.Running
            : atAligner ? ModuleOperationalState.Standby
            : ModuleOperationalState.Idle;

        return Snap(EquipmentModuleId.Aligner, st, hasWafer: atAligner, detail: alignPhase ? "정렬(가상)" : null);
    }

    private static ModuleStateSnapshot BuildSideStorage(Context ctx, bool globalMaint, bool globalAlarm, bool transferActive)
    {
        if (globalMaint)
        {
            return Snap(EquipmentModuleId.SideStorage, ModuleOperationalState.Maintenance);
        }

        bool atSide = ctx.Transfer is not null && ctx.Transfer.HasWaferAt(EquipmentRegion.SideStorage);
        bool fumePhase = transferActive && ctx.Transfer is not null
            && (ctx.Transfer.TmRegion == EquipmentRegion.SideStorage || atSide);

        ModuleOperationalState st = globalAlarm ? ModuleOperationalState.Alarm
            : fumePhase ? ModuleOperationalState.Running
            : atSide ? ModuleOperationalState.Standby
            : ModuleOperationalState.Idle;

        return Snap(EquipmentModuleId.SideStorage, st, hasWafer: atSide, detail: fumePhase ? "Fume 제거(가상)" : null);
    }

    private static ModuleStateSnapshot Snap(
        EquipmentModuleId id,
        ModuleOperationalState state,
        bool? doorClosed = null,
        bool? hasWafer = null,
        string? detail = null) =>
        new()
        {
            ModuleId = id,
            State = state,
            DoorClosed = doorClosed,
            HasWafer = hasWafer,
            Detail = detail
        };
}
