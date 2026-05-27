using IEG3268_Dll;
using SemiToolHMI.Logic;
using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using System.Windows.Forms;
using System.Threading;


namespace SemiToolHMI
{
    /// <summary>
    /// FOUP A → Chamber A → B → C → FOUP B 공정 시나리오
    /// - WaferPipelineSimulator의 Job 구조(FOUPA→A, A→B, B→C, C→FOUPB) 참고
    /// - 실제 축/DO/DI를 사용하는 TM 시퀀스
    /// </summary>
    public static class RobotScenario
    {
        // EtherCAT 공용 인스턴스
        private static IEG3268 M => EthercatMotion.EtherCAT_M;

        // ★ 램프 제어 헬퍼
        public static void SetLampRed(bool on) => M.Digital_Output(0, on);
        public static void SetLampYellow(bool on) => M.Digital_Output(1, on);
        public static void SetLampGreen(bool on) => M.Digital_Output(2, on);

        // ★ 처음 1번만 HOME 실행 여부
        private static bool _homed = false;

        // ★ DeviceControlForm에서 설정하는 서보 ON 상태 플래그
        public static bool ServoOn { get; set; } = false;
        public static WaferPipelineSimulator WaferPipelineLink { get; set; }

        // UI 업데이트 콜백
        public static Action<string, bool> OnWaferPickedUp { get; set; }
        public static Action<string, bool> OnWaferPlaced { get; set; }
        public static Action<int, int> OnFoupCountChanged { get; set; }
        public static Action<string> OnChamberProcessStart { get; set; }
        public static Action<string> OnChamberProcessComplete { get; set; }  // 공정 완료 시 램프 OFF용
        public static Func<string, int> GetRecipeDuration { get; set; } // (chamberName) -> durationMs

        // ★ 램프 상태 추적 (DO 값을 직접 읽을 수 없으므로 상태 저장)
        public static bool LampA { get; private set; } = false;
        public static bool LampB { get; private set; } = false;
        public static bool LampC { get; private set; } = false;

        // ★ UI 상태 표시용 (상단 요약 바에서 읽기)
        public static int FoupACount => foupA?.WaferCount ?? 0;
        public static int FoupBCount => foupB?.WaferCount ?? 0;
        public static bool ChamberAProcessing => chamA?.IsProcessing ?? false;
        public static bool ChamberBProcessing => chamB?.IsProcessing ?? false;
        public static bool ChamberCProcessing => chamC?.IsProcessing ?? false;
        public static string CurrentJob { get; private set; } = "Idle";

        // ★ FOUP 및 Chamber 상태 (UI에서 읽기 위해 static 필드)
        private static FoupState foupA = new FoupState();
        private static FoupState foupB = new FoupState();
        private static ChamberState chamA = new ChamberState();
        private static ChamberState chamB = new ChamberState();
        private static ChamberState chamC = new ChamberState();

        // ★ 램프 깜빡임 제어용 토큰
        private static Dictionary<string, CancellationTokenSource> _blinkTokens = new Dictionary<string, CancellationTokenSource>();

        // ============================================================
        // 일시정지/재개/긴급정지/리셋 제어 플래그
        // ============================================================
        private static bool _isPaused = false;
        private static bool _emergencyStop = false;
        public static bool IsEmergencyStop => _emergencyStop;
        public static bool IsRunning { get; private set; } = false; // ★ 전체 공정 실행 중 여부
        
        /// <summary>
        /// 시나리오 일시정지
        /// </summary>
        public static void Pause()
        {
            _isPaused = true;
            RobotLog.Info("[RobotScenario] 일시정지됨");
        }

        /// <summary>
        /// 시나리오 재개
        /// </summary>
        public static void Resume()
        {
            _isPaused = false;
            RobotLog.Info("[RobotScenario] 재개됨");
        }

        /// <summary>
        /// 긴급정지 - 시나리오 즉시 종료
        /// </summary>
        public static void EmergencyStop()
        {
            _emergencyStop = true;
            _isPaused = false;
            RobotLog.Info("[RobotScenario] 긴급정지 - 시나리오 종료");
            
            // ★ 모든 램프 OFF 후 빨간색 ON
            SetLampYellow(false);
            SetLampGreen(false);
            SetLampRed(true);

            // ★ 모터 전력 차단 (Physical Stop)
            M.Axis1_OFF();
            M.Axis2_OFF();
            ServoOn = false;

            // ★ 흡기/배기 차단
            SetVacuum(false);           // DO_VAC (14) OFF, DO_EXH (15) OFF (SetVacuum(false)는 VAC만 끄므로 EXH도 꺼야 함)
            M.Digital_Output(DO_EXH, false); 
            
            _homed = false;    // ★ 위치 신뢰성 상실 -> 재시작 시 Homing 유도
            IsRunning = false; // ★ 긴급정지 시 실행 상태 해제
            
            _homed = false;    // ★ 위치 신뢰성 상실 -> 재시작 시 Homing 유도
            IsRunning = false; // ★ 긴급정지 시 실행 상태 해제
            
            // ★ 경광등 OFF (여기서는 Red ON 유지하므로 주석 처리 or 명시적 제어?)
            // 긴급정지 시에는 Red ON 만 유지
        }

        /// <summary>
        /// 리셋 - 모든 상태를 초기값으로
        /// </summary>
        public static void Reset()
        {
            _isPaused = false;
            _emergencyStop = false;
            
            // 상태 초기화
            if (foupA != null) foupA.WaferCount = 0;
            if (foupB != null) foupB.WaferCount = 0;
            if (chamA != null) { chamA.HasWafer = false; chamA.IsProcessing = false; chamA.WaferId = 0; }
            if (chamB != null) { chamB.HasWafer = false; chamB.IsProcessing = false; chamB.WaferId = 0; }
            if (chamC != null) { chamC.HasWafer = false; chamC.IsProcessing = false; chamC.WaferId = 0; }
            
            CurrentJob = "Idle";
            IsRunning = false; // ★ 리셋 시 실행 상태 해제
            
            // ★ 리셋 시: Red OFF, Yellow ON (대기 상태)
            SetLampRed(false);
            SetLampGreen(false);
            SetLampYellow(true);
            
            // ★ 리셋 시: 챔버 램프 모두 OFF
            SetChamberLamp("Chamber A", false);
            SetChamberLamp("Chamber B", false);
            SetChamberLamp("Chamber C", false);

            RobotLog.Info("[RobotScenario] 리셋 완료 - 모든 상태 초기화");
            RobotLog.Info("[RobotScenario] 리셋 완료 - 모든 상태 초기화");
        }

        // ============================================================
        // ★ 리셋 + 원점 복귀 (실린더 후진 포함)
        // ============================================================
        public static async Task ResetWithHomingAsync()
        {
            if (!EthercatMotion.EnsureConnected())
            {
                MessageBox.Show("EtherCAT 연결이 필요합니다.");
                return;
            }

            // 1. Servo ON 보장
            if (!ServoOn)
            {
                RobotLog.Info("[Reset] Servo ON 자동 실행");
                M.Axis1_ON();
                M.Axis2_ON();
                ServoOn = true;
                await Task.Delay(500); // Servo 안정화 대기
            }

            // 2. 실린더 전진 상태 확인 -> 후진
            if (IsCylinderForward())
            {
                RobotLog.Warn("[Reset] 실린더 전진 감지 -> 후진 시도");
                SetTmCylinder(false); // 후진 명령
                
                // 후진 완료 대기 (간단히 시간 대기)
                await Task.Delay(3000); 
                
                if (IsCylinderForward())
                {
                    MessageBox.Show("실린더가 후진하지 않았습니다. 리셋 중단.");
                    return;
                }
                RobotLog.Info("[Reset] 실린더 후진 완료");
            }

            // 2-1. 모든 챔버 도어 닫기 (실린더 후진 완료 후 안전하게)
            RobotLog.Info("[Reset] 챔버 도어 닫기 시도");
            
            // Chamber A (DO 5 ON)
            SetChamberDoor(DO_CHAM_A_DOOR_OPEN, DO_CHAM_A_DOOR_CLOSE, false);
            // Chamber B (DO 8 ON)
            SetChamberDoor(DO_CHAM_B_DOOR_OPEN, DO_CHAM_B_DOOR_CLOSE, false);
            // Chamber C (DO 11 ON)
            SetChamberDoor(DO_CHAM_C_DOOR_OPEN, DO_CHAM_C_DOOR_CLOSE, false);
            
            await Task.Delay(1000); // 도어 동작 대기

            // 3. Homing 수행 (강제)
            RobotLog.Info("[Reset] 원점 복귀 시작");
            _homed = false; // 기존 홈 상태 무효화
            await DoHomeOnceAsync();

            // 4. 내부 상태 리셋
            Reset();
            
            MessageBox.Show("리셋 및 원점 복귀 완료.\r\n다시 시작할 준비가 되었습니다.");
        }

        // ============================================================
        // DO / DI 매핑 (DeviceControlForm 버튼 기준)
        // ============================================================
        //
        // A챔버 도어오픈 button14, 하강 button25
        //   button14: DO5 false, DO4 true  → 도어 Open
        //   button25: DO4 false, DO5 true → 도어 Close
        //
        // B챔버 도어오픈 button12, 하강 button13
        //   button12: DO8 false, DO7 true → Open
        //   button13: DO7 false, DO8 true → Close
        //
        // C챔버 도어오픈 button15, 하강 button16
        //   button15: DO11 false, DO10 true → Open
        //   button16: DO10 false, DO11 true → Close
        //
        // 전진 button19, 후진 button20
        //   button19: DO13 false, DO12 true → 전진
        //   button20: DO12 false, DO13 true → 후진
        //
        // 흡기 시작 button21 → DO14 true
        // 흡기 정지 button23 → DO14 false
        // 배기 시작 button22 → DO15 true
        // 배기 정지 button24 → DO15 false

        // TM 전진/후진 실린더 DO
        private const int DO_TM_CYL_FWD = 12;
        private const int DO_TM_CYL_BWD = 13;

        // Chamber A/B/C 도어 DO 쌍
        private const int DO_CHAM_A_DOOR_OPEN = 4;
        private const int DO_CHAM_A_DOOR_CLOSE = 5;

        private const int DO_CHAM_B_DOOR_OPEN = 7;
        private const int DO_CHAM_B_DOOR_CLOSE = 8;

        private const int DO_CHAM_C_DOOR_OPEN = 10;
        private const int DO_CHAM_C_DOOR_CLOSE = 11;

        // Chamber 도어 OPEN 감지 DI (배선 상황에 맞게 조정 가능)
        private const int DI_CHAM_A_DOOR_OPEN = 10;
        private const int DI_CHAM_B_DOOR_OPEN = 11;
        private const int DI_CHAM_C_DOOR_OPEN = 12;

        // ★ 진공 / 배기 DO
        private const int DO_VAC = 14;   // 흡기 ON/OFF
        private const int DO_EXH = 15;   // 배기 ON/OFF

        // ★ 챔버 램프 DO
        private const int DO_LAMP_A = 3;   // Chamber A 램프
        private const int DO_LAMP_B = 6;   // Chamber B 램프
        private const int DO_LAMP_C = 9;   // Chamber C 램프



        // ★ 실린더 후진 후 도어 CLOSE까지 대기 시간 (3초)
        private const int DELAY_AFTER_TM_BWD_BEFORE_DOOR_CLOSE_MS = 3000;

        // DI13 = 실린더 전진 센서
        private static bool IsCylinderForward()
        {
            return M.Digital_Input(13);
        }

        // -----------------------------
        // 로봇 좌표 상수 (절대 좌표라고 가정)
        // -----------------------------
        private static class MotionPos
        {
            public static class FoupA
            {
                // 기본 1층 값 (실제 운전 시에는 층별 배열 사용)
                public const long Up = 250000;
                public const long Load = 180000;
                public const long LR = 13500;
            }

            public static class FoupB
            {
                public const long Up = 250000;
                public const long Load = 180000;
                public const long LR = -394280;
            }

            public static class ChamberA
            {
                // 상/하 모터 상승 위치
                public const long Up = 1234552;

                // 상/하 모터 안착 위치
                public const long Load = 884552;

                // 좌/우 서보 모터 위치
                public const long LR = -59956
;
            }


            public static class ChamberB
            {
                public const long Up = 1234552;
                public const long Load = 884552;
                public const long LR = -191223;
            }

            public static class ChamberC
            {
                public const long Up = 1234552;
                public const long Load = 884552;
                public const long LR = -322500;
            }
        }

        // ============================================================
        // FOUP A/B 층별 Z 값 (엑셀 기반)
        // ============================================================
        //
        // index: [층번호] (0번 인덱스는 사용 안 함)
        // 1층(하단) → 5층(상단)
        private static readonly long[] FoupA_UpZ = { 0, 250000, 930000, 1600000, 2270000, 2940000 };
        private static readonly long[] FoupA_LoadZ = { 0, 180000, 850000, 1520000, 2190000, 2860000 };

        private static readonly long[] FoupB_UpZ = { 0, 250000, 930000, 1600000, 2270000, 2940000 };
        private static readonly long[] FoupB_LoadZ = { 0, 180000, 850000, 1520000, 2190000, 2860000 };

        private static long GetFoupAUpZ(int slot)
        {
            if (slot < 1 || slot >= FoupA_UpZ.Length)
                throw new ArgumentOutOfRangeException(nameof(slot), "FOUP A 슬롯은 1~5층입니다.");
            return FoupA_UpZ[slot];
        }

        private static long GetFoupALoadZ(int slot)
        {
            if (slot < 1 || slot >= FoupA_LoadZ.Length)
                throw new ArgumentOutOfRangeException(nameof(slot), "FOUP A 슬롯은 1~5층입니다.");
            return FoupA_LoadZ[slot];
        }

        private static long GetFoupBUpZ(int slot)
        {
            if (slot < 1 || slot >= FoupB_UpZ.Length)
                throw new ArgumentOutOfRangeException(nameof(slot), "FOUP B 슬롯은 1~5층입니다.");
            return FoupB_UpZ[slot];
        }

        private static long GetFoupBLoadZ(int slot)
        {
            if (slot < 1 || slot >= FoupB_LoadZ.Length)
                throw new ArgumentOutOfRangeException(nameof(slot), "FOUP B 슬롯은 1~5층입니다.");
            return FoupB_LoadZ[slot];
        }

        // ============================================================
        // 축 파라미터 및 딜레이 상수
        // ============================================================
        private const long ACC = 1_000_000;
        private const long DEC = 1_000_000;
        private const long VEL_MAX = 100_000_000;
        private const long VEL = 1_000_000;

        private const int DELAY_HOME_MS = 4000;         // HOME 대기
        private const int DELAY_MOVE_2AXIS_MS = 2500;   // UD+LR 이동 대기
        private const int DELAY_MOVE_UD_MS = 1500;      // UD 단독 이동 대기

        private const int DELAY_TM_FOUP_MS = 500;       // FOUP 앞 픽/언로드 유지 시간
        private const int DELAY_TM_CHAM_MS = 500;       // 챔버 앞 로드/언로드 유지 시간

        private const int DELAY_DOOR_WAIT_MS = 100;     // 도어 open 폴링 주기
        private const int DELAY_DOOR_TIMEOUT_MS = 5000; // 도어 open 타임아웃

        private const int DELAY_CHAM_PROC_MS = 1000;    // 챔버 간단 공정 시간
        private const int DELAY_BEFORE_TM_FWD_MS = 2000; // 도어 열리고 나서 TM 전진까지 대기 2초

        // TM이 챔버 앞에 와 있는지 판단하기 위한 위치 허용 오차 (pulse)
        private const long POS_TOL_UD = 10_000;
        private const long POS_TOL_LR = 10_000;

        private static void EnsureAxisParameter()
        {
            M.Axis1_UD_Config_Update(ACC, DEC, VEL_MAX, VEL);
            M.Axis2_LR_Config_Update(ACC, DEC, VEL_MAX, VEL);
        }

        // ★ 처음 1회만 HOME 수행
        private static async Task DoHomeOnceAsync()
        {
            if (_homed) return;

            MessageBox.Show("처음 실행이므로 축 HOME 동작을 수행합니다.\r\n(서보 ON은 수동으로 먼저 해 주세요)");

            M.Axis1_UD_Homming();
            M.Axis2_LR_Homming();

            await Task.Delay(DELAY_HOME_MS);
            _homed = true;
        }

        // ============================================================
        // 공통 유틸: 진공/배기/TM실린더/도어
        // ============================================================
        private static void SetTmCylinder(bool forward)
        {
            if (forward)
            {
                M.Digital_Output(DO_TM_CYL_BWD, false);
                M.Digital_Output(DO_TM_CYL_FWD, true);
            }
            else
            {
                M.Digital_Output(DO_TM_CYL_FWD, false);
                M.Digital_Output(DO_TM_CYL_BWD, true);
            }
        }
        private static async Task WaitAfterCylinderForwardAsync(int delayMs = 2000)
        {
            // TM 전진 직후 고정 대기
            await Task.Delay(delayMs);
        }

        // ★ 실린더 후진 완료 대기 (DI13이 OFF될 때까지)
        private static async Task WaitCylinderRetractAsync(int timeoutMs = 2000)
        {
            RobotLog.Info("실린더 후진 대기 시작");

            var sw = System.Diagnostics.Stopwatch.StartNew();
            while (sw.ElapsedMilliseconds < timeoutMs)
            {
                if (!IsCylinderForward())
                {
                    RobotLog.Info($"실린더 후진완료 감지 (Elapsed={sw.ElapsedMilliseconds}ms)");
                    return;
                }

                await Task.Delay(50);
            }

            RobotLog.Warn($"실린더 후진 타임아웃 (Elapsed={sw.ElapsedMilliseconds}ms)");
            MessageBox.Show(
                "실린더 후진 완료 DI가 들어오지 않았습니다.\r\n(타임아웃 후 다음 단계 진행)",
                "Cylinder Retract Timeout",
                MessageBoxButtons.OK,
                MessageBoxIcon.Warning);
        }


        // ★ 실제 배선이 "열림/닫힘"이 반대로 매핑되어 있어서
        //    open=true 일 때 doClose 코일을 ON 하도록 수정
        private static void SetChamberDoor(int doOpen, int doClose, bool open)
        {
            if (open)
            {
                // 실제로는 doClose가 "문 열림" 쪽에 연결되어 있다고 가정
                M.Digital_Output(doOpen, false);  // 기존 열림 코일 OFF
                M.Digital_Output(doClose, true);  // 실제로 문이 열리는 코일 ON
            }
            else
            {
                // 실제로는 doOpen이 "문 닫힘" 쪽에 연결되어 있다고 가정
                M.Digital_Output(doClose, false); // 열림 코일 OFF
                M.Digital_Output(doOpen, true);   // 닫힘 코일 ON
            }
        }

        private static void SetVacuum(bool on)
        {
            // 흡기 ON/OFF
            M.Digital_Output(DO_VAC, on);

            if (on)
            {
                // 진공 켜질 땐 배기 OFF 정리 (안전용)
                M.Digital_Output(DO_EXH, false);
            }
        }

        private static async Task PulseExhaustAsync(int ms)
        {
            // 배기 펄스: 필요 시 진공 OFF 후 배기 ON
            M.Digital_Output(DO_VAC, false);
            M.Digital_Output(DO_EXH, true);
            await Task.Delay(ms);
            M.Digital_Output(DO_EXH, false);
        }

        // ★ 챔버 램프 제어 (하드웨어 모드 전용)
        private static void SetChamberLamp(string chamberName, bool on)
        {
            int doChannel = -1;
            switch (chamberName)
            {
                case "Chamber A":
                    doChannel = DO_LAMP_A;
                    LampA = on;  // 상태 저장
                    break;
                case "Chamber B":
                    doChannel = DO_LAMP_B;
                    LampB = on;  // 상태 저장
                    break;
                case "Chamber C":
                    doChannel = DO_LAMP_C;
                    LampC = on;  // 상태 저장
                    break;
            }

            if (doChannel >= 0)
            {
                M.Digital_Output(doChannel, on);
                RobotLog.Info($"[{chamberName}] 램프 {(on ? "ON" : "OFF")}");
            }
        }

        // ★ 램프 깜빡임 시작 (1초 간격 ON/OFF)
        private static void StartBlinking(string chamberName)
        {
            // 이미 깜빡이고 있으면 중지 후 재시작
            StopBlinking(chamberName);

            CancellationTokenSource cts = new CancellationTokenSource();
            _blinkTokens[chamberName] = cts;

            // 백그라운드 태스크로 깜빡임 수행
            Task.Run(async () =>
            {
                try
                {
                    while (!cts.Token.IsCancellationRequested)
                    {
                        // ON
                        SetChamberLamp(chamberName, true);
                        await Task.Delay(1000, cts.Token);

                        // OFF
                        SetChamberLamp(chamberName, false);
                        await Task.Delay(1000, cts.Token);
                    }
                }
                catch (TaskCanceledException)
                {
                    // 취소됨 -> 루프 종료
                }
                finally
                {
                    // 확실하게 끔
                    SetChamberLamp(chamberName, false);
                }
            }, cts.Token);
        }

        // ★ 램프 깜빡임 중지 (및 끄기)
        private static void StopBlinking(string chamberName)
        {
            if (_blinkTokens.ContainsKey(chamberName))
            {
                var cts = _blinkTokens[chamberName];
                if (cts != null)
                {
                    cts.Cancel();
                    cts.Dispose();
                }
                _blinkTokens.Remove(chamberName);
            }
            // 램프 끄기 (Task의 finally에서도 끄지만, 즉시 반영 위해 여기서도 호출)
            SetChamberLamp(chamberName, false);
        }

        private static async Task WaitDoorOpenAsync(int diDoorOpen, int timeoutMs = 10000)
        {
            RobotLog.Info($"DoorOpen 대기 시작 - DI{diDoorOpen}");

            bool inverted = DoorSensorInverted.ContainsKey(diDoorOpen) && DoorSensorInverted[diDoorOpen];

            var sw = System.Diagnostics.Stopwatch.StartNew();

            while (sw.ElapsedMilliseconds < timeoutMs)
            {
                bool val = M.Digital_Input(diDoorOpen);

                bool opened = inverted ? !val : val;

                if (opened)
                {
                    RobotLog.Info($"DoorOpen 감지됨 - DI{diDoorOpen} (Elapsed:{sw.ElapsedMilliseconds}ms)");
                    return;
                }

                await Task.Delay(100);
            }

            RobotLog.Warn($"DoorOpen 타임아웃 - DI{diDoorOpen}");
            MessageBox.Show($"문 열림 DI[{diDoorOpen}] 감지 실패.\r\nTIMEOUT 후 다음 단계 진행.", "Door Open Timeout");
        }
        // === 챔버별 문 센서 반전 여부 (장비 기준으로 수정) ===
        // true = 반전 논리 (DI=0 → Open)
        // false = 일반 논리 (DI=1 → Open)
        // ================================
        // 챔버별 DI 반전 테이블 (C# 7.3 호환)
        // ================================
        private static readonly Dictionary<int, bool> DoorSensorInverted =
            new Dictionary<int, bool>()
            {
        { DI_CHAM_A_DOOR_OPEN, false },
        { DI_CHAM_B_DOOR_OPEN, true },
        { DI_CHAM_C_DOOR_OPEN, false }
            };





        // ============================================================
        // 위치 체크 + 도어 인터락
        // ============================================================
        private static bool IsAtPosition(long targetUd, long targetLr)
        {
            string curUdStr = M.Axis1_is_PosData();
            string curLrStr = M.Axis2_is_PosData();

            long.TryParse(curUdStr, out long curUd);
            long.TryParse(curLrStr, out long curLr);

            long diffUd = curUd - targetUd;
            long diffLr = curLr - targetLr;

            return (System.Math.Abs(diffUd) <= POS_TOL_UD) &&
                   (System.Math.Abs(diffLr) <= POS_TOL_LR);
        }

        /// <summary>
        /// TM 위치 + 실린더 후진 상태를 확인한 뒤에만 챔버 도어를 여는 함수
        /// </summary>
        private static async Task<bool> OpenDoorWithPositionCheckAsync(
            long targetUd,
            long targetLr,
            int doOpen,
            int doClose,
            int diDoorOpen,
            string chamberName)
        {
            // 0) 실린더 전진 상태면 먼저 막기
            if (IsCylinderForward())
            {
                MessageBox.Show(
                    $"{chamberName} 도어를 열 수 없습니다.\r\n" +
                    "TM 실린더가 전진 상태입니다. 후진 후 다시 시도하세요.",
                    "Door Interlock",
                    MessageBoxButtons.OK,
                    MessageBoxIcon.Warning);
                return false;
            }

            // 1) TM 위치 확인
            if (!IsAtPosition(targetUd, targetLr))
            {
                MessageBox.Show(
                    $"{chamberName} 앞 목표 위치에 TM이 없습니다.\r\n" +
                    "도어 오픈 동작을 취소합니다.",
                    "Door Interlock",
                    MessageBoxButtons.OK,
                    MessageBoxIcon.Warning);
                return false;
            }

            // 2) 문 열기 DO
            SetChamberDoor(doOpen, doClose, open: true);

            // 3) 도어 OPEN DI 대기
            await WaitDoorOpenAsync(diDoorOpen);

            return true;
        }

        // ============================================================
        // 공통 이동 함수 (디버그 포함)
        // ============================================================
        private static async Task<bool> MoveToAsync(long udPos, long lrPos, string stepName)
        {
            string curUdStr = M.Axis1_is_PosData();
            string curLrStr = M.Axis2_is_PosData();

            long.TryParse(curUdStr, out long curUd);
            long.TryParse(curLrStr, out long curLr);

            // Safety Interlock: Cylinder Forward Check
            if (IsCylinderForward() && Math.Abs(curLr - lrPos) > POS_TOL_LR)
            {
                // ★ Stabilization: Wait 500ms and check again
                RobotLog.Warn("인터락 감지됨 (실린더 전진). 500ms 안정화 대기...");
                await Task.Delay(500);

                if (IsCylinderForward())
                {
                    MessageBox.Show(
                        "TM 실린더가 전진 상태에서는 좌우(LR) 이동을 할 수 없습니다.\r\n" +
                        "실린더를 후진시킨 후 다시 시도하세요.",
                        "Safety Interlock",
                        MessageBoxButtons.OK,
                        MessageBoxIcon.Error);
                    return false; // 이동 실패
                }
            }

            /*
            MessageBox.Show(
                $"{stepName}\n" +
                $"[이동 전] UD={curUd}, LR={curLr}\n" +
                $"[목표]    UD={udPos}, LR={lrPos}",
                "MoveToAsync DEBUG");
            */

            M.Axis1_UD_POS_Update(udPos);
            M.Axis2_LR_POS_Update(lrPos);

            M.Axis1_UD_Move_Send();
            M.Axis2_LR_Move_Send();

            await Task.Delay(DELAY_MOVE_2AXIS_MS);

            string afterUdStr = M.Axis1_is_PosData();
            string afterLrStr = M.Axis2_is_PosData();

            long.TryParse(afterUdStr, out long afterUd);
            long.TryParse(afterLrStr, out long afterLr);

            /*
            MessageBox.Show(
                $"{stepName}\n" +
                $"[이동 후] UD={afterUd}, LR={afterLr}",
                "MoveToAsync DEBUG 결과");
            */
            
            return true; // 이동 성공
        }

        private static async Task MoveUDAsync(long udPos, string stepName)
        {
            string curUdStr = M.Axis1_is_PosData();
            long.TryParse(curUdStr, out long curUd);

            RobotLog.Info(
                $"{stepName} - UD 이동 전 / UD={curUd}, TargetUD={udPos}");

            M.Axis1_UD_POS_Update(udPos);
            M.Axis1_UD_Move_Send();

            await Task.Delay(DELAY_MOVE_UD_MS);

            string afterUdStr = M.Axis1_is_PosData();
            long.TryParse(afterUdStr, out long afterUd);

            RobotLog.Info(
                $"{stepName} - UD 이동 후 / UD={afterUd}");
        }


        // ============================================================
        // FOUP / CHAMBER PICK / PLACE 시퀀스 공통 함수
        // ============================================================

        /// <summary>
        /// FOUP에서 웨이퍼 1장 꺼내는 시퀀스
        /// 안착 위치 → 실린더 전진 → 흡기 ON → 상승 위치 → 실린더 후진
        /// </summary>
        private static async Task FoupPickAsync(
            string name,
            long slotLoadZ,
            long upZ,
            long lrPos)
        {
            if (!await MoveToAsync(slotLoadZ, lrPos, $"{name} 안착 위치 이동")) return;

            SetTmCylinder(true);
            await WaitAfterCylinderForwardAsync();  // ★ 전진 후 2초 대기
            await Task.Delay(DELAY_TM_CHAM_MS);

            SetVacuum(true);
            await Task.Delay(200);

            await MoveUDAsync(upZ, $"{name} 상승 위치 이동");

            SetTmCylinder(false);
            await WaitCylinderRetractAsync();  // ★ 후진 완료 DI 확인
            await Task.Delay(500);  // ★ 안정화 대기 (500ms)

            if (OnWaferPickedUp != null) OnWaferPickedUp(name, false);
        }

        /// <summary>
        /// FOUP에 웨이퍼 1장 넣는 시퀀스
        /// 상승 → 전진 → 흡기 OFF → 배기 펄스 → 안착 하강 → 후진 → 다시 상승
        /// </summary>
        private static async Task FoupPlaceAsync(
            string name,
            long slotLoadZ,
            long upZ,
            long lrPos)
        {
            if (!await MoveToAsync(upZ, lrPos, $"{name} 상승 위치 이동")) return;

            SetTmCylinder(true);
            await WaitAfterCylinderForwardAsync(); // ★ 2초 대기
            await Task.Delay(DELAY_TM_FOUP_MS);


            SetVacuum(false);
            await PulseExhaustAsync(500);

            await MoveUDAsync(slotLoadZ, $"{name} 안착 위치 하강");

            SetTmCylinder(false);
            await WaitCylinderRetractAsync();  // ★ 후진 완료 DI 확인
            await Task.Delay(500);  // ★ 안정화 대기 (500ms)

            await MoveUDAsync(upZ, $"{name} 상승 위치 복귀");

            if (OnWaferPlaced != null) OnWaferPlaced(name, true);
        }

        /// <summary>
        /// 챔버에 웨이퍼 넣기
        /// 상승 → DOOR OPEN → 2초 → 전진 → 흡기 OFF → 배기 → 안착 하강 → 후진 → (후진 확인+3초) → DOOR CLOSE
        /// </summary>
        private static async Task ChamberPlaceAsync(
            string chamberName,
            long upZ,
            long loadZ,
            long lrPos,
            int doOpen,
            int doClose,
            int diDoorOpen)
        {
            if (!await MoveToAsync(upZ, lrPos, $"{chamberName} 상승 위치 이동")) return;

            bool doorOk = await OpenDoorWithPositionCheckAsync(
                upZ, lrPos,
                doOpen, doClose, diDoorOpen,
                chamberName);

            if (!doorOk) return;

            await Task.Delay(DELAY_BEFORE_TM_FWD_MS);   // 문 열린 상태로 2초 대기

            SetTmCylinder(true);
            await WaitAfterCylinderForwardAsync();  // ★ 전진 후 2초 대기
            await Task.Delay(DELAY_TM_CHAM_MS);


            SetVacuum(false);                           // 흡기 OFF
            await PulseExhaustAsync(500);               // 배기 0.5초

            await MoveUDAsync(loadZ, $"{chamberName} 안착 위치 하강");

            SetTmCylinder(false);                       // TM 후진 명령
            await WaitCylinderRetractAsync();           // 후진 완료 DI 확인

            // ⭐ TM 후진 완료 시점에 UI에 웨이퍼 표시 (로봇은 비우고 챔버는 채움)
            if (OnWaferPlaced != null) OnWaferPlaced(chamberName, true);

            await Task.Delay(DELAY_AFTER_TM_BWD_BEFORE_DOOR_CLOSE_MS); // 추가 3초 대기

            SetChamberDoor(doOpen, doClose, open: false);  // 그 다음에 문 닫기

            // ⭐ 문 닫고 1초 대기 후 공정 시작
            await Task.Delay(1000);
            
            // 🔆 챔버 램프 ON
            SetChamberLamp(chamberName, true);
            
            if (OnChamberProcessStart != null) OnChamberProcessStart(chamberName);
        }

        /// <summary>
        /// 챔버에서 웨이퍼 빼기
        /// 안착 → DOOR OPEN → 2초 → 전진 → 흡기 ON → 상승 → 후진 → (후진 확인+3초) → DOOR CLOSE
        /// </summary>
        private static async Task ChamberPickAsync(
            string chamberName,
            long upZ,
            long loadZ,
            long lrPos,
            int doOpen,
            int doClose,
            int diDoorOpen)
        {
            if (!await MoveToAsync(loadZ, lrPos, $"{chamberName} 안착 위치 이동")) return;

            bool doorOk = await OpenDoorWithPositionCheckAsync(
                loadZ, lrPos,
                doOpen, doClose, diDoorOpen,
                chamberName);

            if (!doorOk) return;

            await Task.Delay(DELAY_BEFORE_TM_FWD_MS);   // 문 열린 상태로 2초 대기

            SetTmCylinder(true);
            await WaitAfterCylinderForwardAsync(); // ★ 2초 대기 추가
            await Task.Delay(DELAY_TM_CHAM_MS);


            SetVacuum(true);                            // 흡기 ON
            await Task.Delay(200);

            await MoveUDAsync(upZ, $"{chamberName} 상승 위치 이동");

            SetTmCylinder(false);                       // TM 후진 명령
            await WaitCylinderRetractAsync();           // 후진 완료 DI 확인
            await Task.Delay(DELAY_AFTER_TM_BWD_BEFORE_DOOR_CLOSE_MS); // 추가 3초 대기

            SetChamberDoor(doOpen, doClose, open: false);  // 그 다음에 문 닫기

            // ★ 픽업 시나리오 완료 시점: 깜빡임 종료 및 램프 OFF
            StopBlinking(chamberName);

            if (OnWaferPickedUp != null) OnWaferPickedUp(chamberName, false);
        }

        // ============================================================
        // (기존) Job 1~4 : FOUP A → A → B → C → FOUP B (1장 기준)
        //  - 파이프라인에서는 아래 Job들을 직접 쓰지는 않고,
        //    공통 시퀀스(Foup/Chamber Pick/Place)를 조합해서 사용함
        // ============================================================
        private static async Task Job_FoupA_to_A(int waferId)
        {
            await FoupPickAsync(
                "FOUP A",
                MotionPos.FoupA.Load,
                MotionPos.FoupA.Up,
                MotionPos.FoupA.LR);

            await ChamberPlaceAsync(
                "Chamber A",
                MotionPos.ChamberA.Up,
                MotionPos.ChamberA.Load,
                MotionPos.ChamberA.LR,
                DO_CHAM_A_DOOR_OPEN,
                DO_CHAM_A_DOOR_CLOSE,
                DI_CHAM_A_DOOR_OPEN);

            await Task.Delay(DELAY_CHAM_PROC_MS);
        }

        private static async Task Job_A_to_B(int waferId)
        {
            await ChamberPickAsync(
                "Chamber A",
                MotionPos.ChamberA.Up,
                MotionPos.ChamberA.Load,
                MotionPos.ChamberA.LR,
                DO_CHAM_A_DOOR_OPEN,
                DO_CHAM_A_DOOR_CLOSE,
                DI_CHAM_A_DOOR_OPEN);

            await ChamberPlaceAsync(
                "Chamber B",
                MotionPos.ChamberB.Up,
                MotionPos.ChamberB.Load,
                MotionPos.ChamberB.LR,
                DO_CHAM_B_DOOR_OPEN,
                DO_CHAM_B_DOOR_CLOSE,
                DI_CHAM_B_DOOR_OPEN);

            await Task.Delay(DELAY_CHAM_PROC_MS);
        }

        private static async Task Job_B_to_C(int waferId)
        {
            await ChamberPickAsync(
                "Chamber B",
                MotionPos.ChamberB.Up,
                MotionPos.ChamberB.Load,
                MotionPos.ChamberB.LR,
                DO_CHAM_B_DOOR_OPEN,
                DO_CHAM_B_DOOR_CLOSE,
                DI_CHAM_B_DOOR_OPEN);

            await ChamberPlaceAsync(
                "Chamber C",
                MotionPos.ChamberC.Up,
                MotionPos.ChamberC.Load,
                MotionPos.ChamberC.LR,
                DO_CHAM_C_DOOR_OPEN,
                DO_CHAM_C_DOOR_CLOSE,
                DI_CHAM_C_DOOR_OPEN);

            await Task.Delay(DELAY_CHAM_PROC_MS);
        }

        private static async Task Job_C_to_FoupB(int waferId)
        {
            await ChamberPickAsync(
                "Chamber C",
                MotionPos.ChamberC.Up,
                MotionPos.ChamberC.Load,
                MotionPos.ChamberC.LR,
                DO_CHAM_C_DOOR_OPEN,
                DO_CHAM_C_DOOR_CLOSE,
                DI_CHAM_C_DOOR_OPEN);

            await FoupPlaceAsync(
                "FOUP B",
                MotionPos.FoupB.Load,
                MotionPos.FoupB.Up,
                MotionPos.FoupB.LR);
        }

        // ============================================================
        // 파이프라인용 내부 상태 클래스
        // ============================================================
        private class ChamberState
        {
            public bool HasWafer { get; set; }
            public bool IsProcessing { get; set; }
            public int WaferId { get; set; }
            public DateTime ProcessEndTime { get; set; }
        }

        private class FoupState
        {
            public int WaferCount { get; set; }
        }


        // ★ 외부(MainForm)에서 런타임 완료 시 호출
        public static void SetChamberProcessComplete(string chamberName)
        {
            if (chamberName == "Chamber A")
            {
                chamA.IsProcessing = false;
                StartBlinking("Chamber A"); // ★ 완료 시 깜빡임 시작
            }
            else if (chamberName == "Chamber B")
            {
                chamB.IsProcessing = false;
                StartBlinking("Chamber B"); // ★ 완료 시 깜빡임 시작
            }
            else if (chamberName == "Chamber C")
            {
                chamC.IsProcessing = false;
                StartBlinking("Chamber C"); // ★ 완료 시 깜빡임 시작
            }

            // 🔆 공정 완료 콜백
            if (OnChamberProcessComplete != null)
                OnChamberProcessComplete(chamberName);
        }

        private static void UpdateChamberProcess(ChamberState ch, DateTime now, string chamberName)
        {
            // ★ 시간 기반 체크 제거: MainForm의 Runtime.Completed 이벤트가 SetChamberProcessComplete를 호출할 때까지 대기
            // if (ch.HasWafer && ch.IsProcessing && now >= ch.ProcessEndTime) ...
        }

        // ============================================================
        // 파이프라인 스케줄러
        //   우선순위:
        //     1) C → FOUP B
        //     2) B → C
        //     3) A → B
        //     4) FOUP A → A
        // ============================================================
        private static async Task RunPipelineAsync(int totalWafers)
        {
            // 상태 초기화 (static 필드에 할당)
            foupA = new FoupState { WaferCount = totalWafers };
            foupB = new FoupState { WaferCount = 0 };
            chamA = new ChamberState();
            chamB = new ChamberState();
            chamC = new ChamberState();

            int nextFoupA_SlotToPick = 1;
            int nextFoupB_SlotToPlace = 1;

            int completed = 0;

            while (completed < totalWafers)
            {
                // ★ 긴급정지 체크
                if (_emergencyStop)
                {
                    RobotLog.Info("[Pipeline] 긴급정지로 인해 시나리오 종료");
                    _emergencyStop = false; // 플래그 리셋
                    return; // 즉시 종료
                }

                // ★ 일시정지 체크
                while (_isPaused)
                {
                    await Task.Delay(100); // 일시정지 중에는 대기
                    
                    // 일시정지 중에도 긴급정지 체크
                    if (_emergencyStop)
                    {
                        RobotLog.Info("[Pipeline] 일시정지 중 긴급정지로 인해 시나리오 종료");
                        _emergencyStop = false;
                        return;
                    }
                }

                await Task.Delay(200); // 200ms 주기 Tick

                DateTime now = DateTime.Now;

                // 1) 공정 완료 체크
                UpdateChamberProcess(chamA, now, "Chamber A");
                UpdateChamberProcess(chamB, now, "Chamber B");
                UpdateChamberProcess(chamC, now, "Chamber C");

                // =====================================================
                // [최적화 조건] FOUP A에 웨이퍼 남아 있고,
                //   - A : 완료된 웨이퍼 있음 (HasWafer && !IsProcessing)
                //   - B : 비어 있음
                //   - C : 완료된 웨이퍼 있음 (HasWafer && !IsProcessing)
                // 이 상황에서는 C→FOUP B보다 A→B를 먼저 실행해서
                // B 공정을 최대한 빨리 시작시키도록 함.
                // =====================================================
                bool foupARemain = (nextFoupA_SlotToPick <= totalWafers);
                bool aDone = chamA.HasWafer && !chamA.IsProcessing;
                bool bEmpty = !chamB.HasWafer;
                bool cDone = chamC.HasWafer && !chamC.IsProcessing;

                if (foupARemain && aDone && bEmpty && cDone)
                {
                    int waferId = chamA.WaferId;

                    RobotLog.Info($"[Sched] 최적화 조건: A→B 우선 실행 (W{waferId})");

                    // ==== A → B 실제 동작 ====
                    await ChamberPickAsync(
                        "Chamber A",
                        MotionPos.ChamberA.Up,
                        MotionPos.ChamberA.Load,
                        MotionPos.ChamberA.LR,
                        DO_CHAM_A_DOOR_OPEN,
                        DO_CHAM_A_DOOR_CLOSE,
                        DI_CHAM_A_DOOR_OPEN);

                    await ChamberPlaceAsync(
                        "Chamber B",
                        MotionPos.ChamberB.Up,
                        MotionPos.ChamberB.Load,
                        MotionPos.ChamberB.LR,
                        DO_CHAM_B_DOOR_OPEN,
                        DO_CHAM_B_DOOR_CLOSE,
                        DI_CHAM_B_DOOR_OPEN);

                    // 상태 갱신
                    chamA.HasWafer = false;
                    chamA.IsProcessing = false;
                    chamA.WaferId = 0;

                    chamB.HasWafer = true;
                    chamB.IsProcessing = true;
                    chamB.WaferId = waferId;
                    
                    int duration = GetRecipeDuration != null ? GetRecipeDuration("Chamber B") : DELAY_CHAM_PROC_MS;
                    chamB.ProcessEndTime = DateTime.Now.AddMilliseconds(duration);

                    // 이 Tick에서는 더 이상 다른 Job 안 하고 다음 Tick으로
                    continue;
                }



                // =====================================================
                // [User Request Optimization - HIGHEST PRIORITY]
                // Condition: B has wafer, C has wafer & done, A empty.
                // Standard behavior would be C->FOUP B (Priority 1).
                // Optimized behavior: FOUP A -> A (fill A first to maximize throughput).
                // =====================================================
                if (chamB.HasWafer && 
                   (chamC.HasWafer && !chamC.IsProcessing) && 
                   !chamA.HasWafer && 
                   (nextFoupA_SlotToPick <= totalWafers))
                {
                    int waferId = nextFoupA_SlotToPick;
                    int slotA = nextFoupA_SlotToPick;

                    CurrentJob = $"Unloading FOUP A (W{waferId})"; // Update Status
                    RobotLog.Info($"[Sched] 최적화 조건(B있음, C완료): FOUP A Slot{slotA} → A 우선 실행 (W{waferId})");

                    await FoupPickAsync(
                        "FOUP A",
                        GetFoupALoadZ(slotA),
                        GetFoupAUpZ(slotA),
                        MotionPos.FoupA.LR);

                    nextFoupA_SlotToPick++;

                    // ⭐ FOUP에서 픽업 즉시 카운트 업데이트
                    if (OnFoupCountChanged != null) 
                        OnFoupCountChanged(totalWafers - nextFoupA_SlotToPick + 1, nextFoupB_SlotToPlace - 1);

                    await ChamberPlaceAsync(
                        "Chamber A",
                        MotionPos.ChamberA.Up,
                        MotionPos.ChamberA.Load,
                        MotionPos.ChamberA.LR,
                        DO_CHAM_A_DOOR_OPEN,
                        DO_CHAM_A_DOOR_CLOSE,
                        DI_CHAM_A_DOOR_OPEN);

                    chamA.HasWafer = true;
                    chamA.IsProcessing = true;
                    chamA.WaferId = waferId;
                    
                    int duration = GetRecipeDuration != null ? GetRecipeDuration("Chamber A") : DELAY_CHAM_PROC_MS;
                    chamA.ProcessEndTime = DateTime.Now.AddMilliseconds(duration);

                    continue;
                }

                // ----------------------------------------------------
                // 1순위: C → FOUP B (완료된 웨이퍼 배출)
                // ----------------------------------------------------
                if (chamC.HasWafer && !chamC.IsProcessing)
                {
                    int waferId = chamC.WaferId;
                    int slotB = nextFoupB_SlotToPlace;

                    CurrentJob = $"Transfer C -> FOUP B (W{waferId})"; // Update Status
                    RobotLog.Info($"[Sched] C→FOUP B 실행 (W{waferId})");

                    await ChamberPickAsync(
                        "Chamber C",
                        MotionPos.ChamberC.Up,
                        MotionPos.ChamberC.Load,
                        MotionPos.ChamberC.LR,
                        DO_CHAM_C_DOOR_OPEN,
                        DO_CHAM_C_DOOR_CLOSE,
                        DI_CHAM_C_DOOR_OPEN);

                    await FoupPlaceAsync(
                        "FOUP B",
                        GetFoupBLoadZ(slotB),
                        GetFoupBUpZ(slotB),
                        MotionPos.FoupB.LR);

                    chamC.HasWafer = false;
                    chamC.IsProcessing = false;
                    chamC.WaferId = 0;

                    nextFoupB_SlotToPlace++;
                    completed++;

                    // ⭐ FOUP B에 배치 즉시 카운트 업데이트
                    if (OnFoupCountChanged != null) 
                        OnFoupCountChanged(totalWafers - nextFoupA_SlotToPick + 1, nextFoupB_SlotToPlace - 1);

                    continue;
                }

                // ----------------------------------------------------
                // 2순위: B → C
                // ----------------------------------------------------
                if (chamB.HasWafer && !chamB.IsProcessing && !chamC.HasWafer)
                {
                    int waferId = chamB.WaferId;

                    CurrentJob = $"Transfer B -> C (W{waferId})"; // Update Status
                    RobotLog.Info($"[Sched] B→C 실행 (W{waferId})");

                    await ChamberPickAsync(
                        "Chamber B",
                        MotionPos.ChamberB.Up,
                        MotionPos.ChamberB.Load,
                        MotionPos.ChamberB.LR,
                        DO_CHAM_B_DOOR_OPEN,
                        DO_CHAM_B_DOOR_CLOSE,
                        DI_CHAM_B_DOOR_OPEN);

                    await ChamberPlaceAsync(
                        "Chamber C",
                        MotionPos.ChamberC.Up,
                        MotionPos.ChamberC.Load,
                        MotionPos.ChamberC.LR,
                        DO_CHAM_C_DOOR_OPEN,
                        DO_CHAM_C_DOOR_CLOSE,
                        DI_CHAM_C_DOOR_OPEN);

                    chamB.HasWafer = false;
                    chamB.IsProcessing = false;
                    chamB.WaferId = 0;

                    chamC.HasWafer = true;
                    chamC.IsProcessing = true;
                    chamC.WaferId = waferId;
                    
                    int duration = GetRecipeDuration != null ? GetRecipeDuration("Chamber C") : DELAY_CHAM_PROC_MS;
                    chamC.ProcessEndTime = DateTime.Now.AddMilliseconds(duration);

                    continue;
                }

                // ----------------------------------------------------
                // 3순위: A → B
                //   (최적화 조건을 못 타는 일반적인 경우)
                // ----------------------------------------------------
                if (chamA.HasWafer && !chamA.IsProcessing && !chamB.HasWafer)
                {
                    int waferId = chamA.WaferId;

                    CurrentJob = $"Transfer A -> B (W{waferId})"; // Update Status
                    RobotLog.Info($"[Sched] A→B 실행 (일반) (W{waferId})");

                    await ChamberPickAsync(
                        "Chamber A",
                        MotionPos.ChamberA.Up,
                        MotionPos.ChamberA.Load,
                        MotionPos.ChamberA.LR,
                        DO_CHAM_A_DOOR_OPEN,
                        DO_CHAM_A_DOOR_CLOSE,
                        DI_CHAM_A_DOOR_OPEN);

                    await ChamberPlaceAsync(
                        "Chamber B",
                        MotionPos.ChamberB.Up,
                        MotionPos.ChamberB.Load,
                        MotionPos.ChamberB.LR,
                        DO_CHAM_B_DOOR_OPEN,
                        DO_CHAM_B_DOOR_CLOSE,
                        DI_CHAM_B_DOOR_OPEN);

                    chamA.HasWafer = false;
                    chamA.IsProcessing = false;
                    chamA.WaferId = 0;

                    chamB.HasWafer = true;
                    chamB.IsProcessing = true;
                    chamB.WaferId = waferId;
                    
                    int duration = GetRecipeDuration != null ? GetRecipeDuration("Chamber B") : DELAY_CHAM_PROC_MS;
                    chamB.ProcessEndTime = DateTime.Now.AddMilliseconds(duration);

                    continue;
                }

                // ----------------------------------------------------
                // 4순위: FOUP A → A (새 웨이퍼 투입)
                // ----------------------------------------------------
                if (nextFoupA_SlotToPick <= totalWafers && !chamA.HasWafer)
                {
                    int waferId = nextFoupA_SlotToPick;
                    int slotA = nextFoupA_SlotToPick;

                    CurrentJob = $"List FOUP A -> A (W{waferId})"; // Update Status
                    RobotLog.Info($"[Sched] FOUP A Slot{slotA} → A 실행 (W{waferId})");

                    await FoupPickAsync(
                        "FOUP A",
                        GetFoupALoadZ(slotA),
                        GetFoupAUpZ(slotA),
                        MotionPos.FoupA.LR);

                    nextFoupA_SlotToPick++;

                    // ⭐ FOUP에서 픽업 즉시 카운트 업데이트
                    if (OnFoupCountChanged != null) 
                        OnFoupCountChanged(totalWafers - nextFoupA_SlotToPick + 1, nextFoupB_SlotToPlace - 1);

                    await ChamberPlaceAsync(
                        "Chamber A",
                        MotionPos.ChamberA.Up,
                        MotionPos.ChamberA.Load,
                        MotionPos.ChamberA.LR,
                        DO_CHAM_A_DOOR_OPEN,
                        DO_CHAM_A_DOOR_CLOSE,
                        DI_CHAM_A_DOOR_OPEN);

                    chamA.HasWafer = true;
                    chamA.IsProcessing = true;
                    chamA.WaferId = waferId;
                    
                    int duration = GetRecipeDuration != null ? GetRecipeDuration("Chamber A") : DELAY_CHAM_PROC_MS;
                    chamA.ProcessEndTime = DateTime.Now.AddMilliseconds(duration);

                    continue;
                }

                // 여기까지 오면 이번 Tick에서는 할 Job이 없음 → 다음 Tick으로
            }

            RobotLog.Info("Pipeline 모드 종료");
            MessageBox.Show("파이프라인 시나리오 완료 (5장 LOT 종료)");
        }

        /// <summary>
        /// 예전 1사이클 테스트용 시나리오 (원본 유지용)
        /// </summary>
        private static async Task RunSingleCycleTestAsync()
        {
            int waferId = 1;

            RobotLog.Info($"[SingleCycle] Job_FoupA_to_A 시작 (W{waferId})");
            await Job_FoupA_to_A(waferId);

            RobotLog.Info($"[SingleCycle] Job_A_to_B 시작 (W{waferId})");
            await Job_A_to_B(waferId);

            RobotLog.Info($"[SingleCycle] Job_B_to_C 시작 (W{waferId})");
            await Job_B_to_C(waferId);

            RobotLog.Info($"[SingleCycle] Job_C_to_FoupB 시작 (W{waferId})");
            await Job_C_to_FoupB(waferId);

            RobotLog.Info("[SingleCycle] 1 사이클 완료");
        }

        // ============================================================
        // 상위 시퀀스 엔트리 포인트
        //   - 이제 RunAsync()가 5장 파이프라인 전체를 실행
        // ============================================================
        public static async Task RunAsync()
        {
            RobotLog.Info("=== RobotScenario.RunAsync START (Pipeline) ===");

            CurrentJob = "Starting Pipeline..."; // ★ 추가
            IsRunning = true; // ★ 공정 시작
            
            // ★ 공정 시작: Yellow OFF, Green ON
            SetLampYellow(false);
            SetLampGreen(true);

            if (!EthercatMotion.EnsureConnected())
            {
                RobotLog.Error("EtherCAT 미연결");
                MessageBox.Show("EtherCAT 연결이 되어 있지 않습니다.");
                SetLampGreen(false); // 실패 시 OFF
                SetLampYellow(true); // 다시 대기 상태
                return;
            }
           
            EnsureAxisParameter();
            RobotLog.Info("Axis 파라미터 설정 완료");

            if (!ServoOn)
            {
                RobotLog.Warn("Servo ON 아님");
                MessageBox.Show("축 서보가 ON 상태가 아닙니다.\r\n먼저 Servo ON 버튼을 눌러주세요.");
                SetLampGreen(false);
                SetLampYellow(true);
                return;
            }

            await DoHomeOnceAsync();
            RobotLog.Info("HOME 동작 완료");

            if (IsCylinderForward())
            {
                RobotLog.Warn("초기 상태에서 실린더 전진 감지");
                MessageBox.Show("웨이퍼 이송 실린더가 전진 상태입니다.\r\n후진 후 다시 실행하세요.");
                SetLampGreen(false);
                SetLampYellow(true);
                return;
            }

            // ★ 여기부터가 핵심 변경: 파이프라인 전체 실행
            int totalWafers = 5;   // FOUP A 5장 → FOUP B 5장

            RobotLog.Info($"Pipeline 모드 시작 - totalWafers={totalWafers}");
            await RunPipelineAsync(totalWafers);
            RobotLog.Info("Pipeline 모드 종료");
            CurrentJob = "Idle";
            IsRunning = false; // ★ 공정 종료
            
            // ★ 공정 종료: Green OFF, Yellow ON
            SetLampGreen(false);
            SetLampYellow(true);

            MessageBox.Show("파이프라인 시나리오 완료 (5장 LOT 종료)");
            RobotLog.Info("=== RobotScenario.RunAsync END (Pipeline) ===");
        }



    }
}
