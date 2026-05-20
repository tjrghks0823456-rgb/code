using System;
using System.Collections.Generic;
using SemiToolHMI.Models;

namespace SemiToolHMI.Logic
{
    /// <summary>
    /// 개별 챔버 1개가 레시피를 실행할 때의 시퀀스 로직
    /// - 인터락 체크
    /// - Step / 시간 진행
    /// - 상태(Idle/Ready/Running/Complete/Alarm) 관리
    /// </summary>
    public class ChamberProcessSequence
    {
        // ─ 상태 / 기본 정보 ────────────────
        public ProcState State { get; private set; } = ProcState.Idle;

        public string ChamberName { get; private set; }

        // 현재 챔버에 들어와 있는 웨이퍼 (단순 정보용)
        public Wafer LoadedWafer { get; private set; }

        // DB에서 읽어온 레시피 Step 목록
        public List<RecipeStep> Steps { get; private set; } = new List<RecipeStep>();

        // 현재 진행 중인 Step 인덱스 (0-based)
        public int StepIndex { get; private set; }

        // 현재 Step에서 경과된 시간(ms)
        public int StepTimeCurMs { get; private set; }

        // 마지막 알람 메시지
        public string LastAlarm { get; private set; } = "";

        // ─ 인터락 플래그 (폼/PLC에서 세팅) ─
        public bool WaferPresent { get; set; }    // 웨이퍼 감지 센서
        public bool DoorClosed { get; set; }      // 도어 닫힘
        public bool PumpOk { get; set; }          // 진공/펌프 정상

        public ChamberProcessSequence(string chamberName)
        {
            ChamberName = chamberName;
            State = ProcState.Idle;
        }

        /// <summary>
        /// FOUP/TM에서 웨이퍼가 들어오고, 선택한 레시피 Step을 세팅
        /// </summary>
        public bool Load(Wafer wafer, IList<RecipeStep> steps)
        {
            // Idle 또는 Complete 상태에서만 새 레시피 로드 허용
            if (State != ProcState.Idle && State != ProcState.Complete)
            {
                Fail("Idle/Complete 상태가 아님");
                return false;
            }

            if (wafer == null)
            {
                Fail("웨이퍼 정보 없음");
                return false;
            }

            if (steps == null || steps.Count == 0)
            {
                Fail("레시피 Step 없음");
                return false;
            }

            LoadedWafer = wafer;
            Steps = new List<RecipeStep>(steps);

            StepIndex = 0;
            StepTimeCurMs = 0;
            LastAlarm = "";
            State = ProcState.Ready;

            return true;
        }

        /// <summary>
        /// 인터락 검사 후 Running 진입 시도
        /// </summary>
        public bool TryStart()
        {
            if (State != ProcState.Ready)
            {
                Fail("Ready 상태가 아님");
                return false;
            }

            if (!WaferPresent)
            {
                Fail("Wafer 센서 Off");
                return false;
            }
            if (!DoorClosed)
            {
                Fail("챔버 Door 열림");
                return false;
            }
            if (!PumpOk)
            {
                Fail("진공/펌프 이상");
                return false;
            }

            State = ProcState.Running;
            StepTimeCurMs = 0;
            return true;
        }

        /// <summary>
        /// 주기적으로 호출 (예: 500ms)
        /// </summary>
        public void Tick(int deltaMs)
        {
            if (State != ProcState.Running)
                return;

            if (StepIndex < 0 || StepIndex >= Steps.Count)
            {
                State = ProcState.Complete;
                return;
            }

            StepTimeCurMs += deltaMs;

            RecipeStep cur = Steps[StepIndex];
            int targetMs = cur.Time_s * 1000;

            if (StepTimeCurMs >= targetMs)
            {
                // 다음 Step으로
                StepIndex++;
                StepTimeCurMs = 0;

                if (StepIndex >= Steps.Count)
                {
                    State = ProcState.Complete;
                }
            }
        }

        /// <summary>
        /// 사용자/알람으로 공정 중단
        /// </summary>
        public void Abort(string reason)
        {
            Fail(reason);
        }

        /// <summary>
        /// Idle 초기화
        /// </summary>
        public void Reset()
        {
            LoadedWafer = null;
            Steps.Clear();
            StepIndex = 0;
            StepTimeCurMs = 0;
            LastAlarm = "";
            State = ProcState.Idle;

            // 인터락은 외부에서 다시 세팅
        }

        private void Fail(string msg)
        {
            LastAlarm = msg;
            State = ProcState.Alarm;
        }
    }
}
