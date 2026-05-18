using System;
using System.Drawing;
using System.Windows.Forms;

namespace SemiToolHMI.Controls
{
    public class StepEditForm : Form
    {
        public int StepNo { get; private set; }
        public string Mode { get; private set; }
        public double TimeSec { get; private set; }
        public double O2 { get; private set; }
        public double NF3 { get; private set; }
        public double CF4 { get; private set; }
        public double Press { get; private set; }
        public double Temp { get; private set; }
        public double RF { get; private set; }

        private TextBox txtStep, txtMode, txtTime, txtO2, txtNF3, txtCF4, txtPress, txtTemp, txtRF;

        public StepEditForm(int stepNo, string mode,
                            double timeSec, double o2, double nf3,
                            double cf4, double press, double temp, double rf)
        {
            Text = "Edit Step";
            FormBorderStyle = FormBorderStyle.FixedDialog;
            StartPosition = FormStartPosition.CenterParent;
            MaximizeBox = MinimizeBox = false;
            ClientSize = new Size(360, 290); // Height increased

            BuildUI();

            // 초기값 세팅
            txtStep.Text = stepNo.ToString();
            txtMode.Text = mode;
            txtTime.Text = timeSec.ToString();
            txtO2.Text = o2.ToString();
            txtNF3.Text = nf3.ToString();
            txtCF4.Text = cf4.ToString();
            txtPress.Text = press.ToString();
            txtTemp.Text = temp.ToString();
            txtRF.Text = rf.ToString();
        }

        private void BuildUI()
        {
            var table = new TableLayoutPanel
            {
                Dock = DockStyle.Top,
                RowCount = 9, // Increased row count
                ColumnCount = 2,
                Height = 230, // Increased height
                Padding = new Padding(10),
                AutoSize = false
            };
            table.ColumnStyles.Add(new ColumnStyle(SizeType.Absolute, 80));
            table.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 100));

            txtStep = AddRow(table, 0, "Step");
            txtMode = AddRow(table, 1, "Mode");
            txtTime = AddRow(table, 2, "Time(s)");
            txtO2 = AddRow(table, 3, "O2");
            txtNF3 = AddRow(table, 4, "NF3");
            txtCF4 = AddRow(table, 5, "CF4");
            txtPress = AddRow(table, 6, "Press");
            txtTemp = AddRow(table, 7, "Temp");
            txtRF = AddRow(table, 8, "RF");

            Controls.Add(table);

            var panelButtons = new FlowLayoutPanel
            {
                Dock = DockStyle.Bottom,
                Height = 40,
                FlowDirection = FlowDirection.RightToLeft,
                Padding = new Padding(10)
            };

            var btnOk = new Button
            {
                Text = "OK",
                DialogResult = DialogResult.OK,
                Width = 80
            };
            btnOk.Click += BtnOk_Click;

            var btnCancel = new Button
            {
                Text = "Cancel",
                DialogResult = DialogResult.Cancel,
                Width = 80
            };

            panelButtons.Controls.Add(btnOk);
            panelButtons.Controls.Add(btnCancel);

            Controls.Add(panelButtons);

            AcceptButton = btnOk;
            CancelButton = btnCancel;
        }

        private TextBox AddRow(TableLayoutPanel t, int row, string label)
        {
            t.RowStyles.Add(new RowStyle(SizeType.Absolute, 24));

            var lbl = new Label
            {
                Text = label,
                Dock = DockStyle.Fill,
                TextAlign = ContentAlignment.MiddleLeft,
                ForeColor = Color.Black
            };
            var txt = new TextBox { Dock = DockStyle.Fill };

            t.Controls.Add(lbl, 0, row);
            t.Controls.Add(txt, 1, row);
            return txt;
        }

        private void BtnOk_Click(object sender, EventArgs e)
        {
            if (!int.TryParse(txtStep.Text, out var stepNo))
            {
                MessageBox.Show("Step는 정수로 입력하세요.");
                DialogResult = DialogResult.None;
                return;
            }

            StepNo = stepNo;
            Mode = txtMode.Text;

            double.TryParse(txtTime.Text, out var time);
            double.TryParse(txtO2.Text, out var o2);
            double.TryParse(txtNF3.Text, out var nf3);
            double.TryParse(txtCF4.Text, out var cf4);
            double.TryParse(txtPress.Text, out var press);
            double.TryParse(txtTemp.Text, out var temp);
            double.TryParse(txtRF.Text, out var rf);

            TimeSec = time;
            O2 = o2;
            NF3 = nf3;
            CF4 = cf4;
            Press = press;
            Temp = temp;
            RF = rf;
        }
    }
}
