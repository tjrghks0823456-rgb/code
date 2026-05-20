using System;
using System.Windows.Forms;

namespace WindowsFormsApp1
{
    // LoginForm
    // - 프로그램 실행 시 가장 먼저 나타나는 로그인 창
    // - Form을 상속하는 윈도우 창이며, ID/PW를 입력받고 검증하는 역할만 담당
    public partial class LoginForm : Form
    {
        public LoginForm()
        {
            InitializeComponent();
            // InitializeComponent()
            // - 디자이너에서 만든 버튼/텍스트박스 등을 실제로 생성하고 화면에 배치
            // - Form 생성자에서 반드시 호출해야 UI 요소가 준비됨
        }

        // "로그인" 버튼 클릭 시 실행되는 이벤트 핸들러
        // sender: 클릭된 버튼 객체
        // e      : 이벤트 정보 (지금은 사용하지 않음)
        private void btnLogin_Click(object sender, EventArgs e)
        {
            // 텍스트박스에서 입력받은 ID/PW 값 가져오기
            // txtId.Text : 사용자가 입력한 아이디
            // txtPw.Text : 사용자가 입력한 비밀번호
            string id = txtId.Text;
            string pw = txtPw.Text;

            // ---------------------------------------------------------------
            // [DB 연동 로그인]
            // UserRepository를 통해 DB에서 아이디/비밀번호 확인
            // ---------------------------------------------------------------
            UserRepository repo = new UserRepository();
            
            // 예외 처리 (DB 연결 등)
            try 
            {
                if (repo.ValidateUser(id, pw))
                {
                    MessageBox.Show("로그인 성공!", "알림");
                    this.DialogResult = DialogResult.OK;
                    this.Close();
                }
                else
                {
                    MessageBox.Show("아이디 또는 비밀번호가 틀렸습니다.", "오류", MessageBoxButtons.OK, MessageBoxIcon.Error);
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show("로그인 처리 중 오류 발생: " + ex.Message, "오류");
            }
        }

        // =====================================================================
        // 사용자 관리 버튼 (추가됨)
        // =====================================================================
        private void btnUserManage_Click(object sender, EventArgs e)
        {
            // 사용자 관리는 관리자만 접근 가능하도록, 
            // 현재 로그인 정보를 확인하거나, 접근 시 비밀번호를 한 번 더 물어볼 수 있음.
            // 여기서는 심플하게 "현재 입력된 ID/PW"가 admin인지 확인하고 열어주거나,
            // 별도의 인증 절차를 넣을 수 있음.
            
            // 과제 요구사항: "로그인 버튼 옆에 사용자 관리 버튼... 누르면 새 사용자 추가 등"
            // 보통 관리자 도구는 로그인을 해야 들어갈 수 있으나,
            // 로그인 창에서 바로 관리자 도구로 가려면 "관리자 인증"이 필요함.
            
            // 여기서는 간단히 텍스트박스에 'admin' / '1234' (초기번) 입력된 상태에서 누르면 열리게 하거나,
            // 아니면 바로 열리되 내부에서 막을 수도 있음. 
            // --> "새 ID, 새 PW" 입력 기능이 포함된 관리창을 띄우겠습니다.
            
            // 안전을 위해, 텍스트박스에 입력된 계정으로 검증 후 오픈
            string id = txtId.Text;
            string pw = txtPw.Text;
            
            UserRepository repo = new UserRepository();
            if (repo.ValidateUser(id, pw) && id.ToLower() == "admin")
            {
                 UserManagementForm form = new UserManagementForm();
                 form.ShowDialog();
            }
            else
            {
                 MessageBox.Show("관리자 계정(admin)으로 ID/PW를 입력 후 눌러주세요.", "관리자 권한 필요");
            }
        }
    }
}
