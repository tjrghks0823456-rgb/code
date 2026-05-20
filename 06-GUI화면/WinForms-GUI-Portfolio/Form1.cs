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
    public partial class Form1 : Form
    {
        public Form1()
        {
            InitializeComponent();
        }

    

       
        private void textBox1_KeyDown(object sender, KeyEventArgs e)
        {
            if (e.KeyCode == Keys.Enter)
            {
                richTextBox1.AppendText(textBox1.Text);
                textBox1.Clear();
            }
        }

        private void textBox1_TextChanged(object sender, EventArgs e)
        {
            richTextBox1.AppendText(textBox1.Text);
            textBox1.Clear();
        }

        private void button1_Click(object sender, EventArgs e)
        {
            richTextBox1.AppendText(textBox1.Text + "\n");
            textBox1.Clear();
        }

        private void button2_Click(object sender, EventArgs e)
        {
            richTextBox1.Clear();
        }

        private void button3_Click(object sender, EventArgs e)
        {
            if (textBox2.Text.Equals("aaa") && textBox3.Text.Equals("1111"))
                MessageBox.Show("환영합니다. 로그인 성공!!");
            else
                MessageBox.Show("정보가 일치하지 않습니다. 로그인 실패!!");
        }
    }
}
