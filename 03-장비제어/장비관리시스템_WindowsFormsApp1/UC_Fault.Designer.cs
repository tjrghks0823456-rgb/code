namespace WindowsFormsApp1
{
    partial class UC_Fault
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

        #region Component Designer generated code

        private void InitializeComponent()
        {
            this.groupBox1 = new System.Windows.Forms.GroupBox();
            this.lblFaultTitle = new System.Windows.Forms.Label();
            this.lblSelectedEquip = new System.Windows.Forms.Label();
            this.lblReason = new System.Windows.Forms.Label();
            this.txtReason = new System.Windows.Forms.TextBox();
            this.btnFault = new System.Windows.Forms.Button();
            this.btnRepair = new System.Windows.Forms.Button();
            this.btnSelect = new System.Windows.Forms.Button();
            this.lvFaultEqui = new System.Windows.Forms.ListView();
            
            // Column Headers
            this.colName = ((System.Windows.Forms.ColumnHeader)(new System.Windows.Forms.ColumnHeader()));
            this.colCategory = ((System.Windows.Forms.ColumnHeader)(new System.Windows.Forms.ColumnHeader()));
            this.colStatus = ((System.Windows.Forms.ColumnHeader)(new System.Windows.Forms.ColumnHeader()));
            this.colUser = ((System.Windows.Forms.ColumnHeader)(new System.Windows.Forms.ColumnHeader()));
            this.colUpdate = ((System.Windows.Forms.ColumnHeader)(new System.Windows.Forms.ColumnHeader()));

            this.groupBox1.SuspendLayout();
            this.SuspendLayout();

            // 
            // groupBox1
            // 
            this.groupBox1.Controls.Add(this.lblFaultTitle);
            this.groupBox1.Controls.Add(this.lblSelectedEquip);
            this.groupBox1.Controls.Add(this.lblReason);
            this.groupBox1.Controls.Add(this.txtReason);
            this.groupBox1.Controls.Add(this.btnFault);
            this.groupBox1.Controls.Add(this.btnRepair);
            this.groupBox1.Controls.Add(this.btnSelect);
            this.groupBox1.Controls.Add(this.lvFaultEqui);
            this.groupBox1.Location = new System.Drawing.Point(13, 15);
            this.groupBox1.Name = "groupBox1";
            this.groupBox1.Size = new System.Drawing.Size(870, 631);
            this.groupBox1.TabIndex = 0;
            this.groupBox1.TabStop = false;
            this.groupBox1.Text = "고장/수리 관리";

            // 
            // lblFaultTitle ("선택한 장비:")
            // 
            this.lblFaultTitle.AutoSize = true;
            this.lblFaultTitle.Location = new System.Drawing.Point(15, 49);
            this.lblFaultTitle.Name = "lblFaultTitle";
            this.lblFaultTitle.Size = new System.Drawing.Size(73, 12);
            this.lblFaultTitle.TabIndex = 0;
            this.lblFaultTitle.Text = "선택한 장비:";

            // 
            // lblSelectedEquip (The actual selected name)
            // 
            this.lblSelectedEquip.AutoSize = true;
            this.lblSelectedEquip.Location = new System.Drawing.Point(117, 49);
            this.lblSelectedEquip.Name = "lblSelectedEquip";
            this.lblSelectedEquip.Size = new System.Drawing.Size(11, 12);
            this.lblSelectedEquip.TabIndex = 1;
            this.lblSelectedEquip.Text = "-";
            this.lblSelectedEquip.AutoEllipsis = true;

            // 
            // lblReason ("고장 사유:")
            // 
            this.lblReason.AutoSize = true;
            this.lblReason.Location = new System.Drawing.Point(15, 93);
            this.lblReason.Name = "lblReason";
            this.lblReason.Size = new System.Drawing.Size(61, 12);
            this.lblReason.TabIndex = 2;
            this.lblReason.Text = "고장 사유:";

            // 
            // txtReason
            // 
            this.txtReason.Location = new System.Drawing.Point(86, 90);
            this.txtReason.Name = "txtReason";
            this.txtReason.Size = new System.Drawing.Size(466, 21);
            this.txtReason.TabIndex = 3;

            // 
            // btnFault (고장 등록)
            // 
            this.btnFault.Location = new System.Drawing.Point(558, 84);
            this.btnFault.Name = "btnFault";
            this.btnFault.Size = new System.Drawing.Size(83, 31);
            this.btnFault.TabIndex = 4;
            this.btnFault.Text = "고장 등록";
            this.btnFault.UseVisualStyleBackColor = true;
            this.btnFault.Click += new System.EventHandler(this.btnFault_Click);

            // 
            // btnRepair (복구 완료)
            // 
            this.btnRepair.Location = new System.Drawing.Point(665, 84);
            this.btnRepair.Name = "btnRepair";
            this.btnRepair.Size = new System.Drawing.Size(83, 31);
            this.btnRepair.TabIndex = 5;
            this.btnRepair.Text = "복구 완료";
            this.btnRepair.UseVisualStyleBackColor = true;
            this.btnRepair.Click += new System.EventHandler(this.btnRepair_Click);

            // 
            // btnSelect (선택)
            // 
            this.btnSelect.Location = new System.Drawing.Point(756, 84);
            this.btnSelect.Name = "btnSelect";
            this.btnSelect.Size = new System.Drawing.Size(83, 31);
            this.btnSelect.TabIndex = 6;
            this.btnSelect.Text = "선택";
            this.btnSelect.UseVisualStyleBackColor = true;
            this.btnSelect.Click += new System.EventHandler(this.btnSelect_Click);

            // 
            // lvFaultEqui
            // 
            this.lvFaultEqui.Columns.AddRange(new System.Windows.Forms.ColumnHeader[] {
            this.colName,
            this.colCategory,
            this.colStatus,
            this.colUser,
            this.colUpdate});
            this.lvFaultEqui.FullRowSelect = true;
            this.lvFaultEqui.GridLines = true;
            this.lvFaultEqui.HideSelection = false;
            this.lvFaultEqui.Location = new System.Drawing.Point(17, 163);
            this.lvFaultEqui.Name = "lvFaultEqui";
            this.lvFaultEqui.Size = new System.Drawing.Size(582, 346);
            this.lvFaultEqui.TabIndex = 7;
            this.lvFaultEqui.UseCompatibleStateImageBehavior = false;
            this.lvFaultEqui.View = System.Windows.Forms.View.Details;
            this.lvFaultEqui.SelectedIndexChanged += new System.EventHandler(this.lvFaultEqui_SelectedIndexChanged);

            // Column Headers
            this.colName.Text = "장비명";
            this.colName.Width = 150;
            
            this.colCategory.Text = "종류";
            this.colCategory.Width = 100;
            
            this.colStatus.Text = "상태";
            this.colStatus.Width = 80;

            this.colUser.Text = "사용자";
            this.colUser.Width = 100;

            this.colUpdate.Text = "마지막 수정";
            this.colUpdate.Width = 150;

            // 
            // UC_Fault
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(7F, 12F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.Controls.Add(this.groupBox1);
            this.Name = "UC_Fault";
            this.Size = new System.Drawing.Size(1163, 779);
            this.Load += new System.EventHandler(this.UC_Fault_Load);
            this.groupBox1.ResumeLayout(false);
            this.groupBox1.PerformLayout();
            this.ResumeLayout(false);

        }

        #endregion

        private System.Windows.Forms.GroupBox groupBox1;
        private System.Windows.Forms.Label lblFaultTitle;
        private System.Windows.Forms.Label lblSelectedEquip;
        private System.Windows.Forms.Label lblReason;
        private System.Windows.Forms.TextBox txtReason;
        private System.Windows.Forms.Button btnFault;
        private System.Windows.Forms.Button btnRepair;
        private System.Windows.Forms.Button btnSelect;
        private System.Windows.Forms.ListView lvFaultEqui;
        private System.Windows.Forms.ColumnHeader colName;
        private System.Windows.Forms.ColumnHeader colCategory;
        private System.Windows.Forms.ColumnHeader colStatus;
        private System.Windows.Forms.ColumnHeader colUser;
        private System.Windows.Forms.ColumnHeader colUpdate;
    }
}
