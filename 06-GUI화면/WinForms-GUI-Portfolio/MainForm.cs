using System;
using System.Drawing;
using System.Windows.Forms;

namespace GUI1
{
    public class MainForm : Form
    {
        public MainForm()
        {
            Text = "WinForms GUI Portfolio";
            StartPosition = FormStartPosition.CenterScreen;
            ClientSize = new Size(420, 300);
            BackColor = Color.White;

            var title = new Label
            {
                Text = "WinForms GUI Portfolio",
                Dock = DockStyle.Top,
                Height = 60,
                Font = new Font("Segoe UI", 18F, FontStyle.Bold),
                TextAlign = ContentAlignment.MiddleCenter
            };

            var panel = new TableLayoutPanel
            {
                Dock = DockStyle.Fill,
                Padding = new Padding(32, 12, 32, 32),
                RowCount = 4,
                ColumnCount = 1
            };

            panel.RowStyles.Add(new RowStyle(SizeType.Percent, 25F));
            panel.RowStyles.Add(new RowStyle(SizeType.Percent, 25F));
            panel.RowStyles.Add(new RowStyle(SizeType.Percent, 25F));
            panel.RowStyles.Add(new RowStyle(SizeType.Percent, 25F));

            panel.Controls.Add(CreateButton("Text / Login Demo", () => new Form1().ShowDialog()), 0, 0);
            panel.Controls.Add(CreateButton("Number Guessing Game", () => new Form2().ShowDialog()), 0, 1);
            panel.Controls.Add(CreateButton("Calculator", () => new Form3().ShowDialog()), 0, 2);
            panel.Controls.Add(CreateButton("Todo List", () => new Form4().ShowDialog()), 0, 3);

            Controls.Add(panel);
            Controls.Add(title);
        }

        private Button CreateButton(string text, Action clickAction)
        {
            var button = new Button
            {
                Text = text,
                Dock = DockStyle.Fill,
                Margin = new Padding(0, 6, 0, 6),
                BackColor = Color.MistyRose,
                FlatStyle = FlatStyle.Flat,
                Font = new Font("Segoe UI", 11F, FontStyle.Bold)
            };

            button.FlatAppearance.BorderColor = Color.LightPink;
            button.Click += (sender, e) => clickAction();

            return button;
        }
    }
}
