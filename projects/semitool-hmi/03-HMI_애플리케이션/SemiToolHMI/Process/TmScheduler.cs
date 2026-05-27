using System.Collections.Generic;
using System.Linq;

namespace SemiToolHMI.Logic
{
    /// <summary>
    /// 웨이퍼가 전체 공정을 어디까지 진행했는지 저장용
    /// </summary>
    public class WaferState
    {
        public int Id { get; set; }        // FOUP 슬롯 번호(1~5 등)
        public int Slot { get; set; }      // 같은 의미로 사용 가능
        public int Stage { get; set; }     // 0=대기, 1=A, 2=B, 3=C, 4=완료 등
        public bool InProcess { get; set; }
    }

    /// <summary>
    /// 간단한 TM 스케줄러 (C# 7.3 호환)
    /// </summary>
    public class TmScheduler
    {
        private readonly List<WaferState> wafers;

        public int SlotCount { get; private set; }

        public bool AllCompleted
        {
            get
            {
                return wafers.All(w => w.Stage >= 4);
            }
        }

        public TmScheduler(int slotCount)
        {
            if (slotCount <= 0) slotCount = 1;

            SlotCount = slotCount;
            wafers = new List<WaferState>();

            // FOUP A 슬롯에 웨이퍼 초기화
            for (int i = 1; i <= SlotCount; i++)
            {
                WaferState ws = new WaferState();
                ws.Id = i;
                ws.Slot = i;
                ws.Stage = 0;      // 아직 아무 공정도 안 함
                ws.InProcess = false;

                wafers.Add(ws);
            }
        }

        /// <summary>
        /// 다음에 처리할 웨이퍼 하나 가져오기 (아직 공정 안한 것부터)
        /// </summary>
        public WaferState GetNextToProcess()
        {
            return wafers
                .Where(w => !w.InProcess && w.Stage < 4)
                .OrderBy(w => w.Id)
                .FirstOrDefault();
        }

        /// <summary>
        /// 웨이퍼 한 스텝 완료 처리
        /// Stage: 0→1(A), 1→2(B), 2→3(C), 3→4(완료)
        /// </summary>
        public void CompleteStep(WaferState w)
        {
            if (w == null) return;

            w.InProcess = false;
            if (w.Stage < 4)
            {
                w.Stage++;
            }
        }

        /// <summary>
        /// 웨이퍼를 챔버에 투입 시작했을 때 호출 (InProcess 플래그만)
        /// </summary>
        public void StartProcess(WaferState w)
        {
            if (w == null) return;
            w.InProcess = true;
        }

        public List<WaferState> GetSnapshot()
        {
            // 외부에서 수정 못 하도록 복사본 리턴
            List<WaferState> copy = new List<WaferState>();
            foreach (WaferState w in wafers)
            {
                WaferState c = new WaferState();
                c.Id = w.Id;
                c.Slot = w.Slot;
                c.Stage = w.Stage;
                c.InProcess = w.InProcess;
                copy.Add(c);
            }
            return copy;
        }
    }
}
