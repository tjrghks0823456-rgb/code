using System;
using System.Drawing;
using System.Windows.Forms;

namespace SemiToolHMI.Controls
{
    public class FoupDetailPanel : UserControl
    {
        private Label lblTitle;
        private Label lblCount;

        public FoupDetailPanel(string title)
        {
            this.Name = $"uc_{title.Replace(" ", "_")}";
            this.BackColor = Color.FromArgb(52, 73, 94); // Dark Gray Matches User Theme
            this.Width = 200; // Adjust as needed
            this.Height = 80;
            this.Margin = new Padding(0, 0, 0, 10); // Spacing between panels

            lblTitle = new Label
            {
                Text = title,
                Left = 10,
                Top = 10,
                AutoSize = true,
                ForeColor = Color.White,
                Font = new Font("Malgun Gothic", 10F, FontStyle.Bold)
            };
            this.Controls.Add(lblTitle);

            lblCount = new Label
            {
                Text = "Wafer Count: 0 / 5",
                Left = 10,
                Top = 40,
                AutoSize = true,
                ForeColor = Color.White,
                Font = new Font("Consolas", 10F, FontStyle.Regular)
            };
            this.Controls.Add(lblCount);
        }

        public void SetWaferCount(int current, int max)
        {
            if (InvokeRequired)
            {
                BeginInvoke(new Action(() => SetWaferCount(current, max)));
                return;
            }
            lblCount.Text = $"Wafer Count: {current} / {max}";
        }
    }
}
