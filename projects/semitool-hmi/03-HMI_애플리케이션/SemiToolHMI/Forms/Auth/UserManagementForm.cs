using System;
using System.Collections.Generic;
using System.Drawing;
using System.IO;
using System.Linq;
using System.Windows.Forms;

namespace SemiToolHMI
{
    public partial class UserManagementForm : Form
    {
        private const string USER_FILE = "users.txt";
        
        private TextBox txtAdminId;
        private TextBox txtAdminPw;
        private Button btnAdminLogin;
        private Panel panelManagement;
        
        private TextBox txtNewId;
        private TextBox txtNewPw;
        private TextBox txtNewName;
        private ComboBox cboRole;
        private Button btnAddUser;
        private ListBox lstUsers;
        private Button btnDeleteUser;

        public UserManagementForm()
        {
            InitializeComponent();
            BuildUI();
        }

        private void InitializeComponent()
        {
            this.SuspendLayout();
            this.ClientSize = new System.Drawing.Size(500, 500);
            this.Name = "UserManagementForm";
            this.Text = "사용자 관리";
            this.StartPosition = FormStartPosition.CenterParent;
            this.FormBorderStyle = FormBorderStyle.FixedDialog;
            this.MaximizeBox = false;
            this.MinimizeBox = false;
            this.BackColor = Color.FromArgb(40, 42, 50);
            this.ResumeLayout(false);
        }

        private void BuildUI()
        {
            // Title
            var lblTitle = new Label
            {
                Text = "사용자 관리 - 관리자 로그인 필요",
                Font = new Font("Malgun Gothic", 12, FontStyle.Bold),
                ForeColor = Color.White,
                AutoSize = true,
                Top = 20,
                Left = 20
            };
            this.Controls.Add(lblTitle);

            // Admin Login Panel
            var lblAdminId = new Label
            {
                Text = "관리자 ID",
                ForeColor = Color.LightGray,
                Top = 60,
                Left = 40,
                Width = 80
            };
            this.Controls.Add(lblAdminId);

            txtAdminId = new TextBox
            {
                Top = 55,
                Left = 130,
                Width = 150,
                Font = new Font("Malgun Gothic", 10),
                BackColor = Color.FromArgb(60, 62, 70),
                ForeColor = Color.White,
                BorderStyle = BorderStyle.FixedSingle
            };
            this.Controls.Add(txtAdminId);

            var lblAdminPw = new Label
            {
                Text = "관리자 PW",
                ForeColor = Color.LightGray,
                Top = 95,
                Left = 40,
                Width = 80
            };
            this.Controls.Add(lblAdminPw);

            txtAdminPw = new TextBox
            {
                Top = 90,
                Left = 130,
                Width = 150,
                Font = new Font("Malgun Gothic", 10),
                BackColor = Color.FromArgb(60, 62, 70),
                ForeColor = Color.White,
                BorderStyle = BorderStyle.FixedSingle,
                PasswordChar = '●'
            };
            this.Controls.Add(txtAdminPw);

            btnAdminLogin = new Button
            {
                Text = "관리자 로그인",
                Top = 85,
                Left = 300,
                Width = 120,
                Height = 35,
                FlatStyle = FlatStyle.Flat,
                BackColor = Color.FromArgb(0, 160, 80),
                ForeColor = Color.White,
                Cursor = Cursors.Hand
            };
            btnAdminLogin.FlatAppearance.BorderSize = 0;
            btnAdminLogin.Click += BtnAdminLogin_Click;
            this.Controls.Add(btnAdminLogin);

            // Management Panel (initially hidden)
            panelManagement = new Panel
            {
                Top = 140,
                Left = 20,
                Width = 460,
                Height = 340,
                BackColor = Color.FromArgb(50, 52, 60),
                Visible = false
            };
            this.Controls.Add(panelManagement);

            BuildManagementPanel();
        }

        private void BuildManagementPanel()
        {
            // Add User Section
            var lblAddUser = new Label
            {
                Text = "새 사용자 추가",
                Font = new Font("Malgun Gothic", 11, FontStyle.Bold),
                ForeColor = Color.White,
                AutoSize = true,
                Top = 15,
                Left = 15
            };
            panelManagement.Controls.Add(lblAddUser);

            var lblNewId = new Label
            {
                Text = "ID",
                ForeColor = Color.LightGray,
                Top = 50,
                Left = 20,
                Width = 60
            };
            panelManagement.Controls.Add(lblNewId);

            txtNewId = new TextBox
            {
                Top = 45,
                Left = 90,
                Width = 120,
                BackColor = Color.FromArgb(60, 62, 70),
                ForeColor = Color.White,
                BorderStyle = BorderStyle.FixedSingle
            };
            panelManagement.Controls.Add(txtNewId);

            var lblNewPw = new Label
            {
                Text = "PW",
                ForeColor = Color.LightGray,
                Top = 80,
                Left = 20,
                Width = 60
            };
            panelManagement.Controls.Add(lblNewPw);

            txtNewPw = new TextBox
            {
                Top = 75,
                Left = 90,
                Width = 120,
                BackColor = Color.FromArgb(60, 62, 70),
                ForeColor = Color.White,
                BorderStyle = BorderStyle.FixedSingle
            };
            panelManagement.Controls.Add(txtNewPw);

            var lblNewName = new Label
            {
                Text = "이름",
                ForeColor = Color.LightGray,
                Top = 110,
                Left = 20,
                Width = 60
            };
            panelManagement.Controls.Add(lblNewName);

            txtNewName = new TextBox
            {
                Top = 105,
                Left = 90,
                Width = 120,
                BackColor = Color.FromArgb(60, 62, 70),
                ForeColor = Color.White,
                BorderStyle = BorderStyle.FixedSingle
            };
            panelManagement.Controls.Add(txtNewName);

            var lblRole = new Label
            {
                Text = "권한",
                ForeColor = Color.LightGray,
                Top = 140,
                Left = 20,
                Width = 60
            };
            panelManagement.Controls.Add(lblRole);

            cboRole = new ComboBox
            {
                Top = 135,
                Left = 90,
                Width = 120,
                DropDownStyle = ComboBoxStyle.DropDownList,
                BackColor = Color.FromArgb(60, 62, 70),
                ForeColor = Color.White,
                FlatStyle = FlatStyle.Flat
            };
            cboRole.Items.AddRange(new object[] { "일반", "관리자" });
            cboRole.SelectedIndex = 0;
            panelManagement.Controls.Add(cboRole);

            btnAddUser = new Button
            {
                Text = "사용자 추가",
                Top = 50,
                Left = 250,
                Width = 180,
                Height = 115,
                FlatStyle = FlatStyle.Flat,
                BackColor = Color.FromArgb(0, 160, 80),
                ForeColor = Color.White,
                Font = new Font("Malgun Gothic", 10, FontStyle.Bold),
                Cursor = Cursors.Hand
            };
            btnAddUser.FlatAppearance.BorderSize = 0;
            btnAddUser.Click += BtnAddUser_Click;
            panelManagement.Controls.Add(btnAddUser);

            // User List Section
            var lblUserList = new Label
            {
                Text = "등록된 사용자 목록",
                Font = new Font("Malgun Gothic", 11, FontStyle.Bold),
                ForeColor = Color.White,
                AutoSize = true,
                Top = 185,
                Left = 15
            };
            panelManagement.Controls.Add(lblUserList);

            lstUsers = new ListBox
            {
                Top = 215,
                Left = 20,
                Width = 310,
                Height = 100,
                BackColor = Color.FromArgb(60, 62, 70),
                ForeColor = Color.White,
                BorderStyle = BorderStyle.FixedSingle,
                Font = new Font("Consolas", 9)
            };
            panelManagement.Controls.Add(lstUsers);

            btnDeleteUser = new Button
            {
                Text = "선택한 사용자\n삭제",
                Top = 215,
                Left = 340,
                Width = 90,
                Height = 100,
                FlatStyle = FlatStyle.Flat,
                BackColor = Color.FromArgb(192, 57, 43),
                ForeColor = Color.White,
                Cursor = Cursors.Hand
            };
            btnDeleteUser.FlatAppearance.BorderSize = 0;
            btnDeleteUser.Click += BtnDeleteUser_Click;
            panelManagement.Controls.Add(btnDeleteUser);

            LoadUserList();
        }

        private void BtnAdminLogin_Click(object sender, EventArgs e)
        {
            string id = txtAdminId.Text.Trim();
            string pw = txtAdminPw.Text.Trim();

            // Check if admin (simple check - ID contains "admin" and password is "1234")
            if (id.ToLower().Contains("admin") && pw == "1234")
            {
                panelManagement.Visible = true;
                MessageBox.Show("관리자 로그인 성공!", "성공", MessageBoxButtons.OK, MessageBoxIcon.Information);
            }
            else
            {
                MessageBox.Show("관리자 권한이 없습니다.", "오류", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }

        private void BtnAddUser_Click(object sender, EventArgs e)
        {
            string id = txtNewId.Text.Trim();
            string pw = txtNewPw.Text.Trim();
            string name = txtNewName.Text.Trim();
            string role = cboRole.SelectedItem.ToString();

            if (string.IsNullOrEmpty(id) || string.IsNullOrEmpty(pw) || string.IsNullOrEmpty(name))
            {
                MessageBox.Show("모든 필드를 입력해주세요.", "입력 오류", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return;
            }

            // Save to file
            try
            {
                string line = $"{id}|{pw}|{name}|{role}";
                File.AppendAllText(USER_FILE, line + Environment.NewLine);
                
                MessageBox.Show($"사용자 '{name}' 추가 완료!", "성공", MessageBoxButtons.OK, MessageBoxIcon.Information);
                
                // Clear fields
                txtNewId.Clear();
                txtNewPw.Clear();
                txtNewName.Clear();
                cboRole.SelectedIndex = 0;
                
                LoadUserList();
            }
            catch (Exception ex)
            {
                MessageBox.Show($"사용자 추가 실패: {ex.Message}", "오류", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }

        private void BtnDeleteUser_Click(object sender, EventArgs e)
        {
            if (lstUsers.SelectedIndex < 0)
            {
                MessageBox.Show("삭제할 사용자를 선택해주세요.", "선택 오류", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return;
            }

            var result = MessageBox.Show("선택한 사용자를 삭제하시겠습니까?", "확인", MessageBoxButtons.YesNo, MessageBoxIcon.Question);
            if (result == DialogResult.Yes)
            {
                try
                {
                    var lines = File.ReadAllLines(USER_FILE).ToList();
                    lines.RemoveAt(lstUsers.SelectedIndex);
                    File.WriteAllLines(USER_FILE, lines);
                    
                    MessageBox.Show("사용자 삭제 완료!", "성공", MessageBoxButtons.OK, MessageBoxIcon.Information);
                    LoadUserList();
                }
                catch (Exception ex)
                {
                    MessageBox.Show($"사용자 삭제 실패: {ex.Message}", "오류", MessageBoxButtons.OK, MessageBoxIcon.Error);
                }
            }
        }

        private void LoadUserList()
        {
            lstUsers.Items.Clear();
            
            if (!File.Exists(USER_FILE))
                return;

            try
            {
                var lines = File.ReadAllLines(USER_FILE);
                foreach (var line in lines)
                {
                    var parts = line.Split('|');
                    if (parts.Length >= 4)
                    {
                        lstUsers.Items.Add($"{parts[0],-15} {parts[2],-15} [{parts[3]}]");
                    }
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show($"사용자 목록 로드 실패: {ex.Message}", "오류", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }
    }
}
