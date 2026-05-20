using System;
using System.Drawing;
using System.Windows.Forms;

namespace SemiToolHMI
{
    public partial class LoginForm : Form
    {
        public string LoggedInUser { get; private set; }

        private TextBox txtUserId;
        private TextBox txtPassword;
        private Button btnLogin;
        private Button btnCancel;
        private Label lblMsg;

        public LoginForm()
        {
            InitializeComponent();
            BuildUI();
        }

        private void InitializeComponent()
        {
            this.SuspendLayout();
            // 
            // LoginForm
            // 
            this.ClientSize = new System.Drawing.Size(350, 220);
            this.Name = "LoginForm";
            this.Text = "Login";
            this.StartPosition = FormStartPosition.CenterParent;
            this.FormBorderStyle = FormBorderStyle.FixedDialog;
            this.MaximizeBox = false;
            this.MinimizeBox = false;
            this.BackColor = Color.FromArgb(40, 42, 50);
            this.ResumeLayout(false);
        }

        private void BuildUI()
        {
            // Title Label
            var lblTitle = new Label
            {
                Text = "SYSTEM LOGIN",
                Font = new Font("Malgun Gothic", 14, FontStyle.Bold),
                ForeColor = Color.White,
                AutoSize = true,
                Top = 20,
                Left = 20
            };
            this.Controls.Add(lblTitle);

            // User Management Button
            var btnUserManagement = new Button
            {
                Text = "사용자 관리",
                Top = 18,
                Left = 240,
                Width = 90,
                Height = 28,
                FlatStyle = FlatStyle.Flat,
                BackColor = Color.FromArgb(52, 152, 219),
                ForeColor = Color.White,
                Cursor = Cursors.Hand,
                Font = new Font("Malgun Gothic", 9)
            };
            btnUserManagement.FlatAppearance.BorderSize = 0;
            btnUserManagement.Click += (s, e) =>
            {
                var userMgmt = new UserManagementForm();
                userMgmt.ShowDialog(this);
            };
            this.Controls.Add(btnUserManagement);

            // ID Label & Text
            var lblId = new Label
            {
                Text = "ID",
                ForeColor = Color.LightGray,
                Top = 70,
                Left = 40,
                Width = 60
            };
            this.Controls.Add(lblId);

            txtUserId = new TextBox
            {
                Top = 65,
                Left = 110,
                Width = 180,
                Font = new Font("Malgun Gothic", 10),
                BackColor = Color.FromArgb(60, 62, 70),
                ForeColor = Color.White,
                BorderStyle = BorderStyle.FixedSingle
            };
            this.Controls.Add(txtUserId);

            // Password Label & Text
            var lblPw = new Label
            {
                Text = "PW",
                ForeColor = Color.LightGray,
                Top = 110,
                Left = 40,
                Width = 60
            };
            this.Controls.Add(lblPw);

            txtPassword = new TextBox
            {
                Top = 105,
                Left = 110,
                Width = 180,
                Font = new Font("Malgun Gothic", 10),
                BackColor = Color.FromArgb(60, 62, 70),
                ForeColor = Color.White,
                BorderStyle = BorderStyle.FixedSingle,
                PasswordChar = '●'
            };
            txtPassword.KeyDown += (s, e) => { if (e.KeyCode == Keys.Enter) btnLogin.PerformClick(); };
            this.Controls.Add(txtPassword);

            // Buttons
            btnLogin = new Button
            {
                Text = "LOGIN",
                Top = 150,
                Left = 110,
                Width = 85,
                Height = 35,
                FlatStyle = FlatStyle.Flat,
                BackColor = Color.FromArgb(0, 160, 80),
                ForeColor = Color.White,
                Cursor = Cursors.Hand
            };
            btnLogin.FlatAppearance.BorderSize = 0;
            btnLogin.Click += BtnLogin_Click;
            this.Controls.Add(btnLogin);

            btnCancel = new Button
            {
                Text = "CANCEL",
                Top = 150,
                Left = 205,
                Width = 85,
                Height = 35,
                FlatStyle = FlatStyle.Flat,
                BackColor = Color.FromArgb(192, 57, 43),
                ForeColor = Color.White,
                Cursor = Cursors.Hand
            };
            btnCancel.FlatAppearance.BorderSize = 0;
            btnCancel.Click += (s, e) => { this.DialogResult = DialogResult.Cancel; this.Close(); };
            this.Controls.Add(btnCancel);

            // Message Label
            lblMsg = new Label
            {
                Text = "",
                ForeColor = Color.Red,
                Top = 190,
                Left = 0,
                Width = 350,
                TextAlign = ContentAlignment.MiddleCenter,
                Font = new Font("Malgun Gothic", 8)
            };
            this.Controls.Add(lblMsg);
        }

        private void BtnLogin_Click(object sender, EventArgs e)
        {
            string id = txtUserId.Text.Trim();
            string pw = txtPassword.Text.Trim();

            if (string.IsNullOrEmpty(id))
            {
                lblMsg.Text = "Please enter ID.";
                return;
            }

            // Simple Mock Authentication
            // In production, check against DB or Auth Service
            if (pw == "1234") 
            {
                LoggedInUser = id;
                this.DialogResult = DialogResult.OK;
                this.Close();
            }
            else
            {
                lblMsg.Text = "Invalid Password.";
                txtPassword.SelectAll();
                txtPassword.Focus();
            }
        }
    }
}
