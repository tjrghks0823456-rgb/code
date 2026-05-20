using System;
using System.Collections.Generic;
using System.Drawing;
using System.Linq;
using System.Windows.Forms;
using System.Windows.Forms.DataVisualization.Charting;

namespace WindowsFormsApp1
{
    // =====================================================================
    // UC_Dashboard
    //  - 장비 현황(정상/대여중/고장)을 차트로 보여줌
    //  - 월간 달력 UI 생성 및 관리(관리자 당번 일정 표시)
    //  - 좌측: 장비 통계 / 우측: 날짜별 당직자 표시 / 하단: 일정 추가·삭제
    // =====================================================================
    public partial class UC_Dashboard : UserControl
    {
        // 장비 상태 조회용 저장소
        private EquipmentRepository _repo;

        // 관리자 일정 저장소
        private ScheduleRepository _scheduleRepo;

        // 현재 보고 있는 달(달력 렌더링 기준)
        private DateTime _currentMonth;

        // 사용자가 클릭하여 선택한 날짜
        private DateTime _selectedDate;

        public UC_Dashboard()
        {
            InitializeComponent();

            _repo = new EquipmentRepository();
            _scheduleRepo = new ScheduleRepository();

            _currentMonth = DateTime.Today;  // 오늘이 포함된 월을 기본 기준으로 사용
            _selectedDate = DateTime.Today;  // 사이드 패널 기본 날짜

            // 이벤트 핸들러 연결
            // 월 이동 버튼(이전/다음달)
            this.btnPrevMonth.Click += (s, e) => ChangeMonth(-1);
            this.btnNextMonth.Click += (s, e) => ChangeMonth(1);

            // 당직자 추가/삭제 버튼
            this.btnAddManager.Click += new System.EventHandler(this.btnAddManager_Click);
            this.btnDelManager.Click += new System.EventHandler(this.btnDelManager_Click);
        }

        // UserControl이 실제로 화면에 표시될 때 호출
        private void UC_Dashboard_Load(object sender, EventArgs e)
        {
            LoadDashboard();          // 장비 상태 차트 표시
            GenerateCalendar();       // 달력 그리기
            LoadSidePanel(_selectedDate); // 오른쪽 패널에 선택 날짜 표시
        }

        // =====================================================================
        // 장비 현황 대시보드 (차트 + 숫자)
        // =====================================================================
        public void LoadDashboard()
        {
            try
            {
                // 장비 상태별 개수 가져오기
                var stats = _repo.GetStatusCounts();

                int normal = stats.ContainsKey("정상") ? stats["정상"] : 0;
                int rented = stats.ContainsKey("대여중") ? stats["대여중"] : 0;
                int fault = stats.ContainsKey("고장") ? stats["고장"] : 0;
                int total = normal + rented + fault;

                // UI 업데이트
                lblTotal.Text = "전체 장비: " + total + "대";
                lblRented.Text = "대여 중: " + rented + "대";
                lblFault.Text = "고장: " + fault + "대";

                // 차트 초기화 후 다시 구성
                chartStatus.Series.Clear();
                Series series = new Series("Status");
                series.ChartType = SeriesChartType.Pie;

                // 장비가 하나 이상 있을 때만 파이차트 생성
                if (total > 0)
                {
                    series.Points.AddXY("정상", normal);
                    series.Points.AddXY("대여중", rented);
                    series.Points.AddXY("고장", fault);

                    // 구분이 잘 되도록 색 지정
                    series.Points[0].Color = Color.LightGreen;
                    series.Points[1].Color = Color.Orange;
                    series.Points[2].Color = Color.Red;
                }

                chartStatus.Series.Add(series);
            }
            catch (Exception ex)
            {
                MessageBox.Show("오류: " + ex.Message);
            }
        }

        private void btnRefresh_Click(object sender, EventArgs e)
        {
            LoadDashboard();
            GenerateCalendar();
        }

        // =====================================================================
        // 달력 로직
        // =====================================================================

        // 월 이동(offset: -1 = 이전달, 1 = 다음달)
        private void ChangeMonth(int offset)
        {
            _currentMonth = _currentMonth.AddMonths(offset);
            GenerateCalendar();
        }

        // 월별 달력 직접 렌더링
        private void GenerateCalendar()
        {
            // 깜빡임 방지
            tlpCalendar.SuspendLayout();
            tlpCalendar.Controls.Clear();

            // 상단 "2025년 12월" 표시
            lblCurrentMonth.Text = _currentMonth.ToString("yyyy년 M월");

            // 요일 헤더 생성
            string[] days = { "일", "월", "화", "수", "목", "금", "토" };
            for (int i = 0; i < 7; i++)
            {
                Label lbl = new Label();
                lbl.Text = days[i];
                lbl.TextAlign = ContentAlignment.MiddleCenter;
                lbl.Dock = DockStyle.Fill;
                lbl.Font = new Font("맑은 고딕", 9, FontStyle.Bold);

                // 일요일 빨강 / 토요일 파랑
                if (i == 0) lbl.ForeColor = Color.Red;
                if (i == 6) lbl.ForeColor = Color.Blue;

                tlpCalendar.Controls.Add(lbl, i, 0);
            }

            // 날짜 계산
            DateTime firstDay = new DateTime(_currentMonth.Year, _currentMonth.Month, 1);
            int daysInMonth = DateTime.DaysInMonth(_currentMonth.Year, _currentMonth.Month);
            int startCol = (int)firstDay.DayOfWeek;

            int row = 1;
            int col = startCol;

            // 날짜 채우기
            for (int day = 1; day <= daysInMonth; day++)
            {
                DateTime date = new DateTime(_currentMonth.Year, _currentMonth.Month, day);

                // 하루 단위 Panel 생성
                Panel pnl = new Panel();
                pnl.Dock = DockStyle.Fill;
                pnl.Margin = new Padding(1);

                // 날짜 선택된 경우 배경을 강조
                pnl.BackColor = (date.Date == _selectedDate.Date)
                                ? Color.LightGoldenrodYellow
                                : Color.White;

                pnl.Tag = date;                // 날짜 정보를 Panel에 저장
                pnl.Click += DayPanel_Click;   // 클릭 이벤트 연결

                // 날짜 숫자 라벨
                Label lblNum = new Label();
                lblNum.Text = day.ToString();
                lblNum.Location = new Point(3, 3);
                lblNum.AutoSize = true;
                lblNum.Font = new Font("맑은 고딕", 9, FontStyle.Bold);

                if (col == 0) lblNum.ForeColor = Color.Red;
                if (col == 6) lblNum.ForeColor = Color.Blue;

                // 라벨을 클릭해도 Panel 클릭과 같은 효과
                lblNum.Click += (s, e) => DayPanel_Click(pnl, e);

                pnl.Controls.Add(lblNum);

                // 해당 날짜의 관리자 목록 표시
                var managers = _scheduleRepo.GetManagers(date);
                if (managers.Count > 0)
                {
                    Label lblNames = new Label();
                    lblNames.Text = string.Join("\r\n", managers); // 여러 명이면 줄바꿈
                    lblNames.Location = new Point(5, 25);
                    lblNames.AutoSize = true;
                    lblNames.Font = new Font("맑은 고딕", 8);
                    lblNames.Click += (s, e) => DayPanel_Click(pnl, e);

                    pnl.Controls.Add(lblNames);
                }

                // 달력 테이블에 Panel 추가
                tlpCalendar.Controls.Add(pnl, col, row);

                col++;
                if (col > 6)  // 다음 주 차로 이동
                {
                    col = 0;
                    row++;
                }
            }

            tlpCalendar.ResumeLayout();
        }

        // 날짜를 클릭했을 때 실행
        private void DayPanel_Click(object sender, EventArgs e)
        {
            Panel pnl = sender as Panel;

            if (pnl != null && pnl.Tag is DateTime date)
            {
                // 선택 날짜 갱신
                _selectedDate = date;

                // 하이라이트 갱신 위해 달력 다시 그림
                GenerateCalendar();

                // 오른쪽 패널 갱신
                LoadSidePanel(date);
            }
        }

        // =====================================================================
        // 오른쪽 사이드 패널 (선택 날짜의 당직자 목록)
        // =====================================================================
        private void LoadSidePanel(DateTime date)
        {
            lstManagers.Items.Clear();

            var managers = _scheduleRepo.GetManagers(date);
            foreach (var m in managers)
                lstManagers.Items.Add(m);

            // "12/5 당직 명단" 형식으로 제목 표시
            lblManagerTitle.Text = $"{date:M/d} 당직 명단";
        }

        // =====================================================================
        // 당직자 추가/삭제 기능
        // =====================================================================
        private void btnAddManager_Click(object sender, EventArgs e)
        {
            string name = txtManagerName.Text.Trim();
            if (string.IsNullOrEmpty(name)) return;

            // 선택 날짜에 추가
            _scheduleRepo.AddManager(_selectedDate, name);
            txtManagerName.Clear();

            // 일정 갱신
            LoadSidePanel(_selectedDate);
            GenerateCalendar();
        }

        private void btnDelManager_Click(object sender, EventArgs e)
        {
            if (lstManagers.SelectedItem == null) return;

            string name = lstManagers.SelectedItem.ToString();

            if (MessageBox.Show($"{name} 님을 삭제하시겠습니까?", "확인",
                MessageBoxButtons.YesNo) == DialogResult.Yes)
            {
                _scheduleRepo.RemoveManager(_selectedDate, name);

                LoadSidePanel(_selectedDate);
                GenerateCalendar();
            }
        }

        private void chartStatus_Click(object sender, EventArgs e)
        {

        }
    }
}
