using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;


namespace SemiToolHMI.Controls
{
    public partial class FoupDetailForm : Form
    {
        public FoupDetailForm(string foupName)
        {
            InitializeComponent();

            this.Text = $"{foupName} 상세 정보";
            lblTitle.Text = $"{foupName} Detail";
            this.BackColor = Color.FromArgb(33, 35, 45);

            // ESC 종료 기능
            this.KeyPreview = true;
            this.KeyDown += (s, e) =>
            {
                if (e.KeyCode == Keys.Escape)
                    this.Close();
            };

            // 버튼 이벤트 연결
            btnOpen.Click += (s, e) => MessageBox.Show("FOUP Open 실행");
            btnClose.Click += (s, e) => MessageBox.Show("FOUP Close 실행");
            btnClamp.Click += (s, e) => MessageBox.Show("Clamp 동작");
            btnRecipe.Click += OnRecipeChange;
        }

        // ============================
        // Recipe 팝업
        // ============================
        private void OnRecipeChange(object sender, EventArgs e)
        {
            using (var dlg = new RecipeSelectForm())
            {
                var result = dlg.ShowSelectDialog();

                if (result.id > 0)
                {
                    lblRecipe.Text = $"Recipe : {result.name} (ID:{result.id})";
                }
            }
        }


        // ============================
        // FOUP 실시간 업데이트 (외부 호출)
        // ============================
        public void UpdateData(string path, string ppid, string lot, string mid, string lockState, int wafer)
        {
            lblPath.Text = $"Path : {path}";
            lblPPID.Text = $"PPID : {ppid}";
            lblLotID.Text = $"LOTID : {lot}";
            lblMID.Text = $"MID : {mid}";
            lblLock.Text = $"Lock : {lockState}";
            lblWafer.Text = $"Wafer : {wafer} / 5";
        }
    }
}

