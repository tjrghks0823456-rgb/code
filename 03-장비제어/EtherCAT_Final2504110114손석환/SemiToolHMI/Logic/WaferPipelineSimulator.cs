using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using System.Windows.Forms;
using SemiToolHMI.Controls;

namespace SemiToolHMI.Logic
{
    /// <summary>
    /// FOUP A → Chamber A → B → C → FOUP B 파이프라인 시뮬레이터
    /// - 로봇은 중앙 고정 + 회전/리프트(+ 옵션: 전후 연장)만 사용
    /// - 각 챔버 공정 시간은 연결된 ChamberRuntime의 레시피 총 TimeSec을 사용
    /// </summary>
    public class WaferPipelineSimulator
    {
        private readonly FOUPPanel foupA;
        private readonly FOUPPanel foupB;
        private readonly ChamberPanel chamberA;
        private readonly ChamberPanel chamberB;
        private readonly ChamberPanel chamberC;
        private readonly RobotRootPanel robot;
        private readonly EquipmentStatusPanel statusA;
        private readonly EquipmentStatusPanel statusB;
        private readonly Action<string> log;

        // ★ 레시피 런타임 (각 챔버별)
        private readonly ChamberRuntime runtimeA;
        private readonly ChamberRuntime runtimeB;
        private readonly ChamberRuntime runtimeC;

        private const int MaxSlots = 5;
        private const int TickMs = 200;      // 공정 타이머 tick

        private int foupACount;
        private int foupBCount;

        private bool isRunning = false;
        public bool IsRunning => isRunning;
        
        // ============================================================
        // 일시정지/재개/긴급정지 제어 플래그
        // ============================================================
        private bool _isPaused = false;
        private bool _emergencyStop = false;

        /// <summary>
        /// 시뮬레이터 일시정지
        /// </summary>
        public void Pause()
        {
            _isPaused = true;
            schedulerTimer.Stop(); // 타이머 중지
            log("[Simulator] 일시정지됨");
        }

        /// <summary>
        /// 시뮬레이터 재개
        /// </summary>
        public void Resume()
        {
            if (_isPaused && isRunning)
            {
                _isPaused = false;
                schedulerTimer.Start(); // 타이머 재시작
                log("[Simulator] 재개됨");
            }
        }

        /// <summary>
        /// 긴급정지 - 시뮬레이터 즉시 종료
        /// </summary>
        public void EmergencyStop()
        {
            _emergencyStop = true;
            _isPaused = false;
            schedulerTimer.Stop();
            isRunning = false;
            log("[Simulator] 긴급정지 - 시뮬레이터 종료");
        }

        /// <summary>
        /// 리셋 - 모든 상태를 초기값으로
        /// </summary>
        public void Reset()
        {
            _isPaused = false;
            _emergencyStop = false;
            schedulerTimer.Stop();
            isRunning = false;
            
            foupACount = MaxSlots;
            foupBCount = 0;
            completedCount = 0;
            nextWaferId = 1;
            
            ResetChambersAndQueues();
            RefreshFoups();
            
            log("[Simulator] 리셋 완료 - 모든 상태 초기화");
        }

        // ================================ 내부 상태 ================================
        private class ChamberState
        {
            public bool HasWafer;
            public bool Busy;
            public int ProcessMs;
            public int RemainMs;
            public int WaferId;
        }

        private class RobotState
        {
            public bool Busy;
            public int WaferId;
        }

        private ChamberState chA;
        private ChamberState chB;
        private ChamberState chC;

        private readonly RobotState robotState = new RobotState();

        private readonly Queue<int> doneA = new Queue<int>();
        private readonly Queue<int> doneB = new Queue<int>();
        private readonly Queue<int> doneC = new Queue<int>();

        private readonly Timer schedulerTimer;

        private int totalWaferTarget;
        private int completedCount;
        private int nextWaferId;

        // ===================== Transfer / SummaryBar용 공개 프로퍼티 =====================
        public int FoupACurrent => foupACount;          // FOUP A 잔여 개수
        public int FoupBCurrent => foupBCount;          // FOUP B 완료 개수
        public int TotalTarget => totalWaferTarget;    // 이번 LOT 총 목표 장수
        public int CompletedCount => completedCount;    // FOUP B에 내려간 장수

        public bool ChamberABusy => chA != null && chA.Busy;
        public bool ChamberBBusy => chB != null && chB.Busy;
        public bool ChamberCBusy => chC != null && chC.Busy;

        // ===================== Transfer 모니터용 상태 =====================
        private string lastRobotJob = "Idle";
        public string LastRobotJob => lastRobotJob;

        public class WaferLocationStatus
        {
            public string Location { get; set; }
            public string Status { get; set; }
        }

        // ========================================================================
        // 생성자
        // ========================================================================
        public WaferPipelineSimulator(
            FOUPPanel foupA,
            FOUPPanel foupB,
            ChamberPanel chamberA,
            ChamberPanel chamberB,
            ChamberPanel chamberC,
            RobotRootPanel robot,
            EquipmentStatusPanel statusA,
            EquipmentStatusPanel statusB,
            Action<string> logAction,
            ChamberRuntime runtimeA,
            ChamberRuntime runtimeB,
            ChamberRuntime runtimeC)
        {
            this.foupA = foupA;
            this.foupB = foupB;
            this.chamberA = chamberA;
            this.chamberB = chamberB;
            this.chamberC = chamberC;
            this.robot = robot;
            this.statusA = statusA;
            this.statusB = statusB;
            this.log = logAction ?? (_ => { });

            this.runtimeA = runtimeA;
            this.runtimeB = runtimeB;
            this.runtimeC = runtimeC;

            foupACount = MaxSlots;
            foupBCount = 0;
            RefreshFoups();

            chA = new ChamberState();
            chB = new ChamberState();
            chC = new ChamberState();

            schedulerTimer = new Timer();
            schedulerTimer.Interval = TickMs;
            schedulerTimer.Tick += SchedulerTick;
        }

        // ========================================================================
        // 파이프라인 시작
        // ========================================================================
        public Task RunPipelineAsync(int waferCount)
        {
            if (isRunning) return Task.CompletedTask;

            waferCount = Math.Min(waferCount, MaxSlots);
            if (waferCount <= 0) return Task.CompletedTask;

            isRunning = true;

            totalWaferTarget = waferCount;
            completedCount = 0;
            nextWaferId = 1;

            foupACount = waferCount;
            foupBCount = 0;
            RefreshFoups();

            ResetChambersAndQueues();

            log($"=== 파이프라인 시작 ({waferCount}장) ===");
            schedulerTimer.Start();

            return Task.CompletedTask;
        }

        private void ResetChambersAndQueues()
        {
            chA = new ChamberState();
            chB = new ChamberState();
            chC = new ChamberState();

            chamberA.SetWafer(false);
            chamberB.SetWafer(false);
            chamberC.SetWafer(false);

            chamberA.SetProcessing(false);
            chamberB.SetProcessing(false);
            chamberC.SetProcessing(false);

            doneA.Clear();
            doneB.Clear();
            doneC.Clear();

            robotState.Busy = false;
            robotState.WaferId = 0;
            lastRobotJob = "Idle";
        }

        // ========================================================================
        // 스케줄러 Tick (공정 진행 + Job 디스패치)
        // ========================================================================
        private async void SchedulerTick(object sender, EventArgs e)
        {
            // --- 공정 시간 감소 ---
            UpdateChamberProcess(chA, doneA, chamberA, "A");
            UpdateChamberProcess(chB, doneB, chamberB, "B");
            UpdateChamberProcess(chC, doneC, chamberC, "C");

            // --- 전체 종료 조건 ---
            if (isRunning &&
                completedCount >= totalWaferTarget &&
                !chA.HasWafer && !chB.HasWafer && !chC.HasWafer &&
                doneA.Count == 0 && doneB.Count == 0 && doneC.Count == 0 &&
                !robotState.Busy)
            {
                log("=== 전체 공정 완료 ===");
                schedulerTimer.Stop();
                isRunning = false;
                lastRobotJob = "Idle";
                return;
            }

            if (robotState.Busy) return;   // 로봇이 일하는 동안은 대기

            // --- 우선순위: C→FOUPB > B→C > A→B > FOUPA→A ---
            if (doneC.Count > 0)
            {
                await Job_C_to_FoupB(doneC.Dequeue());
            }
            else if (doneB.Count > 0 && !chC.Busy && !chC.HasWafer)
            {
                await Job_B_to_C(doneB.Dequeue());
            }
            else if (doneA.Count > 0 && !chB.Busy && !chB.HasWafer)
            {
                await Job_A_to_B(doneA.Dequeue());
            }
            else if (!chA.HasWafer && !chA.Busy &&
                     foupACount > 0 && nextWaferId <= totalWaferTarget)
            {
                await Job_FoupA_to_A(nextWaferId++);
            }
        }

        private void UpdateChamberProcess(
            ChamberState ch,
            Queue<int> doneQueue,
            ChamberPanel panel,
            string name)
        {
            if (!ch.Busy) return;

            ch.RemainMs -= TickMs;
            
            // ★ 진행률 계산 및 UI 업데이트
            if (ch.ProcessMs > 0)
            {
                float progress = 1.0f - (float)ch.RemainMs / ch.ProcessMs;
                panel.SetProgress(progress);
            }

            if (ch.RemainMs <= 0)
            {
                ch.Busy = false;
                panel.SetProcessing(false);
                panel.SetProgress(0f); // 리셋

                doneQueue.Enqueue(ch.WaferId);
                log($"[Chamber {name}] W{ch.WaferId} 공정 완료");
            }
        }

        // ========================================================================
        // 각도 유틸
        // ========================================================================
        private static double Norm360(double angle)
        {
            angle %= 360.0;
            if (angle < 0) angle += 360.0;
            return angle;
        }

        private double GetAngleTo(Control target)
        {
            if (robot == null || target == null) return 0;

            int cx = robot.Left + robot.Width / 2;
            int cy = robot.Top + robot.Height / 2;

            int tx = target.Left + target.Width / 2;
            int ty = target.Top + target.Height / 2;

            double dx = tx - cx;
            double dy = ty - cy;

            return Norm360(Math.Atan2(dy, dx) * 180.0 / Math.PI);
        }

        /// <summary>
        /// FOUP A ~ FOUP B 사이의 "짧은 호"를 금지 구간으로 계산
        /// </summary>
        private (double left, double right) GetForbiddenSector()
        {
            double aFA = Norm360(GetAngleTo(foupA));
            double aFB = Norm360(GetAngleTo(foupB));

            double distFAtoFB = (aFB - aFA + 360.0) % 360.0;
            double distFBtoFA = (aFA - aFB + 360.0) % 360.0;

            double left, right;
            if (distFAtoFB <= distFBtoFA)
            {
                left = aFA;
                right = aFB;
            }
            else
            {
                left = aFB;
                right = aFA;
            }

            log($"[FORBIDDEN] FOUP A angle={aFA:F1}, FOUP B angle={aFB:F1}, 영역=({left:F1} ~ {right:F1})");

            return (left, right);
        }

        private bool IsAngleInSector(double angle, double left, double right)
        {
            angle = Norm360(angle);
            left = Norm360(left);
            right = Norm360(right);

            double distSector = (right - left + 360.0) % 360.0;
            if (distSector <= 0.0 || distSector >= 180.0)
                return false;

            double distFromLeft = (angle - left + 360.0) % 360.0;
            return distFromLeft >= 0.0 && distFromLeft <= distSector;
        }

        /// <summary>
        /// CCW(각도 증가 방향)로 회전할 때, 금지 구간을 통과하는지 샘플링으로 검사
        /// </summary>
        private bool PathCrossesForbiddenCCW(double start, double end, double left, double right, double step)
        {
            start = Norm360(start);
            end = Norm360(end);
            left = Norm360(left);
            right = Norm360(right);

            double dist = (end - start + 360.0) % 360.0;
            if (dist == 0) return false;

            int steps = Math.Max(1, (int)(dist / step));
            double angle = start;

            for (int i = 0; i <= steps; i++)
            {
                if (IsAngleInSector(angle, left, right))
                    return true;

                angle = Norm360(angle + step);
            }

            return false;
        }

        // ========================================================================
        // 로봇 회전/리프트 (+ 전후 연장 옵션)
        // ========================================================================
        private async Task RotateRobotTo(Control target, int speed = 4)
        {
            if (robot == null || robot.Arm == null || target == null) return;

            double currentAngle = Norm360(robot.Arm.GetAngle());
            double destAngle = Norm360(GetAngleTo(target));

            // 금지 구간 계산
            var (left, right) = GetForbiddenSector();

            // CCW / CW 경로가 금지구역을 통과하는지 각각 검사
            bool ccwCross = PathCrossesForbiddenCCW(currentAngle, destAngle, left, right, speed);
            bool cwCross = PathCrossesForbiddenCCW(destAngle, currentAngle, left, right, speed); // CW는 역방향 CCW로 검사

            int dir; // +1 = CCW, -1 = CW

            if (ccwCross && !cwCross)
            {
                dir = -1;
            }
            else if (!ccwCross && cwCross)
            {
                dir = +1;
            }
            else
            {
                double distCCW = (destAngle - currentAngle + 360.0) % 360.0;
                double distCW = (currentAngle - destAngle + 360.0) % 360.0;

                if (ccwCross && cwCross)
                {
                    log("[Rotate] 양 방향 모두 금지 구간 통과 → 최단 경로 사용");
                }

                dir = (distCCW <= distCW) ? +1 : -1;
            }

            // 실제 회전
            double angle = currentAngle;

            while (true)
            {
                double dist = (dir > 0)
                    ? (destAngle - angle + 360.0) % 360.0
                    : (angle - destAngle + 360.0) % 360.0;

                if (dist <= speed)
                    break;

                angle = Norm360(angle + dir * speed);
                robot.Arm.SetAngle((float)angle);
                await Task.Delay(10);
            }

            robot.Arm.SetAngle((float)destAngle);
        }

        // ★ Arm에 SetExtendOffset이 있으면 반영 (없으면 그냥 무시)
        private void SetArmExtendOffset(float value)
        {
            if (robot?.Arm == null) return;

            var mi = robot.Arm.GetType().GetMethod("SetExtendOffset");
            if (mi != null)
            {
                mi.Invoke(robot.Arm, new object[] { value });
            }
        }

        private async Task RobotLiftDown()
        {
            if (robot?.Arm == null) return;

            robot.Arm.SetLiftOffset(10);   // 살짝 내려감
            await Task.Delay(200);
        }

        private async Task RobotLiftUp()
        {
            if (robot?.Arm == null) return;

            robot.Arm.SetLiftOffset(0);    // 원래 위치
            await Task.Delay(200);
        }

        // ★ TM 전/후 모션 (있으면 사용, 없으면 Delay만)
        private async Task RobotExtendForward()
        {
            SetArmExtendOffset(20f);       // 앞으로 조금
            await Task.Delay(200);
        }

        private async Task RobotRetract()
        {
            SetArmExtendOffset(0f);        // 원래 길이
            await Task.Delay(200);
        }

        /// <summary>
        /// (지금은 사용 안 해도 되지만, 남겨두기)
        /// </summary>
        private async Task MoveToTarget(Control target)
        {
            await RotateRobotTo(target);
            await RobotLiftDown();
            await RobotLiftUp();
        }

        private async Task MoveThrough(params Control[] points)
        {
            foreach (var p in points)
                await MoveToTarget(p);
        }

        // ========================================================================
        // Job 정의
        // ========================================================================
        private async Task Job_FoupA_to_A(int waferId)
        {
            robotState.Busy = true;
            lastRobotJob = $"W{waferId} : FOUP A → Chamber A";
            log($"[W{waferId}] FOUP A → Chamber A");

            // 1) FOUP A 앞까지 회전
            await RotateRobotTo(foupA);

            // 2) FOUP A 위에서 웨이퍼 픽업 (안착→전진→상승→후진)
            await RobotLiftDown();      // 안착 위치로 하강
            await RobotExtendForward(); // 전진

            if (foupACount > 0) foupACount--;
            RefreshFoups();
            
            // ✨ 웨이퍼 픽업 - 로봇 암에 표시
            robot.Arm?.SetWafer(true);

            await RobotLiftUp();        // 상승 (웨이퍼 들고)
            await RobotRetract();       // 후진

            // 3) Chamber A 앞으로 회전
            await RotateRobotTo(chamberA);

            // 4) 문 열고 웨이퍼 투입 (전진→하강→후진→상승)
            chamberA.OpenDoor();
            await Task.Delay(250);

            await RobotExtendForward(); // 전진 (웨이퍼 들고)
            await RobotLiftDown();      // 안착 위치까지 하강

            chamberA.SetWafer(true);
            chA.HasWafer = true;
            
            // ✨ 웨이퍼 배치 - 로봇 암에서 숨김
            robot.Arm?.SetWafer(false);

            await RobotRetract();       // 후진
            await RobotLiftUp();        // 상승

            chamberA.CloseDoor();
            await Task.Delay(250);

            // ★ 레시피 기반 공정 시간 적용
            if (runtimeA != null && runtimeA.HasRecipe)
            {
                runtimeA.StartNewCycle();

                int recipeMs = runtimeA.TotalRecipeTimeSec * 1000;
                if (recipeMs <= 0) recipeMs = 1000;
                chA.ProcessMs = recipeMs;
                log($"[Chamber A] 레시피 시간 {runtimeA.TotalRecipeTimeSec}초 적용");
            }
            else
            {
                chA.ProcessMs = 4000;
                log("[Chamber A] 레시피 없음 → 기본 4초 사용");
            }

            chA.Busy = true;
            chA.WaferId = waferId;
            chA.RemainMs = chA.ProcessMs;
            chamberA.SetProcessing(true);

            robotState.Busy = false;
            lastRobotJob = "Idle";
        }

        private async Task Job_A_to_B(int waferId)
        {
            robotState.Busy = true;
            lastRobotJob = $"W{waferId} : Chamber A → B";
            log($"[W{waferId}] Chamber A → B");

            // 1) Chamber A에서 웨이퍼 픽업 (안착→전진→상승→후진)
            await RotateRobotTo(chamberA);

            chamberA.OpenDoor();
            await Task.Delay(250);

            await RobotLiftDown();      // 안착 위치로 하강
            await RobotExtendForward(); // 전진

            chamberA.SetWafer(false);
            chA.HasWafer = false;
            
            // ✨ 웨이퍼 픽업 - 로봇 암에 표시
            robot.Arm?.SetWafer(true);

            await RobotLiftUp();        // 상승 (웨이퍼 들고)
            await RobotRetract();       // 후진

            chamberA.CloseDoor();
            await Task.Delay(250);

            // 2) Chamber B로 이동해서 웨이퍼 투입 (전진→하강→후진→상승)
            await RotateRobotTo(chamberB);

            chamberB.OpenDoor();
            await Task.Delay(250);

            await RobotExtendForward(); // 전진 (웨이퍼 들고)
            await RobotLiftDown();      // 안착 위치까지 하강

            chamberB.SetWafer(true);
            chB.HasWafer = true;
            
            // ✨ 웨이퍼 배치 - 로봇 암에서 숨김
            robot.Arm?.SetWafer(false);

            await RobotRetract();       // 후진
            await RobotLiftUp();        // 상승

            chamberB.CloseDoor();
            await Task.Delay(250);

            // ★ B 레시피 시간 적용
            if (runtimeB != null && runtimeB.HasRecipe)
            {
                runtimeB.StartNewCycle();

                int recipeMs = runtimeB.TotalRecipeTimeSec * 1000;
                if (recipeMs <= 0) recipeMs = 1000;
                chB.ProcessMs = recipeMs;
                log($"[Chamber B] 레시피 시간 {runtimeB.TotalRecipeTimeSec}초 적용");
            }
            else
            {
                chB.ProcessMs = 3000;
                log("[Chamber B] 레시피 없음 → 기본 3초 사용");
            }

            chB.Busy = true;
            chB.WaferId = waferId;
            chB.RemainMs = chB.ProcessMs;
            chamberB.SetProcessing(true);

            robotState.Busy = false;
            lastRobotJob = "Idle";
        }

        private async Task Job_B_to_C(int waferId)
        {
            robotState.Busy = true;
            lastRobotJob = $"W{waferId} : Chamber B → C";
            log($"[W{waferId}] Chamber B → C");

            // 1) Chamber B에서 웨이퍼 픽업 (안착→전진→상승→후진)
            await RotateRobotTo(chamberB);

            chamberB.OpenDoor();
            await Task.Delay(250);

            await RobotLiftDown();      // 안착 위치로 하강
            await RobotExtendForward(); // 전진

            chamberB.SetWafer(false);
            chB.HasWafer = false;
            
            // ✨ 웨이퍼 픽업 - 로봇 암에 표시
            robot.Arm?.SetWafer(true);

            await RobotLiftUp();        // 상승 (웨이퍼 들고)
            await RobotRetract();       // 후진

            chamberB.CloseDoor();
            await Task.Delay(250);

            // 2) Chamber C로 이동해서 웨이퍼 투입 (전진→하강→후진→상승)
            await RotateRobotTo(chamberC);

            chamberC.OpenDoor();
            await Task.Delay(250);

            await RobotExtendForward(); // 전진 (웨이퍼 들고)
            await RobotLiftDown();      // 안착 위치까지 하강

            chamberC.SetWafer(true);
            chC.HasWafer = true;
            
            // ✨ 웨이퍼 배치 - 로봇 암에서 숨김
            robot.Arm?.SetWafer(false);

            await RobotRetract();       // 후진
            await RobotLiftUp();        // 상승

            chamberC.CloseDoor();
            await Task.Delay(250);

            // ★ C 레시피 시간 적용
            if (runtimeC != null && runtimeC.HasRecipe)
            {
                runtimeC.StartNewCycle();

                int recipeMs = runtimeC.TotalRecipeTimeSec * 1000;
                if (recipeMs <= 0) recipeMs = 1000;
                chC.ProcessMs = recipeMs;
                log($"[Chamber C] 레시피 시간 {runtimeC.TotalRecipeTimeSec}초 적용");
            }
            else
            {
                chC.ProcessMs = 5000;
                log("[Chamber C] 레시피 없음 → 기본 5초 사용");
            }

            chC.Busy = true;
            chC.WaferId = waferId;
            chC.RemainMs = chC.ProcessMs;
            chamberC.SetProcessing(true);

            robotState.Busy = false;
            lastRobotJob = "Idle";
        }

        private async Task Job_C_to_FoupB(int waferId)
        {
            robotState.Busy = true;
            lastRobotJob = $"W{waferId} : Chamber C → FOUP B";
            log($"[W{waferId}] Chamber C → FOUP B");

            // 1) Chamber C에서 웨이퍼 픽업 (안착→전진→상승→후진)
            await RotateRobotTo(chamberC);

            chamberC.OpenDoor();
            await Task.Delay(250);

            await RobotLiftDown();      // 안착 위치로 하강
            await RobotExtendForward(); // 전진

            chamberC.SetWafer(false);
            chC.HasWafer = false;
            
            // ✨ 웨이퍼 픽업 - 로봇 암에 표시
            robot.Arm?.SetWafer(true);

            await RobotLiftUp();        // 상승 (웨이퍼 들고)
            await RobotRetract();       // 후진

            chamberC.CloseDoor();
            await Task.Delay(250);

            // 2) FOUP B에 웨이퍼 적재 (전진→하강→후진→상승)
            await RotateRobotTo(foupB);

            await RobotExtendForward(); // 전진 (웨이퍼 들고)
            await RobotLiftDown();      // 안착 위치까지 하강

            if (foupBCount < MaxSlots) foupBCount++;
            RefreshFoups();
            
            // ✨ 웨이퍼 배치 - 로봇 암에서 숨김
            robot.Arm?.SetWafer(false);

            await RobotRetract();       // 후진
            await RobotLiftUp();        // 상승

            completedCount++;
            robotState.Busy = false;
            lastRobotJob = "Idle";
        }

        // ========================================================================
        // 웨이퍼 위치 스냅샷 (Transfer 모니터에서 사용)
        // ========================================================================
        public WaferLocationStatus[] GetLocationSnapshot()
        {
            var list = new List<WaferLocationStatus>();

            // 1) FOUP A Slot1~5 (대략적인 잔여 개수 기준)
            for (int slot = 1; slot <= MaxSlots; slot++)
            {
                string status = (slot <= foupACount) ? $"W{slot}" : "-";
                list.Add(new WaferLocationStatus
                {
                    Location = $"FOUP A Slot {slot}",
                    Status = status
                });
            }

            // 2) Chamber A/B/C
            list.Add(new WaferLocationStatus
            {
                Location = "Chamber A",
                Status = chA.HasWafer
                    ? $"W{chA.WaferId} {(chA.Busy ? "Processing" : "Done")}"
                    : "-"
            });
            list.Add(new WaferLocationStatus
            {
                Location = "Chamber B",
                Status = chB.HasWafer
                    ? $"W{chB.WaferId} {(chB.Busy ? "Processing" : "Done")}"
                    : "-"
            });
            list.Add(new WaferLocationStatus
            {
                Location = "Chamber C",
                Status = chC.HasWafer
                    ? $"W{chC.WaferId} {(chC.Busy ? "Processing" : "Done")}"
                    : "-"
            });

            // 3) FOUP B Slot1~5 (완료된 웨이퍼 수 기준)
            for (int slot = 1; slot <= MaxSlots; slot++)
            {
                string status = (slot <= foupBCount) ? $"W{slot}" : "-";
                list.Add(new WaferLocationStatus
                {
                    Location = $"FOUP B Slot {slot}",
                    Status = status
                });
            }

            return list.ToArray();
        }

        // ========================================================================
        // FOUP 상태 갱신
        // ========================================================================
        private void RefreshFoups()
        {
            foupA?.SetWaferCount(foupACount, MaxSlots);
            foupB?.SetWaferCount(foupBCount, MaxSlots);
            statusA?.SetWaferCount(foupACount, MaxSlots);
            statusB?.SetWaferCount(foupBCount, MaxSlots);

            log($"[FOUP] A:{foupACount} / B:{foupBCount}");
        }

    }
}
