using System;
using System.Net;
using System.Net.Sockets;
using System.Text;

namespace UDPClient
{
    class Program
    {
        // UDP 클라이언트: 연결 없이 서버 주소로 데이터를 보내고 응답을 기다립니다.
        static string SERVERIP = "172.16.11.92";
        const int SERVERPORT = 9000;
        const int BUFSIZE = 512;

        static void Main(string[] args)
        {
            int retval;

            // 명령행 인수가 있으면 IP 주소로 사용
            if (args.Length > 0)
                SERVERIP = args[0];

            Socket sock = null;

            try
            {
                // UDP 소켓 생성
                sock = new Socket(
                    AddressFamily.InterNetwork,
                    SocketType.Dgram,
                    ProtocolType.Udp
                );

                // 서버 응답 대기 시간 설정: 3초
                sock.ReceiveTimeout = 3000;
            }
            catch (Exception e)
            {
                Console.WriteLine("[소켓 생성 오류] " + e.Message);
                Environment.Exit(1);
            }

            // 서버 주소 설정
            IPEndPoint serveraddr = new IPEndPoint(
                IPAddress.Parse(SERVERIP),
                SERVERPORT
            );

            // 수신 버퍼
            byte[] buf = new byte[BUFSIZE];

            Console.WriteLine("[UDP 클라이언트 시작]");
            Console.WriteLine("서버 IP: {0}", SERVERIP);
            Console.WriteLine("서버 PORT: {0}", SERVERPORT);

            while (true)
            {
                Console.Write("\n[보낼 데이터] ");
                string data = Console.ReadLine();

                if (string.IsNullOrEmpty(data))
                {
                    Console.WriteLine("[종료]");
                    break;
                }

                try
                {
                    // 문자열을 바이트 배열로 변환
                    byte[] senddata = Encoding.Default.GetBytes(data);

                    int size = senddata.Length;
                    if (size > BUFSIZE)
                        size = BUFSIZE;

                    // 데이터 보내기
                    retval = sock.SendTo(
                        senddata,
                        0,
                        size,
                        SocketFlags.None,
                        serveraddr
                    );

                    Console.WriteLine("[UDP 클라이언트] {0}바이트를 보냈습니다.", retval);

                    // 데이터 받기
                    IPEndPoint anyaddr = new IPEndPoint(IPAddress.Any, 0);
                    EndPoint peeraddr = (EndPoint)anyaddr;

                    retval = sock.ReceiveFrom(
                        buf,
                        0,
                        BUFSIZE,
                        SocketFlags.None,
                        ref peeraddr
                    );

                    // 받은 데이터 출력
                    Console.WriteLine("[UDP 클라이언트] {0}바이트를 받았습니다.", retval);
                    Console.WriteLine("[보낸 쪽 주소] {0}", peeraddr.ToString());
                    Console.WriteLine("[받은 데이터] {0}",
                        Encoding.Default.GetString(buf, 0, retval));
                }
                catch (SocketException e)
                {
                    if (e.SocketErrorCode == SocketError.TimedOut)
                    {
                        Console.WriteLine("[오류] 서버 응답이 없습니다.");
                        Console.WriteLine("서버가 실행 중인지, IP와 포트가 맞는지 확인하세요.");
                    }
                    else
                    {
                        Console.WriteLine("[소켓 오류] " + e.Message);
                    }
                }
                catch (Exception e)
                {
                    Console.WriteLine("[오류] " + e.Message);
                }
            }

            // 소켓 닫기
            if (sock != null)
                sock.Close();
        }
    }
}
