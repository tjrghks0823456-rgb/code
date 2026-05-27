namespace WindowsFormsApp1
{
    partial class Form1
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
            this.panelMenu = new System.Windows.Forms.Panel();
            this.btnMenuHistory = new System.Windows.Forms.Button();
            this.btnMenuFault = new System.Windows.Forms.Button();
            this.btnMenuRental = new System.Windows.Forms.Button();
            this.btnMenuEquip = new System.Windows.Forms.Button();
            this.btnMenuDashboard = new System.Windows.Forms.Button(); // 추가된 버튼
            this.btnMenuLogin = new System.Windows.Forms.Button(); // 로그인 버튼
            this.panelMain = new System.Windows.Forms.Panel();
            this.panelMenu.SuspendLayout();
            this.SuspendLayout();
            // 
            // panelMenu
            // 
            this.panelMenu.BackColor = System.Drawing.Color.DimGray;
            this.panelMenu.Controls.Add(this.btnMenuHistory);
            this.panelMenu.Controls.Add(this.btnMenuFault);
            this.panelMenu.Controls.Add(this.btnMenuRental);
            this.panelMenu.Controls.Add(this.btnMenuEquip);
            this.panelMenu.Controls.Add(this.btnMenuDashboard); // 컨트롤 추가
            this.panelMenu.Controls.Add(this.btnMenuLogin); // 로그인 버튼 추가
            this.panelMenu.Dock = System.Windows.Forms.DockStyle.Left;
            this.panelMenu.Location = new System.Drawing.Point(0, 0);
            this.panelMenu.Name = "panelMenu";
            this.panelMenu.Size = new System.Drawing.Size(150, 500);
            this.panelMenu.TabIndex = 0;
            // 
            // btnMenuDashboard (New)
            // 
            this.btnMenuDashboard.Location = new System.Drawing.Point(12, 30);
            this.btnMenuDashboard.Name = "btnMenuDashboard";
            this.btnMenuDashboard.Size = new System.Drawing.Size(120, 40);
            this.btnMenuDashboard.TabIndex = 4;
            this.btnMenuDashboard.Text = "대시보드";
            this.btnMenuDashboard.UseVisualStyleBackColor = true;
            this.btnMenuDashboard.Click += new System.EventHandler(this.btnMenuDashboard_Click);
            // 
            // btnMenuEquip
            // 
            this.btnMenuEquip.Location = new System.Drawing.Point(12, 80); // 위치 조정
            this.btnMenuEquip.Name = "btnMenuEquip";
            this.btnMenuEquip.Size = new System.Drawing.Size(120, 40);
            this.btnMenuEquip.TabIndex = 0;
            this.btnMenuEquip.Text = "장비 목록";
            this.btnMenuEquip.UseVisualStyleBackColor = true;
            this.btnMenuEquip.Click += new System.EventHandler(this.btnMenuEquip_Click);
            // 
            // btnMenuRental
            // 
            this.btnMenuRental.Location = new System.Drawing.Point(12, 130); // 위치 조정
            this.btnMenuRental.Name = "btnMenuRental";
            this.btnMenuRental.Size = new System.Drawing.Size(120, 40);
            this.btnMenuRental.TabIndex = 1;
            this.btnMenuRental.Text = "대여/반납";
            this.btnMenuRental.UseVisualStyleBackColor = true;
            this.btnMenuRental.Click += new System.EventHandler(this.btnMenuRental_Click);
            // 
            // btnMenuFault
            // 
            this.btnMenuFault.Location = new System.Drawing.Point(12, 180); // 위치 조정
            this.btnMenuFault.Name = "btnMenuFault";
            this.btnMenuFault.Size = new System.Drawing.Size(120, 40);
            this.btnMenuFault.TabIndex = 2;
            this.btnMenuFault.Text = "고장 관리";
            this.btnMenuFault.UseVisualStyleBackColor = true;
            this.btnMenuFault.Click += new System.EventHandler(this.btnMenuFault_Click);
            // 
            // btnMenuHistory
            // 
            this.btnMenuHistory.Location = new System.Drawing.Point(12, 230); // 위치 조정
            this.btnMenuHistory.Name = "btnMenuHistory";
            this.btnMenuHistory.Size = new System.Drawing.Size(120, 40);
            this.btnMenuHistory.TabIndex = 3;
            this.btnMenuHistory.Text = "이력 조회";
            this.btnMenuHistory.UseVisualStyleBackColor = true;
            this.btnMenuHistory.Click += new System.EventHandler(this.btnMenuHistory_Click);
            // 
            // btnMenuLogin
            // 
            this.btnMenuLogin.Location = new System.Drawing.Point(12, 450); // 하단에 배치
            this.btnMenuLogin.Name = "btnMenuLogin";
            this.btnMenuLogin.Size = new System.Drawing.Size(120, 40);
            this.btnMenuLogin.TabIndex = 5;
            this.btnMenuLogin.Text = "로그인";
            this.btnMenuLogin.UseVisualStyleBackColor = true;
            this.btnMenuLogin.Click += new System.EventHandler(this.btnMenuLogin_Click);
            // 
            // panelMain
            // 
            this.panelMain.Dock = System.Windows.Forms.DockStyle.Fill;
            this.panelMain.Location = new System.Drawing.Point(150, 0);
            this.panelMain.Name = "panelMain";
            this.panelMain.Size = new System.Drawing.Size(650, 500);
            this.panelMain.TabIndex = 1;
            // 
            // Form1
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(7F, 12F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(800, 500);
            this.Controls.Add(this.panelMain);
            this.Controls.Add(this.panelMenu);
            this.Name = "Form1";
            this.Text = "장비 관리 시스템";
            this.StartPosition = System.Windows.Forms.FormStartPosition.CenterScreen;
            this.Load += new System.EventHandler(this.Form1_Load);
            this.panelMenu.ResumeLayout(false);
            this.ResumeLayout(false);

        }

        private System.Windows.Forms.Panel panelMenu;
        private System.Windows.Forms.Button btnMenuHistory;
        private System.Windows.Forms.Button btnMenuFault;
        private System.Windows.Forms.Button btnMenuRental;
        private System.Windows.Forms.Button btnMenuEquip;
        private System.Windows.Forms.Button btnMenuDashboard; // 선언
        private System.Windows.Forms.Button btnMenuLogin; // 선언
        private System.Windows.Forms.Panel panelMain;
    }
}
