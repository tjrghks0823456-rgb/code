using System;
using System.Drawing;
using System.Windows.Forms;

namespace SemiToolHMI.Controls
{
    public class EquipmentStatusPanel : Panel
    {
        private Label lblTitle;
        private Label lblState;
        private Label lblWafer;
        private Label lblLotId;
        private Label lblLock;
        
        private Panel innerPanel;

        private Panel[] waferSlots;
        private int maxSlots = 5;
        private int waferCount = 0;  // 초기값 0으로 설정하여 "---" 표시

        public EquipmentStatusPanel()
        {
            this.Width = 400;
            this.Height = 200;
            this.BackColor = Color.WhiteSmoke;  // 밝은 배경
            this.BorderStyle = BorderStyle.FixedSingle;

            var inner = new Panel
            {
                Dock = DockStyle.Fill,
                BackColor = Color.WhiteSmoke,
                Padding = new Padding(10)
            };
            this.Controls.Add(inner);

            lblTitle = new Label
            {
                Text = "FOUP",
                AutoSize = true,
                ForeColor = Color.Black, // 텍스트 검정
                Font = new Font("Malgun Gothic", 14, FontStyle.Bold),
                Location = new Point(10, 30)
            };
            inner.Controls.Add(lblTitle);

            lblState = new Label
            {
                Text = "상태: 장착",
                AutoSize = true,
                ForeColor = Color.Black,
                Font = new Font("Malgun Gothic", 10, FontStyle.Regular),
                Location = new Point(12, 65)
            };
            inner.Controls.Add(lblState);

            lblWafer = new Label
            {
                Text = "Wafer : ---",
                AutoSize = true,
                ForeColor = Color.Black,
                Font = new Font("Malgun Gothic", 10, FontStyle.Regular),
                Location = new Point(12, 90)
            };
            inner.Controls.Add(lblWafer);

            int lineTop = 115; // Y위치 조정 (90 -> 115)
            int lineGap = 25;

            lblLotId = MakeInfoLabel("LOT: 1", lineTop + lineGap * 0);
            lblLock = MakeInfoLabel("LOCK: 완료", lineTop + lineGap * 1);

            inner.Controls.Add(lblLotId);
            inner.Controls.Add(lblLock);
            
            innerPanel = inner;

            waferSlots = new Panel[maxSlots];
            
            // 리사이즈 이벤트 시 레이아웃 갱신
            inner.Resize += (s, e) =>
            {
                LayoutSlots(inner);
            };
            
            // 초기화
            LayoutSlots(inner);
        }

        private Label MakeInfoLabel(string text, int top)
        {
            return new Label
            {
                Text = text,
                AutoSize = true,
                ForeColor = Color.Black,
                Font = new Font("Malgun Gothic", 10, FontStyle.Regular),
                Location = new Point(12, top)
            };
        }

        private void LayoutSlots(Panel parent)
        {
            // 슬롯 크기 확대 (60x12 -> 100x18)
            int w = 100;
            int h = 18;
            int gap = 8;

            // 오른쪽 정렬 (여백 20)
            int startX = parent.Width - w - 20;
            
            // 수직 중앙 정렬 계산
            // 전체 스택 높이 = 5*h + 4*gap
            int totalHeight = (maxSlots * h) + ((maxSlots - 1) * gap);
            int dependencyY = (parent.Height - totalHeight) / 2; 

            // 바닥 기준점 (아래에서 위로 쌓기 위해 Loop 계산용)
            // i=0(맨아래)의 Top = (전체중앙시작점 + 전체높이) - h
            // 좀 더 쉽게: i=0 이 맨 아래.
            // 맨 아래 Y 좌표 = dependencyY + totalHeight - h;
            
            int baseTop = dependencyY + totalHeight - h; 

            for (int i = 0; i < maxSlots; i++)
            {
                if (waferSlots[i] == null)
                {
                    waferSlots[i] = new Panel
                    {
                        BackColor = Color.LightGray
                    };
                    parent.Controls.Add(waferSlots[i]);
                }

                // 크기 업데이트
                waferSlots[i].Width = w;
                waferSlots[i].Height = h;

                // 위치: i=0이 맨 아래(1번 슬롯), 위로 쌓음
                waferSlots[i].Left = startX;
                waferSlots[i].Top = baseTop - (i * (h + gap));
            }

            RefreshSlots();
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
            
            if (count == 0)
                lblWafer.Text = "Wafer : ---";
            else
                lblWafer.Text = $"Wafer : {waferCount}장";

            RefreshSlots();
        }

        public bool IsSourceMode { get; set; } = false;

        private void RefreshSlots()
        {
            if (waferSlots == null) return;

            for (int i = 0; i < waferSlots.Length; i++)
            {
                if (waferSlots[i] == null) continue;

                bool isPresent;
                if (IsSourceMode)
                {
                    // 소스 모드 (FOUP A): 아래(0번)부터 사라짐 -> 위쪽(큰 인덱스)에 남음
                    // 예: 5개 중 4개 남음 -> 0번 사라짐, 1~4번 남음
                    // i >= (5 - 4) = 1
                    isPresent = (i >= (maxSlots - waferCount));
                }
                else
                {
                    // 기본 모드 (FOUP B): 아래(0번)부터 채워짐
                    isPresent = (i < waferCount);
                }

                waferSlots[i].BackColor = isPresent ? Color.DodgerBlue : Color.LightGray;
            }
        }
        
        public void SetState(string state)
        {
            lblState.Text = $"상태: {state}";
        }
        
        public void SetLot(string lot)
        {
            lblLotId.Text = $"LOT: {lot}";
        }
        
        public void SetLock(string lockStatus)
        {
            lblLock.Text = $"LOCK: {lockStatus}";
        }
        
        public void SetProcessing(bool isProcessing)
        {
            if (isProcessing)
            {
                this.BackColor = Color.Honeydew; // 처리 중 (밝은 녹색)
                if (innerPanel != null)
                    innerPanel.BackColor = Color.Honeydew;
            }
            else
            {
                this.BackColor = Color.WhiteSmoke; // 대기 중 (흰색/회색)
                if (innerPanel != null)
                    innerPanel.BackColor = Color.WhiteSmoke;
            }
        }
    }
}
