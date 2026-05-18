using System;

namespace SemiToolHMI.Logic
{
    public enum ProcState
    {
        Idle,
        Ready,
        Running,
        Complete,
        Alarm
    }

    /// <summary>
    /// 공정 시퀀스 + Step 시간 관리 + Step 이동 처리
    /// (레시피 Step 데이터는 MainForm에서 넣어줌)
    /// </summary>
    public class ProcessSequence
    {
        public ProcState State { get; private set; } = ProcState.Idle;

        // ---- 인터락 입력 ----
        public bool FoupPresent { get; set; }
        public bool DoorClosed { get; set; }
        public bool Clamped { get; set; }
        public bool VacuumOk { get; set; }
        public bool RecipeSelected { get; set; }

        // ---- Step 진행 상태 ----
        public int CurrentStep { get; private set; } = 0;
        public int TotalSteps { get; private set; } = 0;

        public int StepTimeCur { get; private set; } = 0;
        public int StepTimeMax { get; private set; } = 0;

        public string LastAlarm { get; private set; } = "";

        // ===== Setter 안전화 =====
        public void SetStepCount(int total)
        {
            TotalSteps = Math.Max(1, total);
        }

        public void SetCurrentStep(int step)
        {
            CurrentStep = Math.Max(1, step);
        }

        public void SetStepTimeMax(int sec)
        {
            StepTimeMax = Math.Max(1, sec);
        }

        // ====================================================
        // 공정 시작 시도
        // ====================================================
        public bool TryStart()
        {
            if (!FoupPresent) return Fail("FOUP 미장착");
            if (!DoorClosed) return Fail("Door 미닫힘");
            if (!Clamped) return Fail("Clamp 미동작");
            if (!VacuumOk) return Fail("진공 미완료");
            if (!RecipeSelected) return Fail("Recipe 미선택");

            State = ProcState.Running;
            StepTimeCur = 0;
            LastAlarm = "";

            if (CurrentStep <= 0) CurrentStep = 1;
            if (TotalSteps <= 0) TotalSteps = 1;
            if (StepTimeMax <= 0) StepTimeMax = 10;

            return true;
        }

        // ====================================================
        // Tick 호출 (예: 500ms)
        // ====================================================
        public void Tick(int deltaMs)
        {
            if (State != ProcState.Running) return;

            StepTimeCur += deltaMs;

            if (StepTimeCur >= StepTimeMax * 1000)
            {
                // 다음 Step 이동
                CurrentStep++;
                StepTimeCur = 0;

                if (CurrentStep > TotalSteps)
                {
                    State = ProcState.Complete;
                }
            }
        }

        // ====================================================
        public void Reset()
        {
            State = ProcState.Idle;
            CurrentStep = 0;
            TotalSteps = 0;
            StepTimeCur = 0;
            StepTimeMax = 0;
            LastAlarm = "";
        }

        public void Abort(string reason = "사용자 정지")
        {
            State = ProcState.Alarm;
            LastAlarm = reason;
        }

        private bool Fail(string msg)
        {
            State = ProcState.Alarm;
            LastAlarm = msg;
            return false;
        }
    }
}
