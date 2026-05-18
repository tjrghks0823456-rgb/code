using System.Drawing;
using System.Windows.Forms;

namespace SemiToolHMI.Controls
{
    public class RobotRootPanel : Panel
    {
        public PivotPanel Pivot { get; private set; }
        public ArmPanel Arm { get; private set; }

        public RobotRootPanel()
        {
            this.Width = 250;
            this.Height = 250;
            this.BackColor = Color.Transparent;
            this.DoubleBuffered = true;

            // pivot
            Pivot = new PivotPanel();
            Pivot.Width = 40;
            Pivot.Height = 40;
            Pivot.Left = this.Width / 2 - Pivot.Width / 2;
            Pivot.Top = this.Height / 2 - Pivot.Height / 2;
            Controls.Add(Pivot);

            // arm
            Arm = new ArmPanel();
            Arm.Width = this.Width;
            Arm.Height = this.Height;
            Arm.Left = 0;
            Arm.Top = 0;
            Controls.Add(Arm);

            Arm.BringToFront();
            Pivot.BringToFront();
        }
    }
}
