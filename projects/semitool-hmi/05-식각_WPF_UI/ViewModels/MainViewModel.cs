using System.Collections.ObjectModel;
using System.Windows.Media;
using etch_ui.Security;

namespace etch_ui.ViewModels;

/// <summary>메인 HMI 화면 바인딩용 (코드비하인드가 주기적으로 SyncFromRuntime 호출).</summary>
public sealed class MainViewModel : ViewModelBase
{
    private string _currentUserText = "-";
    private bool _showUserManage;
    private string _simAllowButtonText = "시뮬 허용: 끔";
    private string _plcStatusText = "Disconnected";
    private Brush _plcStatusBrush = Brushes.OrangeRed;
    private string _flaskStatusText = "확인 중";
    private Brush _flaskStatusBrush = Brushes.Goldenrod;
    private string _lastUpdateText = "-";
    private string _dataQualityText = "-";
    private Brush _dataQualityBrush = Brushes.LightSteelBlue;

    private string _stateText = "IDLE";
    private Brush _stateBrush = Brushes.DodgerBlue;
    private string _alarmCodeText = "-";
    private Brush _alarmCodeBrush = Brushes.DimGray;
    private string _alarmDetailText = "";
    private Brush _alarmDetailBrush = Brushes.DimGray;
    private string _processPhaseText = "LOAD_LOCK · 대기 (IDLE)";

    private string _temperatureText = "0.00";
    private string _humidityText = "0.00";
    private string _pressureText = "—";
    private string _pressureDetailText = "";
    private string _vibrationText = "0.00";
    private string _accessText = "SAFE";
    private Brush _accessBrush = Brushes.ForestGreen;

    private string _interlockPlcText = "[✗] PLC/시뮬 통신";
    private string _interlockPressureText = "[✗] 압력 정상";
    private string _interlockVibText = "[✗] 진동 정상";
    private string _interlockAccessText = "[✗] 접근 안전";
    private string _interlockTempText = "[✗] 온도 정상";
    private string _interlockHumiText = "[✗] 습도 정상";
    private string _interlockResultText = "공정 시작 불가";
    private Brush _interlockResultBrush = Brushes.OrangeRed;

    private bool _lampReadyOn;
    private bool _lampRunOn;
    private bool _lampWarnOn;
    private bool _lampAlarmOn;

    private bool _canStart;
    private bool _canStop;
    private bool _canReset;
    private bool _canMaint;

    public ObservableCollection<string> LogLines { get; } = new();

    public string CurrentUserText
    {
        get => _currentUserText;
        set => SetField(ref _currentUserText, value);
    }

    public bool ShowUserManage
    {
        get => _showUserManage;
        set => SetField(ref _showUserManage, value);
    }

    public string SimAllowButtonText
    {
        get => _simAllowButtonText;
        set => SetField(ref _simAllowButtonText, value);
    }

    public string PlcStatusText
    {
        get => _plcStatusText;
        set => SetField(ref _plcStatusText, value);
    }

    public Brush PlcStatusBrush
    {
        get => _plcStatusBrush;
        set => SetField(ref _plcStatusBrush, value);
    }

    public string FlaskStatusText
    {
        get => _flaskStatusText;
        set => SetField(ref _flaskStatusText, value);
    }

    public Brush FlaskStatusBrush
    {
        get => _flaskStatusBrush;
        set => SetField(ref _flaskStatusBrush, value);
    }

    public string LastUpdateText
    {
        get => _lastUpdateText;
        set => SetField(ref _lastUpdateText, value);
    }

    public string DataQualityText
    {
        get => _dataQualityText;
        set => SetField(ref _dataQualityText, value);
    }

    public Brush DataQualityBrush
    {
        get => _dataQualityBrush;
        set => SetField(ref _dataQualityBrush, value);
    }

    public string StateText
    {
        get => _stateText;
        set => SetField(ref _stateText, value);
    }

    public Brush StateBrush
    {
        get => _stateBrush;
        set => SetField(ref _stateBrush, value);
    }

    public string AlarmCodeText
    {
        get => _alarmCodeText;
        set => SetField(ref _alarmCodeText, value);
    }

    public Brush AlarmCodeBrush
    {
        get => _alarmCodeBrush;
        set => SetField(ref _alarmCodeBrush, value);
    }

    public string AlarmDetailText
    {
        get => _alarmDetailText;
        set => SetField(ref _alarmDetailText, value);
    }

    public Brush AlarmDetailBrush
    {
        get => _alarmDetailBrush;
        set => SetField(ref _alarmDetailBrush, value);
    }

    public string ProcessPhaseText
    {
        get => _processPhaseText;
        set => SetField(ref _processPhaseText, value);
    }

    public string TemperatureText
    {
        get => _temperatureText;
        set => SetField(ref _temperatureText, value);
    }

    public string HumidityText
    {
        get => _humidityText;
        set => SetField(ref _humidityText, value);
    }

    public string PressureText
    {
        get => _pressureText;
        set => SetField(ref _pressureText, value);
    }

    /// <summary>PLC raw·% 등 부가 설명(압력 스케일 확인용).</summary>
    public string PressureDetailText
    {
        get => _pressureDetailText;
        set => SetField(ref _pressureDetailText, value);
    }

    public string VibrationText
    {
        get => _vibrationText;
        set => SetField(ref _vibrationText, value);
    }

    public string AccessText
    {
        get => _accessText;
        set => SetField(ref _accessText, value);
    }

    public Brush AccessBrush
    {
        get => _accessBrush;
        set => SetField(ref _accessBrush, value);
    }

    public string InterlockPlcText
    {
        get => _interlockPlcText;
        set => SetField(ref _interlockPlcText, value);
    }

    public string InterlockPressureText
    {
        get => _interlockPressureText;
        set => SetField(ref _interlockPressureText, value);
    }

    public string InterlockVibText
    {
        get => _interlockVibText;
        set => SetField(ref _interlockVibText, value);
    }

    public string InterlockAccessText
    {
        get => _interlockAccessText;
        set => SetField(ref _interlockAccessText, value);
    }

    public string InterlockTempText
    {
        get => _interlockTempText;
        set => SetField(ref _interlockTempText, value);
    }

    public string InterlockHumiText
    {
        get => _interlockHumiText;
        set => SetField(ref _interlockHumiText, value);
    }

    public string InterlockResultText
    {
        get => _interlockResultText;
        set => SetField(ref _interlockResultText, value);
    }

    public Brush InterlockResultBrush
    {
        get => _interlockResultBrush;
        set => SetField(ref _interlockResultBrush, value);
    }

    public bool LampReadyOn
    {
        get => _lampReadyOn;
        set => SetField(ref _lampReadyOn, value);
    }

    public bool LampRunOn
    {
        get => _lampRunOn;
        set => SetField(ref _lampRunOn, value);
    }

    public bool LampWarnOn
    {
        get => _lampWarnOn;
        set => SetField(ref _lampWarnOn, value);
    }

    public bool LampAlarmOn
    {
        get => _lampAlarmOn;
        set => SetField(ref _lampAlarmOn, value);
    }

    public bool CanStart
    {
        get => _canStart;
        set => SetField(ref _canStart, value);
    }

    public bool CanStop
    {
        get => _canStop;
        set => SetField(ref _canStop, value);
    }

    public bool CanReset
    {
        get => _canReset;
        set => SetField(ref _canReset, value);
    }

    public bool CanMaint
    {
        get => _canMaint;
        set => SetField(ref _canMaint, value);
    }

    public void PrependLog(string line)
    {
        LogLines.Insert(0, line);
        while (LogLines.Count > 200)
        {
            LogLines.RemoveAt(LogLines.Count - 1);
        }
    }
}
