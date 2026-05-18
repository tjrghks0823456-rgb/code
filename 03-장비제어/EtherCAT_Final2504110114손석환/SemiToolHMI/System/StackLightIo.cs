using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace SemiToolHMI.EtherCAT
{
    public class StackLightIo
    {
        private readonly EthercatController ec;

        public StackLightIo(EthercatController ec)
        {
            this.ec = ec;
        }

        public void Red(bool on)
        {
            ec.WriteDO(IoMap.RED, on);
        }

        public void Yellow(bool on)
        {
            ec.WriteDO(IoMap.YELLOW, on);
        }

        public void Green(bool on)
        {
            ec.WriteDO(IoMap.GREEN, on);
        }

        public void AllOff()
        {
            Red(false);
            Yellow(false);
            Green(false);
        }
    }
}

