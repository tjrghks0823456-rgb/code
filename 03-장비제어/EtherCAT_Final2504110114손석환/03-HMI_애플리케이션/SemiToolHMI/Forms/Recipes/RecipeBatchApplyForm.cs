using System;
using System.Threading.Tasks;          // ★ 추가
using System.Windows.Forms;
using SemiToolHMI.Data;

namespace SemiToolHMI
{
    public class RecipeBatchApplyForm : Form
    {
        private ComboBox cmbA;
        private ComboBox cmbB;
        private ComboBox cmbC;

        private Button btnApply;
        private RecipeRepository repo;

        public RecipeBatchApplyForm()
        {
            this.Text = "레시피 일괄 적용";
            this.Size = new System.Drawing.Size(400, 300);
            this.StartPosition = FormStartPosition.CenterParent;
            this.BackColor = System.Drawing.Color.FromArgb(40, 42, 50);

            repo = new RecipeRepository();

            BuildUI();
            LoadRecipes();
        }

        private void BuildUI()
        {
            Label lblA = new Label { Text = "Chamber A", Top = 30, Left = 20, ForeColor = System.Drawing.Color.White };
            Label lblB = new Label { Text = "Chamber B", Top = 80, Left = 20, ForeColor = System.Drawing.Color.White };
            Label lblC = new Label { Text = "Chamber C", Top = 130, Left = 20, ForeColor = System.Drawing.Color.White };

            cmbA = new ComboBox { Left = 120, Top = 25, Width = 200, DropDownStyle = ComboBoxStyle.DropDownList };
            cmbB = new ComboBox { Left = 120, Top = 75, Width = 200, DropDownStyle = ComboBoxStyle.DropDownList };
            cmbC = new ComboBox { Left = 120, Top = 125, Width = 200, DropDownStyle = ComboBoxStyle.DropDownList };

            btnApply = new Button
            {
                Text = "적용",
                Left = 120,
                Top = 190,
                Width = 200
            };

            // ★ 여기서 async 이벤트 핸들러 연결
            btnApply.Click += BtnApply_Click;

            Controls.Add(lblA);
            Controls.Add(lblB);
            Controls.Add(lblC);

            Controls.Add(cmbA);
            Controls.Add(cmbB);
            Controls.Add(cmbC);

            Controls.Add(btnApply);
        }

        private void LoadRecipes()
        {
            var fullList = repo.GetFullRecipeList(); // id, name, chamber

            cmbA.Items.AddRange(fullList.FindAll(x => x.chamber == "A")
                                        .ConvertAll(x => $"{x.id}:{x.name}")
                                        .ToArray());

            cmbB.Items.AddRange(fullList.FindAll(x => x.chamber == "B")
                                        .ConvertAll(x => $"{x.id}:{x.name}")
                                        .ToArray());

            cmbC.Items.AddRange(fullList.FindAll(x => x.chamber == "C")
                                        .ConvertAll(x => $"{x.id}:{x.name}")
                                        .ToArray());
        }

        // ★ async 로 변경 후, 여기서 시나리오 실행
        private async void BtnApply_Click(object sender, EventArgs e)
        {
            if (cmbA.SelectedIndex < 0 || cmbB.SelectedIndex < 0 || cmbC.SelectedIndex < 0)
            {
                MessageBox.Show("모든 챔버에 레시피를 선택하세요.");
                return;
            }

            string selA = cmbA.SelectedItem.ToString().Split(':')[0];
            string selB = cmbB.SelectedItem.ToString().Split(':')[0];
            string selC = cmbC.SelectedItem.ToString().Split(':')[0];

            // 선택한 레시피 ID를 속성에 저장
            SelectedA = int.Parse(selA);
            SelectedB = int.Parse(selB);
            SelectedC = int.Parse(selC);

            // 폼 닫기 (MainForm에서 레시피 로드 후 실행)
            this.DialogResult = DialogResult.OK;
            this.Close();
        }

        public int SelectedA { get; private set; }
        public int SelectedB { get; private set; }
        public int SelectedC { get; private set; }
    }
}
