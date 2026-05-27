// ★★★★★ 스마트 물류창고 HMI - Form1.cs (FINAL FULL VERSION) ★★★★★

using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.Drawing;
using System.Net.Http;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;
using System.Windows.Forms.DataVisualization.Charting;
using TwinCAT.Ads;

namespace flaskConnect
{
    public partial class Form1 : Form
    {
        // =====================================================================
        // 필드 / 변수
        // =====================================================================

        private Timer timerBlink = new Timer();
        private Timer timerUpdate = new Timer();
        private bool doorOpenForced = false;
        private bool doorCloseForced = false;
        private bool preventEventAfterNormalize = false;
        // -----------------------------------------------------
        // 온도/습도 기준값 (정상/냉장/냉동 모드 허용 범위)
        // -----------------------------------------------------
        private double TempNormalMin = 10;
        private double TempNormalMax = 30;
        private double HumNormalMin = 20;
        private double HumNormalMax = 60;

        private double TempColdMin = 2;
        private double TempColdMax = 8;
        private double HumColdMin = 60;
        private double HumColdMax = 80;

        private double TempFreezeMin = -25;
        private double TempFreezeMax = -16;
        private double HumFreezeMin = 40;
        private double HumFreezeMax = 60;

        // 정상화 종료 후 RAW 센서 1회 무시용 플래그
        private bool skipRawOnceAfterNormalize = false;

        private AdsClient client;
        private HttpClient http = new HttpClient();

        // 아날로그 센서 핸들
        private uint hTempRaw, hHumRaw, hVibRaw, hPresRaw;

        // 디지털 출력
        private uint hLamp1, hLamp2, hLamp3, hLamp4;

        // 디지털 입력
        private uint hDI0, hDI1, hDI2, hDI3;

        // 이벤트 플래그
        private bool alarmPressureLatch = false;
        private bool vibAlarm = false;
        private bool fireMode = false;
        private bool emergencyMode = false;
        private bool powerAlarm = false;

        private bool blinkState = false;

        // 모드 및 전원
        private string manualMode = null;
        private string plcMode = null;
        private string flaskMode = null;
        private bool plcPowerOn = false;

        private bool prevDI0, prevDI1, prevDI2, prevDI3;

        // 정상화 관련
        private bool isNormalizing = false;
        private bool eventsClearedForNormalize = false;
        private DateTime normalizeStartTime;

        private double startTemp, startHum, startVib, startPres;
        private double targetTemp, targetHum, targetVib = 0, targetPres = 100;

        // 누적 값
        private double coldTempAccum = 0, coldHumAccum = 0;
        private double freezeTempAccum = 0, freezeHumAccum = 0;

        // 최근 표시값
        private double lastTemp = 0, lastHum = 0;

        // 계산된 모드 값
        private double tempNormal, tempCold, tempFreeze;
        private double humNormal, humCold, humFreeze;
        private double vibNormal, vibCold, vibFreeze;
        private double presNormal, presCold, presFreeze;


        // =====================================================================
        // 생성자
        // =====================================================================
        // 정전 이벤트 관련
        private bool blackoutEvent = false;
        private bool lastBlackoutEvent = false;

        // 정상화 램핑용 시작값
        private double startTempCold, startHumCold;
        private double startTempFreeze, startHumFreeze;

        // 수동 정상화 트리거 (정전 해제 시 사용)
        private bool manualNormalizeTrigger = false;

        // ★ 화재 시뮬레이션 변수 ★
        private bool isFireSimulating = false;
        private DateTime fireStartTime;
        private double startTempNormalFire, startHumNormalFire;
        private double startTempColdFire, startHumColdFire;
        private double startTempFreezeFire, startHumFreezeFire;

        // ★ 진동 시뮬레이션 변수 ★
        private bool simulateVibEvent = false;
        private double displayedVib = 0; // 진동 표시값 (감쇠용)

        public Form1()
        {
            InitializeComponent();

            client = new AdsClient();

            timerUpdate.Interval = 200;
            timerUpdate.Tick += TimerUpdate_Tick;

            timerBlink.Interval = 500;
            timerBlink.Tick += timerBlink_Tick;
        }


        // =====================================================================
        // Form Load
        // =====================================================================
        private void Form1_Load(object sender, EventArgs e)
        {
            try
            {
                client.Connect(new AmsNetId("127.0.0.1.1.1"), 851);

                // 센서 핸들
                hTempRaw = client.CreateVariableHandle("GVL.NX_AD4203.Temperature_Sensor");
                hHumRaw = client.CreateVariableHandle("GVL.NX_AD4203.Humidity_Sensor");
                hVibRaw = client.CreateVariableHandle("GVL.NX_AD4203.Vibration_Sensor");
                hPresRaw = client.CreateVariableHandle("GVL.NX_AD4203.Pressure_Sensor");

                // DI
                hDI0 = client.CreateVariableHandle("GVL.NX_ID5342.Button1");
                hDI1 = client.CreateVariableHandle("GVL.NX_ID5342.Button2");
                hDI2 = client.CreateVariableHandle("GVL.NX_ID5342.Button3");
                hDI3 = client.CreateVariableHandle("GVL.NX_ID5342.Button4");

                // DO
                hLamp1 = client.CreateVariableHandle("GVL.NX_OD5121.Lamp1");
                hLamp2 = client.CreateVariableHandle("GVL.NX_OD5121.Lamp2");
                hLamp3 = client.CreateVariableHandle("GVL.NX_OD5121.Lamp3");
                hLamp4 = client.CreateVariableHandle("GVL.NX_OD5121.Lamp4");

                InitSeries();

                timerUpdate.Start();
                timerBlink.Start();

                chartTemp.Visible = false;
                UpdateModeUI(null, 0, 0);
            }
            catch (Exception ex)
            {
                MessageBox.Show("TwinCAT 연결 실패: " + ex.Message);
            }
        }


        // =====================================================================
        // Chart 초기화
        // =====================================================================
        private void InitSeries()
        {
            chartTemp.Series.Clear();

            var sN = chartTemp.Series.Add("일반");
            sN.ChartType = SeriesChartType.Line;
            sN.Color = Color.LimeGreen;
            sN.BorderWidth = 3;

            var sC = chartTemp.Series.Add("냉장");
            sC.ChartType = SeriesChartType.Line;
            sC.Color = Color.DeepSkyBlue;
            sC.BorderWidth = 3;

            var sF = chartTemp.Series.Add("냉동");
            sF.ChartType = SeriesChartType.Line;
            sF.Color = Color.RoyalBlue;
            sF.BorderWidth = 3;
        }


        private async void TimerUpdate_Tick(object sender, EventArgs e)
        {
            if (!client.IsConnected) return;

            try
            {
                double dispT = 0, dispH = 0;

                // =====================================================================
                // 0) Flask 정상화 상태 GET
                // =====================================================================
                bool normalizeFlag = false;
                try
                {
                    var ns = await http.GetStringAsync("http://127.0.0.1:5000/api/normalize/status");
                    var nd = JsonConvert.DeserializeObject<Dictionary<string, bool>>(ns);
                    normalizeFlag = nd.ContainsKey("normalize") && nd["normalize"];
                }
                catch
                {
                    normalizeFlag = false;
                }

                // 수동 트리거 확인
                if (manualNormalizeTrigger)
                {
                    normalizeFlag = true;
                    manualNormalizeTrigger = false;
                }

                // =====================================================================
                // 1) PLC DI 입력 (전원 & 모드)
                // =====================================================================
                bool di0 = (bool)client.ReadAny(hDI0, typeof(bool));
                bool di1 = (bool)client.ReadAny(hDI1, typeof(bool));
                bool di2 = (bool)client.ReadAny(hDI2, typeof(bool));
                bool di3 = (bool)client.ReadAny(hDI3, typeof(bool));

                if (di3 && !prevDI3)
                    plcPowerOn = !plcPowerOn;

                if (di0 && !prevDI0) plcMode = (plcMode == "normal") ? null : "normal";
                if (di1 && !prevDI1) plcMode = (plcMode == "cold") ? null : "cold";
                if (di2 && !prevDI2) plcMode = (plcMode == "freeze") ? null : "freeze";

                prevDI0 = di0; prevDI1 = di1; prevDI2 = di2; prevDI3 = di3;

                // =====================================================================
                // 2) Flask 모드 가져오기
                // =====================================================================
                try
                {
                    var fm = await http.GetStringAsync("http://127.0.0.1:5000/api/mode/status");
                    var fd = JsonConvert.DeserializeObject<Dictionary<string, string>>(fm);
                    if (fd.ContainsKey("mode"))
                        flaskMode = fd["mode"];
                }
                catch
                {
                    flaskMode = null;
                }

                // =====================================================================
                // 3) 전원 OFF → UI 리셋
                // =====================================================================
                if (!plcPowerOn)
                {
                    lblDoorState.Text = "전원: OFF";

                    UpdateModeUI(null, 0, 0);
                    chartTemp.Visible = false;

                    coldTempAccum = coldHumAccum = 0;
                    freezeTempAccum = freezeHumAccum = 0;

                    client.WriteAny(hLamp1, false);
                    client.WriteAny(hLamp2, false);
                    client.WriteAny(hLamp3, false);
                    client.WriteAny(hLamp4, false);

                    alarmPressureLatch = false;
                    vibAlarm = false;
                    powerAlarm = false;
                    fireMode = false;
                    emergencyMode = false;

                    return;
                }

                // 전원은 켜져 있음
                lblDoorState.Text = "전원: ON";
                client.WriteAny(hLamp4, true);
                chartTemp.Visible = true;

                // =====================================================================
                // 4) 최종 모드 결정
                // =====================================================================
                string mode = manualMode ?? plcMode ?? flaskMode;

                // =====================================================================
                // 5) RAW 센서 읽기
                // =====================================================================
                int rawTemp = (int)client.ReadAny(hTempRaw, typeof(int));
                int rawHum = (int)client.ReadAny(hHumRaw, typeof(int));
                int rawVib = (int)client.ReadAny(hVibRaw, typeof(int));
                int rawPres = (int)client.ReadAny(hPresRaw, typeof(int));

                double baseTemp = 27 + (rawTemp - 4720) * (3.0 / (5050 - 4720));
                double baseHum = 28 + (rawHum - 2300) * (55.0 / (6700 - 2300));
                double vibration = rawVib * (5.0 / 32767.0);
                double pressure = 5 + (rawPres - 38) * (461.0 / (3750 - 38));

                // ★ 진동 시뮬레이션 적용 ★
                if (simulateVibEvent)
                {
                    vibration = 0.6;
                }

                // 일반 창고
                tempNormal = baseTemp;
                humNormal = baseHum;

                // 냉장/냉동 모델 적용
                const double COLD_TEMP_OFFSET = -23.6;
                const double COLD_HUM_OFFSET = 66.4;
                const double FREEZE_TEMP_OFFSET = -46.6;
                const double FREEZE_HUM_OFFSET = 63.4;

                tempCold = tempNormal + COLD_TEMP_OFFSET;
                humCold = humNormal + COLD_HUM_OFFSET;

                tempFreeze = tempNormal + FREEZE_TEMP_OFFSET;
                humFreeze = humNormal + FREEZE_HUM_OFFSET;

                vibNormal = vibCold = vibFreeze = vibration;
                presNormal = presCold = presFreeze = pressure;

                // =====================================================================
                // 6) 정상화 시작 처리
                // =====================================================================
                if (normalizeFlag && !isNormalizing)
                {
                    isNormalizing = true;
                    normalizeStartTime = DateTime.Now;

                    // 이벤트 탈출
                    doorCloseForced = true;
                    preventEventAfterNormalize = true;

                    startTemp = lastTemp;
                    startHum = lastHum;
                    startVib = vibration;
                    startPres = pressure;

                    // 개별 창고 램핑 시작값 캡처 (현재 계산된 값 = 기본값 + 누적값)
                    startTempCold = tempCold + coldTempAccum;
                    startHumCold = humCold + coldHumAccum;
                    startTempFreeze = tempFreeze + freezeTempAccum;
                    startHumFreeze = humFreeze + freezeHumAccum;

                    if (mode == "normal")
                    {
                        targetTemp = tempNormal;
                        targetHum = humNormal;
                    }
                    else if (mode == "cold")
                    {
                        targetTemp = tempCold;
                        targetHum = humCold;
                    }
                    else if (mode == "freeze")
                    {
                        targetTemp = tempFreeze;
                        targetHum = humFreeze;
                    }
                    else
                    {
                        targetTemp = lastTemp;
                        targetHum = lastHum;
                    }

                    // 램프 OFF
                    alarmPressureLatch = false;
                    vibAlarm = false;
                    powerAlarm = false;

                    // 누적값 초기화 (정상화 시 기존 누적된 온도 상승분 제거)
                    coldTempAccum = 0;
                    coldHumAccum = 0;
                    freezeTempAccum = 0;
                    freezeHumAccum = 0;

                    client.WriteAny(hLamp1, false);
                    client.WriteAny(hLamp2, false);
                    client.WriteAny(hLamp3, false);
                }

                // =====================================================================
                // 7) 정상화 "진행 중" → 단독 처리
                // =====================================================================
                if (isNormalizing)
                {
                    double t = (DateTime.Now - normalizeStartTime).TotalSeconds / 5.0;
                    if (t >= 1.0)
                    {
                        t = 1.0;
                        isNormalizing = false;
                        skipRawOnceAfterNormalize = true;
                        doorCloseForced = false;
                        preventEventAfterNormalize = false;
                    }

                    // 현재 모드 UI용 램핑
                    double dispTemp = startTemp + (targetTemp - startTemp) * t;
                    double dispHum = startHum + (targetHum - startHum) * t;
                    double dispVib = startVib * (1 - t);
                    double dispPres = startPres + (100 - startPres) * t;

                    UpdateModeUI(mode, dispTemp, dispHum);

                    lblVibVal.Text = $"{dispVib:F3}";
                    lblPresVal.Text = $"{dispPres:F2} kW";

                    lastTemp = dispTemp;
                    lastHum = dispHum;

                    // Flask 전송용 개별 창고 램핑 값 계산
                    // tempNormal은 이미 센서값(baseTemp)이므로 그대로 사용하거나, 필요시 램핑 가능.
                    // 여기서는 냉장/냉동만 램핑 처리 (누적값이 있었으므로)
                    double rampColdT = startTempCold + (tempCold - startTempCold) * t;
                    double rampColdH = startHumCold + (humCold - startHumCold) * t;
                    
                    double rampFreezeT = startTempFreeze + (tempFreeze - startTempFreeze) * t;
                    double rampFreezeH = startHumFreeze + (humFreeze - startHumFreeze) * t;

                    // Flask로 데이터 전송 (정상화 중에도 그래프 업데이트를 위해)
                    await SendSensorDataToFlask(dispTemp, dispHum, dispVib, dispPres, di0, di1, di2, di3,
                                                tempNormal, humNormal, rampColdT, rampColdH, rampFreezeT, rampFreezeH);

                    return; // 이벤트/문/누적 완전 차단
                }

                // =====================================================================
                // 8) 정상화 직후 1회 RAW 무시
                // =====================================================================
                if (skipRawOnceAfterNormalize)
                {
                    skipRawOnceAfterNormalize = false;

                    UpdateModeUI(mode, targetTemp, targetHum);

                    lblVibVal.Text = $"{targetVib:F3}";
                    lblPresVal.Text = $"{targetPres:F2} kW";

                    lastTemp = targetTemp;
                    lastHum = targetHum;

                    return;
                }

                // =====================================================================
                // 9) 이벤트 적용 (정상화가 아닐 때)
                // =====================================================================
                bool doorNormal = false, doorCold = false, doorFreeze = false;

                try
                {
                    var evt = await http.GetStringAsync("http://127.0.0.1:5000/event/get");
                    var ev = JsonConvert.DeserializeObject<Dictionary<string, bool>>(evt);

                    if (!doorCloseForced && !preventEventAfterNormalize)
                    {
                        if (ev.ContainsKey("normal")) doorNormal = ev["normal"];
                        if (ev.ContainsKey("cold")) doorCold = ev["cold"];
                        if (ev.ContainsKey("freeze")) doorFreeze = ev["freeze"];
                    }
                }
                catch
                {
                    // 통신 실패 시 모두 닫힘 처리
                }

                // 정전 및 화재 이벤트 확인
                bool currentFireEvent = false;
                bool firewallActive = false;
                try
                {
                    var evtStatus = await http.GetStringAsync("http://127.0.0.1:5000/api/events/status");
                    var evStatus = JsonConvert.DeserializeObject<Dictionary<string, bool>>(evtStatus);
                    if (evStatus.ContainsKey("blackout_event"))
                    {
                        blackoutEvent = evStatus["blackout_event"];
                    }
                    if (evStatus.ContainsKey("fire_event"))
                    {
                        currentFireEvent = evStatus["fire_event"];
                    }
                    if (evStatus.ContainsKey("vib_event"))
                    {
                        simulateVibEvent = evStatus["vib_event"];
                    }
                    if (evStatus.ContainsKey("firewall_active"))
                    {
                        firewallActive = evStatus["firewall_active"];
                    }
                }
                catch
                {
                    blackoutEvent = false;
                }
                // ★ 진동 0.5 이상 시 정전 이벤트 트리거 (방화벽 가동 전까지 유지) ★
                // 사용자 요청: "진동이 0.5 이상 되면... 정전 이벤트 발생" (기존 0.6 -> 0.5로 조정)
                if (vibration >= 0.5 && !blackoutEvent && !firewallActive)
                {
                    try 
                    {
                        var content = new StringContent("{\"event\":\"blackout_event\",\"active\":true}", Encoding.UTF8, "application/json");
                        await http.PostAsync("http://127.0.0.1:5000/api/events/simulate", content);
                        blackoutEvent = true; 
                    }
                    catch {}
                }
                
                // ★ 방화벽 로직 개선 ★
                // 1. 방화벽 활성 상태에서 진동이 0.5 미만으로 떨어지면 방화벽 해제 요청
                if (firewallActive && vibration < 0.5)
                {
                    try 
                    {
                        var content = new StringContent("{\"active\":false}", Encoding.UTF8, "application/json");
                        await http.PostAsync("http://127.0.0.1:5000/api/firewall", content);
                        firewallActive = false;
                    }
                    catch {}
                }

                // 2. 방화벽 활성 시: 온도/습도 정상값 유지 (강제 오버라이드)
                // 진동 값은 감쇠하지 않고 실제 값(또는 시뮬레이션 값)을 유지하여 0.5 미만 감지 가능하게 함
                if (firewallActive)
                {
                    // 현재 모드에 맞는 목표값으로 강제 설정
                    if (mode == "normal") { tempNormal = targetTemp; humNormal = targetHum; }
                    else if (mode == "cold") { tempCold = targetTemp; humCold = targetHum; }
                    else if (mode == "freeze") { tempFreeze = targetTemp; humFreeze = targetHum; }
                    
                    // 화면 표시용 변수도 강제 설정
                    dispT = targetTemp;
                    dispH = targetHum;
                    
                    // 누적치 초기화 (이벤트 영향 제거)
                    coldTempAccum = 0; coldHumAccum = 0;
                    freezeTempAccum = 0; freezeHumAccum = 0;
                }
                
                // 기존 감쇠 로직 제거 (진동은 리얼타임 반영)
                displayedVib = vibration;
                
                vibration = displayedVib;

                // 정전 이벤트 해제 시 (True -> False) 정상화 트리거
                if (lastBlackoutEvent && !blackoutEvent)
                {
                    manualNormalizeTrigger = true;
                }
                lastBlackoutEvent = blackoutEvent;

                // ★ 화재 시뮬레이션 로직 ★
                if (currentFireEvent && !isFireSimulating)
                {
                    isFireSimulating = true;
                    fireStartTime = DateTime.Now;

                    startTempNormalFire = tempNormal;
                    startHumNormalFire = humNormal;
                    
                    startTempColdFire = tempCold + coldTempAccum;
                    startHumColdFire = humCold + coldHumAccum;
                    
                    startTempFreezeFire = tempFreeze + freezeTempAccum;
                    startHumFreezeFire = humFreeze + freezeHumAccum;
                }
                else if (!currentFireEvent && isFireSimulating)
                {
                    isFireSimulating = false;
                }

                if (isFireSimulating)
                {
                    double t = (DateTime.Now - fireStartTime).TotalSeconds / 10.0;
                    if (t > 1.0) t = 1.0;

                    double targetT = 150.0;
                    double targetH = 0.0;

                    double curNormalT = startTempNormalFire + (targetT - startTempNormalFire) * t;
                    double curNormalH = startHumNormalFire + (targetH - startHumNormalFire) * t;

                    double curColdT = startTempColdFire + (targetT - startTempColdFire) * t;
                    double curColdH = startHumColdFire + (targetH - startHumColdFire) * t;

                    double curFreezeT = startTempFreezeFire + (targetT - startTempFreezeFire) * t;
                    double curFreezeH = startHumFreezeFire + (targetH - startHumFreezeFire) * t;

                    coldTempAccum = 0;
                    coldHumAccum = 0;
                    freezeTempAccum = 0;
                    freezeHumAccum = 0;

                    tempNormal = curNormalT;
                    humNormal = curNormalH;
                    
                    tempCold = curColdT;
                    humCold = curColdH;
                    
                    tempFreeze = curFreezeT;
                    humFreeze = curFreezeH;
                }

                // 전역 누적 (모드와 무관하게 계산)
                if (doorCold || blackoutEvent)
                {
                    coldTempAccum += 0.06;
                    coldHumAccum -= 0.06;
                }

                if (doorFreeze || blackoutEvent)
                {
                    freezeTempAccum += 0.06;
                    freezeHumAccum -= 0.06;
                }



                if (mode == "normal")
                {
                    dispT = tempNormal;
                    dispH = humNormal;
                }
                else if (mode == "cold")
                {
                    dispT = tempCold + coldTempAccum;
                    dispH = humCold + coldHumAccum;
                }
                else if (mode == "freeze")
                {
                    dispT = tempFreeze + freezeTempAccum;
                    dispH = humFreeze + freezeHumAccum;
                }

                if (mode == "cold" || mode == "freeze")
                {
                    dispT = Math.Min(dispT, tempNormal);
                    dispH = Math.Max(0, Math.Min(100, dispH));
                }

                lastTemp = dispT;
                lastHum = dispH;

                // =====================================================================
                // 10) 알람 처리
                // =====================================================================
                vibAlarm = (vibration > 0.3);
                client.WriteAny(hLamp2, vibAlarm);

                alarmPressureLatch = (pressure <= 300);
                client.WriteAny(hLamp3, alarmPressureLatch);

                bool tempOut = false, humOut = false;

                if (mode == "normal")
                {
                    tempOut = dispT < TempNormalMin - 2 || dispT > TempNormalMax + 2;
                    humOut = dispH < HumNormalMin - 2 || dispH > HumNormalMax + 2;
                }
                else if (mode == "cold")
                {
                    tempOut = dispT < TempColdMin - 2 || dispT > TempColdMax + 2;
                    humOut = dispH < HumColdMin - 2 || dispH > HumColdMax + 2;
                }
                else if (mode == "freeze")
                {
                    tempOut = dispT < TempFreezeMin - 2 || dispT > TempFreezeMax + 2;
                    humOut = dispH < HumFreezeMin - 2 || dispH > HumFreezeMax + 2;
                }

                bool anyAlarm = tempOut || humOut || alarmPressureLatch || vibAlarm;
                client.WriteAny(hLamp1, anyAlarm);

                lblAlarmState.Text = anyAlarm ? "ALARM ON" : "ALARM OFF";

                // =====================================================================
                // 11) UI 표시
                // =====================================================================
                UpdateModeUI(mode, dispT, dispH);
                lblVibVal.Text = $"{vibration:F3}";
                lblPresVal.Text = $"{pressure:F2} kW";

                // =====================================================================
                // 12) 그래프 업데이트
                // =====================================================================
                chartTemp.Series["일반"].Points.AddY(tempNormal);
                chartTemp.Series["냉장"].Points.AddY(tempCold);
                chartTemp.Series["냉동"].Points.AddY(tempFreeze);

                foreach (var s in chartTemp.Series)
                    if (s.Points.Count > 300)
                        s.Points.RemoveAt(0);

                // =====================================================================
                // 13) Flask로 센서 데이터 전송
                // =====================================================================
                // dispT/dispH는 현재 모드에 따라 표시되는 값이지만,
                // 웹 대시보드에는 3개 창고 값을 모두 보내야 함.
                // tempNormal, tempCold, tempFreeze 등은 위에서 이미 계산됨.
                
                // 단, 냉장/냉동의 경우 문 열림 누적값(coldTempAccum 등)이 반영된 값을 보내야 함.
                double sendNormalT = tempNormal;
                double sendNormalH = humNormal;
                
                double sendColdT = tempCold + coldTempAccum;
                double sendColdH = humCold + coldHumAccum;
                
                double sendFreezeT = tempFreeze + freezeTempAccum;
                double sendFreezeH = humFreeze + freezeHumAccum;

                // 범위 제한 (냉장/냉동은 일반 온도보다 높을 수 없음 등) - 위 로직 참고
                sendColdT = Math.Min(sendColdT, tempNormal);
                sendColdH = Math.Max(0, Math.Min(100, sendColdH));
                
                sendFreezeT = Math.Min(sendFreezeT, tempNormal);
                sendFreezeH = Math.Max(0, Math.Min(100, sendFreezeH));

                await SendSensorDataToFlask(dispT, dispH, vibration, pressure, di0, di1, di2, di3,
                                            sendNormalT, sendNormalH, sendColdT, sendColdH, sendFreezeT, sendFreezeH);
            }
            catch
            {
            }
        }

        private async Task SendSensorDataToFlask(double temp, double hum, double vib, double pres, bool d0, bool d1, bool d2, bool d3,
                                                 double tNormal, double hNormal, double tCold, double hCold, double tFreeze, double hFreeze)
        {
            try
            {
                var data = new
                {
                    temp = temp,
                    hum = hum,
                    vib = vib,
                    pres = pres,
                    DI0 = d0,
                    DI1 = d1,
                    DI2 = d2,
                    DI3 = d3,
                    
                    // 개별 창고 데이터 추가
                    temp_normal = tNormal,
                    hum_normal = hNormal,
                    temp_cold = tCold,
                    hum_cold = hCold,
                    temp_freeze = tFreeze,
                    hum_freeze = hFreeze
                };

                var json = JsonConvert.SerializeObject(data);
                var content = new StringContent(json, Encoding.UTF8, "application/json");
                await http.PostAsync("http://127.0.0.1:5000/sensor", content);
            }
            catch { }
        }








        // =====================================================================
        // UI 업데이트
        // =====================================================================
        private void UpdateModeUI(string mode, double t, double h)
        {
            ResetModeButtonColor();

            if (mode == null)
            {
                lblModeTitle.Text = "창고 선택 필요";
                lblTempVal.Text = "--";
                lblHumVal.Text = "--";
                return;
            }

            if (mode == "normal") ShowNormalModeUI(t, h);
            else if (mode == "cold") ShowColdModeUI(t, h);
            else if (mode == "freeze") ShowFreezeModeUI(t, h);
        }

        private void ResetModeButtonColor()
        {
            btnModeNormal.BackColor = SystemColors.Control;
            btnModeCold.BackColor = SystemColors.Control;
            btnModeFreeze.BackColor = SystemColors.Control;
        }

        private void ShowNormalModeUI(double temperature, double humidity)
        {
            ResetModeButtonColor();
            btnModeNormal.BackColor = Color.LightGreen;

            lblModeTitle.Text = "일반 모드";
            lblTempVal.Text = $"{temperature:F1} ℃";
            lblHumVal.Text = $"{humidity:F1} %";
        }

        private void ShowColdModeUI(double temperature, double humidity)
        {
            ResetModeButtonColor();
            btnModeCold.BackColor = Color.LightSkyBlue;

            lblModeTitle.Text = "냉장 모드";
            lblTempVal.Text = $"{temperature:F1} ℃";
            lblHumVal.Text = $"{humidity:F1} %";
        }

        private void ShowFreezeModeUI(double temperature, double humidity)
        {
            ResetModeButtonColor();
            btnModeFreeze.BackColor = Color.LightSteelBlue;

            lblModeTitle.Text = "냉동 모드";
            lblTempVal.Text = $"{temperature:F1} ℃";
            lblHumVal.Text = $"{humidity:F1} %";
        }


        // =====================================================================
        // 버튼 이벤트 (manualMode)
        // =====================================================================
        private void btnModeNormal_Click(object sender, EventArgs e)
        {
            manualMode = manualMode == "normal" ? null : "normal";
        }

        private void btnModeCold_Click(object sender, EventArgs e)
        {
            manualMode = manualMode == "cold" ? null : "cold";
        }

        private void btnModeFreeze_Click(object sender, EventArgs e)
        {
            manualMode = manualMode == "freeze" ? null : "freeze";
        }


        // =====================================================================
        // 알람 깜빡임
        // =====================================================================
        private void timerBlink_Tick(object sender, EventArgs e)
        {
            try
            {
                bool alarm = (bool)client.ReadAny(hLamp3, typeof(bool));
                blinkState = alarm ? !blinkState : false;

                lblAlarmState.Text = alarm ? "ALARM ON" : "ALARM OFF";
                lblAlarmState.BackColor = (alarm && blinkState)
                    ? Color.Yellow
                    : Color.Transparent;
            }
            catch { }
        }


        // =====================================================================
        // 종료 처리
        // =====================================================================
        private void Form1_FormClosing(object sender, FormClosingEventArgs e)
        {
            timerUpdate.Stop();
            timerBlink.Stop();

            try
            {
                client.DeleteVariableHandle(hTempRaw);
                client.DeleteVariableHandle(hHumRaw);
                client.DeleteVariableHandle(hVibRaw);
                client.DeleteVariableHandle(hPresRaw);

                client.DeleteVariableHandle(hLamp1);
                client.DeleteVariableHandle(hLamp2);
                client.DeleteVariableHandle(hLamp3);
                client.DeleteVariableHandle(hLamp4);

                client.DeleteVariableHandle(hDI0);
                client.DeleteVariableHandle(hDI1);
                client.DeleteVariableHandle(hDI2);
                client.DeleteVariableHandle(hDI3);
            }
            catch { }

            client.Dispose();
        }
    }
}
