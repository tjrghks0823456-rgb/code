using System;
using System.Drawing;
using System.Windows.Forms;

namespace SemiToolHMI.Controls
{
    public class ChamberStatusPanel : Panel
    {
        private Label lblTitle;
        private Label lblMode;
        private Label lblRecipe;

        private Panel colorBar;

        private Panel cardTemp;
        private Panel cardPress;
        private Panel cardFlow;

        private Label lblTempValue;
        private Label lblPressValue;
        private Label lblFlowValue;


        public ChamberStatusPanel()
        {
            this.Width = 520;
            this.Height = 180;
            this.BackColor = Color.FromArgb(50, 52, 60);

            BuildUI();
            
            // 초기에는 모든 정보 숨김 (빨간색 배경만 표시)
            SetVisible(false);

            // 🔥 내부 컨트롤 클릭 → Panel 클릭 이벤트로 전달
            foreach (Control c in this.Controls)
                c.Click += (s, e) => this.OnClick(e);
        }

        private void BuildUI()
        {
            colorBar = new Panel
            {
                Width = 18,
                Height = 140,
                Left = 15,
                Top = 20,
                BackColor = Color.DodgerBlue
            };
            Controls.Add(colorBar);

            lblTitle = MakeLabel("Chamber A", 45, 15, true, 13);
            lblMode = MakeLabel("Mode : ---", 45, 40);
            lblRecipe = MakeLabel("Recipe : ---", 45, 60);

            Controls.Add(lblTitle);
            Controls.Add(lblMode);
            Controls.Add(lblRecipe);

            cardTemp = MakeCard("TEMP", 45, 100);
            lblTempValue = MakeValue(cardTemp, "0 °C");

            cardPress = MakeCard("PRESS", 185, 100);
            lblPressValue = MakeValue(cardPress, "0 Pa");

            cardFlow = MakeCard("FLOW", 325, 100);
            lblFlowValue = MakeValue(cardFlow, "0 SLM");
        }

        private Panel MakeCard(string title, int x, int y)
        {
            var p = new Panel
            {
                Width = 120,
                Height = 60,
                Left = x,
                Top = y,
                BackColor = Color.FromArgb(70, 72, 80)
            };
            Controls.Add(p);

            p.Controls.Add(new Label
            {
                Text = title,
                Left = 10,
                Top = 5,
                AutoSize = true,
                ForeColor = Color.LightGray,
                Font = new Font("Malgun Gothic", 9, FontStyle.Bold)
            });

            return p;
        }

        private Label MakeValue(Panel p, string text)
        {
            var lbl = new Label
            {
                Text = text,
                Left = 10,
                Top = 28,
                AutoSize = true,
                ForeColor = Color.White,
                Font = new Font("Malgun Gothic", 12, FontStyle.Bold)
            };
            p.Controls.Add(lbl);
            return lbl;
        }

        private Label MakeLabel(string t, int x, int y, bool bold = false, int size = 10)
        {
            return new Label
            {
                Text = t,
                Left = x,
                Top = y,
                AutoSize = true,
                ForeColor = Color.White,
                Font = new Font("Malgun Gothic", size, bold ? FontStyle.Bold : FontStyle.Regular)
            };
        }

        // ===== 업데이트 =====
        public void UpdateChamber(string name, string mode, string recipe,
            double temp, double pressure, double flow, string state)
        {
            lblTitle.Text = name;
            lblMode.Text = $"Mode : {mode}";
            lblRecipe.Text = $"Recipe : {recipe}";
            lblTempValue.Text = $"{temp:0.0} °C";
            lblPressValue.Text = $"{pressure:0.00} Pa";
            lblFlowValue.Text = $"{flow:0.0} SLM";

            if (state == "NORMAL") colorBar.BackColor = Color.DodgerBlue;
            else if (state == "WARN") colorBar.BackColor = Color.Gold;
            else colorBar.BackColor = Color.Red;
        }
        
        public void SetVisible(bool visible)
        {
            lblTitle.Visible = visible;
            lblMode.Visible = visible;
            lblRecipe.Visible = visible;
            colorBar.Visible = visible;
            cardTemp.Visible = visible;
            cardPress.Visible = visible;
            cardFlow.Visible = visible;
        }
    }
}
