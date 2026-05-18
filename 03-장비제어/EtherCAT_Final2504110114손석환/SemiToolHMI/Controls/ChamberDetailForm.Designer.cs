namespace SemiToolHMI.Controls
{
    partial class ChamberDetailForm
    {
        private System.ComponentModel.IContainer components = null;

        private System.Windows.Forms.Label lblTitle;
        private System.Windows.Forms.Panel leftPanel;
        private System.Windows.Forms.Label lblRecipe;
        private System.Windows.Forms.TextBox txtRecipe;
        private System.Windows.Forms.Label lblStep;
        private System.Windows.Forms.TextBox txtStepCur;
        private System.Windows.Forms.TextBox txtStepMax;
        private System.Windows.Forms.Label lblMode;
        private System.Windows.Forms.TextBox txtMode;
        private System.Windows.Forms.Label lblTime;
        private System.Windows.Forms.TextBox txtTimeCur;
        private System.Windows.Forms.TextBox txtTimeMax;
        private System.Windows.Forms.Label lblWafer;
        private System.Windows.Forms.ProgressBar waferBar;

        private System.Windows.Forms.Panel panelPvSv;

        private System.Windows.Forms.Button btnStart;
        private System.Windows.Forms.Button btnStop;
        private System.Windows.Forms.Button btnRecipe;

        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
                components.Dispose();
            base.Dispose(disposing);
        }

        private void InitializeComponent()
        {
            this.lblTitle = new System.Windows.Forms.Label();
            this.leftPanel = new System.Windows.Forms.Panel();
            this.lblRecipe = new System.Windows.Forms.Label();
            this.txtRecipe = new System.Windows.Forms.TextBox();
            this.lblStep = new System.Windows.Forms.Label();
            this.txtStepCur = new System.Windows.Forms.TextBox();
            this.txtStepMax = new System.Windows.Forms.TextBox();
            this.lblMode = new System.Windows.Forms.Label();
            this.txtMode = new System.Windows.Forms.TextBox();
            this.lblTime = new System.Windows.Forms.Label();
            this.txtTimeCur = new System.Windows.Forms.TextBox();
            this.txtTimeMax = new System.Windows.Forms.TextBox();
            this.lblWafer = new System.Windows.Forms.Label();
            this.waferBar = new System.Windows.Forms.ProgressBar();
            this.panelPvSv = new System.Windows.Forms.Panel();
            this.btnStart = new System.Windows.Forms.Button();
            this.btnStop = new System.Windows.Forms.Button();
            this.btnRecipe = new System.Windows.Forms.Button();
            this.leftPanel.SuspendLayout();
            this.SuspendLayout();
            // 
            // lblTitle
            // 
            this.lblTitle.AutoSize = true;
            this.lblTitle.Font = new System.Drawing.Font("맑은 고딕", 14F, System.Drawing.FontStyle.Bold);
            this.lblTitle.ForeColor = System.Drawing.Color.White;
            this.lblTitle.Location = new System.Drawing.Point(10, 10);
            this.lblTitle.Name = "lblTitle";
            this.lblTitle.Size = new System.Drawing.Size(93, 25);
            this.lblTitle.TabIndex = 0;
            this.lblTitle.Text = "Chamber";
            // 
            // leftPanel
            // 
            this.leftPanel.BackColor = System.Drawing.Color.Gray;
            this.leftPanel.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.leftPanel.Controls.Add(this.lblRecipe);
            this.leftPanel.Controls.Add(this.txtRecipe);
            this.leftPanel.Controls.Add(this.lblStep);
            this.leftPanel.Controls.Add(this.txtStepCur);
            this.leftPanel.Controls.Add(this.txtStepMax);
            this.leftPanel.Controls.Add(this.lblMode);
            this.leftPanel.Controls.Add(this.txtMode);
            this.leftPanel.Controls.Add(this.lblTime);
            this.leftPanel.Controls.Add(this.txtTimeCur);
            this.leftPanel.Controls.Add(this.txtTimeMax);
            this.leftPanel.Controls.Add(this.lblWafer);
            this.leftPanel.Controls.Add(this.waferBar);
            this.leftPanel.Location = new System.Drawing.Point(5, 40);
            this.leftPanel.Name = "leftPanel";
            this.leftPanel.Size = new System.Drawing.Size(240, 180);
            this.leftPanel.TabIndex = 1;
            // 
            // lblRecipe
            // 
            this.lblRecipe.AutoSize = true;
            this.lblRecipe.ForeColor = System.Drawing.Color.Gainsboro;
            this.lblRecipe.Location = new System.Drawing.Point(10, 18);
            this.lblRecipe.Name = "lblRecipe";
            this.lblRecipe.Size = new System.Drawing.Size(44, 12);
            this.lblRecipe.TabIndex = 0;
            this.lblRecipe.Text = "Recipe";
            // 
            // txtRecipe
            // 
            this.txtRecipe.Location = new System.Drawing.Point(100, 15);
            this.txtRecipe.Name = "txtRecipe";
            this.txtRecipe.ReadOnly = true;
            this.txtRecipe.Size = new System.Drawing.Size(120, 21);
            this.txtRecipe.TabIndex = 1;
            this.txtRecipe.TextAlign = System.Windows.Forms.HorizontalAlignment.Center;
            // 
            // lblStep
            // 
            this.lblStep.AutoSize = true;
            this.lblStep.ForeColor = System.Drawing.Color.Gainsboro;
            this.lblStep.Location = new System.Drawing.Point(10, 48);
            this.lblStep.Name = "lblStep";
            this.lblStep.Size = new System.Drawing.Size(30, 12);
            this.lblStep.TabIndex = 2;
            this.lblStep.Text = "Step";
            // 
            // txtStepCur
            // 
            this.txtStepCur.Location = new System.Drawing.Point(100, 45);
            this.txtStepCur.Name = "txtStepCur";
            this.txtStepCur.ReadOnly = true;
            this.txtStepCur.Size = new System.Drawing.Size(40, 21);
            this.txtStepCur.TabIndex = 3;
            // 
            // txtStepMax
            // 
            this.txtStepMax.Location = new System.Drawing.Point(145, 45);
            this.txtStepMax.Name = "txtStepMax";
            this.txtStepMax.ReadOnly = true;
            this.txtStepMax.Size = new System.Drawing.Size(40, 21);
            this.txtStepMax.TabIndex = 4;
            // 
            // lblMode
            // 
            this.lblMode.AutoSize = true;
            this.lblMode.ForeColor = System.Drawing.Color.Gainsboro;
            this.lblMode.Location = new System.Drawing.Point(10, 78);
            this.lblMode.Name = "lblMode";
            this.lblMode.Size = new System.Drawing.Size(37, 12);
            this.lblMode.TabIndex = 5;
            this.lblMode.Text = "Mode";
            // 
            // txtMode
            // 
            this.txtMode.Location = new System.Drawing.Point(100, 75);
            this.txtMode.Name = "txtMode";
            this.txtMode.ReadOnly = true;
            this.txtMode.Size = new System.Drawing.Size(120, 21);
            this.txtMode.TabIndex = 6;
            // 
            // lblTime
            // 
            this.lblTime.AutoSize = true;
            this.lblTime.ForeColor = System.Drawing.Color.Gainsboro;
            this.lblTime.Location = new System.Drawing.Point(10, 108);
            this.lblTime.Name = "lblTime";
            this.lblTime.Size = new System.Drawing.Size(34, 12);
            this.lblTime.TabIndex = 7;
            this.lblTime.Text = "Time";
            // 
            // txtTimeCur
            // 
            this.txtTimeCur.Location = new System.Drawing.Point(100, 105);
            this.txtTimeCur.Name = "txtTimeCur";
            this.txtTimeCur.ReadOnly = true;
            this.txtTimeCur.Size = new System.Drawing.Size(40, 21);
            this.txtTimeCur.TabIndex = 8;
            // 
            // txtTimeMax
            // 
            this.txtTimeMax.Location = new System.Drawing.Point(145, 105);
            this.txtTimeMax.Name = "txtTimeMax";
            this.txtTimeMax.ReadOnly = true;
            this.txtTimeMax.Size = new System.Drawing.Size(40, 21);
            this.txtTimeMax.TabIndex = 9;
            // 
            // lblWafer
            // 
            this.lblWafer.AutoSize = true;
            this.lblWafer.ForeColor = System.Drawing.Color.Gainsboro;
            this.lblWafer.Location = new System.Drawing.Point(10, 140);
            this.lblWafer.Name = "lblWafer";
            this.lblWafer.Size = new System.Drawing.Size(36, 12);
            this.lblWafer.TabIndex = 10;
            this.lblWafer.Text = "Wafer";
            // 
            // waferBar
            // 
            this.waferBar.Location = new System.Drawing.Point(100, 140);
            this.waferBar.Maximum = 25;
            this.waferBar.Name = "waferBar";
            this.waferBar.Size = new System.Drawing.Size(120, 15);
            this.waferBar.TabIndex = 11;
            // 
            // panelPvSv
            // 
            this.panelPvSv.BackColor = System.Drawing.Color.Silver;
            this.panelPvSv.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.panelPvSv.Location = new System.Drawing.Point(255, 40);
            this.panelPvSv.Name = "panelPvSv";
            this.panelPvSv.Size = new System.Drawing.Size(310, 180);
            this.panelPvSv.TabIndex = 2;
            // 
            // btnStart
            // 
            this.btnStart.Location = new System.Drawing.Point(10, 225);
            this.btnStart.Name = "btnStart";
            this.btnStart.Size = new System.Drawing.Size(80, 28);
            this.btnStart.TabIndex = 3;
            this.btnStart.Text = "Start";
            // 
            // btnStop
            // 
            this.btnStop.Location = new System.Drawing.Point(100, 225);
            this.btnStop.Name = "btnStop";
            this.btnStop.Size = new System.Drawing.Size(80, 28);
            this.btnStop.TabIndex = 4;
            this.btnStop.Text = "Stop";
            // 
            // btnRecipe
            // 
            this.btnRecipe.Location = new System.Drawing.Point(190, 225);
            this.btnRecipe.Name = "btnRecipe";
            this.btnRecipe.Size = new System.Drawing.Size(80, 28);
            this.btnRecipe.TabIndex = 5;
            this.btnRecipe.Text = "Recipe";
            // 
            // ChamberDetailForm
            // 
            this.Controls.Add(this.lblTitle);
            this.Controls.Add(this.leftPanel);
            this.Controls.Add(this.panelPvSv);
            this.Controls.Add(this.btnStart);
            this.Controls.Add(this.btnStop);
            this.Controls.Add(this.btnRecipe);
            this.Name = "ChamberDetailForm";
            this.Size = new System.Drawing.Size(600, 260);
            this.leftPanel.ResumeLayout(false);
            this.leftPanel.PerformLayout();
            this.ResumeLayout(false);
            this.PerformLayout();

        }
    }
}
