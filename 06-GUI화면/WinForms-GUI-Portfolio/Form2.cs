using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace GUI1
{
    public partial class Form2 : Form
    {

        private int num = 0;     // 생성된 숫자
        private int chance = 0;  // 시도횟수 제한


        public Form2()
        {
            InitializeComponent();
            textBox1.Enabled = false;
            button1.Enabled = false;
        }

        private void button1_Click(object sender, EventArgs e)
        {
            int inputNum = Int32.Parse(textBox1.Text);
            if (inputNum == num)
            {
                label1.Text = 11-chance  + "번 만에 맞췄습니다.";
            }
            else
            {
                chance--;
                label1.Text = "도전할 기회는 " + chance + "번 남았습니다.";
            }

            if (chance <= 0)
            {
                label1.Text = "실패했습니다~~";
                textBox1.Enabled = false;
                button1.Enabled = false;
            }
            textBox1.Clear();
        }

        private void button2_Click(object sender, EventArgs e)
        {
            textBox1.Enabled = true;
            button1.Enabled = true;
            var rand = new Random();
            num = rand.Next(1, 101);
            chance = 5;
            label1.Text = "예상하는 숫자를 입력하세요!!";
        }
    }
}
