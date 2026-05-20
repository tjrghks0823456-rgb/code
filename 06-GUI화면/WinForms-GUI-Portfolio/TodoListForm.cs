using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace GUI1
{
    public partial class TodoListForm : Form
    {
        public TodoListForm()
        {
            InitializeComponent();
        }

        private void textBox1_KeyDown(object sender, KeyEventArgs e)
        {
            if (e.KeyCode == Keys.Enter)
            {
                if (string.IsNullOrWhiteSpace(inputArea.Text))
                    return;

                listToDo.Items.Add(inputArea.Text);
                inputArea.Clear();
                e.SuppressKeyPress = true;

            }
        }

        private void button1_Click(object sender, EventArgs e)
        {
            if (listToDo.SelectedIndex >= 0 && !string.IsNullOrWhiteSpace(inputArea.Text))
            {
                int idx = listToDo.SelectedIndex;
                listToDo.Items[idx] = inputArea.Text;
                inputArea.Clear();
            }
            else            
                MessageBox.Show("수정할 항목을 선택한 후 수정할 내용을 입력해주세요!!");
            
        }

        private void button2_Click(object sender, EventArgs e)
        {
            if (listToDo.SelectedIndex >= 0)
                listToDo.Items.RemoveAt(listToDo.SelectedIndex);           
            else
                MessageBox.Show("삭제할 항목을 선택한 후 삭제하세요!!");
        }

        private void button3_Click(object sender, EventArgs e)  //불러오기
        {
            // SaveFileDialog;
            //OpenFileDialog;
            // StreamWriter;
            //StreamReader;  ==> using 블록
            using (OpenFileDialog dlg = new OpenFileDialog())
            {
                dlg.Filter = "텍스트 파일(*.txt)|*.txt";
                dlg.Title = "저장된toDoList불러오기";
                dlg.InitialDirectory = @"D:\GuI손석환";
                if (dlg.ShowDialog() == DialogResult.OK)
                {
                    using (StreamReader sw = new StreamReader(dlg.FileName))
                    {
                        string str;
                        listToDo.Items.Clear();
                        while ((str = sw.ReadLine()) != null)
                            listToDo.Items.Add(str);
                    }
                    MessageBox.Show("파일을 불러왔어!!");

                }
            }
        }

        private void button4_Click(object sender, EventArgs e)  //저장
        {
            using (SaveFileDialog dlg = new SaveFileDialog())
            {
                dlg.Filter = "텍스트 파일(*.txt)|*.txt";
                dlg.Title = "toDoList에 저장";
                dlg.InitialDirectory= @"D:\GuI손석환";

                if (dlg.ShowDialog() == DialogResult.OK)
                {
                    using (StreamWriter sw =  new StreamWriter(dlg.FileName))
                    {
                        foreach (var item in listToDo.Items)
                            sw.WriteLine(item.ToString());
                    }
                    MessageBox.Show("파일에 해야 할 일이 모두 저장되었어!!");
                }

            }
        }
    }
}
