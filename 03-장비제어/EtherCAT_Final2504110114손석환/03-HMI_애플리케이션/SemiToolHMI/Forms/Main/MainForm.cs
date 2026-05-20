using SemiToolHMI.Controls;
using SemiToolHMI.Logic;
using SemiToolHMI.EtherCAT;
using SemiToolHMI.Monitor;     // ★ TransferMonitorForm
using System;
using System.Collections.Generic;
using System.Drawing;
using System.Linq;
using System.Threading.Tasks;
using System.Windows.Forms;
//using IEG3268_Dll;

namespace SemiToolHMI
{
    public partial class MainForm : Form
    {
        // =============================
        // 메인 레이아웃 패널들
        // =============================
        private Panel panelTop;
        private Panel panelTopTabs;
        private Panel panelRight;
        private Panel panelCenter;
        private Panel panelBottomStatus;   // ★ FOUP A/B 상태창 패널 (아래)
        private Panel panelEquipArea;
        private Panel panelDetailArea;
        // MainForm 클래스 안에 (필드 영역)
        private RobotLogicForm _robotLogicForm;


        // 상단 탭 버튼
        private Button btnTabMain;
        private Button btnTabVerification;
        private Button btnTabTransfer;

        // ★ 오른쪽 상단 장비 제어 버튼
        private Button btnEquipControl;

        // ★ 로그인 버튼
        private Button btnLogin;
        private Label lblUserName;

        private WaferPipelineSimulator simulator;

        // 상단 EtherCAT 상태 라벨
        private Label lblEtherStatus;

        // ★ 상단 요약 바 패널 + 라벨들
        private Panel panelTopSummary;
        private Label lblLotSummary;
        // FOUP Status Labels Removed
        private Label lblPm1Status;
        private Label lblPm2Status;
        private Label lblPm3Status;
        private Label lblTmStatus;
        private Label lblAlarmStatus;
        
        // ★ 램프 상태 라벨
        private Label lblLampGreen;
        private Label lblLampYellow;
        private Label lblLampRed;

        // =============================
        // Runtime 객체 (Chamber A/B/C)
        // =============================
        private ChamberRuntime runtimeA;
        private ChamberRuntime runtimeB;
        private ChamberRuntime runtimeC;

        private TextBox txtLog;

        // =============================
        // 설비 UI
        // =============================
        private FOUPPanel foupA;
        private FOUPPanel foupB;

        private ChamberPanel chamberA;
        private ChamberPanel chamberB;
        private ChamberPanel chamberC;
        private RobotRootPanel robot;

        // 아래 FOUP 상태 패널
        private EquipmentStatusPanel statusA;
        private EquipmentStatusPanel statusB;

        // DetailForm
        private ChamberDetailForm chamberDetailA;
        private ChamberDetailForm chamberDetailB;
        private ChamberDetailForm chamberDetailC;

        // Runtime Tick Timer
        private Timer tickTimer;

        // =============================
        // EtherCAT / IO 관련
        // =============================
        private bool isConnecting = false;
        private Timer pingTimer;
        
        // 실제 장비 상태 모니터링 타이머
        private Timer equipmentMonitorTimer;
        private bool useRealEquipment = false;  // 실제 장비 모드 플래그

        private EthercatController ec;
        private ChamberIo chamberAio, chamberBio, chamberCio;
        private StackLightIo stackLight;
        private WaferProcessScenario scenario;

        // 도어 상태
        private bool doorStateA = false;
        private bool doorStateB = false;
        private bool doorStateC = false;

        // ★ 로그 저장소
        private List<string> _systemLogs = new List<string>();
        private List<string> _errorLogs = new List<string>();

        // =============================
        // 생성자
        // =============================
        public MainForm()
        {
            InitializeComponent();

            this.Text = "SemiToolHMI";
            this.BackColor = Color.FromArgb(52, 73, 94); // 어두운 회색 테마
            this.WindowState = FormWindowState.Maximized;
            this.KeyPreview = true;
            this.KeyDown += MainForm_KeyDown;

            // Runtime 생성
            runtimeA = new ChamberRuntime("Chamber A");
            runtimeB = new ChamberRuntime("Chamber B");
            runtimeC = new ChamberRuntime("Chamber C");
            
            // ★ Runtime Completed 이벤트는 RobotScenario의 UpdateChamberProcess에서 처리
            // ★ 램프 제어는 RobotScenario.SetChamberLamp()에서 일괄 처리

            BuildUI();
            BuildTickTimer();
            InitEthercatLayer();
            BuildEtherPingTimer();
            BuildEquipmentMonitorTimer();  // 실제 장비 모니터링 타이머 추가
            
            // ★ 로그인 게이트 제거 (바로 메인 화면 진입)
            // this.Shown += MainForm_Shown;

            // ★ 초기 실행 시 UI 비활성화 (로그인 필요)
            UpdateUIForLogin(false);
        }
        
        private void MainForm_Shown(object sender, EventArgs e)
        {
            // 자동 로그인 팝업 로직 제거됨
        }

        // =====================================================================
        // Runtime Tick 타이머 (레시피 시퀀스 + 상단 요약 바)
        // =====================================================================
        private void MainForm_KeyDown(object sender, KeyEventArgs e)
        {
            if (e.KeyCode == Keys.F12)
            {
                // 이미 열려 있다가 닫혔다면 새로 생성
                if (_robotLogicForm == null || _robotLogicForm.IsDisposed)
                {
                    _robotLogicForm = new RobotLogicForm();
                }

                _robotLogicForm.Show();        // 창 띄우기
                _robotLogicForm.BringToFront(); // 앞쪽으로 가져오기
            }
        }

        private void BuildTickTimer()
        {
            tickTimer = new Timer();
            tickTimer.Interval = 100;  // 100ms
            tickTimer.Tick += (s, e) =>
            {
                runtimeA.Tick();
                runtimeB.Tick();
                runtimeC.Tick();

                // ★ 챔버 램프 상태를 RobotScenario에서 추적한 DO 값으로 표시
                // ★ ON이면 초록색, OFF면 회색
                chamberA.SetLamp(RobotScenario.LampA);
                chamberB.SetLamp(RobotScenario.LampB);
                chamberC.SetLamp(RobotScenario.LampC);

                // ★ 상단 요약 바 업데이트 (RobotScenario 상태 기반)
                // FOUP 상태


                // PM (Chamber) 상태
                SetSummaryStatus(lblPm1Status, 
                    RobotScenario.ChamberAProcessing ? "Run" : "Idle",
                    Color.FromArgb(44, 62, 80), Color.White);
                SetSummaryStatus(lblPm2Status,
                    RobotScenario.ChamberBProcessing ? "Run" : "Idle",
                    Color.FromArgb(44, 62, 80), Color.White);
                SetSummaryStatus(lblPm3Status,
                    RobotScenario.ChamberCProcessing ? "Run" : "Idle",
                    Color.FromArgb(44, 62, 80), Color.White);

                // TM (로봇) 상태
                SetSummaryStatus(lblTmStatus, RobotScenario.CurrentJob,
                    Color.FromArgb(52, 73, 94), Color.White);

                // ==================================
                // 램프 상태 업데이트 (Green/Yellow/Red)
                // ==================================
                
                // 1. Red: 긴급정지 또는 알람 상태
                bool isEmergency = RobotScenario.IsEmergencyStop;
                bool isAlarm = lblAlarmStatus.Text != "Normal";
                bool isRed = isEmergency || isAlarm;

                // 2. Green: 공정 진행 중 (Simulator or RobotScenario Running)
                //    (긴급정지 걸리면 Green 꺼져야 함)
                bool isProcessing = (simulator != null && simulator.IsRunning) || 
                                    RobotScenario.IsRunning;
                                    
                bool isGreen = !isRed && isProcessing;

                // 3. Yellow: EtherCAT 연결됨 AND 대기 중 (Not Green, Not Red)
                bool isConnected = ec != null && ec.IsConnected;
                bool isYellow = !isRed && !isGreen && isConnected;

                // 램프 색상 적용
                lblLampGreen.BackColor = isGreen ? Color.LimeGreen : Color.Gray;
                lblLampYellow.BackColor = isYellow ? Color.Gold : Color.Gray;
                lblLampRed.BackColor = isRed ? Color.Red : Color.Gray;

                // ================================
                // 상단 요약 바 갱신 (Simulator 기반)
                // ================================
                // ================================
                // 상단 요약 바 갱신 (Simulator 기반)
                // ================================
                if (simulator != null && ec.SimulationMode)
                {
                    // 1) TM 상태 (현재 로봇 Job)
                    string job = simulator.LastRobotJob;
                    if (string.IsNullOrEmpty(job))
                        job = "Idle";

                    Color tmBg = (job == "Idle")
                        ? Color.FromArgb(52, 73, 94)      // 기본 TM 색
                        : Color.FromArgb(39, 174, 96);    // 동작 중 = 초록

                    SetSummaryStatus(lblTmStatus, job, tmBg, Color.White);

                    // 2) FOUP A / B 상태 Removed
                    
                    int total = simulator.TotalTarget;  // ★ Fix: Restore total for Lot logic

                    // 3) PM1~PM3 상태 (Chamber Busy 여부)

                    // 3) PM1~PM3 상태 (Chamber Busy 여부)
                    SetSummaryStatus(
                        lblPm1Status,
                        simulator.ChamberABusy ? "Run" : "Idle",
                        Color.FromArgb(44, 62, 80),
                        Color.White);

                    SetSummaryStatus(
                        lblPm2Status,
                        simulator.ChamberBBusy ? "Run" : "Idle",
                        Color.FromArgb(44, 62, 80),
                        Color.White);

                    SetSummaryStatus(
                        lblPm3Status,
                        simulator.ChamberCBusy ? "Run" : "Idle",
                        Color.FromArgb(44, 62, 80),
                        Color.White);

                    // 4) Lot 상태 (진행 중 / 완료)
                    if (total > 0)
                    {
                        if (simulator.CompletedCount >= total)
                        {
                            SetSummaryStatus(
                                lblLotSummary,
                                "Idle",
                                Color.FromArgb(45, 47, 60),
                                Color.White);
                        }
                        else
                        {
                            SetSummaryStatus(
                                lblLotSummary,
                                "Auto Processing",
                                Color.FromArgb(39, 174, 96),
                                Color.White);
                        }
                    }
                }
            };
            tickTimer.Start();
        }

        // =====================================================================
        // EtherCAT 초기화
        // =====================================================================
        private void InitEthercatLayer()
        {
            ec = new EthercatController
            {
                // 하드웨어 없이 테스트: true
                // 실제 장비 연결: false
                SimulationMode = false  // ⭐ 하드웨어 모드 - UI가 장비 상태 따라감
            };

            stackLight = new StackLightIo(ec);

            chamberAio = new ChamberIo(ec, IoMap.A_LAMP, IoMap.A_DOOR_OPEN, IoMap.A_DOOR_CLOSE);
            chamberBio = new ChamberIo(ec, IoMap.B_LAMP, IoMap.B_DOOR_OPEN, IoMap.B_DOOR_CLOSE);
            chamberCio = new ChamberIo(ec, IoMap.C_LAMP, IoMap.C_DOOR_OPEN, IoMap.C_DOOR_CLOSE);

            scenario = new WaferProcessScenario(chamberAio, chamberBio, chamberCio, stackLight);

            // ★ RobotScenario 콜백 설정 (하드웨어 모드 전용)
            SetupRobotScenarioCallbacks();
        }

        // =====================================================================
        // RobotScenario 콜백 설정 (챔버 램프 제어)
        // =====================================================================
        private void SetupRobotScenarioCallbacks()
        {
            // ★ OnChamberProcessStart는 SetupRuntimeCallbacks()에서 설정됨
            // ★ 여기서 설정하면 나중에 설정되는 콜백을 덮어쓰게 됨
            
            // 공정 완료 시 UI 업데이트 (램프는 RobotScenario에서 직접 제어)
            RobotScenario.OnChamberProcessComplete = (chamberName) =>
            {
                // UI 업데이트만 수행 (램프 제어는 RobotScenario 내부에서 처리)
                AppendLog($"[{chamberName}] 공정 완료");
            };
        }

        private void BuildEtherPingTimer()
        {
            pingTimer = new Timer();
            pingTimer.Interval = 1000;
            pingTimer.Tick += (s, e) =>
            {
                // 연결되지 않았으면 Ping 체크 안함
                if (ec == null || !ec.IsConnected) return;

                // Ping 실패 → 연결 끊기
                if (!ec.Ping())
                {
                    ec.Disconnect();
                    UpdateEtherStatus(false);
                    AppendLog("[EtherCAT] Heartbeat Lost → 자동 해제");
                }
            };
            pingTimer.Start();
        }

        // =====================================================================
        // 실제 장비 상태 모니터링 타이머 (UI 애니메이션 동기화)
        // =====================================================================
        private void BuildEquipmentMonitorTimer()
        {
            equipmentMonitorTimer = new Timer();
            equipmentMonitorTimer.Interval = 200;  // 200ms마다 장비 상태 읽기
            equipmentMonitorTimer.Tick += EquipmentMonitorTimer_Tick;
            
            // ⭐ 시뮬레이션 모드에서는 타이머를 시작하지 않음
            if (ec != null && !ec.SimulationMode)
            {
                equipmentMonitorTimer.Start();
            }
        }

        private void EquipmentMonitorTimer_Tick(object sender, EventArgs e)
        {
            // 시뮬레이션 모드이거나 연결되지 않았으면 실제 장비 모니터링 무시
            if (ec == null || !ec.IsConnected || ec.SimulationMode)
                return;

            try
            {
                UpdateRobotAnimationFromEquipment();
                UpdateChamberDoorsFromEquipment();
                UpdateWaferStatusFromEquipment();

            }
            catch (Exception ex)
            {
                // 에러는 로그만 남기고 계속 진행
                AppendLog($"[장비 모니터링 오류] {ex.Message}");
            }
        }

        // 실제 장비 위치를 로봇 UI 애니메이션으로 변환
        private void UpdateRobotAnimationFromEquipment()
        {
            if (robot == null || robot.Arm == null) return;

            // Axis1 (UD, 상하) 위치 읽기
            string axis1PosStr = ec.ReadAxis1Position();
            // Axis2 (LR, 좌우) 위치 읽기
            string axis2PosStr = ec.ReadAxis2Position();

            if (long.TryParse(axis2PosStr, out long lrPos))
            {
                // LR 위치를 로봇 각도로 변환
                float angle = ConvertLrPositionToAngle(lrPos);
                robot.Arm.SetAngle(angle);
            }

            if (long.TryParse(axis1PosStr, out long udPos))
            {
                // UD 위치를 리프트 오프셋으로 변환
                int liftOffset = ConvertUdPositionToLiftOffset(udPos);
                robot.Arm.SetLiftOffset(liftOffset);
            }
        }

        // LR 위치를 각도로 변환 (각 타겟 위치 기준)
        // ※ RobotScenario.cs의 MotionPos 상수값 사용
        private float ConvertLrPositionToAngle(long lrPos)
        {
            // 기준 위치 정의 (RobotScenario의 MotionPos에서 복사)
            const long FOUP_A_LR = 13500;
            const long FOUP_B_LR = -394280;
            const long CHAMBER_A_LR = -59500;
            const long CHAMBER_B_LR = -191223;
            const long CHAMBER_C_LR = -322500;  // RobotScenario.MotionPos.ChamberC.LR 값 사용

            // 각 타겟으로부터의 거리 계산
            var distances = new Dictionary<string, double>
            {
                { "FOUP_A", Math.Abs(lrPos - FOUP_A_LR) },
                { "FOUP_B", Math.Abs(lrPos - FOUP_B_LR) },
                { "CHAMBER_A", Math.Abs(lrPos - CHAMBER_A_LR) },
                { "CHAMBER_B", Math.Abs(lrPos - CHAMBER_B_LR) },
                { "CHAMBER_C", Math.Abs(lrPos - CHAMBER_C_LR) }
            };

            string nearestTarget = distances.OrderBy(d => d.Value).First().Key;

            // UI에서 각 타겟의 각도 계산
            Control target = null;
            switch (nearestTarget)
            {
                case "FOUP_A":
                    target = foupA;
                    break;
                case "FOUP_B":
                    target = foupB;
                    break;
                case "CHAMBER_A":
                    target = chamberA;
                    break;
                case "CHAMBER_B":
                    target = chamberB;
                    break;
                case "CHAMBER_C":
                    target = chamberC;
                    break;
            }

            if (target != null)
            {
                int cx = robot.Left + robot.Width / 2;
                int cy = robot.Top + robot.Height / 2;
                int tx = target.Left + target.Width / 2;
                int ty = target.Top + target.Height / 2;

                double dx = tx - cx;
                double dy = ty - cy;
                double angle = Math.Atan2(dy, dx) * 180.0 / Math.PI;

                return (float)angle;
            }

            return robot.Arm.GetAngle();  // 변화 없으면 현재 각도 유지
        }

        // UD 위치를 리프트 오프셋으로 변환
        // ※ RobotScenario.cs의 MotionPos 상수값 사용
        private int ConvertUdPositionToLiftOffset(long udPos)
        {
            // 기준값: 상단 위치 ~ 하단 위치 (RobotScenario.MotionPos 기준)
            const long UD_UP = 1234552;    // MotionPos.ChamberA/B/C.Up
            const long UD_DOWN = 180000;   // MotionPos.FoupA/B.Load (기본값)

            // 정규화하여 0~10 범위의 오프셋으로 변환
            if (udPos >= UD_UP)
                return 0;  // 최상단
            if (udPos <= UD_DOWN)
                return 10;  // 최하단

            // 보간 계산
            double ratio = (double)(UD_UP - udPos) / (UD_UP - UD_DOWN);
            return (int)(ratio * 10);
        }

        // 실제 장비 도어 상태를 UI에 반영
        private void UpdateChamberDoorsFromEquipment()
        {
            // 챔버 도어 OPEN 센서 읽기 (DeviceControlForm 기준)
            // Chamber A: DI6 (상승), DI7 (하강)
            // Chamber B: DI8 (상승), DI9 (하강)
            // Chamber C: DI10 (상승), DI11 (하강)
            // 도어가 상승(UP) 상태일 때 "OPEN"으로 간주
            bool doorAOpen = ec.ReadDI(6);   // DI_CHAM_A_DOOR_UP
            bool doorBOpen = ec.ReadDI(8);   // DI_CHAM_B_DOOR_UP
            bool doorCOpen = ec.ReadDI(10);  // DI_CHAM_C_DOOR_UP

            // UI에 반영
            if (doorAOpen && !chamberA.IsDoorOpen)
                chamberA.OpenDoor();
            else if (!doorAOpen && chamberA.IsDoorOpen)
                chamberA.CloseDoor();

            if (doorBOpen && !chamberB.IsDoorOpen)
                chamberB.OpenDoor();
            else if (!doorBOpen && chamberB.IsDoorOpen)
                chamberB.CloseDoor();

            if (doorCOpen && !chamberC.IsDoorOpen)
                chamberC.OpenDoor();
            else if (!doorCOpen && chamberC.IsDoorOpen)
                chamberC.CloseDoor();
        }

        // 실제 장비 웨이퍼 상태를 UI에 반영
        private bool lastVacuumState = false;  // 이전 흡기 상태
        private bool lastCylinderFwd = false;  // 이전 실린더 전진 상태
        
        private void UpdateWaferStatusFromEquipment()
        {
            // DO14: 흡기 상태, DI13: 실린더 전진 센서
            bool vacuumOn = ec.ReadDO(14);      // 흡기 ON = 웨이퍼 픽업
            bool cylinderFwd = ec.ReadDI(13);   // 실린더 전진 = FOUP/Chamber 앞

            // UD/LR 위치 읽기
            string udStr = ec.ReadAxis1Position(); // Axis1 UD
            string lrStr = ec.ReadAxis2Position(); // Axis2 LR
            
            long.TryParse(udStr, out long udPos);
            long.TryParse(lrStr, out long lrPos);

            // ========================================
            // 웨이퍼 픽업 감지: 흡기 OFF→ON 전환
            // ========================================
            if (!lastVacuumState && vacuumOn)
            {
                // 웨이퍼 픽업됨!
                robot.Arm?.SetWafer(true);
                AppendLog($"[웨이퍼 픽업] UD={udPos}, LR={lrPos}");
                
                // 픽업 위치에서 챔버의 웨이퍼 제거
                DetectPickupLocation(udPos, lrPos);
            }

            // ========================================
            // 웨이퍼 배치 감지: 흡기 ON→OFF 전환
            // ========================================
            if (lastVacuumState && !vacuumOn)
            {
                // 웨이퍼 배치됨!
                robot.Arm?.SetWafer(false);
                AppendLog($"[웨이퍼 배치] UD={udPos}, LR={lrPos}");
                
                // 배치 위치에 챔버 웨이퍼 추가
                DetectPlacementLocation(udPos, lrPos);
            }

            // 상태 저장
            lastVacuumState = vacuumOn;
            lastCylinderFwd = cylinderFwd;
        }

        // 픽업 위치 판단 (챔버 또는 FOUP에서 웨이퍼 제거)
        private void DetectPickupLocation(long udPos, long lrPos)
        {
            const long posTol = 50000; // 위치 허용 오차

            // Chamber A: LR ≈ -59500
            if (Math.Abs(lrPos - (-59500)) < posTol)
            {
                chamberA?.SetWafer(false);
                AppendLog("[Chamber A] 웨이퍼 픽업됨");
            }
            // Chamber B: LR ≈ -191223
            else if (Math.Abs(lrPos - (-191223)) < posTol)
            {
                chamberB?.SetWafer(false);
                AppendLog("[Chamber B] 웨이퍼 픽업됨");
            }
            // Chamber C: LR ≈ -322500
            else if (Math.Abs(lrPos - (-322500)) < posTol)
            {
                chamberC?.SetWafer(false);
                AppendLog("[Chamber C] 웨이퍼 픽업됨");
            }
            // FOUP A: LR ≈ 13500
            else if (Math.Abs(lrPos - 13500) < posTol)
            {
                AppendLog("[FOUP A] 웨이퍼 픽업됨");
            }
            // FOUP B: LR ≈ -394280
            else if (Math.Abs(lrPos - (-394280)) < posTol)
            {
                AppendLog("[FOUP B] 웨이퍼 픽업됨");
            }
        }

        // 배치 위치 판단 (챔버 또는 FOUP에 웨이퍼 추가)
        private void DetectPlacementLocation(long udPos, long lrPos)
        {
            const long posTol = 50000; // 위치 허용 오차

            // Chamber A
            if (Math.Abs(lrPos - (-59500)) < posTol)
            {
                chamberA?.SetWafer(true);
                AppendLog("[Chamber A] 웨이퍼 배치됨");
            }
            // Chamber B
            else if (Math.Abs(lrPos - (-191223)) < posTol)
            {
                chamberB?.SetWafer(true);
                AppendLog("[Chamber B] 웨이퍼 배치됨");
            }
            // Chamber C
            else if (Math.Abs(lrPos - (-322500)) < posTol)
            {
                chamberC?.SetWafer(true);
                AppendLog("[Chamber C] 웨이퍼 배치됨");
            }
            // FOUP A
            else if (Math.Abs(lrPos - 13500) < posTol)
            {
                AppendLog("[FOUP A] 웨이퍼 배치됨");
            }
            // FOUP B
            else if (Math.Abs(lrPos - (-394280)) < posTol)
            {
                AppendLog("[FOUP B] 웨이퍼 배치됨");
            }
        }





        private void UpdateEtherStatus(bool ok)
        {
            if (lblEtherStatus == null) return;
            lblEtherStatus.Text = ok ? "EtherCAT: Connected" : "EtherCAT: Disconnected";
            lblEtherStatus.ForeColor = ok ? Color.LimeGreen : Color.Red;
        }

        // =====================================================================
        // UI 구성 시작
        // =====================================================================
        private void BuildUI()
        {
            BuildTopPanel();
            BuildTopSummaryBar();   // ★ 상단 요약 바
            BuildTopTabs();

            BuildCenterPanel();     // ★ panelDetailArea 생성
            
            BuildRightPanel();
            BuildLogPanel();
            
            BuildBottomStatusPanel(); // ★ FOUP A/B 상태창이 여기 들어감

            BuildDetailArea();      // ★ panelDetailArea에 DetailForm 추가
            BuildEquipmentLayout();
        }

        // ---------------------------------------------------------------------
        private void BuildTopPanel()
        {
            panelTop = new Panel
            {
                Dock = DockStyle.Top,
                Height = 70,
                BackColor = Color.LightGray // 상단 패널 (Dark -> LightGray)
            };
            Controls.Add(panelTop);

            var lblTitle = new Label
            {
                Text = "SemiToolHMI",
                AutoSize = true,
                Left = 20,
                Top = 5,
                ForeColor = Color.Black, // 글자색 (White -> Black)
                Font = new Font("Malgun Gothic", 18, FontStyle.Bold)
            };
            panelTop.Controls.Add(lblTitle);

            // EtherCAT 상태 표시 라벨
            lblEtherStatus = new Label
            {
                Text = "EtherCAT: Disconnected",
                AutoSize = true,
                ForeColor = Color.Red,
                Font = new Font("Malgun Gothic", 9F),
            };
            lblEtherStatus.Top = 10;
            lblEtherStatus.Left = panelTop.Width - 180;
            lblEtherStatus.Anchor = AnchorStyles.Top | AnchorStyles.Right;

            panelTop.Controls.Add(lblEtherStatus);

            panelTop.Resize += (s, e) =>
            {
                lblEtherStatus.Left = panelTop.Width - lblEtherStatus.Width - 20;
            };
        }





        // ---------------------------------------------------------------------
        // 상단 Lot / FOUP / PM / TM / ALARM 요약 바
        // ---------------------------------------------------------------------
        private void BuildTopSummaryBar()
        {
            panelTopSummary = new Panel
            {
                Dock = DockStyle.Bottom,   // Top 패널 안에서 아래쪽에 붙이기
                Height = 32,
                BackColor = Color.WhiteSmoke, // 요약바 배경 (Dark -> WhiteSmoke)
                Padding = new Padding(5, 4, 5, 4)
            };
            panelTop.Controls.Add(panelTopSummary);
            panelTopSummary.BringToFront();

            var flow = new FlowLayoutPanel
            {
                Dock = DockStyle.Fill,
                FlowDirection = FlowDirection.LeftToRight,
                WrapContents = false,
                BackColor = Color.Transparent,
                Margin = new Padding(0),
                Padding = new Padding(0)
            };
            panelTopSummary.Controls.Add(flow);

            // 공통 블록 생성
            lblLotSummary = CreateSummaryBlock(flow, "Lot", 160, Color.FromArgb(45, 47, 60));
            // FOUP Status Blocks Removed
            lblPm1Status = CreateSummaryBlock(flow, "PM1", 100, Color.FromArgb(44, 62, 80));
            lblPm2Status = CreateSummaryBlock(flow, "PM2", 100, Color.FromArgb(44, 62, 80));
            lblPm3Status = CreateSummaryBlock(flow, "PM3", 100, Color.FromArgb(44, 62, 80));
            lblTmStatus = CreateSummaryBlock(flow, "TM", 100, Color.FromArgb(52, 73, 94));
            lblAlarmStatus = CreateSummaryBlock(flow, "ALARM", 120, Color.FromArgb(192, 57, 43));

            // 램프 추가: Green, Yellow, Red
            lblLampGreen = CreateLampBlock(flow, "RUN", Color.Gray);
            lblLampYellow = CreateLampBlock(flow, "WAIT", Color.Gray);
            lblLampRed = CreateLampBlock(flow, "ERR", Color.Gray);


            // 초기 텍스트
            lblLotSummary.Text = "Idle";
            // FOUP Initial Text Removed
            lblPm1Status.Text = "Idle";
            lblPm2Status.Text = "Idle";
            lblPm3Status.Text = "Idle";
            lblTmStatus.Text = "Idle";
            lblAlarmStatus.Text = "Normal";
        }

        private Label CreateSummaryBlock(FlowLayoutPanel flow, string title, int width, Color backColor)
        {
            var panel = new Panel
            {
                Width = width,
                Height = 24,
                Margin = new Padding(3, 0, 3, 0),
                BackColor = backColor
            };

            var lblTitle = new Label
            {
                Text = title,
                Dock = DockStyle.Left,
                Width = 60,
                TextAlign = ContentAlignment.MiddleCenter,
                ForeColor = Color.White,
                Font = new Font("Malgun Gothic", 8.5f, FontStyle.Bold)
            };

            var lblValue = new Label
            {
                Dock = DockStyle.Fill,
                TextAlign = ContentAlignment.MiddleCenter,
                ForeColor = Color.White,
                Font = new Font("Malgun Gothic", 8.5f, FontStyle.Regular)
            };

            panel.Controls.Add(lblValue);
            panel.Controls.Add(lblTitle);
            flow.Controls.Add(panel);

            return lblValue;
        }

        private Label CreateLampBlock(FlowLayoutPanel flow, string text, Color color)
        {
            var panel = new Panel
            {
                Width = 60,
                Height = 24,
                Margin = new Padding(3, 0, 3, 0),
                BackColor = color
            };

            var lbl = new Label
            {
                Text = text,
                Dock = DockStyle.Fill,
                TextAlign = ContentAlignment.MiddleCenter,
                ForeColor = Color.White,
                Font = new Font("Malgun Gothic", 8F, FontStyle.Bold)
            };

            panel.Controls.Add(lbl);
            flow.Controls.Add(panel);

            // 외부에서 색상을 변경해야 하므로 패널이 아닌 라벨 리턴? 
            // -> 색상은 패널의 BackColor를 바꿔야 잘 보임.
            // 하지만 리턴 타입이 Label이라서, 여기서는 Label을 리턴하고 
            // 실제 제어는 Label.Parent.BackColor를 바꾸는 방식이 깔끔함.
            // 혹은 그냥 Panel을 필드로 저장하는 게 낫지만 기존 구조를 따르기 위해 Label 리턴하고 
            // Control Logic에서 Parent.BackColor를 변경하도록 하거나, 
            // CreateLampBlock이 Panel을 리턴하지 않고 Label을 리턴하도록 했으므로
            // Label 자체의 BackColor를 바꿔도 됨. (Dock=Fill이므로)
            // 위 코드에서 panel.BackColor = color 주었음. 
            // 라벨 배경이 투명하면 패널 색이 보임.
            
            // 수정: Label 자체를 반환하고, 실제 색상 제어는 Label.BackColor를 변경하는 것으로 변경.
            // Panel은 컨테이너 역할.
            lbl.BackColor = color; // 초기값
            
            return lbl;
        }

        // ---------------------------------------------------------------------
        private void BuildTopTabs()
        {
            panelTopTabs = new Panel
            {
                Dock = DockStyle.Top,
                Height = 36,
                BackColor = Color.FromArgb(35, 37, 45)
            };
            Controls.Add(panelTopTabs);

            btnTabMain = MakeTab("MAIN", 0, true);
            btnTabVerification = MakeTab("VERIFICATION", 1, false);
            btnTabTransfer = MakeTab("TRANSFER", 2, false);

            panelTopTabs.Controls.Add(btnTabMain);
            panelTopTabs.Controls.Add(btnTabVerification);
            panelTopTabs.Controls.Add(btnTabTransfer);

            // ===============================================================
            // 로그인 버튼 추가
            // ===============================================================
            btnLogin = new Button
            {
                Text = "LOGIN",
                Width = 100,
                Height = 30,
                Left = btnTabTransfer.Right + 20, // 탭 버튼들 오른쪽에 배치
                Top = 3,
                FlatStyle = FlatStyle.Flat,
                BackColor = Color.FromArgb(52, 152, 219), // 파란색 계열
                ForeColor = Color.White,
                Font = new Font("Malgun Gothic", 9F, FontStyle.Bold)
            };
            btnLogin.Click += BtnLogin_Click;
            panelTopTabs.Controls.Add(btnLogin);

            lblUserName = new Label
            {
                Text = "",
                AutoSize = true,
                ForeColor = Color.Yellow,
                Font = new Font("Malgun Gothic", 9F, FontStyle.Bold),
                Top = 9,
                Left = btnLogin.Right + 10
            };
            panelTopTabs.Controls.Add(lblUserName);

            // TRANSFER 탭 클릭 시 TransferMonitorForm 띄우기
            btnTabTransfer.Click += (s, e) =>
            {
                if (simulator == null)
                {
                    MessageBox.Show("시뮬레이터가 초기화되지 않았습니다.");
                    return;
                }

                var dlg = new TransferMonitorForm(simulator);
                dlg.Show(this); // 모달이면 ShowDialog(this);
            };
        }

        private void BtnLogin_Click(object sender, EventArgs e)
        {
            using (var loginForm = new LoginForm())
            {
                if (loginForm.ShowDialog(this) == DialogResult.OK)
                {
                    string user = loginForm.LoggedInUser;
                    lblUserName.Text = $"User: {user}";
                    btnLogin.Text = "LOGOUT";
                    btnLogin.BackColor = Color.FromArgb(192, 57, 43); // 로그아웃 색상 (Red)
                    
                    // 로그아웃 기능으로 전환
                    btnLogin.Click -= BtnLogin_Click;
                    btnLogin.Click += BtnLogout_Click;
                    
                    // ★ 로그인 성공 시 UI 활성화
                    UpdateUIForLogin(true);

                    MessageBox.Show($"환영합니다, {user}님!", "Login Success");
                }
            }
        }

        private void BtnLogout_Click(object sender, EventArgs e)
        {
            lblUserName.Text = "";
            btnLogin.Text = "LOGIN";
            btnLogin.BackColor = Color.FromArgb(52, 152, 219); // 로그인 색상 (Blue)
            
            // 로그인 기능으로 복귀
            btnLogin.Click -= BtnLogout_Click;
            btnLogin.Click += BtnLogin_Click;
            
            // ★ 로그아웃 시 UI 비활성화
            UpdateUIForLogin(false);

            MessageBox.Show("로그아웃 되었습니다.", "Logout");
        }

        // =====================================================================
        // ★ 로그인 상태에 따른 UI 활성화/비활성화
        // =====================================================================
        private void UpdateUIForLogin(bool loggedIn)
        {
            // 상단 탭 버튼
            if (btnTabMain != null) btnTabMain.Enabled = loggedIn;
            if (btnTabVerification != null) btnTabVerification.Enabled = loggedIn;
            if (btnTabTransfer != null) btnTabTransfer.Enabled = loggedIn;

            // 오른쪽 패널 (장비제어, 공정제어, EtherCAT 등 모든 버튼 포함)
            if (panelRight != null) panelRight.Enabled = loggedIn;

            // 중앙 장비 영역 (도어 클릭 등 방지)
            if (panelEquipArea != null) panelEquipArea.Enabled = loggedIn;
            
            // 상세 영역 (우측 슬라이드 패널)
            if (panelDetailArea != null) panelDetailArea.Enabled = loggedIn;
        }

        private Button MakeTab(string text, int index, bool selected)
        {
            return new Button
            {
                Text = text,
                Width = 150,
                Height = 30,
                Left = 10 + index * 160,
                Top = 3,
                FlatStyle = FlatStyle.Flat,
                BackColor = selected ? Color.FromArgb(0, 160, 80) : Color.FromArgb(60, 62, 70),
                ForeColor = Color.White
            };
        }

        // ---------------------------------------------------------------------
        private void BuildCenterPanel()
        {
            panelCenter = new Panel
            {
                Dock = DockStyle.Fill,
                BackColor = Color.FromArgb(230, 230, 230) // 배경색 변경 (Dark -> White)
            };
            Controls.Add(panelCenter);

            panelEquipArea = new Panel
            {
                Dock = DockStyle.Fill,
                BackColor = panelCenter.BackColor,
                AutoScroll = true  // ★ 스크롤 가능하게 변경 (화면 작아질 때 대응)
            };

            panelDetailArea = new Panel
            {
                Dock = DockStyle.Right,
                Width = 620,
                BackColor = Color.FromArgb(52, 73, 94), // 사용자 지정 Dark Gray
                Padding = new Padding(10, 120, 10, 10)
            };

            // Docking 순서 중요: Right를 먼저 Dock 하려면 Z-Order가 낮아야 함(뒤쪽).
            // Add()는 Index 0(Top)으로 추가하므로, 나중에 추가된 놈이 Top.
            // 따라서 먼저 Dock 되려면 먼저 Add 되거나 SendToBack 해야 함...?
            // 아니다. Reverse Z-Order 순으로 Dock 된다. (Bottom -> Top)
            // Bottom(Back)이 먼저 Dock.
            // Detail(Right)를 먼저 Dock 하려면 Bottom(Back)이어야 함.
            // Equip(Fill)를 나중에 Dock 하려면 Top(Front)이어야 함.
            // 따라서 [Equip, Detail] 순서여야 함 (Equip=0/Top, Detail=1/Bottom).
            // Add(Detail) -> [Detail]
            // Add(Equip)  -> [Equip, Detail]
            // 즉 Detail을 먼저 Add 하고, Equip을 나중에 Add 해야 함.
            
            panelCenter.Controls.Add(panelDetailArea);
            panelCenter.Controls.Add(panelEquipArea);
        }

        // ---------------------------------------------------------------------
        private void BuildRightPanel()
        {
            panelRight = new Panel
            {
                Dock = DockStyle.Right,
                Width = 260,
                BackColor = Color.LightGray // 우측패널 밝은회색
            };
            Controls.Add(panelRight);

            // ===============================================================
            // 0) 장비 제어 버튼 (오른쪽 상단)
            // ===============================================================
            btnEquipControl = new Button
            {
                Text = "장비 제어",
                Left = 10,
                Top = 10,
                Width = 240,
                Height = 32,
                FlatStyle = FlatStyle.Flat,
                BackColor = Color.FromArgb(0, 160, 80),
                ForeColor = Color.White
            };
            panelRight.Controls.Add(btnEquipControl);

            // 실제 DLL 장비 제어 Form 연결은 나중에 여기서 하면 됨
            btnEquipControl.Click += (s, e) =>
            {
                // 장비 제어 윈도우 열기
                var dlg = new DeviceControlForm();   // 장비제어 Form 이름
                dlg.Show(this);                      // 모달로 하고 싶으면 dlg.ShowDialog(this);
            };

            // ===============================================================
            // 1) 공정 제어 그룹
            // ===============================================================
            var grpProcess = new GroupBox
            {
                Text = "공정 제어",
                Left = 10,
                Top = btnEquipControl.Bottom + 10,  // 버튼 아래로
                Width = 240,
                Height = 320,
                ForeColor = Color.Black // 텍스트 검정
            };
            panelRight.Controls.Add(grpProcess);

            // ★ 공정 시작 버튼 (기존 공정 시나리오 버튼을 여기로 이동)
            var btnScenario = MakeRightButton("공정 시작", 30);
            var btnStop = MakeRightButton("정지", 70);
            var btnReset = MakeRightButton("리셋", 110);
            var btnServerOn = MakeRightButton("Server On", 150);
            var btnServerOff = MakeRightButton("Server Off", 190);

            grpProcess.Controls.Add(btnScenario);
            grpProcess.Controls.Add(btnStop);
            grpProcess.Controls.Add(btnReset);
            grpProcess.Controls.Add(btnServerOn);
            grpProcess.Controls.Add(btnServerOff);
            
            // 초기 상태: 긴급정지/리셋 버튼 비활성화
            btnStop.Enabled = false;
            btnReset.Enabled = false;

            // ============================================================
            // 긴급정지: 즉시 모든 동작 중단 + 자동 리셋
            // ============================================================
            btnStop.Click += (s, e) =>
            {
                // 챔버 런타임 정지
                runtimeA.Stop();
                runtimeB.Stop();
                runtimeC.Stop();
                
                // 로봇 시나리오 긴급정지 (시나리오 완전 종료)
                RobotScenario.EmergencyStop();
                
                // 시뮬레이터 긴급정지
                if (simulator != null)
                    simulator.EmergencyStop();
                

                
                AppendLog("[긴급정지] 모든 공정이 즉시 중단되었습니다.");
                
                MessageBox.Show("긴급정지 완료\n모든 동작이 중단되었습니다.\n(리셋 후 다시 시작하세요)", "긴급정지", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                
                // 버튼 상태 업데이트
                btnScenario.Enabled = false;  
                btnStop.Enabled = false;
                btnReset.Enabled = true;      // ★ 리셋 버튼만 활성화 (상태 복구용)
                

            };

            // ============================================================
            // 리셋: 수동으로 모든 상태를 초기값으로
            // ============================================================
            // ============================================================
            // 리셋: 수동으로 모든 상태를 초기값으로 (원점복귀 포함)
            // ============================================================
            btnReset.Click += async (s, e) =>
            {
                btnReset.Enabled = false; // 중복 클릭 방지

                // 챔버 런타임 리셋 (UI 상태만 간단히 초기화)
                runtimeA.ResetState();
                runtimeB.ResetState();
                runtimeC.ResetState();

                // ★ UI 패널 초기화 (레시피, 프로그레스바 등)
                chamberDetailA?.ResetUI();
                chamberDetailB?.ResetUI();
                chamberDetailC?.ResetUI();
                
                // 시뮬레이터 리셋
                if (simulator != null)
                    simulator.Reset();

                // ★ 로봇 시나리오 리셋 + 원점복귀 (비동기)
                await RobotScenario.ResetWithHomingAsync();
                
                // 버튼 상태 업데이트 (초기 상태로)
                btnScenario.Enabled = true;  // 리셋 후 새 시나리오 시작 가능
                btnStop.Enabled = false;
                btnReset.Enabled = false;
            };
            
            btnServerOn.Click += (s, e) =>
            {
                try
                {
                    if (ec == null || !ec.IsConnected)
                    {
                        MessageBox.Show("EtherCAT이 연결되지 않았습니다.\n먼저 EtherCAT 연결을 해주세요.", "Server On 실패");
                        return;
                    }

                    // 실제 하드웨어 서보 ON
                    EthercatMotion.EtherCAT_M.Axis1_ON();
                    EthercatMotion.EtherCAT_M.Axis2_ON();
                    
                    // 시나리오용 ServoOn 플래그 ON
                    RobotScenario.ServoOn = true;
                    

                    
                    AppendLog("[Server On] 서보 모터 활성화 (Axis1, Axis2 ON)");
                    MessageBox.Show("Servo On 완료\n로봇 동작이 가능합니다.", "Server On");
                }
                catch (Exception ex)
                {
                    AppendLog($"[Server On 오류] {ex.Message}");
                    MessageBox.Show($"Servo On 실패:\n{ex.Message}", "오류");
                }
            };
            
            btnServerOff.Click += (s, e) =>
            {
                try
                {
                    if (ec == null || !ec.IsConnected)
                    {
                        MessageBox.Show("EtherCAT이 연결되지 않았습니다.", "Server Off 실패");
                        return;
                    }

                    // 실제 하드웨어 서보 OFF
                    EthercatMotion.EtherCAT_M.Axis1_OFF();
                    EthercatMotion.EtherCAT_M.Axis2_OFF();
                    
                    // 시나리오용 ServoOn 플래그 OFF
                    RobotScenario.ServoOn = false;
                    
                    AppendLog("[Server Off] 서보 모터 비활성화 (Axis1, Axis2 OFF)");
                    MessageBox.Show("Servo Off 완료\n로봇 동작이 중지되었습니다.", "Server Off");
                }
                catch (Exception ex)
                {
                    AppendLog($"[Server Off 오류] {ex.Message}");
                    MessageBox.Show($"Servo Off 실패:\n{ex.Message}", "오류");
                }
            };

            // ===============================================================
            // 2) EtherCAT / Lamp 버튼
            // ===============================================================
            var grpEther = new GroupBox
            {
                Text = "EtherCAT / Lamp",
                Left = 10,
                Top = grpProcess.Bottom + 15,
                Width = 240,
                Height = 160,  // 공정 시나리오 버튼 제거로 높이 감소
                ForeColor = Color.Black // 텍스트 검정
            };
            panelRight.Controls.Add(grpEther);

            var btnEtherConnect = MakeRightButton("EtherCAT 연결", 30);
            var btnEtherDisconnect = MakeRightButton("EtherCAT 해제", 70);
            var btnLampTest = MakeRightButton("램프 테스트", 110);

            grpEther.Controls.Add(btnEtherConnect);
            grpEther.Controls.Add(btnEtherDisconnect);
            grpEther.Controls.Add(btnLampTest);

            // ★ 로그 버튼 (그룹박스 밖으로 이동)
            var btnLog = MakeRightButton("로그 확인", grpEther.Bottom + 10);
            panelRight.Controls.Add(btnLog);
            
            // ===============================================================
            // 3) 레시피 관리 그룹
            // ===============================================================
            var grpRecipe = new GroupBox
            {
                Text = "레시피 관리",
                Left = 10,
                Top = btnLog.Bottom + 10,
                Width = 240,
                Height = 120,
                ForeColor = Color.Black // 텍스트 검정
            };
            panelRight.Controls.Add(grpRecipe);
            
            var btnRecipeEdit = MakeRightButton("레시피 편집", 30);
            var btnBatchRecipe = MakeRightButton("레시피 일괄 적용", 70);
            
            grpRecipe.Controls.Add(btnRecipeEdit);
            grpRecipe.Controls.Add(btnBatchRecipe);
            
            btnRecipeEdit.Click += (s, e) =>
            {
                new RecipeEditorForm().ShowDialog();
            };

            btnBatchRecipe.Click += (s, e) =>
            {
                var dlg = new RecipeBatchApplyForm();
                if (dlg.ShowDialog() == DialogResult.OK)
                {
                    runtimeA.LoadRecipe(dlg.SelectedA);
                    runtimeB.LoadRecipe(dlg.SelectedB);
                    runtimeC.LoadRecipe(dlg.SelectedC);
                    MessageBox.Show("레시피 일괄 적용 완료!");
                }
            };

            btnLog.Click += (s, e) =>
            {
                // 로그 뷰어 열기
                var viewer = new LogViewerForm(_systemLogs, _errorLogs);
                viewer.ShowDialog(this);
            };

            btnEtherConnect.Click += async (s, e) =>
            {
                if (ec == null) return;

                // 이미 연결됐다면 다시 안함
                if (ec.IsConnected)
                {
                    MessageBox.Show("이미 연결되어 있습니다.");
                    return;
                }

                isConnecting = true;
                UpdateEtherStatus(false);
                await Task.Delay(200);

                bool ok = ec.Connect();

                if (ok)
                {
                    UpdateEtherStatus(true);
                    AppendLog("[EtherCAT] 연결 완료");
                    
                    // ★ 연결 완료 시 Yellow ON (Ready)
                    RobotScenario.SetLampYellow(true);
                    RobotScenario.SetLampRed(false);
                    RobotScenario.SetLampGreen(false);
                }
                else
                {
                    UpdateEtherStatus(false);
                    AppendLog("[EtherCAT] 연결 실패");
                    RobotScenario.SetLampYellow(false); // 실패 시 OFF
                }

                isConnecting = false;
            };


            btnEtherDisconnect.Click += (s, e) =>
            {
                if (ec == null) return;

                if (!ec.IsConnected)
                {
                    MessageBox.Show("이미 해제되어 있습니다.");
                    return;
                }

                // ★ 연결 해제 전 램프 OFF (순서 변경)
                RobotScenario.SetLampYellow(false);
                RobotScenario.SetLampGreen(false);
                RobotScenario.SetLampRed(false);
                
                // 잠시 대기 (명령 전송 보장)
                System.Threading.Thread.Sleep(50); 
                
                ec.Disconnect();
                UpdateEtherStatus(false);
                AppendLog("[EtherCAT] 연결 해제됨");
            };


            btnLampTest.Click += (s, e) =>
            {
                if (ec == null || !ec.IsConnected)
                {
                    MessageBox.Show("EtherCAT 먼저 연결하세요.");
                    return;
                }

                stackLight.AllOff();
                stackLight.Red(true);
                Task.Delay(300).Wait();
                stackLight.Red(false);
                stackLight.Yellow(true);
                Task.Delay(300).Wait();
                stackLight.Yellow(false);
                stackLight.Green(true);
            };

            // ===============================================================
            // ★★★ 공정 시나리오 버튼 (레시피 적용 + Pipeline Simulator)
            // ===============================================================
            btnScenario.Click += async (s, e) =>
            {
                if (simulator == null)
                {
                    MessageBox.Show("시뮬레이터가 초기화되지 않았습니다.");
                    return;
                }

                // 1) 시나리오용 레시피 일괄 선택
                var dlg = new RecipeBatchApplyForm();
                if (dlg.ShowDialog() != DialogResult.OK)
                    return;

                // 2) 각 챔버에 레시피 적용
                if (dlg.SelectedA > 0) runtimeA.LoadRecipe(dlg.SelectedA);
                if (dlg.SelectedB > 0) runtimeB.LoadRecipe(dlg.SelectedB);
                if (dlg.SelectedC > 0) runtimeC.LoadRecipe(dlg.SelectedC);

                // 3) 각 챔버 공정 런타임 시작
                // ★ 시뮬레이션 모드에서만 즉시 시작
                //    하드웨어 모드에서는 OnChamberProcessStart 콜백에서 StartNewCycle() 호출됨
                if (ec != null && ec.SimulationMode)
                {
                    runtimeA.Start();
                    runtimeB.Start();
                    runtimeC.Start();
                }
                // 하드웨어 모드에서는 레시피만 로드하고 Start()는 호출하지 않음
                // 웨이퍼가 실제로 챔버에 들어갈 때 StartNewCycle()이 호출됨

                // 4) 버튼 상태 업데이트 (시나리오 시작)
                btnScenario.Enabled = false;  // 시나리오 실행 중에는 새 시작 불가
                btnStop.Enabled = true;       // 긴급정지 가능
                btnReset.Enabled = true;      // 리셋 가능
                


                // 5) 상단 요약바 상태 표시 (시작 시점)
                SetSummaryStatus(lblLotSummary, "Auto Processing", Color.FromArgb(39, 174, 96), Color.White);

                SetSummaryStatus(lblPm1Status, "Run", Color.FromArgb(44, 62, 80), Color.White);
                SetSummaryStatus(lblPm2Status, "Run", Color.FromArgb(44, 62, 80), Color.White);
                SetSummaryStatus(lblPm3Status, "Run", Color.FromArgb(44, 62, 80), Color.White);
                SetSummaryStatus(lblTmStatus, "Running", Color.FromArgb(39, 174, 96), Color.White);
                SetSummaryStatus(lblAlarmStatus, "Normal", Color.FromArgb(192, 57, 43), Color.White);

                // 6) 웨이퍼 파이프라인 시뮬레이터 실행
                // ★ 시뮬레이션 모드일 때만 UI 시뮬레이터 실행
                //    하드웨어 모드일 때는 EquipmentMonitorTimer가 UI를 업데이트함
                if (ec != null && ec.SimulationMode)
                {
                    AppendLog("[시나리오] 레시피 적용 + FOUP A → A → B → C → FOUP B 동작 시작 (Simulation)");
                    await simulator.RunPipelineAsync(5);
                }
                else
                {
                    AppendLog("[시나리오] 레시피 적용 + 하드웨어 공정 시작 (Hardware Monitor)");
                    // 하드웨어 공정 시작
                    await RobotScenario.RunAsync();
                }

                // 7) 완료 후 버튼 상태 복귀
                btnScenario.Enabled = true;   // 시나리오 완료 후 새 시작 가능
                btnStop.Enabled = false;      // 긴급정지 불가
                
                // ★ 긴급정지로 끝났다면 리셋 버튼 활성화
                if (RobotScenario.IsEmergencyStop)
                {
                    btnReset.Enabled = true;
                }
                else
                {
                    btnReset.Enabled = false;
                }



                // 8) 완료 후 요약 상태 복귀 / 결과 반영
                SetSummaryStatus(lblLotSummary, "Idle", Color.FromArgb(45, 47, 60), Color.White);
                SetSummaryStatus(lblPm1Status, "Idle", Color.FromArgb(44, 62, 80), Color.White);
                SetSummaryStatus(lblPm2Status, "Idle", Color.FromArgb(44, 62, 80), Color.White);
                SetSummaryStatus(lblPm3Status, "Idle", Color.FromArgb(44, 62, 80), Color.White);
                SetSummaryStatus(lblTmStatus, "Idle", Color.FromArgb(52, 73, 94), Color.White);
            };
        }

        private Button MakeRightButton(string text, int top)
        {
            return new Button
            {
                Text = text,
                Left = 20,
                Top = top,
                Width = 200,
                Height = 30,
                FlatStyle = FlatStyle.Flat,
                BackColor = Color.FromArgb(70, 72, 80),
                ForeColor = Color.White
            };
        }

        // ---------------------------------------------------------------------
        // 로그 패널 (오른쪽 아래)
        // ---------------------------------------------------------------------
        private void BuildLogPanel()
        {
            txtLog = new TextBox
            {
                Multiline = true,
                Dock = DockStyle.Bottom,
                Height = 180,
                ReadOnly = true,
                ScrollBars = ScrollBars.Vertical,
                BackColor = Color.White,
                ForeColor = Color.Black,
                Font = new Font("Consolas", 10)
            };

            panelRight.Controls.Add(txtLog);
        }

        // ---------------------------------------------------------------------
        // Bottom FOUP 상태 출력 패널 (FOUP A/B)
        // ---------------------------------------------------------------------
        private void BuildBottomStatusPanel()
        {
            panelBottomStatus = new Panel
            {
                Dock = DockStyle.Bottom,
                Height = 300, 
                BackColor = Color.LightGray // 배경색 변경 (Dark -> LightGray)
            };
            // Controls.Add(panelBottomStatus); // 기존: MainForm에 추가
            panelCenter.Controls.Add(panelBottomStatus); // 변경: panelCenter에 추가
            
            // panelBottomStatus.BringToFront(); // 제거

            // ★ Docking Order 중요:
            // 1. panelDetailArea (Right)가 가장 먼저 Dock 되어야 함 (전체 높이 차지)
            // 2. panelBottomStatus (Bottom)가 그 다음 (남은 영역의 바닥)
            // 3. panelEquipArea (Fill)가 나머지 채움
            // WinForms에서는 Z-Order가 낮은(Index가 높은) 순서대로 Dock 됨.
            // 따라서 panelDetailArea를 가장 뒤로(SendToBack) 보내야 함.
            
            panelDetailArea.SendToBack();

            statusA = new EquipmentStatusPanel();
            statusB = new EquipmentStatusPanel();
            
            // ★ 라벨 변경
            statusA.SetTitle("FOUP A");
            statusB.SetTitle("FOUP B");

            // ★ 디스플레이 모드 설정
            statusA.IsSourceMode = true; // FOUP A는 아래(0번)부터 사라짐
            statusB.IsSourceMode = false; // FOUP B는 아래(0번)부터 채워짐

            // ★ 중앙 정렬을 위해 Dock 해제 및 직접 배치
            // statusA.Dock = DockStyle.Left;
            // statusB.Dock = DockStyle.Fill;
            statusA.Width = 400; 
            statusB.Width = 400;
            statusA.Height = 250; // 높이 증가 (200 -> 250)
            statusB.Height = 250; // 높이 증가 (200 -> 250)

            panelBottomStatus.Controls.Add(statusB);
            panelBottomStatus.Controls.Add(statusA);

            // 리사이즈 이벤트에서 중앙 정렬 계산
            panelBottomStatus.Resize += (s, e) =>
            {
                int center = panelBottomStatus.Width / 2;
                int top = (panelBottomStatus.Height - statusA.Height) / 2;
                
                statusA.Left = center - statusA.Width - 10; // 중앙에서 왼쪽으로
                statusA.Top = top;

                statusB.Left = center + 10; // 중앙에서 오른쪽으로
                statusB.Top = top;
            };
        }

        // ---------------------------------------------------------------------
        // 장비(로봇, 챔버, FOUP) 배치 패널
        // ---------------------------------------------------------------------
        private void BuildEquipmentLayout()
        {
            foupA = new FOUPPanel();
            foupA.SetTitle("FOUP A");

            foupB = new FOUPPanel();
            foupB.SetTitle("FOUP B");

            chamberA = new ChamberPanel(); chamberA.SetTitle("Chamber A");
            chamberB = new ChamberPanel(); chamberB.SetTitle("Chamber B");
            chamberC = new ChamberPanel(); chamberC.SetTitle("Chamber C");

            robot = new RobotRootPanel();

            // 도어 IO 바인딩
            chamberA.OnDoorClicked += () => ToggleDoor(chamberAio);
            chamberB.OnDoorClicked += () => ToggleDoor(chamberBio);
            chamberC.OnDoorClicked += () => ToggleDoor(chamberCio);

            // 패널에 추가
            panelEquipArea.Controls.Add(foupA);
            panelEquipArea.Controls.Add(foupB);
            panelEquipArea.Controls.Add(chamberA);
            panelEquipArea.Controls.Add(chamberB);
            panelEquipArea.Controls.Add(chamberC);
            panelEquipArea.Controls.Add(robot);

            // 한 번만 레이아웃 계산
            LayoutEquipment();
            RotateRobotToInitial(foupA);

            // ★ 화면 크기 변경 시 레이아웃 다시 계산 (중앙 정렬 유지)
            panelEquipArea.Resize += (s, e) => LayoutEquipment();

            // Simulator 생성
            simulator = new WaferPipelineSimulator(
                foupA, foupB,
                chamberA, chamberB, chamberC,
                robot,
                statusA, statusB,
                AppendLog,
                runtimeA, runtimeB, runtimeC
            );

            // ⭐ 장비 영역을 최상위로 올려서 다른 패널에 가려지지 않도록 함
            panelEquipArea.BringToFront();

            // ⭐ RobotScenario 콜백 연결 (하드웨어 모드에서 UI 업데이트)
            RobotScenario.OnWaferPickedUp = (location, hasWafer) =>
            {
                if (location.Contains("Chamber A")) chamberA.SetWafer(hasWafer);
                else if (location.Contains("Chamber B")) chamberB.SetWafer(hasWafer);
                else if (location.Contains("Chamber C")) chamberC.SetWafer(hasWafer);
                
                robot.Arm?.SetWafer(true); // 픽업 시 로봇이 웨이퍼 들고 있음
            };

            RobotScenario.OnWaferPlaced = (location, hasWafer) =>
            {
                if (location.Contains("Chamber A")) chamberA.SetWafer(hasWafer);
                else if (location.Contains("Chamber B")) chamberB.SetWafer(hasWafer);
                else if (location.Contains("Chamber C")) chamberC.SetWafer(hasWafer);
                
                robot.Arm?.SetWafer(false); // 배치 시 로봇이 웨이퍼 놓음
            };

            RobotScenario.OnFoupCountChanged = (foupACount, foupBCount) =>
            {
                foupA?.SetWaferCount(foupACount, 5);
                foupB?.SetWaferCount(foupBCount, 5);
                statusA?.SetWaferCount(foupACount, 5);
                statusB?.SetWaferCount(foupBCount, 5);
            };

            RobotScenario.OnChamberProcessStart = (chamberName) =>
            {
                AppendLog($"[콜백] {chamberName} 공정 시작");
                if (chamberName.Contains("Chamber A"))
                {
                    AppendLog($"[디버그] Runtime A - Recipe ID: {runtimeA?.RecipeId}, Steps: {runtimeA?.TotalSteps ?? 0}");
                    runtimeA?.StartNewCycle();
                }
                else if (chamberName.Contains("Chamber B"))
                {
                    AppendLog($"[디버그] Runtime B - Recipe ID: {runtimeB?.RecipeId}, Steps: {runtimeB?.TotalSteps ?? 0}");
                    runtimeB?.StartNewCycle();
                }
                else if (chamberName.Contains("Chamber C"))
                {
                    AppendLog($"[디버그] Runtime C - Recipe ID: {runtimeC?.RecipeId}, Steps: {runtimeC?.TotalSteps ?? 0}");
                    runtimeC?.StartNewCycle();
                }
            };

            // ★ 런타임 완료 시 RobotScenario에 알림 (램프 OFF 동기화)
            if (runtimeA != null)
            {
                runtimeA.Completed += (r) => RobotScenario.SetChamberProcessComplete("Chamber A");
            }
            if (runtimeB != null)
            {
                runtimeB.Completed += (r) => RobotScenario.SetChamberProcessComplete("Chamber B");
            }
            if (runtimeC != null)
            {
                runtimeC.Completed += (r) => RobotScenario.SetChamberProcessComplete("Chamber C");
            }

            RobotScenario.GetRecipeDuration = (chamberName) =>
            {
                if (chamberName.Contains("Chamber A")) return (runtimeA?.TotalRecipeTimeSec ?? 0) * 1000;
                if (chamberName.Contains("Chamber B")) return (runtimeB?.TotalRecipeTimeSec ?? 0) * 1000;
                if (chamberName.Contains("Chamber C")) return (runtimeC?.TotalRecipeTimeSec ?? 0) * 1000;
                return 3000; // 기본값
            };
        }

        // 로봇이 FOUP A 방향을 보도록 초기 회전
        private void RotateRobotToInitial(Control target)
        {
            if (robot == null || robot.Arm == null || target == null) return;

            int cx = robot.Left + robot.Width / 2;
            int cy = robot.Top + robot.Height / 2;

            int tx = target.Left + target.Width / 2;
            int ty = target.Top + target.Height / 2;

            double dx = tx - cx;
            double dy = ty - cy;
            double angle = Math.Atan2(dy, dx) * 180.0 / Math.PI;

            if (angle < -180) angle += 360;
            if (angle > 180) angle -= 360;

            robot.Arm.SetAngle((float)angle);
            robot.Arm.Invalidate();
        }

        // ---------------------------------------------------------------------
        // 장비 배치 (화면 가운데 위치 고정)
        // ---------------------------------------------------------------------
        private void LayoutEquipment()
        {
            // 패널이 없거나 사이즈가 0이면 리턴
            if (panelEquipArea.Width == 0 || panelEquipArea.Height == 0) return;

            // 전체 장비 영역의 가상의 크기 계산 (배치된 요소들을 감싸는 크기)
            // 대략적인 크기: Robot Width + Chamber Width * 2 + 여백
            int totalWidth = robot.Width + chamberA.Width + chamberC.Width + 160; 
            int totalHeight = chamberB.Height + robot.Height + foupA.Height + 100;

            // 화면 중앙 좌표 (스크롤 고려하여 AutoScrollPosition 더함)
            // 하지만 AutoScroll일 때는 컨텐츠의 위치를 직접 잡아야 함.
            // 여기서는 화면 중앙에 오도록 Left, Top을 조정하되,
            // 화면이 너무 작으면 (0,0) 기준으로 배치되도록 함.

            int clientW = panelEquipArea.ClientSize.Width;
            int clientH = panelEquipArea.ClientSize.Height;

            // 중앙점 계산 (화면이 장비 영역보다 작으면 최소 0)
            int startX = Math.Max(0, (clientW - totalWidth) / 2);
            int startY = Math.Max(0, (clientH - totalHeight) / 2);

            // 기준점 (Robot 중심)
            int robotCenterX = startX + chamberA.Width + 80 + robot.Width / 2;
            int robotCenterY = startY + chamberB.Height + 60 + robot.Height / 2;

            // 1) 로봇 위치
            robot.Left = robotCenterX - robot.Width / 2;
            robot.Top = robotCenterY - robot.Height / 2;

            // 2) Chamber B (위)
            chamberB.Left = robotCenterX - chamberB.Width / 2;
            chamberB.Top = robot.Top - chamberB.Height - 60;

            // 3) Chamber A (왼쪽)
            chamberA.Left = robot.Left - chamberA.Width - 80;
            chamberA.Top = robotCenterY - chamberA.Height / 2;

            // 4) Chamber C (오른쪽)
            chamberC.Left = robot.Right + 80;
            chamberC.Top = robotCenterY - chamberC.Height / 2;

            // 5) FOUP A/B (아래)
            foupA.Left = robot.Left - foupA.Width; // 로봇 왼쪽 라인에 맞춤 (조정 가능)
            foupA.Top = robot.Bottom + 40;

            foupB.Left = robot.Right; // 로봇 오른쪽 라인에 맞춤 (조정 가능)
            foupB.Top = robot.Bottom + 40;
            
            // FOUP 위치 미세 조정 (중앙 정렬 느낌 나게)
            foupA.Left = robotCenterX - 10 - foupA.Width;
            foupB.Left = robotCenterX + 10;
        }

        // ---------------------------------------------------------------------
        // 오른쪽 상세 정보 패널: Chamber A/B/C DetailForm
        // ---------------------------------------------------------------------
        private void BuildDetailArea()
        {
            // panelDetailArea는 이미 BuildCenterPanel에서 생성됨
            // 여기서는 ChamberDetailForm들만 생성하고 추가

            chamberDetailA = new ChamberDetailForm("Chamber A", runtimeA);
            chamberDetailB = new ChamberDetailForm("Chamber B", runtimeB);
            chamberDetailC = new ChamberDetailForm("Chamber C", runtimeC);

            chamberDetailA.Dock = DockStyle.Top;
            chamberDetailB.Dock = DockStyle.Top;
            chamberDetailC.Dock = DockStyle.Fill;

            panelDetailArea.Controls.Add(chamberDetailC);
            panelDetailArea.Controls.Add(chamberDetailB);
            panelDetailArea.Controls.Add(chamberDetailA);
        }
        // ---------------------------------------------------------------------
        // 도어 IO 토글
        // ---------------------------------------------------------------------
        private async void ToggleDoor(ChamberIo chamberIo)
        {
            try
            {
                if (chamberIo == chamberAio)
                {
                    doorStateA = !doorStateA;
                    if (doorStateA) await chamberAio.DoorOpen();
                    else await chamberAio.DoorClose();
                }
                else if (chamberIo == chamberBio)
                {
                    doorStateB = !doorStateB;
                    if (doorStateB) await chamberBio.DoorOpen();
                    else await chamberBio.DoorClose();
                }
                else if (chamberIo == chamberCio)
                {
                    doorStateC = !doorStateC;
                    if (doorStateC) await chamberCio.DoorOpen();
                    else await chamberCio.DoorClose();
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show("Door IO Error: " + ex.Message);
            }
        }

        // ---------------------------------------------------------------------
        // 상단 요약 바 상태 변경 헬퍼
        // ---------------------------------------------------------------------
        private void SetSummaryStatus(Label target, string text, Color backColor, Color foreColor)
        {
            if (target == null) return;

            if (InvokeRequired)
            {
                BeginInvoke(new Action(() => SetSummaryStatus(target, text, backColor, foreColor)));
                return;
            }

            target.Text = text;
            target.BackColor = backColor;
            target.ForeColor = foreColor;
        }

        // 로그 출력
        public void AppendLog(string msg)
        {
            if (txtLog != null && txtLog.InvokeRequired)
            {
                txtLog.Invoke(new Action(() => AppendLog(msg)));
                return;
            }

            string timestamp = DateTime.Now.ToString("HH:mm:ss");
            string fullMsg = $"{timestamp}  {msg}";

            // 1. 화면 출력
            txtLog?.AppendText($"{fullMsg}\r\n");

            // 2. 로그 분류 및 저장
            // 에러 키워드: Error, Fail, Exception, 오류, 실패
            bool isError = msg.IndexOf("Error", StringComparison.OrdinalIgnoreCase) >= 0 ||
                           msg.IndexOf("Fail", StringComparison.OrdinalIgnoreCase) >= 0 ||
                           msg.IndexOf("Exception", StringComparison.OrdinalIgnoreCase) >= 0 ||
                           msg.Contains("오류") ||
                           msg.Contains("실패");

            if (isError)
            {
                _errorLogs.Add(fullMsg);
            }
            else
            {
                _systemLogs.Add(fullMsg);
            }
        }
    }
}
