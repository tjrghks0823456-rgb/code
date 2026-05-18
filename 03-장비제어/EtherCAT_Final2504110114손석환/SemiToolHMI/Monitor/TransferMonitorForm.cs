using System;
using System.Drawing;
using System.Windows.Forms;
using SemiToolHMI.Logic;

namespace SemiToolHMI.Monitor
{
    public partial class TransferMonitorForm : Form
    {
        private readonly WaferPipelineSimulator simulator;
        private Timer refreshTimer;

        public TransferMonitorForm(WaferPipelineSimulator simulator)
        {
            this.simulator = simulator ?? throw new ArgumentNullException(nameof(simulator));

            InitializeComponent();   // 디자이너 UI

            // ★ 기본 스타일 한 번 지정
            grid.EnableHeadersVisualStyles = false;
            grid.DefaultCellStyle.ForeColor = Color.Black;
            grid.DefaultCellStyle.BackColor = Color.White;
            grid.DefaultCellStyle.SelectionBackColor = Color.FromArgb(0, 120, 215);
            grid.DefaultCellStyle.SelectionForeColor = Color.Black;

            grid.RowsDefaultCellStyle.ForeColor = Color.Black;
            grid.AlternatingRowsDefaultCellStyle.ForeColor = Color.Black;

            // ★ 셀 그릴 때마다 강제로 색 덮어쓰기
            grid.CellFormatting += Grid_CellFormatting;

            BuildTimer();            // 타이머
        }

        // ★ 여기서 글자색/배경색을 무조건 강제
        private void Grid_CellFormatting(object sender, DataGridViewCellFormattingEventArgs e)
        {
            e.CellStyle.BackColor = Color.White;                  // 평상시 흰 배경
            e.CellStyle.ForeColor = Color.Black;                  // 평상시 검은 글씨
            e.CellStyle.SelectionBackColor = Color.FromArgb(0, 120, 215); // 선택 시 파란 배경
            e.CellStyle.SelectionForeColor = Color.Black;         // 선택 시에도 검은 글씨
        }

        private void BuildTimer()
        {
            refreshTimer = new Timer();
            refreshTimer.Interval = 500;
            refreshTimer.Tick += (s, e) => RefreshFromSimulator();
            refreshTimer.Start();
        }

        private void RefreshFromSimulator()
        {
            if (simulator == null) return;

            var snapshot = simulator.GetLocationSnapshot();

            grid.SuspendLayout();
            grid.Rows.Clear();

            foreach (var s in snapshot)
            {
                grid.Rows.Add(s.Location, s.Status);
            }

            grid.ResumeLayout();

            lblRobotJob.Text = "TM: " + simulator.LastRobotJob;
        }
    }
}
