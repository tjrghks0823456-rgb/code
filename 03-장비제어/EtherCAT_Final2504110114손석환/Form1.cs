using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Reflection.Emit;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using System.Windows.Forms;
using IEG3268_Dll;

namespace WindowsFormsApp1
{
    public partial class Form1 : Form
    {
        IEG3268 EtherCAT_M = new IEG3268();

        private Int64 safeRangePulse = 80000;   // 전진 상태에서 10mm 정도만 조작 가능

        public Form1()
        {
            InitializeComponent();
        }

        private void Form1_Load(object sender, EventArgs e)
        {
            if (EtherCAT_M.CIFX_50RE_Connect() == true)
            {
                label2.Text = "OK";
                EtherCAT_M.ReadData_Send_Start(300);//Timer interval Set
                EtherCAT_M.ReadData_Timer_Start();//Timer Start

                timer1.Interval = 300;
                timer1.Start();
            }
            else
            {
                label2.Text = "NG";
            }
        }

        private void button1_Click(object sender, EventArgs e)
        {
            //Axis Parameter Update
            EtherCAT_M.Axis1_UD_Config_Update((Int64)numericUpDown3.Value, (Int64)numericUpDown4.Value, (Int64)numericUpDown5.Value, (Int64)numericUpDown6.Value);
            EtherCAT_M.Axis2_LR_Config_Update((Int64)numericUpDown3.Value, (Int64)numericUpDown4.Value, (Int64)numericUpDown5.Value, (Int64)numericUpDown6.Value);
        }

        private void button3_Click(object sender, EventArgs e)
        {
            EtherCAT_M.Axis1_ON();
            EtherCAT_M.Axis2_ON();
        }

        private void button4_Click(object sender, EventArgs e)
        {
            EtherCAT_M.Axis1_OFF();
            EtherCAT_M.Axis2_OFF();
        }

        private void timer1_Tick(object sender, EventArgs e)
        {
            if (label2.Text == "OK")
            {
                label28.Text = EtherCAT_M.Axis1_is_PosData(); //POS
                label26.Text = EtherCAT_M.Axis1_Status("PP_M").ToString();
                label22.Text = EtherCAT_M.Axis1_Status("HOME_M").ToString();
                label24.Text = EtherCAT_M.Axis1_Status("PP_D").ToString();
                label15.Text = EtherCAT_M.Axis1_Status("HOME_D").ToString();

                label3.Text = EtherCAT_M.Axis2_is_PosData(); //POS
                label8.Text = EtherCAT_M.Axis2_Status("PP_M").ToString();
                label13.Text = EtherCAT_M.Axis2_Status("HOME_M").ToString();
                label10.Text = EtherCAT_M.Axis2_Status("PP_D").ToString();
                label11.Text = EtherCAT_M.Axis2_Status("HOME_D").ToString();

                label31.Text = EtherCAT_M.Digital_Input(0).ToString();
                label33.Text = EtherCAT_M.Digital_Input(1).ToString();
                label35.Text = EtherCAT_M.Digital_Input(2).ToString();
                label37.Text = EtherCAT_M.Digital_Input(3).ToString();

                label38.Text = EtherCAT_M.Digital_Input(5).ToString();

                label45.Text = EtherCAT_M.Digital_Input(6).ToString();
                label46.Text = EtherCAT_M.Digital_Input(7).ToString();

                label43.Text = EtherCAT_M.Digital_Input(8).ToString();
                label44.Text = EtherCAT_M.Digital_Input(9).ToString();

                label41.Text = EtherCAT_M.Digital_Input(10).ToString();
                label42.Text = EtherCAT_M.Digital_Input(11).ToString();

                label40.Text = EtherCAT_M.Digital_Input(12).ToString();
                label39.Text = EtherCAT_M.Digital_Input(13).ToString();
            }
        }
        private bool IsCylinderForward()
        {
            return (label39.Text == "True" || label39.Text == "1");
        }


        // JOG 왼쪽(<-) 이동
        private void button6_Click(object sender, EventArgs e)
        {
            if (label39.Text == "False")
            {
                Int64 ingpos = Int64.Parse(label3.Text);
                Int64 pos = ingpos + Convert.ToInt64(numericUpDown1.Value);

                EtherCAT_M.Axis2_LR_POS_Update(pos);
                EtherCAT_M.Axis2_LR_Move_Send();
            }
            else
            {
                MessageBox.Show("웨이퍼 이송 실린더가 전진되어 있습니다. " + "\r\n" + "웨이퍼 이송 실린더를 후진해주세요");
            }
        }

        // JOG 오른쪽(->) 이동
        private void button7_Click(object sender, EventArgs e)
        {
            if (label39.Text == "False")
            {
                Int64 ingpos = Int64.Parse(label3.Text);
                Int64 pos = ingpos - Convert.ToInt64(numericUpDown1.Value);

                EtherCAT_M.Axis2_LR_POS_Update(pos);
                EtherCAT_M.Axis2_LR_Move_Send();
            }
            else
            {
                MessageBox.Show("웨이퍼 이송 실린더가 전진되어 있습니다. " + "\r\n" + "웨이퍼 이송 실린더를 후진해주세요");
            }
        }

        // JOG UP 이동
        private void button9_Click(object sender, EventArgs e)
        {
            if (label39.Text == "False")
            {
                Int64 ingpos = Int64.Parse(label28.Text);
                Int64 pos = ingpos + Convert.ToInt64(numericUpDown1.Value);

                EtherCAT_M.Axis1_UD_POS_Update(pos);
                EtherCAT_M.Axis1_UD_Move_Send();
            }
            else
            {
                MessageBox.Show("웨이퍼 이송 실린더가 전진되어 있습니다. " + "\r\n" + "웨이퍼 이송 실린더를 후진해주세요");
            }
        }

        // JOG Down 이동
        private void button10_Click(object sender, EventArgs e)
        {
            Int64 ingpos = Int64.Parse(label28.Text);
            Int64 move = Convert.ToInt64(numericUpDown1.Value);
            Int64 target = ingpos - move;

            // ★ 전진 상태: 너무 아래로 내려가는 것만 제한
            if (IsCylinderForward() && target < ingpos - safeRangePulse)
            {
                MessageBox.Show("전진 상태에서는 제한 범위 이상 하강할 수 없습니다.");
                return;
            }

            // ★ 0 이하 하강 금지 (기본 보호)
            if (target <= 0)
            {
                MessageBox.Show("0 이하로 하강 불가!");
                return;
            }

            EtherCAT_M.Axis1_UD_POS_Update(target);
            EtherCAT_M.Axis1_UD_Move_Send();
        }


        // 상/하 원점 복귀
        private void button5_Click(object sender, EventArgs e)
        {
            if (label39.Text == "False")
            {
                EtherCAT_M.Axis1_UD_Homming();
            }
            else
            {
                MessageBox.Show("웨이퍼 이송 실린더가 전진되어 있습니다. " + "\r\n" + "웨이퍼 이송 실린더를 후진해주세요");
            }
        }

        // 왼쪽/오른쪽 원점 복귀
        private void button8_Click(object sender, EventArgs e)
        {
            if (label39.Text == "False")
            {
                EtherCAT_M.Axis2_LR_Homming();
            }
            else
            {
                MessageBox.Show("웨이퍼 이송 실린더가 전진되어 있습니다. " + "\r\n" + "웨이퍼 이송 실린더를 후진해주세요");
            }
        }

        private void button2_Click(object sender, EventArgs e)
        {
            Int64 ingpos = Int64.Parse(label28.Text);
            Int64 target = (Int64)numericUpDown7.Value;

            // ★ 전진 상태: 지정 위치가 +safeRangePulse 초과하면 금지 (너무 많이 올리면 위험)
            if (IsCylinderForward() && target > ingpos + safeRangePulse)
            {
                MessageBox.Show("전진 상태에서는 제한 범위 이상 상승할 수 없습니다.");
                return;
            }

            // ★ 전진 상태에서 '하강만' 금지 (상승은 허용)
            if (IsCylinderForward() && target < ingpos)
            {
                MessageBox.Show("전진 상태에서는 하강할 수 없습니다.");
                return;
            }

            // ★ 바닥 안전 조건 (전진/후진 관계 없이)
            if (target <= 0)
            {
                MessageBox.Show("0 이하로 하강할 수 없습니다.");
                return;
            }

            // ★ 정상 이동
            EtherCAT_M.Axis1_UD_POS_Update(target);
            EtherCAT_M.Axis1_UD_Move_Send();
        }


        private void button11_Click(object sender, EventArgs e)
        {
            if (label39.Text == "False")
            {
                EtherCAT_M.Axis2_LR_POS_Update((Int64)numericUpDown7.Value);
                EtherCAT_M.Axis2_LR_Move_Send();
            }
            else
            {
                MessageBox.Show("웨이퍼 이송 실린더가 전진되어 있습니다. " + "\r\n" + "웨이퍼 이송 실린더를 후진해주세요");
            }
        }

        private void button34_Click(object sender, EventArgs e)
        {
            EtherCAT_M.Digital_Output(0, true);
        }

        private void button35_Click(object sender, EventArgs e)
        {
            EtherCAT_M.Digital_Output(0, false);
        }

        private void button32_Click(object sender, EventArgs e)
        {
            EtherCAT_M.Digital_Output(1, true);
        }

        private void button33_Click(object sender, EventArgs e)
        {
            EtherCAT_M.Digital_Output(1, false);
        }

        private void button30_Click(object sender, EventArgs e)
        {
            EtherCAT_M.Digital_Output(2, true);
        }

        private void button31_Click(object sender, EventArgs e)
        {
            EtherCAT_M.Digital_Output(2, false);
        }
        private void button28_Click(object sender, EventArgs e)
        {
            EtherCAT_M.Digital_Output(3, true);
        }

        private void button29_Click(object sender, EventArgs e)
        {
            EtherCAT_M.Digital_Output(3, false);
        }

        private void button14_Click(object sender, EventArgs e)
        {
            EtherCAT_M.Digital_Output(5, false);
            EtherCAT_M.Digital_Output(4, true);
        }

        private void button25_Click(object sender, EventArgs e)
        {
            EtherCAT_M.Digital_Output(4, false);
            EtherCAT_M.Digital_Output(5, true);
        }

        private void button26_Click(object sender, EventArgs e)
        {
            EtherCAT_M.Digital_Output(6, true);
        }

        private void button27_Click(object sender, EventArgs e)
        {
            EtherCAT_M.Digital_Output(6, false);
        }

        private void button12_Click(object sender, EventArgs e)
        {
            EtherCAT_M.Digital_Output(8, false);
            EtherCAT_M.Digital_Output(7, true);
        }

        private void button13_Click(object sender, EventArgs e)
        {
            EtherCAT_M.Digital_Output(7, false);
            EtherCAT_M.Digital_Output(8, true);
        }

        private void button17_Click(object sender, EventArgs e)
        {
            EtherCAT_M.Digital_Output(9, true);
        }

        private void button18_Click(object sender, EventArgs e)
        {
            EtherCAT_M.Digital_Output(9, false);
        }

        private void button15_Click(object sender, EventArgs e)
        {
            EtherCAT_M.Digital_Output(11, false);
            EtherCAT_M.Digital_Output(10, true);
        }

        private void button16_Click(object sender, EventArgs e)
        {
            EtherCAT_M.Digital_Output(10, false);
            EtherCAT_M.Digital_Output(11, true);
        }

        private void button19_Click(object sender, EventArgs e)
        {
            EtherCAT_M.Digital_Output(13, false);
            EtherCAT_M.Digital_Output(12, true);
        }

        private void button20_Click(object sender, EventArgs e)
        {
            EtherCAT_M.Digital_Output(12, false);
            EtherCAT_M.Digital_Output(13, true);
        }

        private void button21_Click(object sender, EventArgs e)
        {            
            EtherCAT_M.Digital_Output(14, true);
        }

        private void button23_Click(object sender, EventArgs e)
        {
            EtherCAT_M.Digital_Output(14, false);
        }

        private void button22_Click(object sender, EventArgs e)
        {
            EtherCAT_M.Digital_Output(15, true);
        }

        private void button24_Click(object sender, EventArgs e)
        {
            EtherCAT_M.Digital_Output(15, false);
        }
    }
}
