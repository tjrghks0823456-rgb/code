using System;
using System.Windows.Forms;

namespace WindowsFormsApp1
{
    // =====================================================================
    // UC_History
    //  - history 테이블을 조회하는 전용 UserControl
    //  - 전체 이력 표시 / 기간 검색 기능 제공
    //  - ListView는 History 모델의 ToListViewItem()을 기반으로 자동 구성됨
    // =====================================================================
    public partial class UC_History : UserControl
    {
        // DB에서 이력(history) 데이터를 가져오는 전용 저장소
        // 폼에서는 SQL을 직접 사용하지 않고, Repository에 모든 요청을 위임
        private HistoryRepository _repo = new HistoryRepository();

        public UC_History()
        {
            InitializeComponent();
        }

        // =====================================================================
        // UserControl이 화면에 처음 로드될 때 실행되는 이벤트
        // =====================================================================
        private void UC_History_Load(object sender, EventArgs e)
        {
            // 최근 1주일 범위를 기본값으로 지정
            //  → 관리자는 보통 '최근 이력'을 많이 보기 때문에 편의를 위해 기본 설정
            dtpStart.Value = DateTime.Now.AddDays(-7);
            dtpEnd.Value = DateTime.Now;

            // 전체 이력을 ListView에 출력
            LoadHistory();
        }

        // =====================================================================
        // LoadHistory
        //  - 전체 이력을 가져와서 화면에 표시
        //  - 버튼 새로고침(btnRefresh)에서도 재사용되는 공통 함수
        // =====================================================================
        public void LoadHistory()
        {
            try
            {
                // history 테이블의 모든 데이터를 최신순으로 가져옴
                var list = _repo.SelectAll();

                // ListView 바인딩 함수 사용
                BindListView(list);
            }
            catch (Exception ex)
            {
                MessageBox.Show("이력 로드 중 오류: " + ex.Message);
            }
        }

        // =====================================================================
        // 새로고침 버튼
        // =====================================================================
        private void btnRefresh_Click(object sender, EventArgs e)
        {
            LoadHistory();  // 전체 이력 다시 불러오기
        }

        // =====================================================================
        // 기간 검색 버튼
        //  - 시작일~종료일 범위에 맞는 이력만 검색
        // =====================================================================
        private void btnSearch_Click(object sender, EventArgs e)
        {
            try
            {
                // 날짜 선택 도구(DateTimePicker)는 "날짜 + 시간 00:00:00" 형태로 저장됨.
                // 따라서 검색 정확도를 높이기 위해 시간을 명확하게 설정해준다.

                // 시작일: 00:00:00부터
                DateTime start = dtpStart.Value.Date;

                // 종료일: 선택한 날짜의 "23:59:59"까지 포함되도록 변환
                // 이유: 날짜만 비교하면 당일 오후 데이터가 누락될 수 있기 때문
                DateTime end = dtpEnd.Value.Date.AddDays(1).AddSeconds(-1);

                // 지정 기간 내 데이터 요청
                var list = _repo.SelectByPeriod(start, end);

                BindListView(list);
            }
            catch (Exception ex)
            {
                MessageBox.Show("검색 중 오류: " + ex.Message);
            }
        }

        // =====================================================================
        // BindListView
        //  - History 모델 리스트를 받아서 ListView에 출력하는 공통 함수
        //  - ToListViewItem()을 이용해 History 객체 → string[] 변환
        // =====================================================================
        private void BindListView(System.Collections.Generic.List<History> list)
        {
            // 기존 내용 모두 삭제 후 다시 채움
            lvHistory.Items.Clear();

            foreach (var log in list)
            {
                // History 모델 내부의 ToListViewItem()이
                // ListViewItem 생성에 필요한 string[]를 반환하도록 설계됨
                ListViewItem item = new ListViewItem(log.ToListViewItem());

                lvHistory.Items.Add(item);
            }
        }
    }
}
