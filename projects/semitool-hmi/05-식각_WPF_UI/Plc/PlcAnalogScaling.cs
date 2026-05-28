namespace etch_ui.Plc;

internal static class PlcAnalogScaling
{
    public static double Clamp(double value, double min, double max)
    {
        if (value < min) return min;
        if (value > max) return max;
        return value;
    }

    public static double ScaleLinear(double raw, double rawMin, double rawMax, double valueMin, double valueMax)
    {
        if (Math.Abs(rawMax - rawMin) < double.Epsilon)
            return valueMin;

        double ratio = (raw - rawMin) / (rawMax - rawMin);
        return valueMin + ratio * (valueMax - valueMin);
    }

    public static double ConvertTemperatureCelsius(short raw)
    {
        const double slope = 0.010256;
        const double intercept = -21.0;
        return slope * raw + intercept;
    }

    public static (double HumidityPercent, double TemperatureC, double PressurePercent, bool PressureValid, double VibrationPercent)
        ToEngineering(AnalogInputData data)
    {
        double humidityPercent = Clamp(ScaleLinear(data.HumiditySensor, 5500, 7550, 68, 94), 0, 100);
        double temperatureC = Clamp(ConvertTemperatureCelsius(data.TemperatureSensor), -10, 60);

        bool pressureValid = TryPressurePercent(data.PressureSensor, out double pressurePercent);

        double vibrationPercent = Clamp(ScaleLinear(data.VibrationSensor, 450, 6500, 0, 100), 0, 100);

        return (humidityPercent, temperatureC, pressurePercent, pressureValid, vibrationPercent);
    }

    /// <summary>PLC 압력 채널 raw → 0~100%. raw &lt; PressureRawMin 이면 신호 없음(false).</summary>
    public static bool TryPressurePercent(short raw, out double pressurePercent)
    {
        int rawMin = AppSettings.PressureRawMin;
        int rawMax = AppSettings.PressureRawMax;

        if (raw < rawMin)
        {
            pressurePercent = 0;
            return false;
        }

        if (raw > rawMax)
        {
            pressurePercent = 100.0;
        }
        else
        {
            pressurePercent = ScaleLinear(raw, rawMin, rawMax, 0, 100);
        }

        pressurePercent = Clamp(pressurePercent, 0, 100);
        return true;
    }

    public static double PressurePercentToKpa(double pressurePercent)
    {
        double k0 = AppSettings.PressureKpaAt0Percent;
        double k100 = AppSettings.PressureKpaAt100Percent;
        return k0 + pressurePercent / 100.0 * (k100 - k0);
    }

    public static double VibrationPercentToG(double vibrationPercent)
        => vibrationPercent / 100.0 * 2.0;
}
