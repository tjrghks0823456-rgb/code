namespace WindowsFormsApp1
{
    partial class UC_EquipmentList
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

        #region Designer generated code

        private System.Windows.Forms.GroupBox groupBox1;
        private System.Windows.Forms.ListView lvEquip;
        private System.Windows.Forms.ColumnHeader colName;
        private System.Windows.Forms.ColumnHeader colCategory;
        private System.Windows.Forms.ColumnHeader colStatus;
        private System.Windows.Forms.ColumnHeader colUser;
        private System.Windows.Forms.ColumnHeader colSchedule;
        private System.Windows.Forms.ColumnHeader colRemaining;
        private System.Windows.Forms.Button btnReset;
        private System.Windows.Forms.Button btnSearch;
        private System.Windows.Forms.Button btnRegister;
        private System.Windows.Forms.TextBox txtSearch;
        private System.Windows.Forms.Label lblSearch;
        
        private System.Windows.Forms.Label lblSelectedInfo;
        private System.Windows.Forms.GroupBox grpSpecs;
        private System.Windows.Forms.Label lblSpecs;
        private System.Windows.Forms.GroupBox grpGuide;
        private System.Windows.Forms.Label lblGuide;
        private System.Windows.Forms.PictureBox pbEquipImage;

        private void InitializeComponent()
        {
            this.groupBox1 = new System.Windows.Forms.GroupBox();
            this.lvEquip = new System.Windows.Forms.ListView();
            this.colName = ((System.Windows.Forms.ColumnHeader)(new System.Windows.Forms.ColumnHeader()));
            this.colCategory = ((System.Windows.Forms.ColumnHeader)(new System.Windows.Forms.ColumnHeader()));
            this.colStatus = ((System.Windows.Forms.ColumnHeader)(new System.Windows.Forms.ColumnHeader()));
            this.colUser = ((System.Windows.Forms.ColumnHeader)(new System.Windows.Forms.ColumnHeader()));
            this.colSchedule = ((System.Windows.Forms.ColumnHeader)(new System.Windows.Forms.ColumnHeader()));
            this.colRemaining = ((System.Windows.Forms.ColumnHeader)(new System.Windows.Forms.ColumnHeader()));
            this.btnReset = new System.Windows.Forms.Button();
            this.btnSearch = new System.Windows.Forms.Button();
            this.btnRegister = new System.Windows.Forms.Button();
            this.txtSearch = new System.Windows.Forms.TextBox();
            this.lblSearch = new System.Windows.Forms.Label();
            this.lblSelectedInfo = new System.Windows.Forms.Label();
            this.grpSpecs = new System.Windows.Forms.GroupBox();
            this.lblSpecs = new System.Windows.Forms.Label();
            this.grpGuide = new System.Windows.Forms.GroupBox();
            this.lblGuide = new System.Windows.Forms.Label();
            this.pbEquipImage = new System.Windows.Forms.PictureBox();
            this.groupBox1.SuspendLayout();
            this.grpSpecs.SuspendLayout();
            this.grpGuide.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)(this.pbEquipImage)).BeginInit();
            this.SuspendLayout();
            // 
            // groupBox1
            // 
            this.groupBox1.Controls.Add(this.lvEquip);
            this.groupBox1.Controls.Add(this.btnReset);
            this.groupBox1.Controls.Add(this.btnSearch);
            this.groupBox1.Controls.Add(this.btnRegister);
            this.groupBox1.Controls.Add(this.txtSearch);
            this.groupBox1.Controls.Add(this.lblSearch);
            this.groupBox1.Controls.Add(this.lblSelectedInfo);
            this.groupBox1.Location = new System.Drawing.Point(30, 30);
            this.groupBox1.Name = "groupBox1";
            this.groupBox1.Size = new System.Drawing.Size(710, 350);
            this.groupBox1.TabIndex = 0;
            this.groupBox1.TabStop = false;
            this.groupBox1.Text = "장비 목록";
            // 
            // lvEquip
            // 
            this.lvEquip.Columns.AddRange(new System.Windows.Forms.ColumnHeader[] {
            this.colName,
            this.colCategory,
            this.colStatus,
            this.colUser,
            this.colSchedule,
            this.colRemaining});
            this.lvEquip.FullRowSelect = true;
            this.lvEquip.GridLines = true;
            this.lvEquip.HideSelection = false;
            this.lvEquip.Location = new System.Drawing.Point(20, 100);
            this.lvEquip.Name = "lvEquip";
            this.lvEquip.Size = new System.Drawing.Size(670, 220);
            this.lvEquip.TabIndex = 4;
            this.lvEquip.UseCompatibleStateImageBehavior = false;
            this.lvEquip.View = System.Windows.Forms.View.Details;
            this.lvEquip.SelectedIndexChanged += new System.EventHandler(this.lvEquip_SelectedIndexChanged);
            // 
            // colName
            // 
            this.colName.Text = "장비명";
            this.colName.Width = 100;
            // 
            // colCategory
            // 
            this.colCategory.Text = "종류";
            this.colCategory.Width = 80;
            // 
            // colStatus
            // 
            this.colStatus.Text = "상태";
            this.colStatus.Width = 60;
            // 
            // colUser
            // 
            this.colUser.Text = "사용자";
            this.colUser.Width = 80;
            // 
            // colSchedule
            // 
            this.colSchedule.Text = "예정일";
            this.colSchedule.Width = 150;
            // 
            // colRemaining
            // 
            this.colRemaining.Text = "남은 시간";
            this.colRemaining.Width = 150;
            // 
            // btnReset
            // 
            this.btnReset.Location = new System.Drawing.Point(360, 30);
            this.btnReset.Name = "btnReset";
            this.btnReset.Size = new System.Drawing.Size(70, 30);
            this.btnReset.TabIndex = 3;
            this.btnReset.Text = "초기화";
            this.btnReset.UseVisualStyleBackColor = true;
            this.btnReset.Click += new System.EventHandler(this.btnReset_Click);
            // 
            // btnSearch
            // 
            this.btnSearch.Location = new System.Drawing.Point(285, 30);
            this.btnSearch.Name = "btnSearch";
            this.btnSearch.Size = new System.Drawing.Size(70, 30);
            this.btnSearch.TabIndex = 2;
            this.btnSearch.Text = "검색";
            this.btnSearch.UseVisualStyleBackColor = true;
            this.btnSearch.Click += new System.EventHandler(this.btnSearch_Click);
            // 
            // btnRegister
            // 
            this.btnRegister.Location = new System.Drawing.Point(580, 30);
            this.btnRegister.Name = "btnRegister";
            this.btnRegister.Size = new System.Drawing.Size(110, 30);
            this.btnRegister.TabIndex = 6;
            this.btnRegister.Text = "장비 등록";
            this.btnRegister.UseVisualStyleBackColor = true;
            this.btnRegister.Click += new System.EventHandler(this.btnRegister_Click);
            // 
            // txtSearch
            // 
            this.txtSearch.Location = new System.Drawing.Point(80, 35);
            this.txtSearch.Name = "txtSearch";
            this.txtSearch.Size = new System.Drawing.Size(200, 21);
            this.txtSearch.TabIndex = 1;
            // 
            // lblSearch
            // 
            this.lblSearch.AutoSize = true;
            this.lblSearch.Location = new System.Drawing.Point(20, 39);
            this.lblSearch.Name = "lblSearch";
            this.lblSearch.Size = new System.Drawing.Size(53, 12);
            this.lblSearch.TabIndex = 0;
            this.lblSearch.Text = "장비검색";
            // 
            // lblSelectedInfo
            // 
            this.lblSelectedInfo.AutoSize = true;
            this.lblSelectedInfo.ForeColor = System.Drawing.Color.Blue;
            this.lblSelectedInfo.Location = new System.Drawing.Point(25, 75);
            this.lblSelectedInfo.Name = "lblSelectedInfo";
            this.lblSelectedInfo.Size = new System.Drawing.Size(120, 12);
            this.lblSelectedInfo.TabIndex = 5;
            this.lblSelectedInfo.Text = "선택된 장비: 없음";
            // 
            // grpSpecs
            // 
            this.grpSpecs.Controls.Add(this.lblSpecs);
            this.grpSpecs.Location = new System.Drawing.Point(30, 440);
            this.grpSpecs.Name = "grpSpecs";
            this.grpSpecs.Size = new System.Drawing.Size(710, 300);
            this.grpSpecs.TabIndex = 6;
            this.grpSpecs.TabStop = false;
            this.grpSpecs.Text = "상세 스펙";
            // 
            // lblSpecs
            // 
            this.lblSpecs.Location = new System.Drawing.Point(20, 30);
            this.lblSpecs.Name = "lblSpecs";
            this.lblSpecs.Size = new System.Drawing.Size(670, 280);
            this.lblSpecs.TabIndex = 0;
            this.lblSpecs.Text = "장비를 선택하면 스펙이 표시됩니다.";
            this.lblSpecs.Font = new System.Drawing.Font("맑은 고딕", 10F, System.Drawing.FontStyle.Regular);
            // 
            // grpGuide
            // 
            this.grpGuide.Controls.Add(this.pbEquipImage);
            this.grpGuide.Controls.Add(this.lblGuide);
            this.grpGuide.Location = new System.Drawing.Point(760, 30);
            this.grpGuide.Name = "grpGuide";
            this.grpGuide.Size = new System.Drawing.Size(400, 710);
            this.grpGuide.TabIndex = 7;
            this.grpGuide.TabStop = false;
            this.grpGuide.Text = "사용 가이드 및 주의사항";
            // 
            // lblGuide
            // 
            this.lblGuide.Location = new System.Drawing.Point(20, 30);
            this.lblGuide.Name = "lblGuide";
            this.lblGuide.Size = new System.Drawing.Size(360, 300);
            this.lblGuide.TabIndex = 0;
            this.lblGuide.Text = "장비를 선택하면 가이드가 표시됩니다.";
            this.lblGuide.Font = new System.Drawing.Font("맑은 고딕", 10F, System.Drawing.FontStyle.Regular);
            // 
            // pbEquipImage
            // 
            this.pbEquipImage.Location = new System.Drawing.Point(20, 350);
            this.pbEquipImage.Name = "pbEquipImage";
            this.pbEquipImage.Size = new System.Drawing.Size(360, 330);
            this.pbEquipImage.SizeMode = System.Windows.Forms.PictureBoxSizeMode.Zoom;
            this.pbEquipImage.TabIndex = 1;
            this.pbEquipImage.TabStop = false;
            // 
            // UC_EquipmentList
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(7F, 12F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.Controls.Add(this.grpGuide);
            this.Controls.Add(this.grpSpecs);
            this.Controls.Add(this.groupBox1);
            this.Name = "UC_EquipmentList";
            this.Size = new System.Drawing.Size(1200, 780);
            this.groupBox1.ResumeLayout(false);
            this.groupBox1.PerformLayout();
            this.grpSpecs.ResumeLayout(false);
            this.grpGuide.ResumeLayout(false);
            ((System.ComponentModel.ISupportInitialize)(this.pbEquipImage)).EndInit();
            this.ResumeLayout(false);

        }

        #endregion
    }
}
