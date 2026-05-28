using System.Net.Http;
using System.Threading;
using System.Text;
using System.Text.Json;

namespace etch_ui.Services;

public sealed class EtchFlaskClient : IDisposable
{
    private static readonly JsonSerializerOptions JsonOptions = new()
    {
        PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
        WriteIndented = false
    };

    private readonly HttpClient _http = new()
    {
        Timeout = TimeSpan.FromSeconds(10)
    };

    public string BaseUrl { get; set; } = "http://127.0.0.1:5000";

    public async Task<bool> TryHealthCheckAsync(CancellationToken cancellationToken = default)
    {
        try
        {
            using HttpResponseMessage response = await _http
                .GetAsync($"{BaseUrl.TrimEnd('/')}/api/sensors", cancellationToken)
                .ConfigureAwait(false);
            return response.IsSuccessStatusCode;
        }
        catch
        {
            return false;
        }
    }

    public async Task<bool> TryPostEtchSensorDataAsync(EtchTelemetryPayload payload)
    {
        try
        {
            string json = JsonSerializer.Serialize(payload, JsonOptions);
            using var content = new StringContent(json, Encoding.UTF8, "application/json");
            using HttpResponseMessage response = await _http.PostAsync($"{BaseUrl.TrimEnd('/')}/api/etch/sensor-data", content)
                .ConfigureAwait(false);
            return response.IsSuccessStatusCode;
        }
        catch
        {
            return false;
        }
    }

    public void Dispose() => _http.Dispose();
}

public sealed class EtchTelemetryPayload
{
    public int EquipmentId { get; set; } = 1;
    public bool PowerOn { get; set; } = true;
    public bool Connected { get; set; }
    public string LastUpdate { get; set; } = string.Empty;
    public double Temperature { get; set; }
    public double Humidity { get; set; }
    public double Pressure { get; set; }
    public double Vibration { get; set; }
    public bool AccessSafe { get; set; }
    public string EquipmentState { get; set; } = string.Empty;
    public string? AlarmCode { get; set; }
    public bool InterlockOk { get; set; }
    public string? Username { get; set; }
}
