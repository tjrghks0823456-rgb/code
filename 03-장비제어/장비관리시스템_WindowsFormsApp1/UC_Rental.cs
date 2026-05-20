using System;
using System.Drawing;
using System.Windows.Forms;

namespace WindowsFormsApp1
{
    // =====================================================================
    // UC_Rental
    //  - 장비 대여/반납을 수행하는 화면(UserControl)
    //  - 장비 리스트 표시 / 대여자 입력 / 반납 예정일 선택 기능 포함
    //  - 실제 DB 업데이트는 Repository 패턴을 이용해 수행
    // =====================================================================
    public partial class UC_Rental : UserControl
    {
        // 장비 상태 및 대여/반납 작업을 위한 저장소
        private EquipmentRepository _equipRepo = new EquipmentRepository();

        // 대여/반납 시 이력을 기록하기 위한 저장소
        private HistoryRepository _historyRepo = new HistoryRepository();

        public UC_Rental()
        {
            InitializeComponent();
        }

        // =====================================================================
        // SetEquipmentName
        //  - Form1에서 선택된 장비 이름을 전달받아 표시하는 함수
        //  - 예: 목록 화면 → 대여 화면으로 이동할 때 자동 반영되도록 함
        // =====================================================================
        public void SetEquipmentName(string name)
        {
            lblSelectedEquip.Text = name;
            LoadRentalList(); // 화면의 장비 목록도 최신 상태로 갱신
        }

        // =====================================================================
        // LoadRentalList
        //  - 전체 장비를 조회하여 ListView에 표시하는 공통 함수
        //  - '대여중' / '고장'은 색으로 구분하여 시각적으로 빠르게 파악 가능
        // =====================================================================
        public void LoadRentalList()
        {
            try
            {
                lvRental.Items.Clear();
                var list = _equipRepo.SelectAll();

                foreach (var equip in list)
                {
                    // 모델 내부의 ToListViewItem()을 사용해 ListViewItem 생성
                    ListViewItem item = new ListViewItem(equip.ToListViewItem());

                    // 상태에 따라 색상 지정
                    if (equip.Status == "고장")
                        item.BackColor = Color.LightCoral;              // 빨강 = 사용 불가
                    else if (equip.Status == "대여중")
                        item.BackColor = Color.LightGoldenrodYellow;    // 노랑 = 현재 사용 중

                    lvRental.Items.Add(item);
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show("목록 로드 실패: " + ex.Message);
            }
        }

        // =====================================================================
        // 대여 버튼 클릭
        //  - 사용자 입력 검증
        //  - 리포지토리(Rent) 호출 → DB 업데이트
        //  - 이력 기록
        // =====================================================================
        private void btnRent_Click(object sender, EventArgs e)
        {
            string equip = lblSelectedEquip.Text; // 어떤 장비를 대여하는지
            string user = txtUser.Text.Trim();    // 대여자 이름
            DateTime dueDate = dtpDueDate.Value;  // 반납 예정일

            // 기본 입력 확인
            if (string.IsNullOrEmpty(equip) || equip == "-")
            {
                MessageBox.Show("장비를 선택하세요.");
                return;
            }
            if (string.IsNullOrEmpty(user))
            {
                MessageBox.Show("사용자명을 입력하세요.");
                return;
            }

            // 반납 날짜가 과거일 수는 없으므로 검증
            if (dueDate <= DateTime.Now)
            {
                MessageBox.Show("반납 예정일은 현재 시간보다 미래여야 합니다.");
                return;
            }

            try
            {
                // 1) 대여 처리 (Repo 내부에서 status='대여중', user, due_date 등을 업데이트)
                _equipRepo.Rent(equip, user, dueDate);

                // 2) 이력 저장
                _historyRepo.AddLog("대여", user, equip);

                MessageBox.Show($"대여 완료! (반납 예정: {dueDate:yyyy-MM-dd HH:mm})");

                // 3) 화면 갱신
                LoadRentalList();
            }
            catch (Exception ex)
            {
                MessageBox.Show(ex.Message, "대여 실패", MessageBoxButtons.OK, MessageBoxIcon.Warning);
            }
        }

        // =====================================================================
        // 반납 버튼 클릭
        //  - 장비의 상태를 '정상'으로 되돌리고, due_date 초기화
        //  - 이력 기록 시 관리자 처리로 기록
        // =====================================================================
        private void btnReturn_Click(object sender, EventArgs e)
        {
            string equip = lblSelectedEquip.Text;

            if (string.IsNullOrEmpty(equip) || equip == "-")
            {
                MessageBox.Show("장비를 선택하세요.");
                return;
            }

            try
            {
                // 1) 반납 처리
                _equipRepo.Return(equip);

                // 2) 이력 저장 (누가 반납 처리했는지 기록)
                _historyRepo.AddLog("반납", "시스템/관리자", equip);

                MessageBox.Show("반납 완료!");

                LoadRentalList();
            }
            catch (Exception ex)
            {
                MessageBox.Show(ex.Message, "반납 실패", MessageBoxButtons.OK, MessageBoxIcon.Warning);
            }
        }

        // =====================================================================
        // 화면 로드 시 초기 설정
        //  - 장비 목록 로딩
        //  - 기본 반납 예정일을 '7일 후'로 설정
        //  - NumericUpDown도 7로 맞춰두어 날짜/일수 연동이 시작되는 기준점 제공
        // =====================================================================
        private void UC_Rental_Load(object sender, EventArgs e)
        {
            LoadRentalList();

            dtpDueDate.Value = DateTime.Now.AddDays(7); // 기본: 일주일 후
            nudDays.Value = 7;                          // NumericUpDown에도 반영
        }

        // =====================================================================
        // 일수 변경 → 날짜 자동 계산
        //  - 예: "3일"로 바꾸면 반납 날짜가 오늘+3일로 자동 변함
        // =====================================================================
        private void nudDays_ValueChanged(object sender, EventArgs e)
        {
            dtpDueDate.Value = DateTime.Now.AddDays((double)nudDays.Value);
        }

        // =====================================================================
        // 날짜 변경 → 일수 자동 계산
        //  - 날짜를 직접 선택한 경우, 남은 일수를 NumericUpDown에 다시 반영
        // =====================================================================
        private void dtpDueDate_ValueChanged(object sender, EventArgs e)
        {
            TimeSpan diff = dtpDueDate.Value - DateTime.Now;

            if (diff.TotalDays < 0)
            {
                // 과거 날짜 선택은 허용하지 않지만,
                // 여기서는 버튼 클릭 시 검증하므로 즉시 막지는 않는다.
                return;
            }

            int days = (int)Math.Ceiling(diff.TotalDays);

            // 일수 범위 제한 (1~365)
            if (days < 1) days = 1;
            if (days > 365) days = 365;

            nudDays.Value = days;
        }

        // =====================================================================
        // 리스트에서 장비 선택 → 화면에 선택한 장비명 표시
        // =====================================================================
        private void btnSelect_Click(object sender, EventArgs e)
        {
            if (lvRental.SelectedItems.Count == 0)
            {
                MessageBox.Show("목록에서 장비를 먼저 선택해주세요.");
                return;
            }

            string selectedName = lvRental.SelectedItems[0].Text;
            lblSelectedEquip.Text = selectedName;

            MessageBox.Show($"'{selectedName}' 장비가 선택되었습니다.");
        }

        private void lvRental_SelectedIndexChanged(object sender, EventArgs e)
        {

        }
    }
}
