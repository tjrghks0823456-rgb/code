using SemiToolHMI.Models;
using System;
using System.Drawing;
using System.Windows.Forms;

namespace SemiToolHMI
{
    public class StepEditDialog : Form
    {
        private TextBox txtMode;
        private NumericUpDown numStepNo;
        private NumericUpDown numTime;
        private NumericUpDown numO2;
        private NumericUpDown numNF3;
        private NumericUpDown numCF4;
        private NumericUpDown numPress;
        private NumericUpDown numTemp;

        public RecipeStep Step { get; private set; }

        public StepEditDialog(RecipeStep step = null)
        {
            this.Text = "Edit Step";
            this.Size = new Size(350, 500);
            this.StartPosition = FormStartPosition.CenterParent;
            this.BackColor = Color.FromArgb(35, 37, 45);
            this.FormBorderStyle = FormBorderStyle.FixedDialog;

            Step = step ?? new RecipeStep();

            BuildUI();
            LoadExisting(Step);
        }

        private void BuildUI()
        {
            int labelX = 30;
            int inputX = 120;
            int y = 20;
            int gap = 45;

            // === StepNo ===
            AddLabel("Step No", labelX, y);
            numStepNo = AddNumber(1, 999, inputX, y);
            y += gap;

            // === Mode ===
            AddLabel("Mode", labelX, y);
            txtMode = AddTextbox(inputX, y);
            y += gap;

            // === Time ===
            AddLabel("Time(s)", labelX, y);
            numTime = AddNumber(0, 9999, inputX, y);
            y += gap;

            // === O2 ===
            AddLabel("O2", labelX, y);
            numO2 = AddNumber(0, 9999, inputX, y);
            y += gap;

            // === NF3 ===
            AddLabel("NF3", labelX, y);
            numNF3 = AddNumber(0, 9999, inputX, y);
            y += gap;

            // === CF4 ===
            AddLabel("CF4", labelX, y);
            numCF4 = AddNumber(0, 9999, inputX, y);
            y += gap;

            // === Press ===
            AddLabel("Press", labelX, y);
            numPress = AddNumber(0, 9999, inputX, y);
            y += gap;

            // === Temp ===
            AddLabel("Temp", labelX, y);
            numTemp = AddNumber(0, 9999, inputX, y);
            y += gap;

            // === OK Button ===
            var btnOK = new Button
            {
                Text = "OK",
                Width = 80,
                Height = 30,
                Left = (this.Width / 2) - 50,
                Top = y + 10,
                BackColor = Color.FromArgb(50, 52, 60),
                ForeColor = Color.White
            };
            btnOK.Click += BtnOk_Click;

            this.Controls.Add(btnOK);
        }

        private void LoadExisting(RecipeStep s)
        {
            numStepNo.Value = s.StepNo <= 0 ? 1 : s.StepNo;
            txtMode.Text = s.Mode;
            numTime.Value = s.Time_s;
            numO2.Value = (decimal)s.O2_SV;
            numNF3.Value = (decimal)s.NF3_SV;
            numCF4.Value = (decimal)s.CF4_SV;
            numPress.Value = (decimal)s.Press_SV;
            numTemp.Value = (decimal)s.Temp_SV;
        }

        private void BtnOk_Click(object sender, EventArgs e)
        {
            Step.StepNo = (int)numStepNo.Value;
            Step.Mode = txtMode.Text;
            Step.Time_s = (int)numTime.Value;
            Step.O2_SV = (double)numO2.Value;
            Step.NF3_SV = (double)numNF3.Value;
            Step.CF4_SV = (double)numCF4.Value;
            Step.Press_SV = (double)numPress.Value;
            Step.Temp_SV = (double)numTemp.Value;

            this.DialogResult = DialogResult.OK;
        }

        private void AddLabel(string text, int x, int y)
        {
            this.Controls.Add(new Label
            {
                Text = text,
                Left = x,
                Top = y + 5,
                Width = 80,
                ForeColor = Color.White
            });
        }

        private TextBox AddTextbox(int x, int y)
        {
            var t = new TextBox
            {
                Left = x,
                Top = y,
                Width = 150,
                BackColor = Color.FromArgb(50, 52, 60),
                ForeColor = Color.White
            };
            this.Controls.Add(t);
            return t;
        }

        private NumericUpDown AddNumber(int min, int max, int x, int y)
        {
            var n = new NumericUpDown
            {
                Minimum = min,
                Maximum = max,
                DecimalPlaces = 2,
                Increment = 0.1M,
                Left = x,
                Top = y,
                Width = 150,
                BackColor = Color.FromArgb(50, 52, 60),
                ForeColor = Color.White
            };
            this.Controls.Add(n);
            return n;
        }
    }
}
