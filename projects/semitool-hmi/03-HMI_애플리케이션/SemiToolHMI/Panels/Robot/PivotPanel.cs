using System.Drawing;
using System.Windows.Forms;

namespace SemiToolHMI.Controls
{
    public class PivotPanel : Panel
    {
        public PivotPanel()
        {
            this.Width = 40;
            this.Height = 40;
            this.BackColor = Color.Transparent;
            this.DoubleBuffered = true;
        }

        protected override void OnPaint(PaintEventArgs e)
        {
            base.OnPaint(e);

            var g = e.Graphics;
            g.SmoothingMode = System.Drawing.Drawing2D.SmoothingMode.AntiAlias;

            using (var p = new Pen(Color.DeepSkyBlue, 6))
            {
                g.DrawEllipse(p, 3, 3, Width - 6, Height - 6);
            }
        }
    }
}
