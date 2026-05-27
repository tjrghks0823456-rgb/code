namespace SemiToolHMI.Controls
{
    partial class RecipeEditorForm
    {
        private System.ComponentModel.IContainer components = null;

        private System.Windows.Forms.Label lblName;
        private System.Windows.Forms.TextBox txtName;

        private System.Windows.Forms.Label lblChamber;
        private System.Windows.Forms.ComboBox cmbChamber;

        private System.Windows.Forms.ListView grid;
        private System.Windows.Forms.Button btnAdd;
        private System.Windows.Forms.Button btnSave;
        private System.Windows.Forms.Button btnLoad;   // ★ 추가됨

        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
                components.Dispose();
            base.Dispose(disposing);
        }

        private void InitializeComponent()
        {
            this.lblName = new System.Windows.Forms.Label();
            this.txtName = new System.Windows.Forms.TextBox();
            this.lblChamber = new System.Windows.Forms.Label();
            this.cmbChamber = new System.Windows.Forms.ComboBox();
            this.grid = new System.Windows.Forms.ListView();
            this.btnAdd = new System.Windows.Forms.Button();
            this.btnDelete = new System.Windows.Forms.Button();
            this.btnSave = new System.Windows.Forms.Button();
            this.btnLoad = new System.Windows.Forms.Button();
            this.SuspendLayout();
            // 
            // lblName
            // 
            this.lblName.AutoSize = true;
            this.lblName.ForeColor = System.Drawing.Color.Black;
            this.lblName.Location = new System.Drawing.Point(20, 20);
            this.lblName.Name = "lblName";
            this.lblName.Size = new System.Drawing.Size(86, 12);
            this.lblName.TabIndex = 0;
            this.lblName.Text = "Recipe Name:";
            // 
            // txtName
            // 
            this.txtName.BackColor = System.Drawing.Color.White;
            this.txtName.ForeColor = System.Drawing.Color.White;
            this.txtName.Location = new System.Drawing.Point(150, 17);
            this.txtName.Name = "txtName";
            this.txtName.Size = new System.Drawing.Size(220, 21);
            this.txtName.TabIndex = 1;
            // 
            // lblChamber
            // 
            this.lblChamber.AutoSize = true;
            this.lblChamber.ForeColor = System.Drawing.Color.Black;
            this.lblChamber.Location = new System.Drawing.Point(390, 20);
            this.lblChamber.Name = "lblChamber";
            this.lblChamber.Size = new System.Drawing.Size(61, 12);
            this.lblChamber.TabIndex = 2;
            this.lblChamber.Text = "Chamber:";
            // 
            // cmbChamber
            // 
            this.cmbChamber.BackColor = System.Drawing.Color.FromArgb(((int)(((byte)(55)))), ((int)(((byte)(57)))), ((int)(((byte)(65)))));
            this.cmbChamber.DropDownStyle = System.Windows.Forms.ComboBoxStyle.DropDownList;
            this.cmbChamber.ForeColor = System.Drawing.Color.White;
            this.cmbChamber.Location = new System.Drawing.Point(470, 17);
            this.cmbChamber.Name = "cmbChamber";
            this.cmbChamber.Size = new System.Drawing.Size(120, 20);
            this.cmbChamber.TabIndex = 3;
            // 
            // grid
            // 
            this.grid.BackColor = System.Drawing.Color.White;
            this.grid.ForeColor = System.Drawing.Color.Black;
            this.grid.FullRowSelect = true;
            this.grid.GridLines = true;
            this.grid.HideSelection = false;
            this.grid.Location = new System.Drawing.Point(20, 60);
            this.grid.Name = "grid";
            this.grid.Size = new System.Drawing.Size(940, 460);
            this.grid.TabIndex = 4;
            this.grid.UseCompatibleStateImageBehavior = false;
            this.grid.View = System.Windows.Forms.View.Details;
            // 
            // btnAdd
            // 
            this.btnAdd.BackColor = System.Drawing.Color.SlateGray;
            this.btnAdd.ForeColor = System.Drawing.Color.Black;
            this.btnAdd.Location = new System.Drawing.Point(20, 540);
            this.btnAdd.Name = "btnAdd";
            this.btnAdd.Size = new System.Drawing.Size(120, 30);
            this.btnAdd.TabIndex = 5;
            this.btnAdd.Text = "Add Step";
            this.btnAdd.UseVisualStyleBackColor = false;
            // 
            // btnDelete
            // 
            this.btnDelete.BackColor = System.Drawing.Color.SlateGray;
            this.btnDelete.Location = new System.Drawing.Point(150, 540);
            this.btnDelete.Name = "btnDelete";
            this.btnDelete.Size = new System.Drawing.Size(120, 30);
            this.btnDelete.TabIndex = 6;
            this.btnDelete.Text = "Delete Step";
            this.btnDelete.UseVisualStyleBackColor = false;
            // 
            // btnSave
            // 
            this.btnSave.AutoEllipsis = true;
            this.btnSave.BackColor = System.Drawing.Color.SlateGray;
            this.btnSave.ForeColor = System.Drawing.Color.Black;
            this.btnSave.Location = new System.Drawing.Point(820, 540);
            this.btnSave.Name = "btnSave";
            this.btnSave.Size = new System.Drawing.Size(140, 30);
            this.btnSave.TabIndex = 8;
            this.btnSave.Text = "Save Recipe";
            this.btnSave.UseVisualStyleBackColor = false;
            // 
            // btnLoad
            // 
            this.btnLoad.BackColor = System.Drawing.Color.SlateGray;
            this.btnLoad.ForeColor = System.Drawing.Color.Black;
            this.btnLoad.Location = new System.Drawing.Point(280, 540);
            this.btnLoad.Name = "btnLoad";
            this.btnLoad.Size = new System.Drawing.Size(140, 30);
            this.btnLoad.TabIndex = 7;
            this.btnLoad.Text = "Load Recipe";
            this.btnLoad.UseVisualStyleBackColor = false;
            // 
            // RecipeEditorForm
            // 
            this.BackColor = System.Drawing.Color.Gainsboro;
            this.ClientSize = new System.Drawing.Size(980, 600);
            this.Controls.Add(this.lblName);
            this.Controls.Add(this.txtName);
            this.Controls.Add(this.lblChamber);
            this.Controls.Add(this.cmbChamber);
            this.Controls.Add(this.grid);
            this.Controls.Add(this.btnAdd);
            this.Controls.Add(this.btnDelete);
            this.Controls.Add(this.btnLoad);
            this.Controls.Add(this.btnSave);
            this.FormBorderStyle = System.Windows.Forms.FormBorderStyle.FixedDialog;
            this.Name = "RecipeEditorForm";
            this.Text = "Create / Edit Recipe";
            this.ResumeLayout(false);
            this.PerformLayout();

        }

        private System.Windows.Forms.Button btnDelete;
    }
}
