using System;
using System.Windows.Forms;

namespace WindowsFormsApp1
{
    // =====================================================================
    // Form1
    //  - 프로그램의 메인 화면(Form)
    //  - 왼쪽 메뉴 버튼을 클릭하면 중앙 영역(panelMain)에
    //    해당 UserControl을 불러오는 "화면 전환 기능"을 담당
    //  - 전체 프로젝트의 '네비게이션 허브'
    // =====================================================================
    public partial class Form1 : Form
    {
        // 다른 UserControl에서 선택한 장비 이름을 전달하기 위한 공유 변수
        // 예: 목록 화면에서 장비 선택 → 대여/고장 화면에서 동일 장비 이름 자동 표시
        public string SelectedEquipmentName = "";

        // ---------------------------------------------------------------------
        // 화면(UserControl) 인스턴스 생성
        //  - 화면 간 전환이 매우 빠르게 이루어지도록,
        //    미리 한 번만 생성해두고 계속 재사용하는 방식.
        //  - 매번 new를 하지 않아도 되어 성능에 유리하고,
        //    각 화면의 상태가 유지됨.
        // ---------------------------------------------------------------------
        private UC_Dashboard pageDashboard = new UC_Dashboard();
        private UC_EquipmentList pageEquip = new UC_EquipmentList();
        private UC_Rental pageRental = new UC_Rental();
        private UC_Fault pageFault = new UC_Fault();
        private UC_History pageHistory = new UC_History();

        public Form1()
        {
            InitializeComponent();
        }

        // =====================================================================
        // Form1_Load
        //  - 프로그램이 처음 실행될 때 호출되는 이벤트
        //  - 기본 시작 화면을 '대시보드'로 설정
        // =====================================================================
        private void Form1_Load(object sender, EventArgs e)
        {
            // 프로그램 시작 시 UI 비활성화 (로그인 전)
            SetLoginState(false);
        }

        // =====================================================================
        // ShowPage(UserControl page)
        //  - panelMain 내부에 전달받은 UserControl 화면을 띄우는 공통 함수
        //  - 모든 메뉴 버튼이 이 함수를 통해 화면을 바꿈
        // =====================================================================
        private void ShowPage(UserControl page)
        {
            // 기존 화면 제거 → 새로운 화면만 보이게 함
            panelMain.Controls.Clear();

            // 화면을 panelMain 영역 전체에 맞게 Dock
            page.Dock = DockStyle.Fill;

            // panelMain에 화면 추가
            panelMain.Controls.Add(page);

            // 만약 대시보드 화면이면, 실시간 통계를 다시 불러오게 함
            // 왜?
            // → 대여/반납/고장 처리 후 다시 홈으로 오면,
            //    최신 장비 통계가 자동으로 반영되도록 하기 위해
            if (page is UC_Dashboard dash)
            {
                dash.LoadDashboard();
            }
        }

        // =====================================================================
        // 메뉴 버튼들
        //  - 각각의 버튼은 미리 만들어둔 UserControl을 ShowPage()로 전달
        // =====================================================================

        // 대시보드 버튼
        private void btnMenuDashboard_Click(object sender, EventArgs e)
        {
            ShowPage(pageDashboard);
        }

        // 장비 목록 버튼
        private void btnMenuEquip_Click(object sender, EventArgs e)
        {
            // 목록 화면으로 갈 때 데이터 갱신
            // 이유: 새로운 대여나 반납이 있으면 목록에도 적용되어야 함
            pageEquip.LoadEquipmentList();

            ShowPage(pageEquip);
        }

        // 대여 화면
        private void btnMenuRental_Click(object sender, EventArgs e)
        {
            // 현재 선택된 장비 이름을 대여 화면에 전달
            // 이유: 목록 → 대여로 이동 시 선택 반영
            pageRental.SetEquipmentName(SelectedEquipmentName);

            ShowPage(pageRental);
        }

        // 고장 신고 화면
        private void btnMenuFault_Click(object sender, EventArgs e)
        {
            // 같은 방식으로 선택된 장비 이름 전달
            pageFault.SetEquipmentName(SelectedEquipmentName);

            ShowPage(pageFault);
        }

        // 이력 조회 화면
        private void btnMenuHistory_Click(object sender, EventArgs e)
        {
            // 이력은 항상 최신 데이터를 보여주는 것이 중요하므로
            // 화면 이동 전에 무조건 새로 로딩
            pageHistory.LoadHistory();

            ShowPage(pageHistory);
        }

        // =====================================================================
        // 로그인 버튼 (추가됨)
        // =====================================================================
        private void btnMenuLogin_Click(object sender, EventArgs e)
        {
            // 현재 로그인 상태인지 확인 (버튼 텍스트로 판단)
            if (btnMenuLogin.Text == "로그아웃")
            {
                // 로그아웃 처리
                SetLoginState(false);
                MessageBox.Show("로그아웃 되었습니다.", "알림");
                return;
            }

            // 로그인 창 띄우기
            LoginForm login = new LoginForm();
            if (login.ShowDialog() == DialogResult.OK)
            {
                // 로그인 성공 시 UI 활성화
                SetLoginState(true);
                
                // 첫 화면으로 대시보드 로드
                ShowPage(pageDashboard);
            }
        }

        // =====================================================================
        // 로그인 상태에 따른 UI 활성화/비활성화 처리
        // =====================================================================
        private void SetLoginState(bool isLoggedIn)
        {
            // 1. 메뉴 버튼 활성화/비활성화
            btnMenuDashboard.Enabled = isLoggedIn;
            btnMenuEquip.Enabled = isLoggedIn;
            btnMenuRental.Enabled = isLoggedIn;
            btnMenuFault.Enabled = isLoggedIn;
            btnMenuHistory.Enabled = isLoggedIn;

            // 2. 메인 패널 보이기/숨기기
            panelMain.Visible = isLoggedIn;

            // 3. 로그인 버튼 텍스트 변경 (로그인 <-> 로그아웃) - 옵션
            if (isLoggedIn)
            {
                btnMenuLogin.Text = "로그아웃";
            }
            else
            {
                btnMenuLogin.Text = "로그인";
                // 로그아웃 상태면 메인 패널 비우기
                panelMain.Controls.Clear();
            }
        }
    }
}
