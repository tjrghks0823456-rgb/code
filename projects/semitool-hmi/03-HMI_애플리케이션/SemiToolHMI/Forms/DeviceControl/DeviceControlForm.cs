using System;
using System.Drawing;
using System.Threading.Tasks;
using System.Windows.Forms;
using IEG3268_Dll;

namespace SemiToolHMI
{
    public partial class DeviceControlForm : Form
    {
        // ---------------------------------------------------------
        //  IEG3268 EtherCAT 모션 컨트롤러 (공용 객체 사용)
        // ---------------------------------------------------------
        private IEG3268 EtherCAT_M => EthercatMotion.EtherCAT_M;

        // 전진 상태에서 허용하는 하강/상승 범위(펄스)
        private readonly long safeRangePulse = 80000;

        // ★ SafeLift 기준 위치 기억용
        private bool lastCylinderForward = false;
        private long forwardRefPos = 0;

        public DeviceControlForm()
        {
            InitializeComponent();
        }

        // ====== Form Load =====================================================
        private void Form1_Load(object sender, EventArgs e)
        {
            // ★ 공용 EtherCAT 연결 사용
            if (EthercatMotion.EnsureConnected())
            {
                label2.Text = "OK";

                // ReadData 타이머는 EthercatMotion 쪽에서 돌고 있다고 가정
                // 여기서는 화면 업데이트용 타이머만 사용
                timer1.Interval = 300;
                timer1.Start();
            }
            else
            {
                label2.Text = "NG";
            }

            // 다크 테마 적용
            ApplyDarkTheme();
        }

        // ======================================================================
        // UI 스타일 통합
        // ======================================================================
        private void ApplyDarkTheme()
        {
            BackColor = Color.FromArgb(28, 30, 38);
            Font = new Font("Malgun Gothic", 9F, FontStyle.Regular);

            foreach (Control ctrl in Controls)
                ApplyControlStyle(ctrl);
        }

        private void ApplyControlStyle(Control ctrl)
        {
            if (ctrl is GroupBox gb)
            {
                gb.BackColor = Color.FromArgb(40, 42, 52);
                gb.ForeColor = Color.White;
                gb.Font = new Font("Malgun Gothic", 10F, FontStyle.Bold);
            }
            else if (ctrl is Label lbl)
            {
                lbl.ForeColor = Color.White;
                lbl.BackColor = Color.Transparent;
                lbl.Font = new Font("Malgun Gothic", 9F);
            }
            else if (ctrl is Button btn)
            {
                btn.FlatStyle = FlatStyle.Flat;
                btn.BackColor = Color.FromArgb(58, 60, 70);
                btn.ForeColor = Color.White;
                btn.Font = new Font("Malgun Gothic", 9F, FontStyle.Bold);
                btn.FlatAppearance.BorderSize = 1;
                btn.FlatAppearance.BorderColor = Color.FromArgb(90, 90, 90);
            }
            else if (ctrl is NumericUpDown nud)
            {
                nud.BackColor = Color.FromArgb(48, 50, 58);
                nud.ForeColor = Color.White;
                nud.BorderStyle = BorderStyle.FixedSingle;
            }
            else if (ctrl is Panel pnl)
            {
                pnl.BackColor = Color.FromArgb(28, 30, 38);
            }

            foreach (Control child in ctrl.Controls)
                ApplyControlStyle(child);
        }

        // ======================================================================
        // 상태 업데이트 타이머
        // ======================================================================
        private string OnOff(bool v) => v ? "ON" : "OFF";

        private void timer1_Tick(object sender, EventArgs e)
        {
            if (!EthercatMotion.IsConnected)
                return;

            // 축 위치/상태
            label28.Text = EtherCAT_M.Axis1_is_PosData();                  // UD pos
            label26.Text = EtherCAT_M.Axis1_Status("PP_M").ToString();
            label22.Text = EtherCAT_M.Axis1_Status("HOME_M").ToString();
            label24.Text = EtherCAT_M.Axis1_Status("PP_D").ToString();
            label15.Text = EtherCAT_M.Axis1_Status("HOME_D").ToString();

            label3.Text = EtherCAT_M.Axis2_is_PosData();                   // LR pos
            label8.Text = EtherCAT_M.Axis2_Status("PP_M").ToString();
            label13.Text = EtherCAT_M.Axis2_Status("HOME_M").ToString();
            label10.Text = EtherCAT_M.Axis2_Status("PP_D").ToString();
            label11.Text = EtherCAT_M.Axis2_Status("HOME_D").ToString();

            // DI → 라벨 표시
            bool di0 = EtherCAT_M.Digital_Input(0);
            bool di1 = EtherCAT_M.Digital_Input(1);
            bool di2 = EtherCAT_M.Digital_Input(2);
            bool di3 = EtherCAT_M.Digital_Input(3);
            bool di5 = EtherCAT_M.Digital_Input(5);
            bool di6 = EtherCAT_M.Digital_Input(6);
            bool di7 = EtherCAT_M.Digital_Input(7);
            bool di8 = EtherCAT_M.Digital_Input(8);
            bool di9 = EtherCAT_M.Digital_Input(9);
            bool di10 = EtherCAT_M.Digital_Input(10);
            bool di11 = EtherCAT_M.Digital_Input(11);
            bool di12 = EtherCAT_M.Digital_Input(12);
            bool di13 = EtherCAT_M.Digital_Input(13);

            // other input 그룹
            label31.Text = OnOff(di0);
            label33.Text = OnOff(di1);
            label35.Text = OnOff(di2);
            label37.Text = OnOff(di3);
            label38.Text = OnOff(di5);

            // A/B/C 도어, 실린더 등
            label45.Text = OnOff(di6);
            label46.Text = OnOff(di7);
            label43.Text = OnOff(di8);
            label44.Text = OnOff(di9);
            label41.Text = OnOff(di10);
            label42.Text = OnOff(di11);
            label40.Text = OnOff(di12);
            label39.Text = OnOff(di13);

            // ★ SafeLift 기준 위치 갱신 (전진으로 바뀌는 순간 캡처)
            UpdateSafeLiftReference(di13);
        }

        // ★ 실린더 전진 여부
        private bool IsCylinderForward()
        {
            // DI13: 실린더 전진 상태라고 가정
            return EtherCAT_M.Digital_Input(13);
        }

        // ★ 전진으로 바뀌는 순간, 현재 Z(UD) 위치를 기준 위치로 기억
        private void UpdateSafeLiftReference(bool currentForward)
        {
            if (currentForward && !lastCylinderForward)
            {
                // label28: Axis1(UD) 현재 위치 문자열
                if (!long.TryParse(label28.Text, out forwardRefPos))
                    forwardRefPos = 0;
            }

            lastCylinderForward = currentForward;
        }

        // ★ SafeLift 체크: 실린더 전진 상태에서 UD 타겟이 기준 ±safeRangePulse 안인지 확인
        private bool CheckSafeUDMove(long targetPos)
        {
            if (!IsCylinderForward())
                return true;    // 후진 상태면 제한 없음

            long diff = targetPos - forwardRefPos;
            if (Math.Abs(diff) <= safeRangePulse)
                return true;

            MessageBox.Show(
                $"실린더 전진 상태에서는 기준 위치 ±{safeRangePulse} pulse만 허용됩니다.\r\n" +
                $"기준 위치: {forwardRefPos}, 요청 위치: {targetPos}",
                "SafeLift 보호",
                MessageBoxButtons.OK,
                MessageBoxIcon.Warning);

            return false;
        }

        // ======================================================================
        // 기존 JOG / HOMING / FREE MOVE / DO 제어
        // ======================================================================
        private void button1_Click(object sender, EventArgs e)
        {
            EtherCAT_M.Axis1_UD_Config_Update(
                (long)numericUpDown3.Value,
                (long)numericUpDown4.Value,
                (long)numericUpDown5.Value,
                (long)numericUpDown6.Value);

            EtherCAT_M.Axis2_LR_Config_Update(
                (long)numericUpDown3.Value,
                (long)numericUpDown4.Value,
                (long)numericUpDown5.Value,
                (long)numericUpDown6.Value);
        }

        private void button3_Click(object sender, EventArgs e)
        {
            EtherCAT_M.Axis1_ON();
            EtherCAT_M.Axis2_ON();

            // ★ 시나리오용 ServoOn 플래그 ON
            RobotScenario.ServoOn = true;
        }

        private void button4_Click(object sender, EventArgs e)
        {
            EtherCAT_M.Axis1_OFF();
            EtherCAT_M.Axis2_OFF();

            // ★ 시나리오용 ServoOn 플래그 OFF
            RobotScenario.ServoOn = false;
        }

        // === LR JOG +X ========================================================
        private void button6_Click(object sender, EventArgs e)
        {
            if (!IsCylinderForward())
            {
                long ingpos = long.Parse(label3.Text);
                long pos = ingpos + (long)numericUpDown1.Value;

                EtherCAT_M.Axis2_LR_POS_Update(pos);
                EtherCAT_M.Axis2_LR_Move_Send();
            }
            else
            {
                MessageBox.Show("웨이퍼 이송 실린더가 전진되어 있습니다.\r\n후진해주세요.");
            }
        }

        // === LR JOG -X ========================================================
        private void button7_Click(object sender, EventArgs e)
        {
            if (!IsCylinderForward())
            {
                long ingpos = long.Parse(label3.Text);
                long pos = ingpos - (long)numericUpDown1.Value;

                EtherCAT_M.Axis2_LR_POS_Update(pos);
                EtherCAT_M.Axis2_LR_Move_Send();
            }
            else
            {
                MessageBox.Show("웨이퍼 이송 실린더가 전진되어 있습니다.\r\n후진해주세요.");
            }
        }

        // === UD JOG +Z (상승) – SafeLift 적용 =================================
        private void button9_Click(object sender, EventArgs e)
        {
            long ingpos = long.Parse(label28.Text);
            long pos = ingpos + (long)numericUpDown1.Value;

            // ★ SafeLift 체크
            if (!CheckSafeUDMove(pos))
                return;

            EtherCAT_M.Axis1_UD_POS_Update(pos);
            EtherCAT_M.Axis1_UD_Move_Send();
        }

        // === UD JOG -Z (하강) – SafeLift + 0 이하 방지 =========================
        private void button10_Click(object sender, EventArgs e)
        {
            long ingpos = long.Parse(label28.Text);
            long move = (long)numericUpDown1.Value;
            long target = ingpos - move;

            if (target <= 0)
            {
                MessageBox.Show("0 이하로 하강 불가!");
                return;
            }

            // ★ SafeLift 체크
            if (!CheckSafeUDMove(target))
                return;

            EtherCAT_M.Axis1_UD_POS_Update(target);
            EtherCAT_M.Axis1_UD_Move_Send();
        }

        private void button5_Click(object sender, EventArgs e)
        {
            if (!IsCylinderForward())
                EtherCAT_M.Axis1_UD_Homming();
            else
                MessageBox.Show("웨이퍼 이송 실린더가 전진되어 있습니다.\r\n후진해주세요.");
        }

        private void button8_Click(object sender, EventArgs e)
        {
            if (!IsCylinderForward())
                EtherCAT_M.Axis2_LR_Homming();
            else
                MessageBox.Show("웨이퍼 이송 실린더가 전진되어 있습니다.\r\n후진해주세요.");
        }

        // === UD 절대 위치 이동 – SafeLift 적용 =================================
        private void button2_Click(object sender, EventArgs e)
        {
            long target = (long)numericUpDown7.Value;

            if (target <= 0)
            {
                MessageBox.Show("0 이하로 하강 불가!");
                return;
            }

            // ★ SafeLift 체크
            if (!CheckSafeUDMove(target))
                return;

            EtherCAT_M.Axis1_UD_POS_Update(target);
            EtherCAT_M.Axis1_UD_Move_Send();
        }

        // === LR 절대 위치 이동 (실린더 전진 시에는 여전히 금지) ================
        private void button11_Click(object sender, EventArgs e)
        {
            if (!IsCylinderForward())
            {
                EtherCAT_M.Axis2_LR_POS_Update((long)numericUpDown7.Value);
                EtherCAT_M.Axis2_LR_Move_Send();
            }
            else
            {
                MessageBox.Show("웨이퍼 이송 실린더가 전진되어 있습니다.\r\n후진해주세요.");
            }
        }

        // Digital Output (수동 제어용 버튼들 그대로 유지)
        private void button34_Click(object sender, EventArgs e) => EtherCAT_M.Digital_Output(0, true);
        private void button35_Click(object sender, EventArgs e) => EtherCAT_M.Digital_Output(0, false);
        private void button32_Click(object sender, EventArgs e) => EtherCAT_M.Digital_Output(1, true);
        private void button33_Click(object sender, EventArgs e) => EtherCAT_M.Digital_Output(1, false);
        private void button30_Click(object sender, EventArgs e) => EtherCAT_M.Digital_Output(2, true);
        private void button31_Click(object sender, EventArgs e) => EtherCAT_M.Digital_Output(2, false);
        private void button28_Click(object sender, EventArgs e) => EtherCAT_M.Digital_Output(3, true);
        private void button29_Click(object sender, EventArgs e) => EtherCAT_M.Digital_Output(3, false);
        private void button14_Click(object sender, EventArgs e) { EtherCAT_M.Digital_Output(5, false); EtherCAT_M.Digital_Output(4, true); }
        private void button25_Click(object sender, EventArgs e) { EtherCAT_M.Digital_Output(4, false); EtherCAT_M.Digital_Output(5, true); }
        private void button26_Click(object sender, EventArgs e) => EtherCAT_M.Digital_Output(6, true);
        private void button27_Click(object sender, EventArgs e) => EtherCAT_M.Digital_Output(6, false);
        private void button12_Click(object sender, EventArgs e) { EtherCAT_M.Digital_Output(8, false); EtherCAT_M.Digital_Output(7, true); }
        private void button13_Click(object sender, EventArgs e) { EtherCAT_M.Digital_Output(7, false); EtherCAT_M.Digital_Output(8, true); }
        private void button17_Click(object sender, EventArgs e) => EtherCAT_M.Digital_Output(9, true);
        private void button18_Click(object sender, EventArgs e) => EtherCAT_M.Digital_Output(9, false);
        private void button15_Click(object sender, EventArgs e) { EtherCAT_M.Digital_Output(11, false); EtherCAT_M.Digital_Output(10, true); }
        private void button16_Click(object sender, EventArgs e) { EtherCAT_M.Digital_Output(10, false); EtherCAT_M.Digital_Output(11, true); }
        private void button19_Click(object sender, EventArgs e) { EtherCAT_M.Digital_Output(13, false); EtherCAT_M.Digital_Output(12, true); }
        private void button20_Click(object sender, EventArgs e) { EtherCAT_M.Digital_Output(12, false); EtherCAT_M.Digital_Output(13, true); }
        private void button21_Click(object sender, EventArgs e) => EtherCAT_M.Digital_Output(14, true);
        private void button23_Click(object sender, EventArgs e) => EtherCAT_M.Digital_Output(14, false);
        private void button22_Click(object sender, EventArgs e) => EtherCAT_M.Digital_Output(15, true);
        private void button24_Click(object sender, EventArgs e) => EtherCAT_M.Digital_Output(15, false);

        // ======================================================================
        // 공정 시나리오 실행 (이 폼에서는 단순히 RobotScenario 호출)
        // ======================================================================
        private async void btnScenario_Click(object sender, EventArgs e)
        {
            if (!EthercatMotion.IsConnected)
            {
                MessageBox.Show("EtherCAT 연결이 되어 있지 않습니다.");
                return;
            }

            // ★ 서보 ON은 이제 수동 제어 (별도 버튼에서 Axis1_ON / Axis2_ON 눌러야 함)
            // RobotScenario.RunAsync 내에서 ServoOn 플래그를 보고 판단

            btnScenario.Enabled = false;
            try
            {
                await RobotScenario.RunAsync();
            }
            finally
            {
                btnScenario.Enabled = true;
            }
        }
    }
}
