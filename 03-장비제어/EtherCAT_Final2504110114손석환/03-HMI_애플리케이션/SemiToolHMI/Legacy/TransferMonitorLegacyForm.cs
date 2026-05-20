using System;
using System.Drawing;
using System.Windows.Forms;
using SemiToolHMI.Logic;

namespace SemiToolHMI
{
    /// <summary>
    /// FOUP/Chamber/FOUP B 웨이퍼 위치 + TM Job 모니터링 창
    /// </summary>
    public class TransferMonitorLegacyForm : Form
    {
        private readonly WaferPipelineSimulator _simulator;

        private DataGridView _grid;
        private Label _lblRobotJob;
        private Timer _timer;

        public TransferMonitorLegacyForm(WaferPipelineSimulator simulator)
        {
            _simulator = simulator ?? throw new ArgumentNullException(nameof(simulator));

            Text = "Transfer Monitor";
            Size = new Size(600, 450);
            StartPosition = FormStartPosition.CenterParent;
            BackColor = Color.FromArgb(33, 35, 45);
            ForeColor = Color.White;
            FormBorderStyle = FormBorderStyle.FixedDialog;
            MaximizeBox = false;
            MinimizeBox = false;

            KeyPreview = true;
            KeyDown += (s, e) =>
            {
                if (e.KeyCode == Keys.Escape) Close();
            };

            BuildUI();
            BuildTimer();
        }

        // ======================= UI 구성 =======================
        private void BuildUI()
        {
            // 상단 TM Job 라벨
            _lblRobotJob = new Label
            {
                Dock = DockStyle.Top,
                Height = 40,
                TextAlign = ContentAlignment.MiddleLeft,
                Padding = new Padding(10, 0, 0, 0),
                Font = new Font("Malgun Gothic", 9f, FontStyle.Bold),
                Text = "TM: Idle"
            };
            Controls.Add(_lblRobotJob);

            // 웨이퍼 위치 그리드
            _grid = new DataGridView
            {
                Dock = DockStyle.Fill,
                ReadOnly = true,
                AllowUserToAddRows = false,
                AllowUserToDeleteRows = false,
                RowHeadersVisible = false,
                BackgroundColor = Color.FromArgb(33, 35, 45),
                BorderStyle = BorderStyle.None,
                AutoSizeColumnsMode = DataGridViewAutoSizeColumnsMode.Fill,
                SelectionMode = DataGridViewSelectionMode.FullRowSelect
            };

            _grid.ColumnHeadersDefaultCellStyle.BackColor = Color.FromArgb(50, 52, 60);
            _grid.ColumnHeadersDefaultCellStyle.ForeColor = Color.White;
            _grid.EnableHeadersVisualStyles = false;

            _grid.Columns.Add("Location", "Location");
            _grid.Columns.Add("Status", "Status");

            Controls.Add(_grid);
            _grid.BringToFront();
        }

        // ======================= 타이머 =======================
        private void BuildTimer()
        {
            _timer = new Timer();
            _timer.Interval = 300;   // 0.3s마다 갱신
            _timer.Tick += (s, e) => RefreshSnapshot();
            _timer.Start();

            FormClosed += (s, e) =>
            {
                if (_timer != null)
                {
                    _timer.Stop();
                    _timer.Dispose();
                }
            };
        }

        // ======================= 상태 갱신 =======================
        private void RefreshSnapshot()
        {
            if (_simulator == null) return;

            // TM Job 표시
            string job = _simulator.LastRobotJob;
            if (string.IsNullOrEmpty(job)) job = "Idle";
            _lblRobotJob.Text = "TM: " + job;

            // 웨이퍼 위치 스냅샷
            var snap = _simulator.GetLocationSnapshot();
            _grid.Rows.Clear();

            if (snap == null) return;

            foreach (var s in snap)
            {
                _grid.Rows.Add(s.Location, s.Status);
            }
        }
    }
}
