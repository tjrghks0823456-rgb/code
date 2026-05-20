using System;
using System.Drawing;
using System.Windows.Forms;

namespace SemiToolHMI
{
    // ★ 중요: partial 로 선언해야 Designer 쪽과 합쳐집니다.
    public partial class RobotLogicForm : Form
    {
        public RobotLogicForm()
        {
            InitializeComponent();   // 디자이너가 만든 컨트롤 생성

            // txtLog 기본 스타일 세팅 (원하는 로그 콘솔 느낌)
            txtLog.Multiline = true;
            txtLog.ScrollBars = ScrollBars.Both;
            txtLog.Font = new Font("Consolas", 9);
            txtLog.BackColor = Color.Black;
            txtLog.ForeColor = Color.Lime;
            txtLog.ReadOnly = true;
            txtLog.WordWrap = false;
        }

        /// <summary>
        /// RobotScenario / RobotLog 에서 호출할 실제 로그 출력 함수
        /// </summary>
        public void AppendLog(string line)
        {
            if (txtLog.InvokeRequired)
            {
                // 다른 스레드에서 호출되면 UI 스레드로 마샬링
                txtLog.BeginInvoke(new Action<string>(AppendLog), line);
                return;
            }

            txtLog.AppendText(line + Environment.NewLine);
        }

        // ===== 폼 생명주기 / 버튼 이벤트 =====

        protected override void OnShown(EventArgs e)
        {
            base.OnShown(e);

            // 이 폼이 화면에 나타날 때 RobotLog에 등록
            RobotLog.Register(AppendLog);
            RobotLog.Info("=== RobotLogicForm Open ===");
        }

        protected override void OnFormClosed(FormClosedEventArgs e)
        {
            // 폼 닫힐 때 로그 대상 해제
            RobotLog.Register(null);
            base.OnFormClosed(e);
        }

        // 디자이너가 this.btnClear.Click += btnClear_Click; 을 가지고 있을 가능성이 높아서
        // 실제 핸들러 메서드를 만들어 준다.

        private void btnClear_Click(object sender, EventArgs e)
        {
            txtLog.Clear();
        }

        private void btnCopy_Click(object sender, EventArgs e)
        {
            if (!string.IsNullOrEmpty(txtLog.Text))
            {
                Clipboard.SetText(txtLog.Text);
            }
        }
    }
}
