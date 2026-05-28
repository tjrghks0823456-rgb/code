using System.Windows;
using System.Windows.Media;
using System.Windows.Threading;
using etch_ui.Plc;
using etch_ui.Security;
using etch_ui.Services;
using etch_ui.ViewModels;
using System.Threading.Tasks;

namespace etch_ui;

public partial class MainWindow : Window
{
    private readonly MainViewModel _vm = new();
    private readonly DatabaseService _db;
    private readonly PlcAdsService _plc = new();
    private readonly EtchFlaskClient _flask = new();

    private readonly DispatcherTimer _uiTimer = new();

    private readonly Random _rand = new();
    private bool _useSimulation;
    private bool _maintenanceMode;

    private readonly bool[] _hwPrev = new bool[4];
    private bool _hwInit;

    private EquipmentState _state = EquipmentState.Idle;
    private EquipmentState _lastLoggedState = EquipmentState.Idle;
    private string? _lastAlarmCode;

    private double _temp = 24.0;
    private double _humi = 45.0;
    /// <summary>시뮬·초기 기본 97.5 kPa (= 스케일 50%, 95~100 kPa 선형).</summary>
    private double _pressure = 97.5;
    private double _pressurePercent = 50.0;
    private short _pressureRaw;
    private bool _pressureSignalValid = true;
    private double _vib = 0.10;
    private bool _accessSafe = true;

    private int _flaskCounter;

    private bool _flaskProbeDone;
    private bool _flaskReachable;
    private DateTime _nextFlaskFailLogUtc = DateTime.MinValue;

    private DateTime _lastProcessSampleUtc = DateTime.MinValue;

    /// <summary>appsettings 초깃값·메인 창 버튼으로 바꿀 수 있음. false면 PLC 실패 시 시뮬 대체 안 함.</summary>
    private bool _simulationFallbackEnabled;

    /// <summary>PLC 실데이터 없음을 한 번만 로그했는지(성공 시 리셋).</summary>
    private bool _loggedPlcRequiredOffline;

    private enum EquipmentState
    {
        Idle,
        Ready,
        Running,
        Warning,
        Alarm,
        Maintenance
    }

    public MainWindow(DatabaseService databaseService)
    {
        _db = databaseService;
        InitializeComponent();
        DataContext = _vm;
        _simulationFallbackEnabled = AppSettings.SimulationEnabled;
        Loaded += async (_, _) => await OnWindowLoadedAsync();
        Closed += (_, _) => OnWindowClosed();
        InitializeRuntime();
        SyncViewModel();
    }

    private async Task OnWindowLoadedAsync()
    {
        _flask.BaseUrl = AppSettings.FlaskBaseUrl;

        if (_plc.TryConnect(AppSettings.AdsPort))
        {
            _useSimulation = false;
            _db.AppendEventLog(CurrentUserName(), null, null, "PLC ADS 연결 성공");
            AddLog($"PLC 연결 성공 (ADS 포트 {AppSettings.AdsPort})");
        }
        else
        {
            string err = _plc.LastError ?? "알 수 없음";
            if (_simulationFallbackEnabled)
            {
                _useSimulation = true;
                _db.AppendEventLog(CurrentUserName(), null, "A001", $"PLC 연결 실패(시뮬 전환): {err}");
                AddLog($"PLC 연결 실패 — 시뮬 허용 ON이므로 데모 센서 모드: {err}");
            }
            else
            {
                _useSimulation = false;
                ApplyOfflineSensorPlaceholder();
                _db.AppendEventLog(CurrentUserName(), "ALARM", "A001", $"PLC 연결 실패(시뮬 꺼짐, 실데이터 없음): {err}");
                AddLog($"PLC 연결 실패 — 시뮬 허용 OFF, 시뮬 대체 안 함: {err}");
                _loggedPlcRequiredOffline = true;
            }
        }

        try
        {
            _flaskReachable = await _flask.TryHealthCheckAsync().ConfigureAwait(false);
        }
        catch
        {
            _flaskReachable = false;
        }

        _flaskProbeDone = true;
        Dispatcher.Invoke(() =>
        {
            if (_flaskReachable)
            {
                AddLog($"Flask 응답 OK ({_flask.BaseUrl})");
                _db.AppendEventLog(CurrentUserName(), null, null, $"Flask 헬스체크 성공 ({_flask.BaseUrl})");
            }
            else
            {
                AddLog($"Flask 미응답 — C:\\etchflask\\run_flask.bat 실행 후 확인 ({_flask.BaseUrl})");
                _db.AppendEventLog(CurrentUserName(), null, null, $"Flask 헬스체크 실패 ({_flask.BaseUrl})");
            }

            SyncViewModel();
        });
    }

    private void OnWindowClosed()
    {
        _plc.Dispose();
        _flask.Dispose();
    }

    private void InitializeRuntime()
    {
        AddLog("시스템 초기화 완료");
        ApplyRolePermissions();

        _uiTimer.Interval = TimeSpan.FromSeconds(1);
        _uiTimer.Tick += (_, _) => UiTimerOnTick();
        _uiTimer.Start();
    }

    private void UiTimerOnTick()
    {
        if (!_useSimulation)
        {
            if (_plc.TryReadSnapshot(out PlcProcessSnapshot snap))
            {
                ApplyPlcSnapshot(snap);
            }
            else
            {
                string err = _plc.LastError ?? "읽기 실패";
                _plc.Disconnect();
                if (_simulationFallbackEnabled)
                {
                    _useSimulation = true;
                    _db.AppendEventLog(CurrentUserName(), "ALARM", "A001", $"PLC 통신 끊김(시뮬 전환): {err}");
                    AddLog($"PLC 읽기 실패 — 시뮬 허용 ON, 데모 센서로 전환: {err}");
                    SimulateSensors();
                }
                else
                {
                    _useSimulation = false;
                    ApplyOfflineSensorPlaceholder();
                    if (!_loggedPlcRequiredOffline)
                    {
                        _db.AppendEventLog(CurrentUserName(), "ALARM", "A001", $"PLC 통신 끊김(시뮬 꺼짐): {err}");
                        AddLog($"PLC 읽기 실패 — 시뮬 허용 OFF, 시뮬 없음: {err}");
                        _loggedPlcRequiredOffline = true;
                    }
                }
            }
        }
        else
        {
            SimulateSensors();
        }

        AutoEvaluateState();
        PushOutputsToPlc();
        SyncViewModel();

        _flaskCounter++;
        if (_flaskCounter >= 2)
        {
            _flaskCounter = 0;
            _ = PublishFlaskAsync();
        }

        LogStateTransitionIfNeeded();
    }

    /// <summary>PLC 필수 모드에서 통신 불가일 때 표시·인터락이 “유효 데이터 없음”으로 보이도록 초기화.</summary>
    private void ApplyOfflineSensorPlaceholder()
    {
        _temp = 0;
        _humi = 0;
        _pressure = 0;
        _pressurePercent = 0;
        _pressureRaw = 0;
        _pressureSignalValid = false;
        _vib = 0;
        _accessSafe = false;
        _lastProcessSampleUtc = DateTime.MinValue;
    }

    private void ApplyPlcSnapshot(PlcProcessSnapshot snap)
    {
        _loggedPlcRequiredOffline = false;
        _temp = Math.Round(snap.TemperatureC, 2);
        _humi = Math.Round(snap.HumidityPercent, 2);
        _pressure = Math.Round(snap.PressureKpa, 2);
        _pressurePercent = Math.Round(snap.PressurePercent, 1);
        _pressureRaw = snap.PressureRaw;
        _pressureSignalValid = snap.PressureSignalValid;
        _vib = Math.Round(snap.VibrationG, 2);
        _accessSafe = snap.AccessSafe;
        _lastProcessSampleUtc = DateTime.UtcNow;
        ProcessHardwareButtons(snap.DigitalInputBits);
    }

    /// <summary>버튼으로 시뮬 켤 때 등, 데모 시작값.</summary>
    private void SeedSimulationValues()
    {
        _temp = 24.0;
        _humi = 45.0;
        _pressure = PlcAnalogScaling.PressurePercentToKpa(50.0);
        _pressurePercent = 50.0;
        _pressureRaw = 0;
        _pressureSignalValid = true;
        _vib = 0.10;
        _accessSafe = true;
    }

    private void SimulateSensors()
    {
        _temp = Math.Round(_temp + (_rand.NextDouble() - 0.5) * 0.35, 2);
        _humi = Math.Round(_humi + (_rand.NextDouble() - 0.5) * 0.7, 2);
        _pressure = Math.Round(_pressure + (_rand.NextDouble() - 0.5) * 0.45, 2);
        _vib = Math.Round(Math.Max(0, _vib + (_rand.NextDouble() - 0.5) * 0.06), 2);

        if (_rand.NextDouble() < 0.02)
        {
            _accessSafe = !_accessSafe;
            AddLog(_accessSafe ? "접근 센서: SAFE" : "접근 센서: DETECTED");
        }

        _lastProcessSampleUtc = DateTime.UtcNow;
    }

    private bool IsPressureNormal =>
        _pressureSignalValid
        && _pressure >= AppSettings.PressureKpaMin
        && _pressure <= AppSettings.PressureKpaMax;

    private bool IsVibrationNormal => _vib <= AppSettings.VibrationGMax;

    private bool IsTempNormal =>
        _temp >= AppSettings.TempCMin && _temp <= AppSettings.TempCMax;

    private bool IsHumiNormal =>
        _humi >= AppSettings.HumiMin && _humi <= AppSettings.HumiMax;

    private bool PlcLinkOk => _useSimulation || _plc.IsConnected;

    private bool InterlockOk => PlcLinkOk && IsPressureNormal && IsVibrationNormal && _accessSafe && IsTempNormal && IsHumiNormal;

    private string? ComputePrimaryAlarmCode()
    {
        if (_maintenanceMode)
        {
            return null;
        }

        if (!PlcLinkOk)
        {
            return "A001";
        }

        if (!_accessSafe)
        {
            return "A004";
        }

        if (!IsPressureNormal)
        {
            return "A002";
        }

        if (!IsVibrationNormal)
        {
            return "A003";
        }

        if (!IsTempNormal)
        {
            return "A005";
        }

        if (!IsHumiNormal)
        {
            return "A006";
        }

        return null;
    }

    private void AutoEvaluateState()
    {
        if (_maintenanceMode)
        {
            _state = EquipmentState.Maintenance;
            return;
        }

        bool severe = !PlcLinkOk || !_accessSafe || !IsPressureNormal || !IsVibrationNormal;
        if (severe)
        {
            _state = EquipmentState.Alarm;
            return;
        }

        if (_state == EquipmentState.Alarm)
        {
            return;
        }

        if (!IsTempNormal || !IsHumiNormal)
        {
            if (_state == EquipmentState.Running)
            {
                _state = EquipmentState.Warning;
            }
            else if (_state is EquipmentState.Idle or EquipmentState.Ready)
            {
                _state = EquipmentState.Ready;
            }

            return;
        }

        if (_state is EquipmentState.Idle or EquipmentState.Warning)
        {
            _state = EquipmentState.Ready;
        }
    }

    private void PushOutputsToPlc()
    {
        if (_useSimulation || !_plc.IsConnected)
        {
            return;
        }

        ushort bits = _state switch
        {
            EquipmentState.Ready => 1 << 0,
            EquipmentState.Running => 1 << 1,
            EquipmentState.Warning => 1 << 2,
            EquipmentState.Alarm => 1 << 3,
            _ => 0
        };

        _plc.WriteDigitalOutputLamps(bits);
    }

    private void ProcessHardwareButtons(ushort bits)
    {
        bool b1 = (bits & 1) != 0;
        bool b2 = (bits & (1 << 1)) != 0;
        bool b3 = (bits & (1 << 2)) != 0;
        bool b4 = (bits & (1 << 3)) != 0;

        if (!_hwInit)
        {
            _hwPrev[0] = b1;
            _hwPrev[1] = b2;
            _hwPrev[2] = b3;
            _hwPrev[3] = b4;
            _hwInit = true;
            return;
        }

        if (b1 && !_hwPrev[0])
        {
            RequestStart("HW Start");
        }

        if (b2 && !_hwPrev[1])
        {
            RequestStop("HW Stop");
        }

        if (b3 && !_hwPrev[2])
        {
            RequestReset("HW Reset");
        }

        if (b4 && !_hwPrev[3])
        {
            RequestMaintenanceToggle("HW Maint");
        }

        _hwPrev[0] = b1;
        _hwPrev[1] = b2;
        _hwPrev[2] = b3;
        _hwPrev[3] = b4;
    }

    private void SyncViewModel()
    {
        _vm.CurrentUserText = SessionContext.CurrentUser is null
            ? "-"
            : $"{SessionContext.CurrentUser.Username} ({SessionContext.CurrentUser.Role.ToDisplayKorean()})";
        _vm.ShowUserManage = SessionContext.HasRole(UserRole.Admin);
        _vm.SimAllowButtonText = _simulationFallbackEnabled ? "시뮬 허용: 켬" : "시뮬 허용: 끔";

        if (_useSimulation)
        {
            _vm.PlcStatusText = "SIMULATION";
            _vm.PlcStatusBrush = Brushes.Goldenrod;
        }
        else if (_plc.IsConnected)
        {
            _vm.PlcStatusText = "Connected";
            _vm.PlcStatusBrush = Brushes.LimeGreen;
        }
        else
        {
            _vm.PlcStatusText = _simulationFallbackEnabled ? "Disconnected" : "Disconnected (PLC 필수)";
            _vm.PlcStatusBrush = Brushes.OrangeRed;
        }

        if (!_flaskProbeDone)
        {
            _vm.FlaskStatusText = "…";
            _vm.FlaskStatusBrush = Brushes.Goldenrod;
        }
        else
        {
            _vm.FlaskStatusText = _flaskReachable ? "OK" : "OFF";
            _vm.FlaskStatusBrush = _flaskReachable ? Brushes.LimeGreen : Brushes.OrangeRed;
        }

        _vm.LastUpdateText = DateTime.Now.ToString("HH:mm:ss");

        if (_lastProcessSampleUtc == DateTime.MinValue)
        {
            _vm.DataQualityText = "유효 샘플 없음";
            _vm.DataQualityBrush = Brushes.OrangeRed;
        }
        else if (_useSimulation)
        {
            _vm.DataQualityText = "시뮬 · " + _lastProcessSampleUtc.ToLocalTime().ToString("HH:mm:ss");
            _vm.DataQualityBrush = Brushes.Goldenrod;
        }
        else
        {
            _vm.DataQualityText = "PLC ADS · " + _lastProcessSampleUtc.ToLocalTime().ToString("HH:mm:ss");
            _vm.DataQualityBrush = Brushes.DeepSkyBlue;
        }

        _vm.StateText = _state.ToString().ToUpperInvariant();
        _vm.StateBrush = _state switch
        {
            EquipmentState.Running => Brushes.LimeGreen,
            EquipmentState.Warning => Brushes.Goldenrod,
            EquipmentState.Alarm => Brushes.OrangeRed,
            EquipmentState.Maintenance => Brushes.MediumPurple,
            _ => Brushes.DodgerBlue,
        };

        string? code = _state == EquipmentState.Alarm ? ComputePrimaryAlarmCode() : null;
        _vm.AlarmCodeText = code ?? "-";
        _vm.AlarmCodeBrush = code is null ? Brushes.DimGray : Brushes.OrangeRed;

        var alarmInfo = AlarmCatalog.TryGet(code);
        if (alarmInfo.HasValue)
        {
            AlarmCatalog.AlarmInfo ai = alarmInfo.Value;
            _vm.AlarmDetailText = $"{ai.Detail}\n▶ 조치: {ai.Action}";
            _vm.AlarmDetailBrush = Brushes.DarkRed;
        }
        else if (_state == EquipmentState.Warning)
        {
            _vm.AlarmDetailText = "환경(온·습도)이 편향되었습니다. 공정 유지 시 모니터링을 강화하세요.";
            _vm.AlarmDetailBrush = Brushes.DarkGoldenrod;
        }
        else
        {
            _vm.AlarmDetailText =
                $"정상 대역: 압력 {AppSettings.PressureKpaMin:F1}–{AppSettings.PressureKpaMax:F1} kPa " +
                $"(스케일 {AppSettings.PressureKpaAt0Percent:F0}–{AppSettings.PressureKpaAt100Percent:F0}), " +
                $"진동 ≤ {AppSettings.VibrationGMax:F2} g, 온도 {AppSettings.TempCMin:F1}–{AppSettings.TempCMax:F1} ℃, " +
                $"습도 {AppSettings.HumiMin:F1}–{AppSettings.HumiMax:F1} %";
            _vm.AlarmDetailBrush = Brushes.DimGray;
        }

        _vm.ProcessPhaseText = DescribeProcessPhase(_state);
        _vm.TemperatureText = _temp.ToString("F2");
        _vm.HumidityText = _humi.ToString("F2");
        _vm.VibrationText = _vib.ToString("F2");
        _vm.AccessText = _accessSafe ? "SAFE" : "DETECTED";
        _vm.AccessBrush = _accessSafe ? Brushes.ForestGreen : Brushes.OrangeRed;

        if (!_pressureSignalValid && !_useSimulation)
        {
            _vm.PressureText = "—";
            _vm.PressureDetailText =
                $"PLC 압력 신호 없음 (raw {_pressureRaw} < {AppSettings.PressureRawMin}). 예전 로직은 이때 95 kPa로 보였음.";
        }
        else
        {
            _vm.PressureText = _pressure.ToString("F2");
            if (_useSimulation)
            {
                _vm.PressureDetailText =
                    $"시뮬 · {_pressurePercent:F0}% → 기본 {PlcAnalogScaling.PressurePercentToKpa(50):F1} kPa";
            }
            else
            {
                _vm.PressureDetailText =
                    $"PLC raw {_pressureRaw} → {_pressurePercent:F1}% → kPa (맵 {AppSettings.PressureKpaAt0Percent:F0}–{AppSettings.PressureKpaAt100Percent:F0})";
            }
        }

        _vm.InterlockPlcText = $"[{ToMark(PlcLinkOk)}] PLC/시뮬 통신";
        _vm.InterlockPressureText = _pressureSignalValid || _useSimulation
            ? $"[{ToMark(IsPressureNormal)}] 압력 정상"
            : "[✗] 압력 신호 없음";
        _vm.InterlockVibText = $"[{ToMark(IsVibrationNormal)}] 진동 정상";
        _vm.InterlockAccessText = $"[{ToMark(_accessSafe)}] 접근 안전";
        _vm.InterlockTempText = $"[{ToMark(IsTempNormal)}] 온도 정상";
        _vm.InterlockHumiText = $"[{ToMark(IsHumiNormal)}] 습도 정상";
        _vm.InterlockResultText = InterlockOk ? "공정 시작 가능" : "공정 시작 불가";
        _vm.InterlockResultBrush = InterlockOk ? Brushes.ForestGreen : Brushes.OrangeRed;

        _vm.LampReadyOn = _state == EquipmentState.Ready;
        _vm.LampRunOn = _state == EquipmentState.Running;
        _vm.LampWarnOn = _state == EquipmentState.Warning;
        _vm.LampAlarmOn = _state == EquipmentState.Alarm;

        _vm.CanStart = SessionContext.HasRole(UserRole.Worker);
        _vm.CanStop = SessionContext.HasRole(UserRole.Worker);
        _vm.CanReset = SessionContext.HasRole(UserRole.Admin);
        _vm.CanMaint = SessionContext.HasRole(UserRole.Admin);
    }

    private static string DescribeProcessPhase(EquipmentState state) =>
        state switch
        {
            EquipmentState.Maintenance => "MAINTENANCE · 현장 유지보수",
            EquipmentState.Running => "CHAMBER · 공정 운전 중",
            EquipmentState.Alarm => "ALARM · 안전/공정 조건 점검 필요",
            EquipmentState.Warning => "WARNING · 환경 편차 모니터링",
            EquipmentState.Ready => "LOAD_LOCK · 공정 시작 가능",
            _ => "LOAD_LOCK · 대기 (IDLE)",
        };

    private static string ToMark(bool ok) => ok ? "✓" : "✗";

    private void AddLog(string message)
    {
        _vm.PrependLog($"{DateTime.Now:HH:mm:ss} | {message}");
    }

    private void BtnStart_Click(object sender, RoutedEventArgs e) => RequestStart("UI Start");

    private void BtnStop_Click(object sender, RoutedEventArgs e) => RequestStop("UI Stop");

    private void BtnReset_Click(object sender, RoutedEventArgs e) => RequestReset("UI Reset");

    private void BtnMaint_Click(object sender, RoutedEventArgs e) => RequestMaintenanceToggle("UI Maint");

    private void RequestStart(string source)
    {
        if (!SessionContext.HasRole(UserRole.Worker))
        {
            AddLog("권한 부족: Start 불가");
            return;
        }

        if (_maintenanceMode)
        {
            AddLog("MAINTENANCE 모드에서는 Start 불가");
            return;
        }

        if (!InterlockOk)
        {
            _state = EquipmentState.Alarm;
            string ac = ComputePrimaryAlarmCode() ?? "A004";
            _db.AppendEventLog(CurrentUserName(), "ALARM", ac, $"{source}: 인터락 불만족 Start 차단");
            AddLog($"{source}: {ac} 인터락 불만족 Start 차단");
            SyncViewModel();
            return;
        }

        _state = EquipmentState.Running;
        _db.AppendEventLog(CurrentUserName(), "RUNNING", null, $"{source}: 운전 시작");
        AddLog($"{source}: RUNNING 진입");
        SyncViewModel();
    }

    private void RequestStop(string source)
    {
        if (!SessionContext.HasRole(UserRole.Worker))
        {
            AddLog("권한 부족: Stop 불가");
            return;
        }

        _state = InterlockOk ? EquipmentState.Ready : EquipmentState.Idle;
        _db.AppendEventLog(CurrentUserName(), _state.ToString().ToUpperInvariant(), null, $"{source}: 정지");
        AddLog($"{source}: Stop");
        SyncViewModel();
    }

    private void RequestReset(string source)
    {
        if (!SessionContext.HasRole(UserRole.Admin))
        {
            AddLog("권한 부족: Alarm Reset 불가");
            return;
        }

        if (_state == EquipmentState.Alarm && InterlockOk)
        {
            _state = EquipmentState.Ready;
            _db.AppendEventLog(CurrentUserName(), "READY", null, $"{source}: Alarm Reset 완료");
            AddLog($"{source}: Alarm Reset 완료");
        }
        else if (_state == EquipmentState.Alarm)
        {
            AddLog($"{source}: Alarm Reset 실패 — 인터락 미충족");
        }
        else
        {
            AddLog($"{source}: Reset");
        }

        SyncViewModel();
    }

    private void RequestMaintenanceToggle(string source)
    {
        if (!SessionContext.HasRole(UserRole.Admin))
        {
            AddLog("권한 부족: Maintenance 불가");
            return;
        }

        _maintenanceMode = !_maintenanceMode;
        _state = _maintenanceMode ? EquipmentState.Maintenance : EquipmentState.Idle;
        _db.AppendEventLog(CurrentUserName(), _state.ToString().ToUpperInvariant(), null,
            _maintenanceMode ? $"{source}: 유지보수 진입" : $"{source}: 유지보수 해제");
        AddLog(_maintenanceMode ? $"{source}: 유지보수 모드" : $"{source}: 일반 모드");
        SyncViewModel();
    }

    private async Task PublishFlaskAsync()
    {
        try
        {
            var payload = new EtchTelemetryPayload
            {
                EquipmentId = 1,
                PowerOn = true,
                Connected = !_useSimulation && _plc.IsConnected,
                LastUpdate = DateTime.UtcNow.ToString("o"),
                Temperature = _temp,
                Humidity = _humi,
                Pressure = _pressure,
                Vibration = _vib,
                AccessSafe = _accessSafe,
                EquipmentState = _state.ToString().ToUpperInvariant(),
                AlarmCode = _state == EquipmentState.Alarm ? ComputePrimaryAlarmCode() : null,
                InterlockOk = InterlockOk,
                Username = CurrentUserName()
            };

            bool ok = await _flask.TryPostEtchSensorDataAsync(payload).ConfigureAwait(false);
            Dispatcher.Invoke(() =>
            {
                _flaskReachable = ok;
                if (!ok)
                {
                    if (DateTime.UtcNow >= _nextFlaskFailLogUtc)
                    {
                        _nextFlaskFailLogUtc = DateTime.UtcNow.AddSeconds(25);
                        AddLog($"Flask 전송 실패 — {_flask.BaseUrl} 서버·방화벽 확인");
                    }
                }

                SyncViewModel();
            });
        }
        catch
        {
            // ignore
        }
    }

    private void LogStateTransitionIfNeeded()
    {
        EquipmentState previous = _lastLoggedState;
        if (_state == previous)
        {
            return;
        }

        _lastLoggedState = _state;
        _db.AppendEventLog(CurrentUserName(), _state.ToString().ToUpperInvariant(), null, "상태 전이");

        string? ac = ComputePrimaryAlarmCode();
        if (_state == EquipmentState.Alarm && ac is not null && ac != _lastAlarmCode)
        {
            _lastAlarmCode = ac;
            _db.AppendEventLog(CurrentUserName(), "ALARM", ac, "알람 코드 갱신");
        }
        else if (previous == EquipmentState.Alarm && _state != EquipmentState.Alarm)
        {
            _lastAlarmCode = null;
        }
    }

    private void BtnSimAllow_Click(object sender, RoutedEventArgs e)
    {
        _simulationFallbackEnabled = !_simulationFallbackEnabled;
        if (_simulationFallbackEnabled)
        {
            AddLog("시뮬 허용 ON — PLC 끊기면 데모 센서로 대체합니다.");
            if (_plc.TryReadSnapshot(out PlcProcessSnapshot snap))
            {
                _useSimulation = false;
                ApplyPlcSnapshot(snap);
            }
            else if (_plc.TryConnect(AppSettings.AdsPort) && _plc.TryReadSnapshot(out snap))
            {
                _useSimulation = false;
                ApplyPlcSnapshot(snap);
            }
            else
            {
                _useSimulation = true;
                SeedSimulationValues();
                AddLog("PLC 미연결 — 지금부터 시뮬 데이터 사용.");
            }
        }
        else
        {
            AddLog("시뮬 허용 OFF — PLC 실데이터만 사용합니다.");
            _useSimulation = false;
            if (_plc.TryConnect(AppSettings.AdsPort) && _plc.TryReadSnapshot(out PlcProcessSnapshot snap))
            {
                ApplyPlcSnapshot(snap);
            }
            else
            {
                ApplyOfflineSensorPlaceholder();
                _loggedPlcRequiredOffline = true;
                AddLog("PLC 데이터 없음 — 오프라인 표시.");
            }
        }

        AutoEvaluateState();
        PushOutputsToPlc();
        SyncViewModel();
    }

    private void BtnUserManage_Click(object sender, RoutedEventArgs e)
    {
        if (!SessionContext.HasRole(UserRole.Admin))
        {
            return;
        }

        var dialog = new UserManagementWindow(_db)
        {
            Owner = this
        };
        dialog.ShowDialog();
    }

    private void BtnLogout_Click(object sender, RoutedEventArgs e)
    {
        _db.AppendEventLog(CurrentUserName(), null, null, "로그아웃");
        SessionContext.Clear();
        Application.Current.Shutdown();
    }

    private void ApplyRolePermissions()
    {
        if (SessionContext.CurrentUser is null)
        {
            AddLog("로그인 사용자 없음");
            return;
        }

        AddLog($"로그인: {SessionContext.CurrentUser.Username} ({SessionContext.CurrentUser.Role.ToDisplayKorean()})");
    }

    private static string? CurrentUserName() => SessionContext.CurrentUser?.Username;
}
