using System;
using System.Text;
using System.Net.Sockets;

namespace ConsoleApp2
{
    class Program
    {
        // TCP 클라이언트: 서버에 먼저 연결한 뒤 데이터를 순서대로 보냅니다.
        static string SERVERIP = "172.16.11.92";
        const int SERVERPORT = 9000;
        const int BUFSIZE = 50;

        static void Main(string[] args)
        {
            int retval;

            if (args.Length > 0)
                SERVERIP = args[0];

            Socket sock = null;

            try
            {
                sock = new Socket(AddressFamily.InterNetwork,
                    SocketType.Stream, ProtocolType.Tcp);

                sock.Connect(SERVERIP, SERVERPORT);
                Console.WriteLine("서버 접속 성공");
            }
            catch (Exception e)
            {
                Console.WriteLine("접속 오류: " + e.Message);
                Environment.Exit(1);
            }

            byte[] buf = new byte[BUFSIZE];

            string[] testdata =
            {
                "장준영",
                "안녕하세요",
                "저 들어왔습니다",
                "반갑습니다"
            };

            for (int i = 0; i < testdata.Length; i++)
            {
                Array.Clear(buf, 0, buf.Length);

                byte[] senddata = Encoding.Default.GetBytes(testdata[i]);

                int len = senddata.Length;
                if (len > BUFSIZE)
                    len = BUFSIZE;

                Array.Copy(senddata, 0, buf, 0, len);

                for (int j = len; j < BUFSIZE; j++)
                {
                    buf[j] = (byte)'#';
                }

                try
                {
                    retval = sock.Send(buf, 0, BUFSIZE, SocketFlags.None);
                    Console.WriteLine("[TCP 클라이언트] {0}바이트 보냄: {1}", retval, testdata[i]);
                }
                catch (Exception e)
                {
                    Console.WriteLine("전송 오류: " + e.Message);
                    break;
                }
            }

            sock.Close();
            Console.WriteLine("종료");
        }
    }
}
