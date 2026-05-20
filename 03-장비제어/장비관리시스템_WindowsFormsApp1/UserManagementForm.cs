using System;
using System.Collections.Generic;
using System.Windows.Forms;

namespace WindowsFormsApp1
{
    public partial class UserManagementForm : Form
    {
        private UserRepository _userRepo = new UserRepository();

        public UserManagementForm()
        {
            InitializeComponent();
        }

        private void UserManagementForm_Load(object sender, EventArgs e)
        {
            LoadUserList();
        }

        private void LoadUserList()
        {
            listViewUsers.Items.Clear();
            List<User> users = _userRepo.SelectAll();

            foreach (var u in users)
            {
                ListViewItem item = new ListViewItem(u.ToListViewItem());
                listViewUsers.Items.Add(item);
            }
        }

        private void btnAdd_Click(object sender, EventArgs e)
        {
            string newId = txtNewId.Text.Trim();
            string newPw = txtNewPw.Text.Trim();

            if (string.IsNullOrEmpty(newId) || string.IsNullOrEmpty(newPw))
            {
                MessageBox.Show("아이디와 비밀번호를 모두 입력해주세요.", "경고", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return;
            }

            try
            {
                _userRepo.AddUser(newId, newPw);
                MessageBox.Show($"사용자 [{newId}] 추가 완료!", "성공");
                
                txtNewId.Text = "";
                txtNewPw.Text = "";
                LoadUserList();
            }
            catch (Exception ex)
            {
                MessageBox.Show("사용자 추가 실패: " + ex.Message, "오류", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }

        private void btnDelete_Click(object sender, EventArgs e)
        {
            if (listViewUsers.SelectedItems.Count == 0)
            {
                MessageBox.Show("삭제할 사용자를 선택해주세요.", "알림");
                return;
            }

            ListViewItem selected = listViewUsers.SelectedItems[0];
            string userId = selected.SubItems[1].Text; // 0: Id, 1: Username

            if (MessageBox.Show($"정말 사용자 [{userId}]를 삭제하시겠습니까?", "확인", MessageBoxButtons.YesNo, MessageBoxIcon.Question) == DialogResult.Yes)
            {
                try
                {
                    _userRepo.DeleteUser(userId);
                    MessageBox.Show("삭제되었습니다.", "성공");
                    LoadUserList();
                }
                catch (Exception ex)
                {
                    MessageBox.Show("삭제 실패: " + ex.Message, "오류");
                }
            }
        }

        private void btnClose_Click(object sender, EventArgs e)
        {
            this.Close();
        }
    }
}
