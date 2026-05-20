using SemiToolHMI.Data;
using SemiToolHMI.Logic;
using SemiToolHMI.Models;
using System;
using System.Collections.Generic;
using System.Drawing;
using System.Windows.Forms;

namespace SemiToolHMI.Controls
{
    public partial class ChamberDetailForm : UserControl
    {
        private const int ParamCount = 6; // NF3, O2, CF4, Press, Temp, RF

        private string chamberName;

        private readonly TextBox[,] pvsv = new TextBox[ParamCount, 2];
        private readonly string[] labels = { "NF3", "O2", "CF4", "Press", "Temp", "RF" };
        private readonly string[] units = { "sccm", "sccm", "sccm", "Torr", "°C", "W" };

        private readonly RecipeRepository repo;
        private List<RecipeStep> currentSteps = new List<RecipeStep>();

        private readonly ChamberRuntime runtime;

        public ChamberDetailForm(string chamberName, ChamberRuntime runtime)
        {
            InitializeComponent();

            this.chamberName = chamberName;
            this.runtime = runtime;

            this.Name = $"uc_{chamberName.Replace(" ", "_")}";
            lblTitle.Text = chamberName;
            this.BackColor = Color.FromArgb(52, 73, 94); // 사용자 지정 Dark Gray

            repo = new RecipeRepository();

            BuildPVSVTable(panelPvSv);

            // 런타임 이벤트 구독
            if (this.runtime != null)
            {
                this.runtime.Updated += Runtime_Updated;
                this.runtime.StepChanged += Runtime_StepChanged;
            }

            btnStart.Click += (s, e) => this.runtime?.Start();
            btnStop.Click += (s, e) => this.runtime?.Stop();
            btnRecipe.Click += OnRecipeChange;

            // 버튼 색상 회색으로 변경
            btnStart.BackColor = Color.Gray;
            btnStop.BackColor = Color.Gray;
            btnRecipe.BackColor = Color.Gray;
            btnStart.ForeColor = Color.White;
            btnStop.ForeColor = Color.White;
            btnRecipe.ForeColor = Color.White;

            // Progress Bar Init
            waferBar.Minimum = 0;
            waferBar.Maximum = 100;
            waferBar.Style = ProgressBarStyle.Continuous;
        }

        // =====================================================================
        // 런타임 이벤트 → UI 스레드 마샬링
        // =====================================================================
        private void Runtime_Updated(ChamberRuntime rt)
        {
            if (InvokeRequired)
            {
                BeginInvoke(new Action(() => UpdateFromRuntime(rt)));
                return;
            }
            UpdateFromRuntime(rt);
        }

        private void Runtime_StepChanged(ChamberRuntime rt)
        {
            if (InvokeRequired)
            {
                BeginInvoke(new Action(() => UpdateStep(rt)));
                return;
            }
            UpdateStep(rt);
        }

        // =====================================================================
        // 레시피 선택 (Chamber별 필터링)
        // =====================================================================
        private void OnRecipeChange(object sender, EventArgs e)
        {
            // "Chamber A" → 'A'
            string chamberCode = chamberName.Substring(chamberName.Length - 1);

            using (var dlg = new RecipeSelectForm(chamberCode))
            {
                var (rid, rname) = dlg.ShowSelectDialog();
                if (rid <= 0) return;

                runtime?.LoadRecipe(rid);
                txtRecipe.Text = rname;
            }
        }

        // =====================================================================
        // PV/SV 테이블 생성
        // =====================================================================
        private void BuildPVSVTable(Panel host)
        {
            var table = new TableLayoutPanel
            {
                Dock = DockStyle.Fill,
                ColumnCount = 4,
                RowCount = 1 + labels.Length,
                BackColor = Color.Gray, // 사용자 요청: 회색
                CellBorderStyle = TableLayoutPanelCellBorderStyle.None,
                Margin = new Padding(0),
                Padding = new Padding(2)
            };

            table.ColumnStyles.Add(new ColumnStyle(SizeType.Absolute, 90));
            table.ColumnStyles.Add(new ColumnStyle(SizeType.Absolute, 60));
            table.ColumnStyles.Add(new ColumnStyle(SizeType.Absolute, 60));
            table.ColumnStyles.Add(new ColumnStyle(SizeType.Absolute, 70));

            table.RowStyles.Add(new RowStyle(SizeType.Absolute, 24));
            for (int i = 0; i < labels.Length; i++)
                table.RowStyles.Add(new RowStyle(SizeType.Absolute, 24));

            AddHeader(table, 0, "Param");
            AddHeader(table, 1, "PV");
            AddHeader(table, 2, "SV");
            AddHeader(table, 3, "Unit");

            for (int i = 0; i < labels.Length; i++)
            {
                int row = i + 1;

                var lbl = new Label
                {
                    Text = labels[i],
                    Dock = DockStyle.Fill,
                    ForeColor = Color.White,
                    TextAlign = ContentAlignment.MiddleLeft,
                    Margin = new Padding(3, 0, 3, 0)
                };
                table.Controls.Add(lbl, 0, row);

                var txtPv = new TextBox
                {
                    Dock = DockStyle.Fill,
                    ReadOnly = true,
                    Text = "0",
                    TextAlign = HorizontalAlignment.Center,
                    Margin = new Padding(3, 2, 3, 2)
                };

                var txtSv = new TextBox
                {
                    Dock = DockStyle.Fill,
                    ReadOnly = true,
                    Text = "0",
                    TextAlign = HorizontalAlignment.Center,
                    Margin = new Padding(3, 2, 3, 2)
                };

                pvsv[i, 0] = txtPv;
                pvsv[i, 1] = txtSv;

                table.Controls.Add(txtPv, 1, row);
                table.Controls.Add(txtSv, 2, row);

                var lblUnit = new Label
                {
                    Text = units[i],
                    Dock = DockStyle.Fill,
                    ForeColor = Color.White,
                    TextAlign = ContentAlignment.MiddleCenter,
                    Margin = new Padding(3, 0, 3, 0)
                };
                table.Controls.Add(lblUnit, 3, row);
            }

            host.Controls.Clear();
            host.Controls.Add(table);
        }

        private void AddHeader(TableLayoutPanel t, int col, string text)
        {
            var lbl = new Label
            {
                Text = text,
                Dock = DockStyle.Fill,
                ForeColor = Color.White,
                Font = new Font("Malgun Gothic", 9F, FontStyle.Bold),
                TextAlign = ContentAlignment.MiddleCenter,
                Margin = new Padding(3, 0, 3, 0)
            };
            t.Controls.Add(lbl, col, 0);
        }

        // =====================================================================
        // Runtime → UI 전체 업데이트
        // =====================================================================
        public void UpdateFromRuntime(ChamberRuntime rt)
        {
            if (rt == null)
                return;

            // Recipe 이름
            txtRecipe.Text = rt.RecipeName;

            // 왼쪽 Step: 레시피에서 지정한 StepNo (예: 5)
            txtStepCur.Text = rt.CurrentStepNo.ToString();

            // 오른쪽 Step: 이 Step을 몇 번째 실행 중인지 (웨이퍼 몇 장째인지)
            int cnt = (rt.CycleCount > 0) ? rt.CycleCount : 0;
            txtStepMax.Text = cnt.ToString();

            // Mode / Time
            txtMode.Text = rt.CurrentMode;
            txtTimeCur.Text = rt.CurrentStepElapsedSec.ToString("0");
            txtTimeMax.Text = rt.CurrentStepTotalSec.ToString("0");

            // PV
            pvsv[0, 0].Text = rt.PvNF3.ToString("0.0");
            pvsv[1, 0].Text = rt.PvO2.ToString("0.0");
            pvsv[2, 0].Text = rt.PvCF4.ToString("0.0");
            pvsv[3, 0].Text = rt.PvPress.ToString("0.0");
            pvsv[4, 0].Text = rt.PvTemp.ToString("0.0");
            pvsv[5, 0].Text = rt.PvRF.ToString("0.0");

            // SV
            pvsv[0, 1].Text = rt.SvNF3.ToString("0.0");
            pvsv[1, 1].Text = rt.SvO2.ToString("0.0");
            pvsv[2, 1].Text = rt.SvCF4.ToString("0.0");
            pvsv[3, 1].Text = rt.SvPress.ToString("0.0");
            pvsv[4, 1].Text = rt.SvTemp.ToString("0.0");
            pvsv[5, 1].Text = rt.SvRF.ToString("0.0");

            // ★ Wafer Progress Bar Update
            UpdateProgressBar(rt);
        }

        // =====================================================================
        // Step 변경 시 UI 업데이트
        // =====================================================================
        public void UpdateStep(ChamberRuntime rt)
        {
            if (rt == null) return;

            // 왼쪽 Step: 레시피 StepNo
            txtStepCur.Text = rt.CurrentStepNo.ToString();

            // 오른쪽 Step: 실행 횟수(웨이퍼 몇 장째)
            int cnt = (rt.CycleCount > 0) ? rt.CycleCount : 0;
            txtStepMax.Text = cnt.ToString();

            txtMode.Text = rt.CurrentMode;
            txtTimeCur.Text = "0";
            txtTimeMax.Text = rt.CurrentStepTotalSec.ToString("0");

            // ★ Step 변경/초기화 시에도 프로그레스 바 동기화
            UpdateProgressBar(rt);
        }

        private void UpdateProgressBar(ChamberRuntime rt)
        {
            double totalDur = rt.TotalRecipeTimeSec;
            double curElapsed = rt.TotalElapsedSec;
            int pct = (totalDur > 0) ? (int)((curElapsed / totalDur) * 100.0) : 0;
            if (pct < 0) pct = 0;
            if (pct > 100) pct = 100;

            waferBar.Value = pct;
        }

        // ★ UI 초기화 (리셋 버튼 클릭 시 호출)
        public void ResetUI()
        {
            if (InvokeRequired)
            {
                BeginInvoke(new Action(ResetUI));
                return;
            }

            // 1) 텍스트 필드 초기화
            txtRecipe.Text = "";
            txtStepCur.Text = "";
            txtStepMax.Text = "";
            txtMode.Text = "";
            txtTimeCur.Text = "0";
            txtTimeMax.Text = "0";

            // 2) 프로그레스 바 리셋
            waferBar.Value = 0;

            // 3) PV/SV 테이블 초기화
            for (int i = 0; i < ParamCount; i++)
            {
                // PV
                if (pvsv[i, 0] != null) pvsv[i, 0].Text = "0.0";
                // SV
                if (pvsv[i, 1] != null) pvsv[i, 1].Text = "0.0";
            }
        }
    }
}
