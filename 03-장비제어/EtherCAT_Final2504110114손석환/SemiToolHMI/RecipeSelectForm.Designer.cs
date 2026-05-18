namespace SemiToolHMI
{
    partial class RecipeSelectForm
    {
        private System.ComponentModel.IContainer components = null;

        private System.Windows.Forms.ListView list;
        private System.Windows.Forms.Button btnOk;
        private System.Windows.Forms.Button btnCancel;

        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
                components.Dispose();

            base.Dispose(disposing);
        }

        private void InitializeComponent()
        {
            this.list = new System.Windows.Forms.ListView();
            this.btnOk = new System.Windows.Forms.Button();
            this.btnCancel = new System.Windows.Forms.Button();
            this.SuspendLayout();

            // list
            this.list.Location = new System.Drawing.Point(10, 10);
            this.list.Size = new System.Drawing.Size(360, 400);

            // btnOk
            this.btnOk.Text = "OK";
            this.btnOk.Location = new System.Drawing.Point(200, 420);
            this.btnOk.Size = new System.Drawing.Size(70, 28);

            // btnCancel
            this.btnCancel.Text = "Cancel";
            this.btnCancel.Location = new System.Drawing.Point(280, 420);
            this.btnCancel.Size = new System.Drawing.Size(70, 28);

            // Form
            this.ClientSize = new System.Drawing.Size(380, 460);
            this.Controls.Add(this.list);
            this.Controls.Add(this.btnOk);
            this.Controls.Add(this.btnCancel);
            this.FormBorderStyle = System.Windows.Forms.FormBorderStyle.FixedDialog;
            this.StartPosition = System.Windows.Forms.FormStartPosition.CenterParent;
            this.Text = "Select Recipe";

            this.ResumeLayout(false);
        }
    }
}
