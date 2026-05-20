using System;
using System.Drawing;
using System.Windows.Forms;

namespace WindowsFormsApp1
{
    // UC_Fault:
    // 장비의 "고장 신고"와 "수리 완료" 기능을 담당하는 화면 구성 요소(UserControl).
    // 화면(UI)과 데이터베이스(DB) 로직을 분리하기 위해 Repository를 사용했고,
    // 이 컨트롤은 사용자의 입력과 결과 표시만 담당하도록 설계됨.
    public partial class UC_Fault : UserControl
    {
        // 장비 상태 변경(DB 업데이트)을 담당하는 저장소 클래스.
        // UI는 DB 로직을 직접 작성하지 않고 Repository에 맡겨 역할을 분리함.
        private EquipmentRepository _equipRepo = new EquipmentRepository();

        // 고장 신고 및 수리 완료 이력을 기록하는 전용 저장소.
        // 이력(Log)은 추후 문제 분석 및 기록 유지에 필요하므로 별도 테이블로 관리.
        private HistoryRepository _historyRepo = new HistoryRepository();

        // UserControl 생성자:
        // 디자이너에서 배치된 버튼, 텍스트박스 등 UI 요소를 초기화.
        public UC_Fault()
        {
            InitializeComponent();
        }

        // 외부(Form1 등)에서 “선택된 장비명”을 전달해주는 메서드.
        // 다른 화면에서 장비를 선택하면, 이 컨트롤이 해당 장비로 고장 신고/수리 기능을 수행할 수 있게 하는 구조.
        public void SetEquipmentName(string name)
        {
            // name이 비었으면 "-"로 표시하여 선택된 장비가 없다는 것을 표현.
            lblSelectedEquip.Text = string.IsNullOrEmpty(name) ? "-" : name;

            // Label을 갱신한 후 전체 목록도 함께 다시 불러 화면을 최신 상태로 유지.
            LoadFaultList();
        }

        // 전체 장비 목록을 DB에서 읽어와 ListView에 채우는 메서드.
        // UI는 DB 구조를 몰라도 되고, Repository가 모든 데이터를 제공.
        private void LoadFaultList()
        {
            try
            {
                // ListView 화면을 초기화하여 중복 표시 방지.
                lvFaultEqui.Items.Clear();

                // DB에서 모든 장비 목록 가져오기.
                var list = _equipRepo.SelectAll();

                // 하나씩 ListViewItem으로 변환하여 UI에 추가.
                foreach (var equip in list)
                {
                    // Equipment 모델이 제공하는 ToListViewItem()은
                    // 장비 정보를 화면용 배열(string[])로 변환하는 역할.
                    ListViewItem item = new ListViewItem(equip.ToListViewItem());

                    // 상태에 따라 시각적으로 구분하기 위해 색상 사용.
                    if (equip.Status == "고장")
                        item.BackColor = Color.LightCoral; // 고장 → 붉은색
                    else if (equip.Status == "대여중")
                        item.BackColor = Color.LightGoldenrodYellow; // 대여중 → 노란색

                    lvFaultEqui.Items.Add(item);
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show("목록 로드 실패: " + ex.Message);
            }
        }

        // ListView에서 항목을 클릭할 때 실행되는 이벤트.
        // 사용자가 어떤 장비를 선택했는지 UI에 반영하는 역할.
        private void lvFaultEqui_SelectedIndexChanged(object sender, EventArgs e)
        {
            // 선택된 항목이 없으면 기본 상태로 되돌림.
            if (lvFaultEqui.SelectedItems.Count == 0) return;

            // 첫 번째 선택 항목의 텍스트(장비명)를 Label에 설정.
            // 이 Label이 이후 고장 신고/수리 기능의 대상이 됨.
            lblSelectedEquip.Text = lvFaultEqui.SelectedItems[0].Text;
        }

        // 고장 신고 버튼 클릭 시 실행되는 메서드.
        // 사용자가 “고장 신고”를 누르면 DB 업데이트 + 이력 기록을 처리함.
        private void btnFault_Click(object sender, EventArgs e)
        {
            // 현재 Label에 표시된 장비명 가져오기.
            string equip = lblSelectedEquip.Text;

            // 고장 사유 입력값을 앞뒤 공백 제거 후 가져오기.
            string reason = txtReason.Text.Trim();

            // 장비 선택 여부 확인.
            if (string.IsNullOrEmpty(equip) || equip == "-")
            {
                MessageBox.Show("장비를 선택하세요.");
                return;
            }

            // 고장 사유가 비어 있으면 신고 불가.
            if (string.IsNullOrEmpty(reason))
            {
                MessageBox.Show("고장 사유를 입력하세요.");
                return;
            }

            try
            {
                // 1) 장비 상태를 DB에서 "고장"으로 변경.
                _equipRepo.ReportFault(equip);

                // 2) 고장 이력 로그 기록.
                //    고장 사유를 남겨야 문제 재발 시 참고 가능.
                _historyRepo.AddLog("고장신고", "관리자(" + reason + ")", equip);

                MessageBox.Show("고장 등록 완료!");

                // 3) 화면 갱신: 최신 상태로 목록 표시.
                LoadFaultList();
            }
            catch (Exception ex)
            {
                MessageBox.Show(ex.Message);
            }
        }

        // 수리 완료 버튼 클릭 시 실행되는 메서드.
        // 해당 장비의 상태를 정상으로 되돌리고, 이력에 기록함.
        private void btnRepair_Click(object sender, EventArgs e)
        {
            string equip = lblSelectedEquip.Text;

            // 장비가 선택되지 않은 경우 처리.
            if (string.IsNullOrEmpty(equip) || equip == "-")
            {
                MessageBox.Show("장비를 선택하세요.");
                return;
            }

            try
            {
                // 1) 장비 상태를 정상으로 변경.
                _equipRepo.CompleteRepair(equip);

                // 2) 수리 완료 로그 추가.
                _historyRepo.AddLog("수리완료", "관리자", equip);

                MessageBox.Show("복구 완료!");

                // 3) 화면 갱신.
                LoadFaultList();
            }
            catch (Exception ex)
            {
                MessageBox.Show(ex.Message);
            }
        }

        // UserControl이 화면에 표시될 때 최초로 실행되는 이벤트.
        // 화면이 초기화되는 즉시 장비 목록을 불러 표시함.
        private void UC_Fault_Load(object sender, EventArgs e)
        {
            LoadFaultList();
        }

        // '선택' 버튼 클릭 시 실행되는 메서드.
        // 사용자가 목록에서 선택한 장비를 명확하게 Label에 반영해줌.
        private void btnSelect_Click(object sender, EventArgs e)
        {
            if (lvFaultEqui.SelectedItems.Count == 0)
            {
                MessageBox.Show("목록에서 장비를 먼저 선택해주세요.");
                return;
            }

            // 실제 선택된 장비명
            string selectedName = lvFaultEqui.SelectedItems[0].Text;

            // Label에 반영
            lblSelectedEquip.Text = selectedName;

            MessageBox.Show($"'{selectedName}' 장비가 선택되었습니다.");
        }
    }
}
