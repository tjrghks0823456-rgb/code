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
    public partial class Form3 : Form
    {
        double firstNum = 0;
        double secondNum = 0;
        string op = "";

        public Form3()
        {
            InitializeComponent();
        }

        private void opWork(Button btn)
        {
            firstNum = Double.Parse(Display.Text);
            op = btn.Text;
            Display.Text = "";
        }

        private void NumberWork(Button btn)
        {
            if(Display.Text=="0") 
                Display.Text=" ";

            Display.Text += btn.Text;
        }

        private void ButtonResult_Click(object sender, EventArgs e)
        {
            secondNum = Double.Parse(Display.Text);
            if (op == "+")
                Display.Text = (firstNum + secondNum).ToString();
            else if (op == "-")
                Display.Text = (firstNum - secondNum).ToString();
            else if (op == "×")
                Display.Text = (firstNum * secondNum).ToString();
            else if (op == "÷")
                Display.Text = (firstNum / secondNum).ToString();
        }

        private void AC_Click(object sender, EventArgs e)
        {
            firstNum = 0;
            secondNum = 0;
            op = "";
            Display.Text = "0";
        }

        private void ButtonPoint_Click(object sender, EventArgs e)
        {
            NumberWork(sender as Button);
        }

       

        private void ButtonDivide_Click(object sender, EventArgs e)
        {
            opWork(sender as Button);
        }
        private void ButtonMultiply_Click(object sender, EventArgs e)
        {
            opWork(sender as Button);
        }

        private void ButtonSubtract_Click(object sender, EventArgs e)
        {
            opWork(sender as Button);
        }

        private void ButtonAdd_Click(object sender, EventArgs e)
        {
            opWork(sender as Button);
        }

        private void ButtonSeven_Click(object sender, EventArgs e)
        {
           NumberWork(sender as Button);
        }

        private void ButtonEight_Click(object sender, EventArgs e)
        {
            NumberWork(sender as Button);
        }

        private void ButtonNine_Click(object sender, EventArgs e)
        {
            NumberWork(sender as Button);
        }


        private void ButtonFour_Click(object sender, EventArgs e)
        {
            NumberWork(sender as Button);
        }

        private void ButtonFive_Click(object sender, EventArgs e)
        {
            NumberWork(sender as Button);
        }

        private void ButtonSix_Click(object sender, EventArgs e)
        {
            NumberWork(sender as Button);
        }

        private void ButtonOne_Click(object sender, EventArgs e)
        {
            NumberWork(sender as Button);
        }

        private void ButtonTwo_Click(object sender, EventArgs e)
        {
            NumberWork(sender as Button);
        }

        private void ButtonThree_Click(object sender, EventArgs e)
        {
            NumberWork(sender as Button);
        }

        private void ButtonZero_Click(object sender, EventArgs e)
        {
            NumberWork(sender as Button);
        }

        

    }
}
