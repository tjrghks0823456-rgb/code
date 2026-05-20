namespace WindowsFormsApp1
{
    partial class UC_Dashboard
    {
        private System.ComponentModel.IContainer components = null;

        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
            {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        private void InitializeComponent()
        {
            System.Windows.Forms.DataVisualization.Charting.ChartArea chartArea1 = new System.Windows.Forms.DataVisualization.Charting.ChartArea();
            System.Windows.Forms.DataVisualization.Charting.Legend legend1 = new System.Windows.Forms.DataVisualization.Charting.Legend();
            this.lblTotal = new System.Windows.Forms.Label();
            this.lblRented = new System.Windows.Forms.Label();
            this.lblFault = new System.Windows.Forms.Label();
            this.chartStatus = new System.Windows.Forms.DataVisualization.Charting.Chart();
            this.btnRefresh = new System.Windows.Forms.Button();
            this.grpSchedule = new System.Windows.Forms.GroupBox();
            this.btnNextMonth = new System.Windows.Forms.Button();
            this.lblCurrentMonth = new System.Windows.Forms.Label();
            this.btnPrevMonth = new System.Windows.Forms.Button();
            this.tlpCalendar = new System.Windows.Forms.TableLayoutPanel();
            this.btnDelManager = new System.Windows.Forms.Button();
            this.btnAddManager = new System.Windows.Forms.Button();
            this.txtManagerName = new System.Windows.Forms.TextBox();
            this.lblManagerTitle = new System.Windows.Forms.Label();
            this.lstManagers = new System.Windows.Forms.ListBox();
            ((System.ComponentModel.ISupportInitialize)(this.chartStatus)).BeginInit();
            this.grpSchedule.SuspendLayout();
            this.SuspendLayout();
            // 
            // lblTotal
            // 
            this.lblTotal.AutoSize = true;
            this.lblTotal.Font = new System.Drawing.Font("맑은 고딕", 14F, System.Drawing.FontStyle.Bold);
            this.lblTotal.Location = new System.Drawing.Point(30, 30);
            this.lblTotal.Name = "lblTotal";
            this.lblTotal.Size = new System.Drawing.Size(118, 25);
            this.lblTotal.TabIndex = 0;
            this.lblTotal.Text = "전체 장비: 0";
            // 
            // lblRented
            // 
            this.lblRented.AutoSize = true;
            this.lblRented.Font = new System.Drawing.Font("맑은 고딕", 12F);
            this.lblRented.ForeColor = System.Drawing.Color.DarkOrange;
            this.lblRented.Location = new System.Drawing.Point(30, 70);
            this.lblRented.Name = "lblRented";
            this.lblRented.Size = new System.Drawing.Size(83, 21);
            this.lblRented.TabIndex = 1;
            this.lblRented.Text = "대여 중: 0";
            // 
            // lblFault
            // 
            this.lblFault.AutoSize = true;
            this.lblFault.Font = new System.Drawing.Font("맑은 고딕", 12F);
            this.lblFault.ForeColor = System.Drawing.Color.Red;
            this.lblFault.Location = new System.Drawing.Point(150, 70);
            this.lblFault.Name = "lblFault";
            this.lblFault.Size = new System.Drawing.Size(61, 21);
            this.lblFault.TabIndex = 2;
            this.lblFault.Text = "고장: 0";
            // 
            // chartStatus
            // 
            chartArea1.Name = "ChartArea1";
            this.chartStatus.ChartAreas.Add(chartArea1);
            legend1.Name = "Legend1";
            this.chartStatus.Legends.Add(legend1);
            this.chartStatus.Location = new System.Drawing.Point(30, 110);
            this.chartStatus.Name = "chartStatus";
            this.chartStatus.Size = new System.Drawing.Size(400, 300);
            this.chartStatus.TabIndex = 3;
            this.chartStatus.Click += new System.EventHandler(this.chartStatus_Click);
            // 
            // btnRefresh
            // 
            this.btnRefresh.Location = new System.Drawing.Point(350, 30);
            this.btnRefresh.Name = "btnRefresh";
            this.btnRefresh.Size = new System.Drawing.Size(80, 30);
            this.btnRefresh.TabIndex = 4;
            this.btnRefresh.Text = "새로고침";
            this.btnRefresh.UseVisualStyleBackColor = true;
            this.btnRefresh.Click += new System.EventHandler(this.btnRefresh_Click);
            // 
            // grpSchedule
            // 
            this.grpSchedule.Controls.Add(this.btnNextMonth);
            this.grpSchedule.Controls.Add(this.lblCurrentMonth);
            this.grpSchedule.Controls.Add(this.btnPrevMonth);
            this.grpSchedule.Controls.Add(this.tlpCalendar);
            this.grpSchedule.Controls.Add(this.btnDelManager);
            this.grpSchedule.Controls.Add(this.btnAddManager);
            this.grpSchedule.Controls.Add(this.txtManagerName);
            this.grpSchedule.Controls.Add(this.lblManagerTitle);
            this.grpSchedule.Controls.Add(this.lstManagers);
            this.grpSchedule.Location = new System.Drawing.Point(450, 30);
            this.grpSchedule.Name = "grpSchedule";
            this.grpSchedule.Size = new System.Drawing.Size(1050, 750);
            this.grpSchedule.TabIndex = 5;
            this.grpSchedule.TabStop = false;
            this.grpSchedule.Text = "당직 근무표";
            // 
            // btnNextMonth
            // 
            this.btnNextMonth.Location = new System.Drawing.Point(280, 25);
            this.btnNextMonth.Name = "btnNextMonth";
            this.btnNextMonth.Size = new System.Drawing.Size(40, 30);
            this.btnNextMonth.TabIndex = 8;
            this.btnNextMonth.Text = ">";
            this.btnNextMonth.UseVisualStyleBackColor = true;
            // 
            // lblCurrentMonth
            // 
            this.lblCurrentMonth.Font = new System.Drawing.Font("맑은 고딕", 14F, System.Drawing.FontStyle.Bold);
            this.lblCurrentMonth.Location = new System.Drawing.Point(70, 25);
            this.lblCurrentMonth.Name = "lblCurrentMonth";
            this.lblCurrentMonth.Size = new System.Drawing.Size(200, 30);
            this.lblCurrentMonth.TabIndex = 7;
            this.lblCurrentMonth.Text = "2024년 1월";
            this.lblCurrentMonth.TextAlign = System.Drawing.ContentAlignment.MiddleCenter;
            // 
            // btnPrevMonth
            // 
            this.btnPrevMonth.Location = new System.Drawing.Point(20, 25);
            this.btnPrevMonth.Name = "btnPrevMonth";
            this.btnPrevMonth.Size = new System.Drawing.Size(40, 30);
            this.btnPrevMonth.TabIndex = 6;
            this.btnPrevMonth.Text = "<";
            this.btnPrevMonth.UseVisualStyleBackColor = true;
            // 
            // tlpCalendar
            // 
            this.tlpCalendar.CellBorderStyle = System.Windows.Forms.TableLayoutPanelCellBorderStyle.Single;
            this.tlpCalendar.ColumnCount = 7;
            this.tlpCalendar.ColumnStyles.Add(new System.Windows.Forms.ColumnStyle(System.Windows.Forms.SizeType.Percent, 14.28F));
            this.tlpCalendar.ColumnStyles.Add(new System.Windows.Forms.ColumnStyle(System.Windows.Forms.SizeType.Percent, 14.28F));
            this.tlpCalendar.ColumnStyles.Add(new System.Windows.Forms.ColumnStyle(System.Windows.Forms.SizeType.Percent, 14.28F));
            this.tlpCalendar.ColumnStyles.Add(new System.Windows.Forms.ColumnStyle(System.Windows.Forms.SizeType.Percent, 14.28F));
            this.tlpCalendar.ColumnStyles.Add(new System.Windows.Forms.ColumnStyle(System.Windows.Forms.SizeType.Percent, 14.28F));
            this.tlpCalendar.ColumnStyles.Add(new System.Windows.Forms.ColumnStyle(System.Windows.Forms.SizeType.Percent, 14.28F));
            this.tlpCalendar.ColumnStyles.Add(new System.Windows.Forms.ColumnStyle(System.Windows.Forms.SizeType.Percent, 14.28F));
            this.tlpCalendar.Location = new System.Drawing.Point(20, 70);
            this.tlpCalendar.Name = "tlpCalendar";
            this.tlpCalendar.RowCount = 7;
            this.tlpCalendar.RowStyles.Add(new System.Windows.Forms.RowStyle(System.Windows.Forms.SizeType.Absolute, 30F));
            this.tlpCalendar.RowStyles.Add(new System.Windows.Forms.RowStyle(System.Windows.Forms.SizeType.Percent, 16.66F));
            this.tlpCalendar.RowStyles.Add(new System.Windows.Forms.RowStyle(System.Windows.Forms.SizeType.Percent, 16.66F));
            this.tlpCalendar.RowStyles.Add(new System.Windows.Forms.RowStyle(System.Windows.Forms.SizeType.Percent, 16.66F));
            this.tlpCalendar.RowStyles.Add(new System.Windows.Forms.RowStyle(System.Windows.Forms.SizeType.Percent, 16.66F));
            this.tlpCalendar.RowStyles.Add(new System.Windows.Forms.RowStyle(System.Windows.Forms.SizeType.Percent, 16.66F));
            this.tlpCalendar.RowStyles.Add(new System.Windows.Forms.RowStyle(System.Windows.Forms.SizeType.Percent, 16.66F));
            this.tlpCalendar.Size = new System.Drawing.Size(700, 650);
            this.tlpCalendar.TabIndex = 9;
            // 
            // btnDelManager
            // 
            this.btnDelManager.Location = new System.Drawing.Point(940, 620);
            this.btnDelManager.Name = "btnDelManager";
            this.btnDelManager.Size = new System.Drawing.Size(80, 23);
            this.btnDelManager.TabIndex = 5;
            this.btnDelManager.Text = "삭제";
            this.btnDelManager.UseVisualStyleBackColor = true;
            // 
            // btnAddManager
            // 
            this.btnAddManager.Location = new System.Drawing.Point(940, 590);
            this.btnAddManager.Name = "btnAddManager";
            this.btnAddManager.Size = new System.Drawing.Size(80, 23);
            this.btnAddManager.TabIndex = 4;
            this.btnAddManager.Text = "추가";
            this.btnAddManager.UseVisualStyleBackColor = true;
            // 
            // txtManagerName
            // 
            this.txtManagerName.Location = new System.Drawing.Point(740, 590);
            this.txtManagerName.Name = "txtManagerName";
            this.txtManagerName.Size = new System.Drawing.Size(180, 21);
            this.txtManagerName.TabIndex = 3;
            // 
            // lblManagerTitle
            // 
            this.lblManagerTitle.AutoSize = true;
            this.lblManagerTitle.Font = new System.Drawing.Font("맑은 고딕", 9F, System.Drawing.FontStyle.Bold);
            this.lblManagerTitle.Location = new System.Drawing.Point(740, 40);
            this.lblManagerTitle.Name = "lblManagerTitle";
            this.lblManagerTitle.Size = new System.Drawing.Size(100, 15);
            this.lblManagerTitle.TabIndex = 2;
            this.lblManagerTitle.Text = "당직/관리자 명단";
            // 
            // lstManagers
            // 
            this.lstManagers.FormattingEnabled = true;
            this.lstManagers.ItemHeight = 12;
            this.lstManagers.Location = new System.Drawing.Point(740, 70);
            this.lstManagers.Name = "lstManagers";
            this.lstManagers.Size = new System.Drawing.Size(280, 496);
            this.lstManagers.TabIndex = 1;
            // 
            // UC_Dashboard
            // 
            this.Controls.Add(this.grpSchedule);
            this.Controls.Add(this.btnRefresh);
            this.Controls.Add(this.chartStatus);
            this.Controls.Add(this.lblFault);
            this.Controls.Add(this.lblRented);
            this.Controls.Add(this.lblTotal);
            this.Name = "UC_Dashboard";
            this.Size = new System.Drawing.Size(1600, 800);
            this.Load += new System.EventHandler(this.UC_Dashboard_Load);
            ((System.ComponentModel.ISupportInitialize)(this.chartStatus)).EndInit();
            this.grpSchedule.ResumeLayout(false);
            this.grpSchedule.PerformLayout();
            this.ResumeLayout(false);
            this.PerformLayout();

        }

        private System.Windows.Forms.Label lblTotal;
        private System.Windows.Forms.Label lblRented;
        private System.Windows.Forms.Label lblFault;
        private System.Windows.Forms.DataVisualization.Charting.Chart chartStatus;
        private System.Windows.Forms.Button btnRefresh;
        private System.Windows.Forms.GroupBox grpSchedule;
        private System.Windows.Forms.TableLayoutPanel tlpCalendar;
        private System.Windows.Forms.Button btnPrevMonth;
        private System.Windows.Forms.Button btnNextMonth;
        private System.Windows.Forms.Label lblCurrentMonth;
        private System.Windows.Forms.ListBox lstManagers;
        private System.Windows.Forms.Label lblManagerTitle;
        private System.Windows.Forms.TextBox txtManagerName;
        private System.Windows.Forms.Button btnAddManager;
        private System.Windows.Forms.Button btnDelManager;
    }
}
