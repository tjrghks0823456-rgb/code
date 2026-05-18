using SemiToolHMI.Data;
using SemiToolHMI.Models;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Windows.Forms;

namespace SemiToolHMI.Logic
{
    /// <summary>
    /// 챔버 공정 런타임:
    /// - 레시피 Step 시퀀스 관리
    /// - PV → SV 수렴 시뮬레이션
    /// - Tick() 호출로 시간 진행
    /// - Updated / StepChanged / Completed 이벤트로 UI에서 표시
    /// </summary>
    public class ChamberRuntime
    {
        // ==========================
        // 구성 / 상태
        // ==========================
        public string ChamberName { get; }

        /// <summary>
        /// 현재 적용된 레시피 ID / 이름
        /// </summary>
        public int RecipeId { get; private set; }
        public string RecipeName { get; private set; } = "";

        // 로딩된 레시피 스텝들
        private List<RecipeStep> steps = new List<RecipeStep>();

        // 현재 스텝 인덱스 (0 기반)
        private int stepIndex = -1;

        // 현재 스텝에서 경과 시간 (ms)
        private int elapsedMs = 0;

        /// <summary>
        /// 이 레시피로 현재까지 처리한 웨이퍼 수 (1,2,3…)
        /// → Detail 화면 Step 오른쪽 박스에 표시
        /// </summary>
        public int CycleCount { get; private set; } = 0;

        // 실행 여부
        public bool IsRunning { get; private set; }
        
        // 일시정지 여부
        public bool IsPaused { get; private set; }

        // ==========================
        // 시뮬레이션 설정
        // ==========================
        public const int DefaultTickIntervalMs = 100;
        private const double PvSmoothingFactor = 0.1;

        // ==========================
        // 현재 Step / 공정 정보
        // ==========================
        public int CurrentStepIndex => stepIndex;

        /// <summary>
        /// 레시피에 적어 둔 Step 번호 (예: 5,10,20…)
        /// → Detail 화면 Step 왼쪽 박스에 그대로 표시
        /// </summary>
        public int CurrentStepNo =>
            (stepIndex >= 0 && stepIndex < steps.Count) ? steps[stepIndex].StepNo : 0;

        /// <summary>
        /// 레시피 전체 시간(초) 합
        /// </summary>
        public int TotalRecipeTimeSec => steps.Sum(s => (int)s.TimeSec);

        /// <summary>
        /// 현재 Step에서 경과 시간(초)
        /// </summary>
        public double CurrentStepElapsedSec => elapsedMs / 1000.0;

        /// <summary>
        /// 현재 Step의 총 시간(초)
        /// </summary>
        public double CurrentStepTotalSec =>
            (stepIndex >= 0 && stepIndex < steps.Count) ? steps[stepIndex].TimeSec : 0.0;

        /// <summary>
        /// 현재 Step의 Mode 문자열
        /// </summary>
        public string CurrentMode =>
            (stepIndex >= 0 && stepIndex < steps.Count) ? steps[stepIndex].Mode : "";

        /// <summary>
        /// 로딩된 Step 개수
        /// </summary>
        public int TotalSteps => steps.Count;

        /// <summary>
        /// 레시피 로딩 여부
        /// </summary>
        public bool HasRecipe => steps != null && steps.Count > 0;

        /// <summary>
        /// 현재 레시피 전체 누적 진행 시간(초)
        /// </summary>
        public double TotalElapsedSec
        {
            get
            {
                if (steps == null || stepIndex < 0) return 0.0;
                double sum = 0;
                // 현재 Step 이전까지의 시간 합
                for (int i = 0; i < stepIndex; i++)
                {
                    if (i < steps.Count) sum += steps[i].TimeSec;
                }
                // 현재 Step의 진행 시간 합산
                sum += (elapsedMs / 1000.0);
                return sum;
            }
        }

        // ==========================
        // 6개 항목 SV / PV
        // NF3, O2, CF4, Press, Temp, RF
        // ==========================

        // --- SV (Target) ---
        public double SvNF3 { get; private set; }
        public double SvO2 { get; private set; }
        public double SvCF4 { get; private set; }
        public double SvPress { get; private set; }
        public double SvTemp { get; private set; }
        public double SvRF { get; private set; }

        // --- PV (Current) ---
        public double PvNF3 { get; private set; }
        public double PvO2 { get; private set; }
        public double PvCF4 { get; private set; }
        public double PvPress { get; private set; }
        public double PvTemp { get; private set; }
        public double PvRF { get; private set; }

        // ==========================
        // 이벤트 (UI에서 구독)
        // ==========================
        public event Action<ChamberRuntime> Updated;
        public event Action<ChamberRuntime> StepChanged;
        public event Action<ChamberRuntime> Completed;

        // ==========================
        // 생성자
        // ==========================
        public ChamberRuntime(string chamberName)
        {
            ChamberName = chamberName;
        }

        // ==========================
        // 레시피 로드
        // ==========================
        public void LoadRecipeSteps(List<RecipeStep> recipeSteps)
        {
            steps = recipeSteps?
                .OrderBy(s => s.StepNo)
                .ToList() ?? new List<RecipeStep>();

            ResetState();
            RaiseUpdated();
        }

        public void LoadRecipe(int recipeId)
        {
            var repo = new RecipeRepository();
            var (name, chamber, loadedSteps) = repo.LoadRecipe(recipeId);

            if (loadedSteps == null || loadedSteps.Count == 0)
            {
                MessageBox.Show($"레시피(ID:{recipeId}) 읽기 실패 또는 비어있음");
                return;
            }

            RecipeId = recipeId;
            RecipeName = name ?? "";

            LoadRecipeSteps(loadedSteps);

            if (steps.Count > 0)
            {
                SetStep(0);
                RaiseUpdated();
            }
        }

        // ==========================
        // Start / Stop / Reset
        // ==========================

        /// <summary>
        /// 수동 시작 버튼용 (처음 시작할 때만 CycleCount 증가)
        /// </summary>
        public void Start()
        {
            if (steps.Count == 0)
                return;

            if (stepIndex < 0 || stepIndex >= steps.Count)
            {
                CycleCount++;
                SetStep(0);
            }

            IsRunning = true;
            RaiseUpdated();
        }

        /// <summary>
        /// TM이 웨이퍼를 넣고 문이 닫힌 시점에서 호출
        /// → 웨이퍼 한 장 처리 시작 (CycleCount 1 증가)
        /// </summary>
        public void StartNewCycle()
        {
            System.Diagnostics.Debug.WriteLine($"[{ChamberName}] StartNewCycle - HasRecipe:{HasRecipe}, Steps:{steps.Count}, RecipeId:{RecipeId}");
            
            if (!HasRecipe)
            {
                System.Diagnostics.Debug.WriteLine($"[{ChamberName}] StartNewCycle ABORTED - No recipe loaded");
                return;
            }

            CycleCount++;      // 몇 번째 웨이퍼인지

            IsRunning = false;
            stepIndex = -1;
            elapsedMs = 0;

            SvNF3 = SvO2 = SvCF4 = SvPress = SvTemp = SvRF = 0;
            PvNF3 = PvO2 = PvCF4 = PvPress = PvTemp = PvRF = 0;

            IsRunning = true;
            System.Diagnostics.Debug.WriteLine($"[{ChamberName}] Calling SetStep(0)...");
            SetStep(0);
            System.Diagnostics.Debug.WriteLine($"[{ChamberName}] After SetStep - stepIndex:{stepIndex}, CurrentStepNo:{CurrentStepNo}");
            RaiseUpdated();
        }

        public void Stop()
        {
            IsRunning = false;
            IsPaused = false;  // 정지 시 일시정지 상태도 해제
            RaiseUpdated();
        }

        /// <summary>
        /// 공정 일시정지
        /// </summary>
        public void Pause()
        {
            if (IsRunning && !IsPaused)
            {
                IsPaused = true;
                IsRunning = false;  // 시간 진행은 멈춤
                RaiseUpdated();
            }
        }

        /// <summary>
        /// 공정 재개 (일시정지 해제)
        /// </summary>
        public void Resume()
        {
            if (IsPaused && !IsRunning)
            {
                IsPaused = false;
                IsRunning = true;  // 시간 진행 재개
                RaiseUpdated();
            }
        }

        public void ResetState()
        {
            IsRunning = false;
            IsPaused = false;  // 리셋 시 일시정지 상태도 해제
            stepIndex = -1;
            elapsedMs = 0;

            CycleCount = 0;   // 웨이퍼 카운트 초기화

            SvNF3 = SvO2 = SvCF4 = SvPress = SvTemp = SvRF = 0;
            PvNF3 = PvO2 = PvCF4 = PvPress = PvTemp = PvRF = 0;
        }

        // ==========================
        // Tick (타이머에서 주기적으로 호출)
        // ==========================
        public void Tick(int deltaMs = DefaultTickIntervalMs)
        {
            // 일시정지 상태에서는 시간 진행하지 않음 (상태는 유지)
            if (!IsRunning || IsPaused)
                return;

            if (stepIndex < 0 || stepIndex >= steps.Count)
                return;

            var cur = steps[stepIndex];

            // 1) 시간 진행
            elapsedMs += deltaMs;
            int stepDurationMs = (int)(cur.TimeSec * 1000);

            // 2) PV를 SV 쪽으로 수렴
            SimulatePvConvergence();

            // 3) Step 완료 체크
            if (elapsedMs >= stepDurationMs)
            {
                if (stepIndex + 1 < steps.Count)
                {
                    // 다음 Step으로 이동
                    SetStep(stepIndex + 1);
                }
                else
                {
                    // 마지막 Step까지 완료
                    IsRunning = false;
                    RaiseUpdated();       // 최종 상태 알림
                    Completed?.Invoke(this);
                    return;
                }
            }

            // 4) UI에 상태 변경 알림
            RaiseUpdated();
        }

        // ==========================
        // 내부 헬퍼들
        // ==========================
        private void SetStep(int newIndex)
        {
            if (newIndex < 0 || newIndex >= steps.Count)
                return;

            stepIndex = newIndex;
            elapsedMs = 0;

            var s = steps[stepIndex];

            // 현재 Step의 SV 값
            SvO2 = s.O2;
            SvNF3 = s.NF3;
            SvCF4 = s.CF4;
            SvPress = s.Press;
            SvTemp = s.Temp;
            SvRF = s.RF;

            StepChanged?.Invoke(this);
        }

        private void SimulatePvConvergence()
        {
            PvNF3 += (SvNF3 - PvNF3) * PvSmoothingFactor;
            PvO2 += (SvO2 - PvO2) * PvSmoothingFactor;
            PvCF4 += (SvCF4 - PvCF4) * PvSmoothingFactor;
            PvPress += (SvPress - PvPress) * PvSmoothingFactor;
            PvTemp += (SvTemp - PvTemp) * PvSmoothingFactor;
            PvRF += (SvRF - PvRF) * PvSmoothingFactor;
        }

        private void RaiseUpdated()
        {
            Updated?.Invoke(this);
        }
    }
}
