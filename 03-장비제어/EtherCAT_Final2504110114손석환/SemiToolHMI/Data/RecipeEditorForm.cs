using SemiToolHMI.Data;
using SemiToolHMI.Models;
using System;
using System.Collections.Generic;
using System.Windows.Forms;

namespace SemiToolHMI.Controls
{
    public partial class RecipeEditorForm : Form
    {
        private readonly RecipeRepository repo = new RecipeRepository();

        // 새 레시피: 0, 기존 레시피 수정: > 0
        private int editingRecipeId = 0;

        // ==============================
        // 생성자
        // ==============================
        public RecipeEditorForm()
        {
            InitializeComponent();
            InitUi();
        }

        /// <summary>
        /// 기존 레시피 수정용 생성자
        /// </summary>
        public RecipeEditorForm(int recipeId) : this()
        {
            editingRecipeId = recipeId;
            LoadRecipeForEdit(recipeId);
        }

        // ==============================
        // UI 초기 설정
        // ==============================
        private void InitUi()
        {
            // Chamber 콤보박스 기본 값
            if (cmbChamber.Items.Count == 0)
            {
                cmbChamber.Items.Add("A");
                cmbChamber.Items.Add("B");
                cmbChamber.Items.Add("C");
            }

            // ListView 컬럼 설정 (디자이너에서 이미 만들었으면 생략 가능)
            if (grid.Columns.Count == 0)
            {
                grid.View = View.Details;
                grid.FullRowSelect = true;
                grid.GridLines = true;

                // 화면에 보이는 순서 그대로: Step | Mode | Time(s) | O2 | NF3 | CF4 | Press | Temp
                grid.Columns.Add("Step", 50);
                grid.Columns.Add("Mode", 80);
                grid.Columns.Add("Time(s)", 70);
                grid.Columns.Add("O2", 60);
                grid.Columns.Add("NF3", 60);
                grid.Columns.Add("CF4", 60);
                grid.Columns.Add("Press", 70);

                grid.Columns.Add("Temp", 70);
                grid.Columns.Add("RF", 60);
            }

            // 버튼 이벤트 연결 (디자이너에서 안 걸려 있다면 필수)
            btnAdd.Click += btnAdd_Click;
            btnDelete.Click += btnDelete_Click;
            btnSave.Click += btnSave_Click;
            btnLoad.Click += btnLoad_Click;

            // 리스트 더블클릭 → Step 수정
            grid.DoubleClick += Grid_DoubleClick;
        }

        // ==============================
        // 기존 레시피 로드
        // ==============================
        private void LoadRecipeForEdit(int recipeId)
        {
            try
            {
                var (name, chamber, steps) = repo.LoadRecipe(recipeId);

                txtName.Text = name ?? "";
                if (!string.IsNullOrEmpty(chamber))
                    cmbChamber.SelectedItem = chamber;

                grid.Items.Clear();

                if (steps != null)
                {
                    foreach (var s in steps)
                    {
                        // DB 모델 기준 (Time_s, *_SV 사용)
                        var item = new ListViewItem(s.StepNo.ToString());  // Step
                        item.SubItems.Add(s.Mode ?? "");                   // Mode
                        item.SubItems.Add(s.Time_s.ToString("0"));         // Time(s)
                        item.SubItems.Add(s.O2_SV.ToString("0.0"));        // O2
                        item.SubItems.Add(s.NF3_SV.ToString("0.0"));       // NF3
                        item.SubItems.Add(s.CF4_SV.ToString("0.0"));       // CF4
                        item.SubItems.Add(s.Press_SV.ToString("0.0"));     // Press

                        item.SubItems.Add(s.Temp_SV.ToString("0.0"));      // Temp
                        item.SubItems.Add(s.RF_SV.ToString("0.0"));        // RF

                        grid.Items.Add(item);
                    }
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show("레시피 로딩 중 오류: " + ex.Message);
            }
        }

        // ==============================
        // Step 행 추가
        // ==============================
        private void btnAdd_Click(object sender, EventArgs e)
        {
            int nextStep = grid.Items.Count + 1;

            var item = new ListViewItem(nextStep.ToString());  // Step
            item.SubItems.Add("PROC");   // Mode 기본값
            item.SubItems.Add("10");     // Time(s)
            item.SubItems.Add("0");      // O2
            item.SubItems.Add("0");      // NF3
            item.SubItems.Add("0");      // CF4
            item.SubItems.Add("0");      // Press

            item.SubItems.Add("0");      // Temp
            item.SubItems.Add("0");      // RF

            grid.Items.Add(item);
        }

        // ==============================
        // Step 행 삭제
        // ==============================
        private void btnDelete_Click(object sender, EventArgs e)
        {
            if (grid.SelectedItems.Count == 0)
            {
                MessageBox.Show("삭제할 Step을 선택하세요.");
                return;
            }

            foreach (ListViewItem item in grid.SelectedItems)
                grid.Items.Remove(item);
        }

        // ==============================
        // 레시피 불러오기 (Load Recipe 버튼)
        // ==============================
        private void btnLoad_Click(object sender, EventArgs e)
        {
            if (cmbChamber.SelectedItem == null)
            {
                MessageBox.Show("먼저 Chamber를 선택하세요.");
                return;
            }

            string chamber = cmbChamber.SelectedItem.ToString();

            // 챔버별 레시피 선택 팝업
            using (var dlg = new RecipeSelectForm(chamber))
            {
                var (rid, rname) = dlg.ShowSelectDialog();
                if (rid <= 0) return;   // 취소

                editingRecipeId = rid;
                LoadRecipeForEdit(rid);
            }
        }

        // ==============================
        // Step 더블클릭 → 수정 다이얼로그
        // ==============================
        private void Grid_DoubleClick(object sender, EventArgs e)
        {
            if (grid.SelectedItems.Count == 0)
                return;

            var item = grid.SelectedItems[0];

            // 현재 값 읽기 (Step | Mode | Time | O2 | NF3 | CF4 | Press | Temp)
            int stepNo = int.TryParse(item.SubItems[0].Text, out var n) ? n : 1;
            string mode = item.SubItems[1].Text;

            double time = double.TryParse(item.SubItems[2].Text, out var d0) ? d0 : 0;
            double o2 = double.TryParse(item.SubItems[3].Text, out var d1) ? d1 : 0;
            double nf3 = double.TryParse(item.SubItems[4].Text, out var d2) ? d2 : 0;
            double cf4 = double.TryParse(item.SubItems[5].Text, out var d3) ? d3 : 0;
            double press = double.TryParse(item.SubItems[6].Text, out var d4) ? d4 : 0;

            double temp = double.TryParse(item.SubItems[7].Text, out var d5) ? d5 : 0;
            double rf = double.TryParse(item.SubItems[8].Text, out var d6) ? d6 : 0;

            using (var dlg = new StepEditForm(stepNo, mode, time, o2, nf3, cf4, press, temp, rf))
            {
                if (dlg.ShowDialog(this) != DialogResult.OK)
                    return;

                // 수정된 값 반영
                item.SubItems[0].Text = dlg.StepNo.ToString();
                item.SubItems[1].Text = dlg.Mode;
                item.SubItems[2].Text = dlg.TimeSec.ToString("0");
                item.SubItems[3].Text = dlg.O2.ToString("0.0");
                item.SubItems[4].Text = dlg.NF3.ToString("0.0");
                item.SubItems[5].Text = dlg.CF4.ToString("0.0");
                item.SubItems[6].Text = dlg.Press.ToString("0.0");

                item.SubItems[7].Text = dlg.Temp.ToString("0.0");
                item.SubItems[8].Text = dlg.RF.ToString("0.0");
            }
        }

        // ==============================
        // 저장 버튼
        // ==============================
        private void btnSave_Click(object sender, EventArgs e)
        {
            if (string.IsNullOrWhiteSpace(txtName.Text))
            {
                MessageBox.Show("레시피 이름을 입력하세요.");
                return;
            }

            if (cmbChamber.SelectedItem == null)
            {
                MessageBox.Show("Chamber를 선택하세요.");
                return;
            }

            if (grid.Items.Count == 0)
            {
                MessageBox.Show("최소 1개 이상의 Step을 추가하세요.");
                return;
            }

            string recipeName = txtName.Text.Trim();
            string chamber = cmbChamber.SelectedItem.ToString();

            var steps = new List<RecipeStep>();

            for (int i = 0; i < grid.Items.Count; i++)
            {
                var item = grid.Items[i];

                // Step 번호: 사용자가 입력한 값 우선
                int stepNo;
                if (!int.TryParse(item.SubItems[0].Text, out stepNo))
                    stepNo = i + 1;

                string mode = item.SubItems[1].Text;

                double timeSec = 0;
                double o2 = 0, nf3 = 0, cf4 = 0, press = 0, temp = 0;

                double.TryParse(item.SubItems[2].Text, out timeSec);
                double.TryParse(item.SubItems[3].Text, out o2);
                double.TryParse(item.SubItems[4].Text, out nf3);
                double.TryParse(item.SubItems[5].Text, out cf4);
                double.TryParse(item.SubItems[6].Text, out press);

                double.TryParse(item.SubItems[7].Text, out temp);
                double.TryParse(item.SubItems[8].Text, out var rf);

                steps.Add(new RecipeStep
                {
                    StepNo = stepNo,
                    Mode = mode,
                    Time_s = (int)timeSec,   // DB: INTEGER
                    O2_SV = o2,
                    NF3_SV = nf3,
                    CF4_SV = cf4,
                    Press_SV = press,
                    Temp_SV = temp,
                    RF_SV = rf

                    // Liquid_SV, N2_SV 는 기본값 0
                });
            }

            // StepNo 기준 정렬 (10,20,30 처럼 써도 순서 유지)
            steps.Sort((a, b) => a.StepNo.CompareTo(b.StepNo));

            try
            {
                if (editingRecipeId == 0)
                {
                    // 새 레시피
                    repo.InsertRecipe(recipeName, chamber, steps);
                    MessageBox.Show("레시피가 저장되었습니다.");
                }
                else
                {
                    // 기존 레시피 수정
                    repo.UpdateRecipe(editingRecipeId, recipeName, chamber, steps);
                    MessageBox.Show("레시피가 수정되었습니다.");
                }

                this.DialogResult = DialogResult.OK;
                this.Close();
            }
            catch (Exception ex)
            {
                MessageBox.Show("레시피 저장 중 오류: " + ex.Message);
            }
        }
    }
}
