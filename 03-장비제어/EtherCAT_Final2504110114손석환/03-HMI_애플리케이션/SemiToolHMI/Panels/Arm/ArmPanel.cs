using System;
using System.Drawing;
using System.Windows.Forms;

namespace SemiToolHMI.Controls
{
    public class ArmPanel : Panel
    {
        private float armAngle = 0f;    // 회전 각도
        private int liftOffset = 0;     // 리프트 표현용
        private bool hasWafer = false;  // 웨이퍼 보유 여부

        public ArmPanel()
        {
            this.Width = 250;
            this.Height = 250;
            this.BackColor = Color.Transparent;
            this.DoubleBuffered = true;
        }

        // ==============================
        //  회전 각도 설정
        // ==============================
        public void SetAngle(float angle)
        {
            armAngle = angle;
            Invalidate();
        }

        public float GetAngle()
        {
            return armAngle;
        }

        // ==============================
        // 리프트 오프셋 (위/아래)
        // ==============================
        public void SetLiftOffset(int offset)
        {
            liftOffset = offset;
            Invalidate();
        }

        // ==============================
        // 웨이퍼 보유 여부 설정
        // ==============================
        public void SetWafer(bool holding)
        {
            hasWafer = holding;
            Invalidate();
        }

        public bool HasWafer()
        {
            return hasWafer;
        }

        // ==============================
        // 암 그리기
        // ==============================
        protected override void OnPaint(PaintEventArgs e)
        {
            base.OnPaint(e);

            var g = e.Graphics;
            g.SmoothingMode = System.Drawing.Drawing2D.SmoothingMode.AntiAlias;

            // 중심점
            int cx = Width / 2;
            int cy = Height / 2 + liftOffset;   // liftOffset 반영

            int armLength = 85;

            double rad = armAngle * Math.PI / 180.0;

            int ex = cx + (int)(Math.Cos(rad) * armLength);
            int ey = cy + (int)(Math.Sin(rad) * armLength);

            using (var p = new Pen(Color.DeepSkyBlue, 12))
            {
                p.StartCap = System.Drawing.Drawing2D.LineCap.Round;
                p.EndCap = System.Drawing.Drawing2D.LineCap.Round;
                g.DrawLine(p, cx, cy, ex, ey);
            }

            // 웨이퍼를 들고 있을 때만 표시
            if (hasWafer)
            {
                int waferSize = 18;
                g.FillEllipse(Brushes.Gold, ex - waferSize / 2, ey - waferSize / 2, waferSize, waferSize);
                g.DrawEllipse(Pens.DarkGoldenrod, ex - waferSize / 2, ey - waferSize / 2, waferSize, waferSize);
            }
        }
    }
}
