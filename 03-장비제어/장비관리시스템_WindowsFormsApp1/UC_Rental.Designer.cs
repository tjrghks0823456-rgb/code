namespace WindowsFormsApp1
{
    partial class UC_Rental
    {
        /// <summary> 
        /// 필수 디자이너 변수입니다.
        /// </summary>
        private System.ComponentModel.IContainer components = null;

        /// <summary> 
        /// 사용 중인 모든 리소스를 정리합니다.
        /// </summary>
        /// <param name="disposing">관리되는 리소스를 삭제해야 하면 true이고, 그렇지 않으면 false입니다.</param>
        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
            {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        #region 구성 요소 디자이너에서 생성한 코드

        /// <summary> 
        /// 디자이너 지원에 필요한 메서드입니다. 
        /// 이 메서드의 내용을 코드 편집기로 수정하지 마세요.
        /// </summary>
        private System.Windows.Forms.GroupBox hh;
        private System.Windows.Forms.ListView lvRental;
        private System.Windows.Forms.ColumnHeader columnHeader3;
        private System.Windows.Forms.ColumnHeader columnHeader4;
        private System.Windows.Forms.ColumnHeader columnHeader5;
        private System.Windows.Forms.ColumnHeader columnHeader6;
        private System.Windows.Forms.ColumnHeader columnHeader7;
        private System.Windows.Forms.Button btnReturn;
        private System.Windows.Forms.Button btnRent;
        private System.Windows.Forms.TextBox txtUser;
        private System.Windows.Forms.Label label2;
        private System.Windows.Forms.Label lblSelectedEquip;
        private System.Windows.Forms.Label lblTitle;
        private System.Windows.Forms.DateTimePicker dtpDueDate;
        // 추가
        private System.Windows.Forms.NumericUpDown nudDays;
        private System.Windows.Forms.Label lblDays;
        private System.Windows.Forms.Button btnSelect; // 선택 버튼 추가

        private void InitializeComponent()
        {
            this.hh = new System.Windows.Forms.GroupBox();
            this.lvRental = new System.Windows.Forms.ListView();
            this.columnHeader3 = ((System.Windows.Forms.ColumnHeader)(new System.Windows.Forms.ColumnHeader()));
            this.columnHeader4 = ((System.Windows.Forms.ColumnHeader)(new System.Windows.Forms.ColumnHeader()));
            this.columnHeader5 = ((System.Windows.Forms.ColumnHeader)(new System.Windows.Forms.ColumnHeader()));
            this.columnHeader6 = ((System.Windows.Forms.ColumnHeader)(new System.Windows.Forms.ColumnHeader()));
            this.columnHeader7 = ((System.Windows.Forms.ColumnHeader)(new System.Windows.Forms.ColumnHeader()));
            this.btnReturn = new System.Windows.Forms.Button();
            this.btnRent = new System.Windows.Forms.Button();
            this.txtUser = new System.Windows.Forms.TextBox();
            this.label2 = new System.Windows.Forms.Label();
            this.lblSelectedEquip = new System.Windows.Forms.Label();
            this.lblTitle = new System.Windows.Forms.Label();
            this.dtpDueDate = new System.Windows.Forms.DateTimePicker();
            this.nudDays = new System.Windows.Forms.NumericUpDown();
            this.lblDays = new System.Windows.Forms.Label();
            this.btnSelect = new System.Windows.Forms.Button();
            this.hh.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)(this.nudDays)).BeginInit();
            this.SuspendLayout();
            // 
            // hh
            // 
            this.hh.BackColor = System.Drawing.SystemColors.ButtonFace;
            this.hh.Controls.Add(this.lvRental);
            this.hh.Controls.Add(this.btnReturn);
            this.hh.Controls.Add(this.btnRent);
            this.hh.Controls.Add(this.txtUser);
            this.hh.Controls.Add(this.label2);
            this.hh.Controls.Add(this.lblSelectedEquip);
            this.hh.Controls.Add(this.lblTitle);
            this.hh.Controls.Add(this.dtpDueDate);
            this.hh.Controls.Add(this.nudDays);
            this.hh.Controls.Add(this.lblDays);
            this.hh.Controls.Add(this.btnSelect);
            this.hh.ForeColor = System.Drawing.SystemColors.ControlText;
            this.hh.Location = new System.Drawing.Point(18, 30);
            this.hh.Name = "hh";
            this.hh.Size = new System.Drawing.Size(722, 532);
            this.hh.TabIndex = 10;
            this.hh.TabStop = false;
            this.hh.Text = "UC_Rental";
            // 
            // lvRental
            // 
            this.lvRental.Columns.AddRange(new System.Windows.Forms.ColumnHeader[] {
            this.columnHeader3,
            this.columnHeader4,
            this.columnHeader5,
            this.columnHeader6,
            this.columnHeader7});
            this.lvRental.FullRowSelect = true;
            this.lvRental.GridLines = true;
            this.lvRental.HideSelection = false;
            this.lvRental.Location = new System.Drawing.Point(17, 103);
            this.lvRental.Name = "lvRental";
            this.lvRental.Size = new System.Drawing.Size(634, 318);
            this.lvRental.TabIndex = 6;
            this.lvRental.UseCompatibleStateImageBehavior = false;
            this.lvRental.View = System.Windows.Forms.View.Details;
            this.lvRental.SelectedIndexChanged += new System.EventHandler(this.lvRental_SelectedIndexChanged);
            // 
            // columnHeader3
            // 
            this.columnHeader3.Text = "장비명";
            this.columnHeader3.Width = 150;
            // 
            // columnHeader4
            // 
            this.columnHeader4.Text = "종류";
            this.columnHeader4.Width = 100;
            // 
            // columnHeader5
            // 
            this.columnHeader5.Text = "상태";
            this.columnHeader5.Width = 80;
            // 
            // columnHeader6
            // 
            this.columnHeader6.Text = "사용자";
            this.columnHeader6.Width = 100;
            // 
            // columnHeader7
            // 
            this.columnHeader7.Text = "마지막 수정";
            this.columnHeader7.Width = 150;
            // 
            // btnReturn
            // 
            this.btnReturn.Location = new System.Drawing.Point(580, 60);
            this.btnReturn.Name = "btnReturn";
            this.btnReturn.Size = new System.Drawing.Size(74, 26);
            this.btnReturn.TabIndex = 5;
            this.btnReturn.Text = "반납하기";
            this.btnReturn.UseVisualStyleBackColor = true;
            this.btnReturn.Click += new System.EventHandler(this.btnReturn_Click);
            // 
            // btnRent
            // 
            this.btnRent.Location = new System.Drawing.Point(500, 60);
            this.btnRent.Name = "btnRent";
            this.btnRent.Size = new System.Drawing.Size(74, 26);
            this.btnRent.TabIndex = 4;
            this.btnRent.Text = "대여하기";
            this.btnRent.UseVisualStyleBackColor = true;
            this.btnRent.Click += new System.EventHandler(this.btnRent_Click);
            // 
            // txtUser
            // 
            this.txtUser.Location = new System.Drawing.Point(57, 62);
            this.txtUser.Name = "txtUser";
            this.txtUser.Size = new System.Drawing.Size(119, 21);
            this.txtUser.TabIndex = 3;
            // 
            // label2
            // 
            this.label2.AutoSize = true;
            this.label2.Location = new System.Drawing.Point(6, 65);
            this.label2.Name = "label2";
            this.label2.Size = new System.Drawing.Size(45, 12);
            this.label2.TabIndex = 2;
            this.label2.Text = "사용자:";
            // 
            // lblSelectedEquip
            // 
            this.lblSelectedEquip.AutoSize = true;
            this.lblSelectedEquip.Location = new System.Drawing.Point(130, 28);
            this.lblSelectedEquip.Name = "lblSelectedEquip";
            this.lblSelectedEquip.Size = new System.Drawing.Size(11, 12);
            this.lblSelectedEquip.TabIndex = 1;
            this.lblSelectedEquip.Text = "-";
            // 
            // lblTitle
            // 
            this.lblTitle.AutoSize = true;
            this.lblTitle.Location = new System.Drawing.Point(6, 28);
            this.lblTitle.Name = "lblTitle";
            this.lblTitle.Size = new System.Drawing.Size(73, 12);
            this.lblTitle.TabIndex = 0;
            this.lblTitle.Text = "선택한 장비:";
            // 
            // dtpDueDate
            // 
            this.dtpDueDate.CustomFormat = "yyyy-MM-dd HH:mm";
            this.dtpDueDate.Format = System.Windows.Forms.DateTimePickerFormat.Custom;
            this.dtpDueDate.Location = new System.Drawing.Point(185, 62);
            this.dtpDueDate.Name = "dtpDueDate";
            this.dtpDueDate.Size = new System.Drawing.Size(160, 21);
            this.dtpDueDate.TabIndex = 7;
            this.dtpDueDate.ValueChanged += new System.EventHandler(this.dtpDueDate_ValueChanged);
            // 
            // nudDays
            // 
            this.nudDays.Location = new System.Drawing.Point(360, 62);
            this.nudDays.Maximum = new decimal(new int[] {
            365,
            0,
            0,
            0});
            this.nudDays.Minimum = new decimal(new int[] {
            1,
            0,
            0,
            0});
            this.nudDays.Name = "nudDays";
            this.nudDays.Size = new System.Drawing.Size(50, 21);
            this.nudDays.TabIndex = 8;
            this.nudDays.Value = new decimal(new int[] {
            7,
            0,
            0,
            0});
            this.nudDays.ValueChanged += new System.EventHandler(this.nudDays_ValueChanged);
            // 
            // lblDays
            // 
            this.lblDays.AutoSize = true;
            this.lblDays.Location = new System.Drawing.Point(415, 66);
            this.lblDays.Name = "lblDays";
            this.lblDays.Size = new System.Drawing.Size(45, 12);
            this.lblDays.TabIndex = 9;
            this.lblDays.Text = "일 동안";
            // 
            // btnSelect
            // 
            this.btnSelect.Location = new System.Drawing.Point(660, 60);
            this.btnSelect.Name = "btnSelect";
            this.btnSelect.Size = new System.Drawing.Size(50, 26);
            this.btnSelect.TabIndex = 6;
            this.btnSelect.Text = "선택";
            this.btnSelect.UseVisualStyleBackColor = true;
            this.btnSelect.Click += new System.EventHandler(this.btnSelect_Click);
            // 
            // UC_Rental
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(7F, 12F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.BackColor = System.Drawing.SystemColors.ButtonFace;
            this.Controls.Add(this.hh);
            this.Name = "UC_Rental";
            this.Size = new System.Drawing.Size(818, 622);
            this.Load += new System.EventHandler(this.UC_Rental_Load);
            this.hh.ResumeLayout(false);
            this.hh.PerformLayout();
            ((System.ComponentModel.ISupportInitialize)(this.nudDays)).EndInit();
            this.ResumeLayout(false);

        }

        #endregion

    }
}
