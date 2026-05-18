using System;
using System.Drawing;
using System.Windows.Forms;
using SemiToolHMI.Logic;

namespace SemiToolHMI
{
    public class VerificationForm : Form
    {
        private readonly WaferPipelineSimulator simulator;

        private Label lblLot;
        private Label lblFoupA;
        private Label lblFoupB;
        private Label lblChA;
        private Label lblChB;
        private Label lblChC;

        private Timer timer;

        public VerificationForm(WaferPipelineSimulator simulator)
        {
            this.simulator = simulator ?? throw new ArgumentNullException(nameof(simulator));

            Text = "Verification - Process Overview";
            Size = new Size(420, 260);
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

        private void BuildUI()
        {
            var layout = new TableLayoutPanel
            {
                Dock = DockStyle.Fill,
                ColumnCount = 2,
                RowCount = 6,
                Padding = new Padding(15),
            };
            layout.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 40));
            layout.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 60));

            Controls.Add(layout);

            lblLot = AddRow(layout, 0, "Lot 상태");
            lblFoupA = AddRow(layout, 1, "FOUP A");
            lblFoupB = AddRow(layout, 2, "FOUP B");
            lblChA = AddRow(layout, 3, "Chamber A");
            lblChB = AddRow(layout, 4, "Chamber B");
            lblChC = AddRow(layout, 5, "Chamber C");
        }

        private Label AddRow(TableLayoutPanel layout, int row, string title)
        {
            layout.RowStyles.Add(new RowStyle(SizeType.Percent, 100f / 6f));

            var lblTitle = new Label
            {
                Text = title,
                Dock = DockStyle.Fill,
                TextAlign = ContentAlignment.MiddleLeft,
                Font = new Font("Malgun Gothic", 9f, FontStyle.Bold)
            };
            var lblValue = new Label
            {
                Text = "-",
                Dock = DockStyle.Fill,
                TextAlign = ContentAlignment.MiddleLeft,
                Font = new Font("Malgun Gothic", 9f, FontStyle.Regular)
            };

            layout.Controls.Add(lblTitle, 0, row);
            layout.Controls.Add(lblValue, 1, row);

            return lblValue;
        }

        private void BuildTimer()
        {
            timer = new Timer();
            timer.Interval = 300;  // 0.3초마다 갱신
            timer.Tick += (s, e) => RefreshStatus();
            timer.Start();

            FormClosed += (s, e) => timer.Stop();
        }

        private void RefreshStatus()
        {
            if (simulator == null) return;

            int total = simulator.TotalTarget;
            int comp = simulator.CompletedCount;
            int aCnt = simulator.FoupACurrent;
            int bCnt = simulator.FoupBCurrent;

            if (total <= 0)
            {
                lblLot.Text = "Idle";
            }
            else
            {
                lblLot.Text = (comp >= total)
                    ? $"완료 ({comp}/{total})"
                    : $"진행 중 ({comp}/{total})";
            }

            lblFoupA.Text = (total <= 0)
                ? "대기"
                : $"잔여 {aCnt} / {total}";

            lblFoupB.Text = (total <= 0)
                ? "대기"
                : $"완료 {bCnt} / {total}";

            lblChA.Text = simulator.ChamberABusy ? "Processing" : "Idle";
            lblChB.Text = simulator.ChamberBBusy ? "Processing" : "Idle";
            lblChC.Text = simulator.ChamberCBusy ? "Processing" : "Idle";
        }
    }
}
