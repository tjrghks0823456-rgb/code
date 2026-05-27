using SemiToolHMI.Data;
using System;
using System.Drawing;
using System.Windows.Forms;

namespace SemiToolHMI
{
    public partial class RecipeSelectForm : Form
    {
        private readonly RecipeRepository repo = new RecipeRepository();
        public int SelectedId { get; private set; }
        public string SelectedName { get; private set; }

        private string chamberFilter = "";   // ★ 필터 저장용

        // 기본 생성자 (기존)
        public RecipeSelectForm()
        {
            InitializeComponent();
            ConfigureUI();
            LoadRecipes();
        }

        // ★ 새로운 생성자 --- Chamber별 필터링 가능
        public RecipeSelectForm(string chamber)
        {
            InitializeComponent();
            ConfigureUI();

            chamberFilter = chamber;
            LoadRecipes();
        }


        private void ConfigureUI()
        {
            list.View = View.Details;
            list.FullRowSelect = true;

            list.Columns.Add("ID", 60);
            list.Columns.Add("Recipe Name", 200);

            list.DoubleClick += (s, e) => AcceptSelection();

            btnOk.Click += (s, e) => AcceptSelection();
            btnCancel.Click += (s, e) => this.DialogResult = DialogResult.Cancel;
        }

        private void LoadRecipes()
        {
            list.Items.Clear();
            list.Columns.Clear();

            list.Columns.Add("ID", 60);
            list.Columns.Add("Name", 160);
            list.Columns.Add("Chamber", 80);

            var rows = repo.    GetFullRecipeList();

            foreach (var r in rows)
            {
                // ★ Chamber 필터 있으면 해당 Chamber만 표시
                if (!string.IsNullOrEmpty(chamberFilter) && r.chamber != chamberFilter)
                    continue;

                var li = new ListViewItem(r.id.ToString());
                li.SubItems.Add(r.name);
                li.SubItems.Add(r.chamber);

                list.Items.Add(li);
            }
        }


        private void AcceptSelection()
        {
            if (list.SelectedItems.Count == 0)
                return;

            SelectedId = int.Parse(list.SelectedItems[0].Text);
            SelectedName = list.SelectedItems[0].SubItems[1].Text;

            this.DialogResult = DialogResult.OK;
            this.Close();
        }

        // 외부에서 호출하는 편의 함수
        public (int id, string name) ShowSelectDialog()
        {
            return this.ShowDialog() == DialogResult.OK
                ? (SelectedId, SelectedName)
                : (0, "");
        }
    }
}
