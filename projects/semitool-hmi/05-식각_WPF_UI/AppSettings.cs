using System.IO;
using System.Text.Json;
using etch_ui.Plc;

namespace etch_ui;

/// <summary>
/// 출력 폴더의 appsettings.json (없으면 기본값).
/// </summary>
public static class AppSettings
{
    public static string FlaskBaseUrl { get; }
    public static int AdsPort { get; }

    /// <summary>
    /// 시작 시 시뮬 허용 여부(메인 창에서 변경 가능, 앱 재시작 시 여기서 다시 읽음).
    /// </summary>
    public static bool SimulationEnabled { get; }

    public static double PressureKpaMin { get; }
    public static double PressureKpaMax { get; }
    public static double VibrationGMax { get; }
    public static double TempCMin { get; }
    public static double TempCMax { get; }
    public static double HumiMin { get; }
    public static double HumiMax { get; }

    /// <summary>PLC 압력 raw 이 값 미만이면 신호 없음(표시 —, 인터락 NG).</summary>
    public static int PressureRawMin { get; }

    public static int PressureRawMax { get; }

    /// <summary>압력 0% 일 때 kPa (기본 95).</summary>
    public static double PressureKpaAt0Percent { get; }

    /// <summary>압력 100% 일 때 kPa (기본 100). 50% → (95+100)/2 = 97.5 kPa.</summary>
    public static double PressureKpaAt100Percent { get; }

    static AppSettings()
    {
        FlaskBaseUrl = "http://127.0.0.1:5000";
        AdsPort = PlcAdsService.DefaultPort;
        SimulationEnabled = false;
        PressureKpaMin = 95.0;
        PressureKpaMax = 100.0;
        PressureRawMin = 5;
        PressureRawMax = 3575;
        PressureKpaAt0Percent = 95.0;
        PressureKpaAt100Percent = 100.0;
        VibrationGMax = 0.80;
        TempCMin = 20.0;
        TempCMax = 30.0;
        HumiMin = 30.0;
        HumiMax = 55.0;

        try
        {
            string path = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "appsettings.json");
            if (!File.Exists(path))
            {
                return;
            }

            using JsonDocument doc = JsonDocument.Parse(File.ReadAllText(path));
            JsonElement root = doc.RootElement;
            if (root.TryGetProperty("FlaskBaseUrl", out JsonElement f))
            {
                string? u = f.GetString();
                if (!string.IsNullOrWhiteSpace(u))
                {
                    FlaskBaseUrl = u.TrimEnd('/');
                }
            }

            if (root.TryGetProperty("AdsPort", out JsonElement p) && p.TryGetInt32(out int port) && port > 0)
            {
                AdsPort = port;
            }

            if (root.TryGetProperty("SimulationEnabled", out JsonElement s))
            {
                if (s.ValueKind is JsonValueKind.True or JsonValueKind.False)
                {
                    SimulationEnabled = s.GetBoolean();
                }
                else if (s.ValueKind is JsonValueKind.Number && s.TryGetInt32(out int n))
                {
                    SimulationEnabled = n != 0;
                }
            }

            if (root.TryGetProperty("Interlock", out JsonElement il) && il.ValueKind == JsonValueKind.Object)
            {
                if (il.TryGetProperty("PressureKpaMin", out JsonElement pmin) && pmin.TryGetDouble(out double pkMin))
                {
                    PressureKpaMin = pkMin;
                }

                if (il.TryGetProperty("PressureKpaMax", out JsonElement pmax) && pmax.TryGetDouble(out double pkMax))
                {
                    PressureKpaMax = pkMax;
                }

                if (il.TryGetProperty("VibrationGMax", out JsonElement vib) && vib.TryGetDouble(out double vibMax))
                {
                    VibrationGMax = vibMax;
                }

                if (il.TryGetProperty("TempCMin", out JsonElement tMn) && tMn.TryGetDouble(out double tMin))
                {
                    TempCMin = tMin;
                }

                if (il.TryGetProperty("TempCMax", out JsonElement tMx) && tMx.TryGetDouble(out double tMax))
                {
                    TempCMax = tMax;
                }

                if (il.TryGetProperty("HumiMin", out JsonElement hMn) && hMn.TryGetDouble(out double huMin))
                {
                    HumiMin = huMin;
                }

                if (il.TryGetProperty("HumiMax", out JsonElement hMx) && hMx.TryGetDouble(out double huMax))
                {
                    HumiMax = huMax;
                }
            }

            if (root.TryGetProperty("PressureScale", out JsonElement ps) && ps.ValueKind == JsonValueKind.Object)
            {
                if (ps.TryGetProperty("RawMin", out JsonElement rmn) && rmn.TryGetInt32(out int rawMin))
                {
                    PressureRawMin = rawMin;
                }

                if (ps.TryGetProperty("RawMax", out JsonElement rmx) && rmx.TryGetInt32(out int rawMax))
                {
                    PressureRawMax = rawMax;
                }

                if (ps.TryGetProperty("KpaAt0Percent", out JsonElement k0) && k0.TryGetDouble(out double kpa0))
                {
                    PressureKpaAt0Percent = kpa0;
                }

                if (ps.TryGetProperty("KpaAt100Percent", out JsonElement k100) && k100.TryGetDouble(out double kpa100))
                {
                    PressureKpaAt100Percent = kpa100;
                }
            }
        }
        catch
        {
            // 기본값 유지
        }
    }
}
