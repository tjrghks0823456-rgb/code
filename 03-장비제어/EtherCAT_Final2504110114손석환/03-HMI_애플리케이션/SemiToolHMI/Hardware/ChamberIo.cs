using System.Threading.Tasks;

namespace SemiToolHMI.EtherCAT
{
    public class ChamberIo
    {
        private readonly EthercatController ec;

        // 충돌 방지를 위해 필드 이름 변경 (DoorOpen(), DoorClose()와의 이름 충돌 해결)
        private readonly int lampChannel;
        private readonly int doorOpenChannel;
        private readonly int doorCloseChannel;

        public ChamberIo(EthercatController ec, int lampCh, int doorOpenCh, int doorCloseCh)
        {
            this.ec = ec;
            this.lampChannel = lampCh;
            this.doorOpenChannel = doorOpenCh;
            this.doorCloseChannel = doorCloseCh;
        }

        // ------------------------
        // Lamp 제어
        // ------------------------
        public void Lamp(bool on)
        {
            ec.WriteDO(lampChannel, on);
        }

        // ------------------------
        // Door 제어 (실제 EtherCAT DO 방식)
        // ------------------------
        public async Task DoorOpen()
        {
            // OPEN = Open DO true, Close DO false
            ec.WriteDO(doorOpenChannel, true);
            ec.WriteDO(doorCloseChannel, false);
            await Task.Delay(200);   // async 유지 목적
        }

        public async Task DoorClose()
        {
            // CLOSE = Open DO false, Close DO true
            ec.WriteDO(doorOpenChannel, false);
            ec.WriteDO(doorCloseChannel, true);
            await Task.Delay(200);   // async 유지 목적
        }
    }
}
