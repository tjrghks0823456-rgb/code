using System;
using System.Drawing;
using System.Windows.Forms;

namespace WindowsFormsApp1
{
    public class EquipmentRegistrationForm : Form
    {
        private TextBox txtEquipmentName;
        private ComboBox cmbCategory;
        private Button btnSave;
        private Button btnCancel;

        public string EquipmentName
        {
            get { return txtEquipmentName.Text.Trim(); }
        }

        public string EquipmentCategory
        {
            get { return cmbCategory.Text.Trim(); }
        }

        public EquipmentRegistrationForm()
        {
            InitializeLayout();
        }

        private void InitializeLayout()
        {
            this.Text = "장비 등록";
            this.StartPosition = FormStartPosition.CenterParent;
            this.FormBorderStyle = FormBorderStyle.FixedDialog;
            this.MaximizeBox = false;
            this.MinimizeBox = false;
            this.ClientSize = new Size(420, 210);
            this.Font = new Font("맑은 고딕", 9F, FontStyle.Regular);

            Label lblEquipmentName = new Label();
            lblEquipmentName.Text = "장비명";
            lblEquipmentName.Location = new Point(30, 35);
            lblEquipmentName.Size = new Size(90, 25);

            txtEquipmentName = new TextBox();
            txtEquipmentName.Location = new Point(130, 32);
            txtEquipmentName.Size = new Size(240, 23);

            Label lblCategory = new Label();
            lblCategory.Text = "종류";
            lblCategory.Location = new Point(30, 80);
            lblCategory.Size = new Size(90, 25);

            cmbCategory = new ComboBox();
            cmbCategory.Location = new Point(130, 77);
            cmbCategory.Size = new Size(240, 23);
            cmbCategory.DropDownStyle = ComboBoxStyle.DropDown;
            cmbCategory.AutoCompleteMode = AutoCompleteMode.SuggestAppend;
            cmbCategory.AutoCompleteSource = AutoCompleteSource.ListItems;
            cmbCategory.Items.AddRange(new object[]
            {
                "세정장비",
                "코팅장비",
                "포토장비",
                "노광장비",
                "식각장비",
                "증착장비",
                "열처리",
                "연마장비",
                "검사장비",
                "측정장비",
                "환경장비",
                "유틸리티",
                "자동화",
                "기타"
            });

            btnSave = new Button();
            btnSave.Text = "등록";
            btnSave.Location = new Point(210, 145);
            btnSave.Size = new Size(75, 32);
            btnSave.Click += btnSave_Click;

            btnCancel = new Button();
            btnCancel.Text = "취소";
            btnCancel.Location = new Point(295, 145);
            btnCancel.Size = new Size(75, 32);
            btnCancel.DialogResult = DialogResult.Cancel;

            this.Controls.Add(lblEquipmentName);
            this.Controls.Add(txtEquipmentName);
            this.Controls.Add(lblCategory);
            this.Controls.Add(cmbCategory);
            this.Controls.Add(btnSave);
            this.Controls.Add(btnCancel);

            this.AcceptButton = btnSave;
            this.CancelButton = btnCancel;
        }

        private void btnSave_Click(object sender, EventArgs e)
        {
            if (string.IsNullOrWhiteSpace(EquipmentName))
            {
                MessageBox.Show("장비명을 입력하세요.", "입력 확인");
                txtEquipmentName.Focus();
                return;
            }

            if (string.IsNullOrWhiteSpace(EquipmentCategory))
            {
                MessageBox.Show("장비 종류를 입력하세요.", "입력 확인");
                cmbCategory.Focus();
                return;
            }

            this.DialogResult = DialogResult.OK;
            this.Close();
        }
    }
}
