using System.Drawing;
using System.Windows.Forms;

namespace SemiToolHMI.Controls
{
    public class FOUPPanel : Panel
    {
        private Label lblTitle;
        private Label lblWafer;

        private int waferCount = 0;
        private int maxSlots = 5;

        public FOUPPanel()
        {
            this.Width = 160;
            this.Height = 50;
            this.BackColor = Color.WhiteSmoke;
            this.BorderStyle = BorderStyle.FixedSingle;

            lblTitle = new Label
            {
                Text = "FOUP",
                AutoSize = false,
                TextAlign = ContentAlignment.MiddleCenter,
                Dock = DockStyle.Top,
                Height = 24,
                ForeColor = Color.Black,
                Font = new Font("Malgun Gothic", 9, FontStyle.Bold)
            };
            this.Controls.Add(lblTitle);

            lblWafer = new Label
            {
                Text = "W: 0",
                AutoSize = false,
                Height = 18,
                Dock = DockStyle.Bottom,
                TextAlign = ContentAlignment.MiddleRight,
                ForeColor = Color.DarkGreen,
                Font = new Font("Consolas", 9, FontStyle.Regular),
                Padding = new Padding(0, 0, 6, 0)
            };
            this.Controls.Add(lblWafer);
        }

        public void SetTitle(string title)
        {
            lblTitle.Text = title;
        }

        public void SetWaferCount(int count, int maxSlots = 5)
        {
            this.maxSlots = maxSlots;
            if (count < 0) count = 0;
            if (count > maxSlots) count = maxSlots;

            waferCount = count;
            lblWafer.Text = $"W: {waferCount}";
        }
    }
}
