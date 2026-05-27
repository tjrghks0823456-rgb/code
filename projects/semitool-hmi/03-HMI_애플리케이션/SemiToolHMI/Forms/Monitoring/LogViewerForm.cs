using System;
using System.Collections.Generic;
using System.Drawing;
using System.Windows.Forms;

namespace SemiToolHMI
{
    public partial class LogViewerForm : Form
    {
        private TabControl tabControl;
        private ListBox lstSystemLog;
        private ListBox lstErrorLog;
        private Button btnClose;

        public LogViewerForm(List<string> systemLogs, List<string> errorLogs)
        {
            InitializeComponent();
            BuildUI();
            LoadLogs(systemLogs, errorLogs);
        }

        private void InitializeComponent()
        {
            this.SuspendLayout();
            // 
            // LogViewerForm
            // 
            this.ClientSize = new System.Drawing.Size(600, 450);
            this.Name = "LogViewerForm";
            this.Text = "Log Viewer";
            this.StartPosition = FormStartPosition.CenterParent;
            this.BackColor = Color.FromArgb(40, 42, 50);
            this.ResumeLayout(false);
        }

        private void BuildUI()
        {
            // Tab Control
            tabControl = new TabControl
            {
                Dock = DockStyle.Top,
                Height = 380,
                Font = new Font("Malgun Gothic", 9F)
            };
            this.Controls.Add(tabControl);

            // System Log Tab
            var tabSystem = new TabPage("System Log");
            tabSystem.BackColor = Color.FromArgb(28, 30, 38);
            lstSystemLog = CreateLogListBox();
            tabSystem.Controls.Add(lstSystemLog);
            tabControl.TabPages.Add(tabSystem);

            // Error Log Tab
            var tabError = new TabPage("Error Log");
            tabError.BackColor = Color.FromArgb(28, 30, 38);
            lstErrorLog = CreateLogListBox();
            lstErrorLog.ForeColor = Color.Salmon; // Error logs in reddish color
            tabError.Controls.Add(lstErrorLog);
            tabControl.TabPages.Add(tabError);

            // Close Button
            btnClose = new Button
            {
                Text = "Close",
                Width = 100,
                Height = 35,
                Left = (this.ClientSize.Width - 100) / 2,
                Top = tabControl.Bottom + 10,
                FlatStyle = FlatStyle.Flat,
                BackColor = Color.FromArgb(70, 72, 80),
                ForeColor = Color.White,
                Cursor = Cursors.Hand
            };
            btnClose.Click += (s, e) => this.Close();
            this.Controls.Add(btnClose);
        }

        private ListBox CreateLogListBox()
        {
            return new ListBox
            {
                Dock = DockStyle.Fill,
                BackColor = Color.FromArgb(28, 30, 38),
                ForeColor = Color.White,
                Font = new Font("Consolas", 9F),
                BorderStyle = BorderStyle.None,
                HorizontalScrollbar = true
            };
        }

        private void LoadLogs(List<string> systemLogs, List<string> errorLogs)
        {
            lstSystemLog.Items.Clear();
            if (systemLogs != null)
            {
                foreach (var log in systemLogs)
                {
                    lstSystemLog.Items.Add(log);
                }
                // Scroll to bottom
                if (lstSystemLog.Items.Count > 0)
                    lstSystemLog.TopIndex = lstSystemLog.Items.Count - 1;
            }

            lstErrorLog.Items.Clear();
            if (errorLogs != null)
            {
                foreach (var log in errorLogs)
                {
                    lstErrorLog.Items.Add(log);
                }
                // Scroll to bottom
                if (lstErrorLog.Items.Count > 0)
                    lstErrorLog.TopIndex = lstErrorLog.Items.Count - 1;
            }
        }
    }
}
