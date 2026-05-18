using IEG3268_Dll;

namespace SemiToolHMI
{
    /// <summary>
    /// EtherCAT 모션 컨트롤러 공용 컨텍스트
    /// (MainForm, DeviceControlForm 등에서 같이 사용)
    /// </summary>
    public static class EthercatMotion
    {
        public static readonly IEG3268 EtherCAT_M = new IEG3268();

        public static bool IsConnected { get; private set; } = false;

        public static bool EnsureConnected()
        {
            if (IsConnected) return true;

            if (EtherCAT_M.CIFX_50RE_Connect())
            {
                EtherCAT_M.ReadData_Send_Start(300);
                EtherCAT_M.ReadData_Timer_Start();
                IsConnected = true;
                return true;
            }
            return false;
        }
    }
}
