# Wafer Transfer Pipeline Architecture

## 1. Generalized Pipeline

The transfer flow is modeled as a pipeline:

`FOUP Slot Queue -> Scheduler -> Dispatcher -> Resource Lock -> Module State Machine -> Event Log`

Each wafer is a job. Each module is an independent state machine. The scheduler keeps the next wafer prepared while chambers are processing so robot and chamber idle time stay low.

## 2. Portable Module Structure

- EFEM: atmosphere-side FOUP pick/place and aligner handoff
- Aligner/Buffer: pre-stage wafer before Load Lock entry
- Load Lock: atmosphere/vacuum boundary and door/pump state
- Transfer Robot: vacuum-side arm motion and wafer handoff
- Process Module: PM1/PM2/PM3/PM4 chamber process execution
- Side Storage: optional wait/buffer location

## 3. State Machine

Recommended module states:

- IDLE: no assigned work
- READY: interlock satisfied and commandable
- BUSY: executing motion or process
- WAIT: blocked by resource, recipe, vacuum, or downstream module
- COMPLETE: command finished and result acknowledged
- ERROR: fault latched, scheduler must stop issuing dependent jobs

## 4. Queue / Scheduler / Dispatcher

- Queue: stores wafer jobs and their route steps
- Scheduler: selects next executable job based on chamber availability, robot availability, recipe, and interlock state
- Dispatcher: converts the selected route step into module commands
- Module Controller: owns the actual state machine and reports completion/faults

## 5. Collision Prevention

- Use one resource lock per physical conflict zone: robot arm, Load Lock door, chamber port, vacuum path, FOUP port
- Acquire locks in a fixed global order
- Never allow two modules to own the same wafer ID
- Require handoff acknowledgment before releasing source module

## 6. Deadlock Prevention

- Keep lock acquisition order deterministic
- Use timeouts for every motion/process wait
- Do not hold a robot lock while waiting for long chamber processing
- Release upstream locks immediately after safe handoff
- Detect circular waits through a scheduler wait graph or lock owner table

## 7. Recommended C# Class Shape

```csharp
public interface IEquipmentModule
{
    string ModuleId { get; }
    ModuleState State { get; }
    Task<ModuleResult> ExecuteAsync(ModuleCommand command, CancellationToken ct);
}

public sealed class WaferJob
{
    public string WaferId { get; init; } = "";
    public int SourceSlot { get; init; }
    public Queue<RouteStep> Route { get; } = new();
}

public sealed class TransferScheduler
{
    public SchedulerDecision Decide(
        IReadOnlyList<WaferJob> queue,
        ResourceSnapshot resources,
        ModuleSnapshot modules);
}

public sealed class CommandDispatcher
{
    public Task DispatchAsync(SchedulerDecision decision, CancellationToken ct);
}

public sealed class ResourceLockManager
{
    public Task<ResourceLease> AcquireAsync(
        IReadOnlyList<string> resourceIds,
        TimeSpan timeout,
        CancellationToken ct);
}
```

## 8. Refactoring Direction

- Extract module state machines from UI code
- Keep WPF ViewModel as a subscriber to module/scheduler events
- Keep PLC/ADS read/write behind adapter interfaces
- Make recipe steps data-driven
- Replace direct cross-module calls with dispatcher commands

## 9. Maintainability

- One owner per wafer job
- One owner per resource lock
- Structured logs for every state transition
- Route steps stored as recipe data, not hard-coded UI flow
- Simulation and real hardware share interfaces, but use different adapters

## 10. Semiconductor Equipment Pattern

- SEMI-style event model: command issued, command accepted, busy, complete, alarm
- EFEM handles atmosphere-side flow
- Load Lock owns vacuum boundary interlocks
- Motion axis controller owns move completion and servo faults
- PLC adapter owns actual IO, door, pump, valve, and sensor signals
- Scheduler owns production flow and dead-time reduction
