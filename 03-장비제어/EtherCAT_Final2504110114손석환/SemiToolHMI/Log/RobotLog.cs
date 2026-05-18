using System;

namespace SemiToolHMI
{
    /// <summary>
    /// RobotScenario 등에서 사용하는 간단한 로그 헬퍼
    /// - UI 쪽에서 LogTarget을 등록해주면 그쪽으로 문자열을 보내줌
    /// </summary>
    public static class RobotLog
    {
        // 실제로 로그를 출력할 대상을 등록 (예: Debug 폼의 AppendLog)
        public static Action<string> LogTarget { get; private set; }

        public static void Register(Action<string> target)
        {
            LogTarget = target;
        }

        private static void Write(string level, string message)
        {
            var line = $"[{DateTime.Now:HH:mm:ss.fff}] [{level}] {message}";
            LogTarget?.Invoke(line);
        }

        public static void Info(string message) => Write("INFO", message);
        public static void Warn(string message) => Write("WARN", message);
        public static void Error(string message) => Write("ERROR", message);
    }
}
