using System;
using System.Threading.Tasks;

namespace SemiToolHMI.EtherCAT
{
    public class WaferProcessScenario
    {
        private readonly ChamberIo chamberA;
        private readonly ChamberIo chamberB;
        private readonly ChamberIo chamberC;
        private readonly StackLightIo light;

        // 로그 이벤트
        public event Action<string> OnLog;

        public WaferProcessScenario(ChamberIo a, ChamberIo b, ChamberIo c, StackLightIo light)
        {
            this.chamberA = a;
            this.chamberB = b;
            this.chamberC = c;
            this.light = light;
        }

        // =============================================================
        // 단독 공정 실행 (기존 기능)
        // =============================================================
        public async Task RunProcess()
        {
            light.Green(true);

            // A
            chamberA.Lamp(true);
            await chamberA.DoorOpen();
            await Task.Delay(1000);
            await chamberA.DoorClose();

            // B
            chamberB.Lamp(true);
            await chamberB.DoorOpen();
            await Task.Delay(1000);
            await chamberB.DoorClose();

            // C
            chamberC.Lamp(true);
            await chamberC.DoorOpen();
            await Task.Delay(1000);
            await chamberC.DoorClose();

            light.Green(false);
            light.Yellow(true);
            await Task.Delay(500);
            light.Yellow(false);
        }

        // =============================================================
        // 웨이퍼 파이프라인 시뮬레이션
        // =============================================================
        public async Task RunPipeline(int waferCount)
        {
            for (int w = 1; w <= waferCount; w++)
            {
                Log($"[W{w}] 시작");

                // 1) FOUP → A 로딩
                Log($"[W{w}] FOUP → Chamber A 로딩");
                await chamberA.DoorOpen();
                await Task.Delay(800);
                await chamberA.DoorClose();

                // 2) A 공정
                Log($"[W{w}] Chamber A 공정 시작");
                await RunChamberProcess(chamberA, "A", 10);
                Log($"[W{w}] Chamber A 공정 완료");

                // 3) A → B 이동
                Log($"[W{w}] Chamber A → B 이동");
                await chamberA.DoorOpen();
                await Task.Delay(600);
                await chamberA.DoorClose();
                await chamberB.DoorOpen();
                await Task.Delay(600);
                await chamberB.DoorClose();

                // 4) Chamber B 공정
                Log($"[W{w}] Chamber B 공정 시작");
                await RunChamberProcess(chamberB, "B", 8);
                Log($"[W{w}] Chamber B 공정 완료");

                // 5) B → C 이동
                Log($"[W{w}] Chamber B → C 이동");
                await chamberB.DoorOpen();
                await Task.Delay(600);
                await chamberB.DoorClose();
                await chamberC.DoorOpen();
                await Task.Delay(600);
                await chamberC.DoorClose();

                // 6) Chamber C 공정
                Log($"[W{w}] Chamber C 공정 시작");
                await RunChamberProcess(chamberC, "C", 12);
                Log($"[W{w}] Chamber C 공정 완료");

                // 7) Finished → FOUP B
                Log($"[W{w}] Chamber C → FOUP B 언로딩");
                await chamberC.DoorOpen();
                await Task.Delay(600);
                await chamberC.DoorClose();

                Log($"[W{w}] 완료");
            }

            Log("=== 모든 웨이퍼 작업 완료 ===");
        }

        // =============================================================
        // 공정 진행 함수
        // =============================================================
        private async Task RunChamberProcess(ChamberIo chamber, string name, int sec)
        {
            // chamber 매개변수는 향후 확장을 위해 유지
            _ = chamber; // 사용하지 않는 매개변수 경고 방지
            
            for (int t = 1; t <= sec; t++)
            {
                Log($"{name} Chamber 공정 진행중… {t}/{sec}s");
                await Task.Delay(1000);
            }
        }

        // =============================================================
        // 로그 함수
        // =============================================================
        private void Log(string msg)
        {
            OnLog?.Invoke($"{DateTime.Now:HH:mm:ss} {msg}");
        }
    }
}
