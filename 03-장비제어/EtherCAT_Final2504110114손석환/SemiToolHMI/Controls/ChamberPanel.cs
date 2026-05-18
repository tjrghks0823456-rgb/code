using System;
using System.Drawing;
using System.Windows.Forms;

namespace SemiToolHMI.Controls
{
    public class ChamberPanel : Panel
    {
        private Label lblName;

        // 램프
        private Panel lamp;

        // 도어 UI
        private Panel doorPanel;
        private Timer doorTimer;

        private enum DoorState { Closed, Opening, Open, Closing }
        private DoorState doorState = DoorState.Closed;

        private const int DoorClosedWidth = 60;
        private const int DoorOpenWidth = 4;
        private const int DoorStep = 4;

        public event Action OnDoorClicked;

        // 공정 / 웨이퍼 상태
        private bool isProcessing = false;
        private bool hasWafer = false;

        private Color normalBack = Color.FromArgb(70, 72, 80); // 다시 Dark Gray
        private Color processingBack = Color.FromArgb(90, 100, 140);

        public ChamberPanel()
        {
            this.Width = 200;
            this.Height = 120;
            this.BackColor = normalBack;
            this.BorderStyle = BorderStyle.FixedSingle;

            // 제목
            lblName = new Label
            {
                AutoSize = true,
                ForeColor = Color.White, // 텍스트 흰색
                Left = 10,
                Top = 10
            };
            Controls.Add(lblName);

            InitializeLamp();

            // 도어
            doorPanel = new Panel
            {
                Width = DoorClosedWidth,
                Height = 40,
                BackColor = Color.FromArgb(130, 130, 150),
                Top = this.Height - 10 - 40
            };
            doorPanel.Left = (this.Width - doorPanel.Width) / 2;
            doorPanel.Anchor = AnchorStyles.Bottom;
            Controls.Add(doorPanel);

            doorTimer = new Timer { Interval = 30 };
            doorTimer.Tick += DoorTimer_Tick;
        }

        public void SetTitle(string title)
        {
            lblName.Text = title;
        }

        private void InitializeLamp()
        {
            lamp = new Panel
            {
                Width = 16,
                Height = 16,
                BackColor = Color.DimGray,
                Left = this.Width - 30,
                Top = 10,
                BorderStyle = BorderStyle.FixedSingle,
                Anchor = AnchorStyles.Top | AnchorStyles.Right
            };
            Controls.Add(lamp);
        }

        public void SetLamp(bool on)
        {
            lamp.BackColor = on ? Color.LimeGreen : Color.DimGray;
        }

        // ... methods ...

        // ... skipping middle methods ... (NOT VALID TO SKIP IN REPLACE)
        // I must use ReplaceFileContent on targeted areas or MultiReplace.
        
        // I will use chunks.

        // ===== 도어 제어 =====
        public void OpenDoor()
        {
            if (doorState == DoorState.Closed || doorState == DoorState.Closing)
            {
                doorState = DoorState.Opening;
                doorTimer.Start();
            }
        }

        public void CloseDoor()
        {
            if (doorState == DoorState.Open || doorState == DoorState.Opening)
            {
                doorState = DoorState.Closing;
                doorTimer.Start();
            }
        }

        public void ToggleDoor()
        {
            if (doorState == DoorState.Open || doorState == DoorState.Opening)
                CloseDoor();
            else
                OpenDoor();
        }

        public bool IsDoorOpen => doorState == DoorState.Open;

        private void DoorTimer_Tick(object sender, EventArgs e)
        {
            if (doorState == DoorState.Opening)
            {
                if (doorPanel.Width > DoorOpenWidth)
                {
                    doorPanel.Width -= DoorStep;
                    doorPanel.Left = (this.Width - doorPanel.Width) / 2;
                }
                else
                {
                    doorPanel.Width = DoorOpenWidth;
                    doorState = DoorState.Open;
                    doorTimer.Stop();
                }
            }
            else if (doorState == DoorState.Closing)
            {
                if (doorPanel.Width < DoorClosedWidth)
                {
                    doorPanel.Width += DoorStep;
                    doorPanel.Left = (this.Width - doorPanel.Width) / 2;
                }
                else
                {
                    doorPanel.Width = DoorClosedWidth;
                    doorState = DoorState.Closed;
                    doorTimer.Stop();
                }
            }
        }

        // ===== 공정 / 웨이퍼 상태 제어 =====
        private float progress = 0f;

        public void SetProcessing(bool on)
        {
            isProcessing = on;
            this.BackColor = on ? processingBack : normalBack;
            // 공정 시작/종료 시 진행률 리셋
            if (!on) progress = 0f;
            Invalidate();
        }

        public void SetProgress(float val)
        {
            progress = Math.Max(0f, Math.Min(1f, val));
            Invalidate(); // 다시 그리기 요청
        }

        public void SetWafer(bool present)
        {
            hasWafer = present;
            Invalidate();
        }

        protected override void OnClick(EventArgs e)
        {
            base.OnClick(e);
            OnDoorClicked?.Invoke();
        }

        protected override void OnPaint(PaintEventArgs e)
        {
            base.OnPaint(e);
            var g = e.Graphics;

            // ★ 공정 진행률 게이지 (배경 위에 그리기)
            if (isProcessing && progress > 0)
            {
                int barWidth = (int)(this.Width * progress);
                using (var brush = new SolidBrush(Color.FromArgb(50, 46, 204, 113))) // 반투명 초록
                {
                    g.FillRectangle(brush, 0, 0, barWidth, this.Height);
                }
                
                // 하단에 얇은 진한 바 추가
                using (var brush = new SolidBrush(Color.LimeGreen))
                {
                    g.FillRectangle(brush, 0, this.Height - 5, barWidth, 5);
                }
            }

            if (hasWafer)
            {
                int r = 16;
                int cx = this.Width / 2;
                int cy = this.Height / 2 + 10;

                var rect = new Rectangle(cx - r, cy - r, r * 2, r * 2);
                using (var b = new SolidBrush(Color.LightSkyBlue))
                using (var p = new Pen(Color.White, 2))
                {
                    g.FillEllipse(b, rect);
                    g.DrawEllipse(p, rect);
                }
            }
        }
    }
}
