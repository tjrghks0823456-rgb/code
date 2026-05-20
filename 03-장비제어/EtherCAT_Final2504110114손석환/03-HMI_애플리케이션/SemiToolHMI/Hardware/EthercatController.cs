using IEG3268_Dll;

namespace SemiToolHMI.EtherCAT
{
    public class EthercatController
    {
        private readonly IEG3268 ecat = new IEG3268();

        public bool SimulationMode { get; set; } = false;
        public bool IsConnected { get; private set; } = false;
        // 기존:
        // private bool[] DO = new bool[64];

        // 수정:
        public bool[] DO = new bool[64];

        public bool ReadDO(int ch)
        {
            if (ch < 0 || ch >= 64) return false;
            return DO[ch];
        }
        public bool Connect()
        {
            if (SimulationMode)
            {
                IsConnected = true;
                return true;
            }

            try
            {
                if (ecat.CIFX_50RE_Connect())
                {
                    ecat.ReadData_Send_Start(300);
                    ecat.ReadData_Timer_Start();
                    IsConnected = true;
                    return true;
                }
            }
            catch { }

            IsConnected = false;
            return false;
        }

        public void Disconnect()
        {
            if (!IsConnected) return;
            ecat.CIFX_50RE_Disconnect();
            IsConnected = false;
        }

        public bool Ping()
        {
            if (SimulationMode) return true;
            return IsConnected; // 기본 heartbeat
        }

        // =======================
        // 실제 DO 출력!!! (핵심)
        // =======================
        public void WriteDO(int ch, bool value)
        {
            if (SimulationMode) return;

            ecat.Digital_Output(ch, value);
        }

        public bool ReadDI(int ch)
        {
            if (SimulationMode) return false;
            return ecat.Digital_Input(ch);
        }

        // =======================
        // 축 위치 데이터 읽기
        // =======================
        public string ReadAxis1Position()
        {
            if (SimulationMode) return "0";
            try
            {
                return ecat.Axis1_is_PosData();
            }
            catch
            {
                return "0";
            }
        }

        public string ReadAxis2Position()
        {
            if (SimulationMode) return "0";
            try
            {
                return ecat.Axis2_is_PosData();
            }
            catch
            {
                return "0";
            }
        }

        // =======================
        // 축 상태 읽기
        // =======================
        public bool ReadAxis1Status(string statusName)
        {
            if (SimulationMode) return false;
            try
            {
                return ecat.Axis1_Status(statusName);
            }
            catch
            {
                return false;
            }
        }

        public bool ReadAxis2Status(string statusName)
        {
            if (SimulationMode) return false;
            try
            {
                return ecat.Axis2_Status(statusName);
            }
            catch
            {
                return false;
            }
        }
    }
}
