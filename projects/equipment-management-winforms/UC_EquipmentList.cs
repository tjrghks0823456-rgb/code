using System;
using System.Drawing;
using System.IO;
using System.Windows.Forms;

namespace WindowsFormsApp1
{
    // =====================================================================
    // UC_EquipmentList
    //  - 데이터베이스에 저장된 장비 목록을 화면에 보여주는 UserControl
    //  - 사용자가 장비를 클릭하면:
    //       1) 장비 스펙
    //       2) 사용 가이드
    //       3) 장비 이미지
    //    를 자동으로 표시하는 "장비 조회 UI" 역할을 담당함
    //
    //  - UI와 DB 접근 로직을 분리하기 위해 Repository 패턴 사용
    //    → 유지보수 쉬움 + UI 코드가 깔끔해짐
    // =====================================================================
    public partial class UC_EquipmentList : UserControl
    {
        // Repository는 "DB와 직접 이야기하는 역할"
        // UserControl은 화면 구성에 집중하고,
        // SQL은 Repository 내에서만 수행되도록 설계(관심사 분리)
        private EquipmentRepository _repo = new EquipmentRepository();
        private HistoryRepository _historyRepo = new HistoryRepository();

        // -------------------------------------------------------------
        // 생성자
        //  - InitializeComponent()는 디자이너에서 만들어진 UI 요소를 실제 객체로 생성하는 역할
        // -------------------------------------------------------------
        public UC_EquipmentList()
        {
            InitializeComponent();
        }

        // =====================================================================
        // UC_EquipmentList_Load
        //  - UserControl이 화면에 처음 표시될 때 자동 실행되는 이벤트
        //  - 처음부터 장비 목록이 보이도록 LoadEquipmentList() 호출
        // =====================================================================
        private void UC_EquipmentList_Load(object sender, EventArgs e)
        {
            LoadEquipmentList();
        }

        // =====================================================================
        // LoadEquipmentList
        //  - equipment 테이블의 데이터를 전체 조회하여 ListView에 출력
        //  - UI는 "표시"만 하고, 실제 데이터 로딩은 Repository에 위임
        // =====================================================================
        public void LoadEquipmentList()
        {
            try
            {
                // 기존 목록을 먼저 삭제 → 최신 데이터만 반영되도록 함
                lvEquip.Items.Clear();

                // 저장소(Repo)에게 "모든 장비 가져와줘" 요청
                var list = _repo.SelectAll();

                // 가져온 장비들을 ListViewItem으로 변환하여 화면에 표시
                foreach (var equip in list)
                {
                    // 모델 내부의 ToListViewItem()
                    // → 한 장비 객체를 ListViewItem에 맞는 string[]로 변환
                    // UI는 이 결과만 받아서 표시하면 됨 → UI 코드 단순화
                    ListViewItem item = new ListViewItem(equip.ToListViewItem());

                    // 장비 상태를 색으로 표시
                    // WHY?
                    //   - "고장"과 "대여중"을 글로만 보는 것보다 색으로 보는 것이 훨씬 빠름
                    //   - 유지보수나 관리자 입장에서 위험 장비를 즉시 인지 가능
                    if (equip.Status == "고장")
                        item.BackColor = Color.LightCoral;              // 고장 → 빨강 계열
                    else if (equip.Status == "대여중")
                        item.BackColor = Color.LightGoldenrodYellow;    // 대여중 → 노랑 계열

                    lvEquip.Items.Add(item);
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show("목록 로드 실패: " + ex.Message);
            }
        }

        // =====================================================================
        // 장비를 ListView에서 선택하면 실행되는 이벤트
        //  - 스펙(왼쪽 아래)
        //  - 가이드(오른쪽 아래)
        //  - 장비 이미지
        //    를 자동으로 보여줌
        //
        // WHY?
        //   사용자가 장비 하나를 선택하면 그 장비의 모든 정보를 한눈에 볼 수 있도록 하기 위해.
        // =====================================================================
        private void lvEquip_SelectedIndexChanged(object sender, EventArgs e)
        {
            // 아무 것도 선택 안된 경우 → 초기 안내 문구 표시
            if (lvEquip.SelectedItems.Count == 0)
            {
                ResetSelectedEquipment();
                return;
            }

            // ListView에서 선택한 장비의 이름(name)과 종류(category) 추출
            // WHY SubItems[1]?
            //    ListViewItem 구조: [0]=이름, [1]=종류, [2]=상태, …
            string equipName = lvEquip.SelectedItems[0].Text;
            string category = lvEquip.SelectedItems[0].SubItems[1].Text;

            // 선택된 장비명 표시
            lblSelectedInfo.Text = "선택된 장비: " + equipName;

            // 스펙 생성 함수 호출
            lblSpecs.Text = GetSpecs(equipName, category);

            // 가이드 생성 함수 호출
            lblGuide.Text = GetGuide(equipName, category);

            // 장비 이미지 로드
            LoadImage(category);

            // 선택한 장비명을 Form1에 전달하여 다른 화면에서도 재사용 가능하도록 함
            // 예: 대여 화면 / 고장 화면에서 동일 장비 자동 표시
            Form1 parent = this.FindForm() as Form1;
            if (parent != null)
                parent.SelectedEquipmentName = equipName;
        }

        private void ResetSelectedEquipment()
        {
            lblSelectedInfo.Text = "선택된 장비: 없음";
            lblSpecs.Text = "장비를 선택하면 스펙이 표시됩니다.";
            lblGuide.Text = "장비를 선택하면 가이드가 표시됩니다.";
            pbEquipImage.Image = null;

            Form1 parent = this.FindForm() as Form1;
            if (parent != null)
                parent.SelectedEquipmentName = "";
        }

        // =====================================================================
        // GetSpecs
        //  - 선택된 장비의 스펙을 “문자열 형태”로 구성
        //  - 공통 정보 + 종류별 상세 스펙
        // WHY 문자열로 반환?
        //    UI에서 그대로 붙여넣어 표시하기 쉽기 때문
        // =====================================================================
        private string GetSpecs(string name, string category)
        {
            string common =
                $"[기본 정보]\r\n모델명: {name}\r\n제조사: SemiTech Inc.\r\n전원: 220V 3-Phase\r\n";

            string detail = "";

            if (category.Contains("세정"))
                detail = "Wafer Size: 300mm\r\nCleaning Method: Wet Bench\r\nNumber of Baths: 4\r\nChemicals: HF, SC-1, DI Water";
            else if (category.Contains("노광"))
                detail = "Light Source: EUV/ArF\r\nResolution: 14nm\r\nOverlay Accuracy: 2nm\r\nScan Speed: 500mm/s";
            else if (category.Contains("식각"))
                detail = "Etch Type: ICP\r\nRF Power: 2000W\r\nGas Lines: SF6, O2, C4F8\r\nEnd Point Detection: OES";
            else if (category.Contains("증착"))
                detail = "Deposition: PECVD/ALD\r\nTemperature: 200–650°C\r\nPressure: 10^-6 Torr\r\nUniformity: <1%";
            else if (category.Contains("검사") || category.Contains("계측"))
                detail = "Resolution: 0.5nm\r\nMagnification: 10k–200k\r\nBeam Voltage: 5–30kV\r\nDetector: SE/BSE";
            else
                detail = "Standard Interface: SECS/GEM\r\nSafety Grade: S2\r\nMax Throughput: 150 wph";

            return common + "\r\n[상세 스펙]\r\n" + detail;
        }

        // =====================================================================
        // GetGuide
        //  - 장비 종류(category)에 따라 작업 시 주의사항 + 사용 방법 제공
        //  - 종류별 작업 환경이 완전히 다르기 때문에 필수 기능
        // =====================================================================
        private string GetGuide(string name, string category)
        {
            if (category.Contains("세정"))
                return "[주의사항]\r\n1. 산(Acid) 취급 시 보호구 착용\r\n2. DI Water 저항값 확인\r\n3. 도어 개방 시 센서 확인\r\n\r\n[사용방법]\r\n1. Cassette Loading\r\n2. Recipe 선택\r\n3. Start 실행";

            if (category.Contains("노광"))
                return "[주의사항]\r\n1. Yellow Room 내 작업\r\n2. Mask 오염 주의\r\n3. 노광 조건 확인\r\n\r\n[사용방법]\r\n1. Mask Loading\r\n2. Wafer 정렬\r\n3. Exposure 실행";

            if (category.Contains("식각"))
                return "[주의사항]\r\n1. 가스 누출 주의\r\n2. RF Power 접근 금지\r\n3. 공정 후 클리닝\r\n\r\n[사용방법]\r\n1. 진공 확인\r\n2. Gas Flow 안정화\r\n3. Plasma 점화";

            if (category.Contains("증착"))
                return "[주의사항]\r\n1. 고온 위험\r\n2. 전구체 독성 주의\r\n3. 진공도 확인\r\n\r\n[사용방법]\r\n1. Heater 설정\r\n2. Source 확인\r\n3. Deposition 실행";

            return "[공통]\r\n1. 사용 전 로그북 기록\r\n2. 알람 발생 시 즉시 관리자 호출\r\n3. 사용 후 장비 청소\r\n4. 정기 점검 일정 확인";
        }

        // =====================================================================
        // LoadImage
        //  - 선택된 장비 종류(category)에 맞는 이미지를 PictureBox에 표시
        //  - 이미지 파일 잠김 방지를 위해 기존 Image는 반드시 Dispose() 처리
        // =====================================================================
        private void LoadImage(string category)
        {
            string imageName = "";

            if (category.Contains("세정")) imageName = "Cleaning.png";
            else if (category.Contains("노광")) imageName = "Lithography.png";
            else if (category.Contains("식각")) imageName = "Etching.png";
            else if (category.Contains("증착")) imageName = "Deposition.png";
            else if (category.Contains("열처리")) imageName = "Furnace.png";
            else if (category.Contains("이온")) imageName = "IonImplant.png";
            else if (category.Contains("연마")) imageName = "CMP.png";

            string folderPath = Path.Combine(Application.StartupPath, "Images");
            string fullPath = Path.Combine(folderPath, imageName);

            // 기존 이미지가 있으면 먼저 제거해야 파일 잠김이 풀림
            if (pbEquipImage.Image != null)
            {
                var old = pbEquipImage.Image;
                pbEquipImage.Image = null;
                old.Dispose();
            }

            // 이미지 파일이 실제 존재하면 로드
            if (File.Exists(fullPath))
            {
                using (FileStream fs = new FileStream(fullPath, FileMode.Open, FileAccess.Read))
                {
                    pbEquipImage.Image = Image.FromStream(fs);
                }
            }
        }

        // =====================================================================
        // 검색 버튼
        //  - 키워드를 포함한 장비만 조회하여 목록 표시
        //  - Repository.SelectByKeyword()로 실제 DB 검색 수행
        // =====================================================================
        private void btnSearch_Click(object sender, EventArgs e)
        {
            string keyword = txtSearch.Text.Trim();

            if (string.IsNullOrEmpty(keyword))
            {
                MessageBox.Show("검색어를 입력하세요.");
                return;
            }

            try
            {
                lvEquip.Items.Clear();

                var list = _repo.SelectByKeyword(keyword);

                foreach (var equip in list)
                {
                    ListViewItem item = new ListViewItem(equip.ToListViewItem());

                    if (equip.Status == "고장")
                        item.BackColor = Color.LightCoral;
                    else if (equip.Status == "대여중")
                        item.BackColor = Color.LightGoldenrodYellow;

                    lvEquip.Items.Add(item);
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show("검색 중 오류 발생: " + ex.Message);
            }
        }

        // =====================================================================
        // 초기화 버튼
        //  - 검색 상태를 원래대로 되돌림 (검색어 삭제 + 전체 목록 다시 로딩)
        // =====================================================================
        private void btnReset_Click(object sender, EventArgs e)
        {
            txtSearch.Text = "";
            LoadEquipmentList();
        }

        // =====================================================================
        // 장비 등록 버튼
        //  - 신규 장비 입력 창을 열고, 저장 성공 시 목록과 이력을 갱신
        // =====================================================================
        private void btnRegister_Click(object sender, EventArgs e)
        {
            using (EquipmentRegistrationForm form = new EquipmentRegistrationForm())
            {
                if (form.ShowDialog(this) != DialogResult.OK)
                    return;

                try
                {
                    _repo.AddEquipment(form.EquipmentName, form.EquipmentCategory);
                    _historyRepo.AddLog("장비등록", "관리자", form.EquipmentName);

                    txtSearch.Text = "";
                    LoadEquipmentList();
                    SelectEquipment(form.EquipmentName);

                    MessageBox.Show("장비가 등록되었습니다.", "등록 완료");
                }
                catch (Exception ex)
                {
                    MessageBox.Show("장비 등록 실패: " + ex.Message, "오류");
                }
            }
        }

        // =====================================================================
        // 장비 삭제 버튼
        //  - 목록에서 선택한 장비를 삭제하고, 삭제 이력을 남긴다.
        //  - 대여중 장비는 반납 절차가 먼저 필요하므로 삭제를 막는다.
        // =====================================================================
        private void btnDelete_Click(object sender, EventArgs e)
        {
            if (lvEquip.SelectedItems.Count == 0)
            {
                MessageBox.Show("삭제할 장비를 목록에서 선택하세요.", "선택 확인");
                return;
            }

            string equipmentName = lvEquip.SelectedItems[0].Text;
            string status = lvEquip.SelectedItems[0].SubItems[2].Text;

            if (status == "대여중")
            {
                MessageBox.Show("대여중인 장비는 반납 처리 후 삭제할 수 있습니다.", "삭제 불가");
                return;
            }

            DialogResult result = MessageBox.Show(
                $"'{equipmentName}' 장비를 삭제하시겠습니까?\r\n삭제 후 장비 목록에서는 사라지고, 기존 이력은 남습니다.",
                "장비 삭제 확인",
                MessageBoxButtons.YesNo,
                MessageBoxIcon.Warning);

            if (result != DialogResult.Yes)
                return;

            try
            {
                _repo.DeleteEquipment(equipmentName);
                _historyRepo.AddLog("장비삭제", "관리자", equipmentName);

                txtSearch.Text = "";
                LoadEquipmentList();
                ResetSelectedEquipment();

                MessageBox.Show("장비가 삭제되었습니다.", "삭제 완료");
            }
            catch (Exception ex)
            {
                MessageBox.Show("장비 삭제 실패: " + ex.Message, "오류");
            }
        }

        private void SelectEquipment(string equipmentName)
        {
            foreach (ListViewItem item in lvEquip.Items)
            {
                if (item.Text == equipmentName)
                {
                    item.Selected = true;
                    item.EnsureVisible();
                    lvEquip.Focus();
                    return;
                }
            }
        }
    }
}
