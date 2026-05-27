using System.Drawing;

namespace SemiToolHMI.Controls
{
    partial class FoupDetailForm
    {
        private System.ComponentModel.IContainer components = null;

        private System.Windows.Forms.Label lblTitle;
        private System.Windows.Forms.Label lblPath;
        private System.Windows.Forms.Label lblPPID;
        private System.Windows.Forms.Label lblLotID;
        private System.Windows.Forms.Label lblMID;
        private System.Windows.Forms.Label lblLock;
        private System.Windows.Forms.Label lblWafer;
        private System.Windows.Forms.Label lblRecipe;

        private System.Windows.Forms.Button btnOpen;
        private System.Windows.Forms.Button btnClose;
        private System.Windows.Forms.Button btnClamp;
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
            this.lblPath = new System.Windows.Forms.Label();
            this.lblPPID = new System.Windows.Forms.Label();
            this.lblLotID = new System.Windows.Forms.Label();
            this.lblMID = new System.Windows.Forms.Label();
            this.lblLock = new System.Windows.Forms.Label();
            this.lblWafer = new System.Windows.Forms.Label();
            this.lblRecipe = new System.Windows.Forms.Label();

            this.btnOpen = new System.Windows.Forms.Button();
            this.btnClose = new System.Windows.Forms.Button();
            this.btnClamp = new System.Windows.Forms.Button();
            this.btnRecipe = new System.Windows.Forms.Button();

            this.SuspendLayout();

            // Title
            this.lblTitle.AutoSize = true;
            this.lblTitle.Font = new System.Drawing.Font("Malgun Gothic", 20F, System.Drawing.FontStyle.Bold);
            this.lblTitle.ForeColor = System.Drawing.Color.White;
            this.lblTitle.Location = new System.Drawing.Point(20, 20);
            this.lblTitle.Text = "FOUP Detail";

            int y = 80;

            // Common Style
            Font f = new System.Drawing.Font("Malgun Gothic", 12F);

            this.lblPath.AutoSize = true;
            this.lblPath.ForeColor = System.Drawing.Color.White;
            this.lblPath.Font = f;
            this.lblPath.Location = new System.Drawing.Point(40, y);
            this.lblPath.Text = "Path : ---";
            y += 30;

            this.lblPPID.AutoSize = true;
            this.lblPPID.ForeColor = System.Drawing.Color.White;
            this.lblPPID.Font = f;
            this.lblPPID.Location = new System.Drawing.Point(40, y);
            this.lblPPID.Text = "PPID : ---";
            y += 30;

            this.lblLotID.AutoSize = true;
            this.lblLotID.ForeColor = System.Drawing.Color.White;
            this.lblLotID.Font = f;
            this.lblLotID.Location = new System.Drawing.Point(40, y);
            this.lblLotID.Text = "LOTID : ---";
            y += 30;

            this.lblMID.AutoSize = true;
            this.lblMID.ForeColor = System.Drawing.Color.White;
            this.lblMID.Font = f;
            this.lblMID.Location = new System.Drawing.Point(40, y);
            this.lblMID.Text = "MID : ---";
            y += 30;

            this.lblLock.AutoSize = true;
            this.lblLock.ForeColor = System.Drawing.Color.White;
            this.lblLock.Font = f;
            this.lblLock.Location = new System.Drawing.Point(40, y);
            this.lblLock.Text = "Lock : ---";
            y += 30;

            this.lblWafer.AutoSize = true;
            this.lblWafer.ForeColor = System.Drawing.Color.White;
            this.lblWafer.Font = f;
            this.lblWafer.Location = new System.Drawing.Point(40, y);
            this.lblWafer.Text = "Wafer : 0 / 5";
            y += 30;

            this.lblRecipe.AutoSize = true;
            this.lblRecipe.ForeColor = System.Drawing.Color.White;
            this.lblRecipe.Font = f;
            this.lblRecipe.Location = new System.Drawing.Point(40, y);
            this.lblRecipe.Text = "Recipe : ---";

            // Buttons
            int bx = 40;
            int by = 310;

            this.btnOpen.Text = "Open";
            this.btnOpen.Location = new System.Drawing.Point(bx, by);
            this.btnOpen.Size = new System.Drawing.Size(100, 38);
            this.btnOpen.ForeColor = System.Drawing.Color.White;
            this.btnOpen.BackColor = System.Drawing.Color.FromArgb(70, 72, 80);
            this.btnOpen.FlatStyle = System.Windows.Forms.FlatStyle.Flat;

            this.btnClose.Text = "Close";
            this.btnClose.Location = new System.Drawing.Point(bx + 110, by);
            this.btnClose.Size = new System.Drawing.Size(100, 38);
            this.btnClose.ForeColor = System.Drawing.Color.White;
            this.btnClose.BackColor = System.Drawing.Color.FromArgb(70, 72, 80);
            this.btnClose.FlatStyle = System.Windows.Forms.FlatStyle.Flat;

            this.btnClamp.Text = "Clamp";
            this.btnClamp.Location = new System.Drawing.Point(bx + 220, by);
            this.btnClamp.Size = new System.Drawing.Size(100, 38);
            this.btnClamp.ForeColor = System.Drawing.Color.White;
            this.btnClamp.BackColor = System.Drawing.Color.FromArgb(70, 72, 80);
            this.btnClamp.FlatStyle = System.Windows.Forms.FlatStyle.Flat;

            this.btnRecipe.Text = "Recipe Change";
            this.btnRecipe.Location = new System.Drawing.Point(40, by + 60);
            this.btnRecipe.Size = new System.Drawing.Size(330, 38);
            this.btnRecipe.ForeColor = System.Drawing.Color.White;
            this.btnRecipe.BackColor = System.Drawing.Color.FromArgb(70, 72, 80);
            this.btnRecipe.FlatStyle = System.Windows.Forms.FlatStyle.Flat;

            // Form
            this.ClientSize = new System.Drawing.Size(520, 460);
            this.Controls.Add(this.lblTitle);
            this.Controls.Add(this.lblPath);
            this.Controls.Add(this.lblPPID);
            this.Controls.Add(this.lblLotID);
            this.Controls.Add(this.lblMID);
            this.Controls.Add(this.lblLock);
            this.Controls.Add(this.lblWafer);
            this.Controls.Add(this.lblRecipe);

            this.Controls.Add(this.btnOpen);
            this.Controls.Add(this.btnClose);
            this.Controls.Add(this.btnClamp);
            this.Controls.Add(this.btnRecipe);

            this.FormBorderStyle = System.Windows.Forms.FormBorderStyle.FixedDialog;

            this.ResumeLayout(false);
            this.PerformLayout();
        }
    }
}
