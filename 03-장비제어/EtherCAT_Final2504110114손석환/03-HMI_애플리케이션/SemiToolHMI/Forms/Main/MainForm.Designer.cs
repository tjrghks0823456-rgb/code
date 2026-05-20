namespace SemiToolHMI
{
    partial class MainForm
    {
        private System.ComponentModel.IContainer components = null;

        /// <summary>
        /// 리소스 정리
        /// </summary>
        /// <param name="disposing"></param>
        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
            {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        #region Windows Form Designer generated code

        /// <summary>
        /// InitializeComponent — 폼 초기화
        /// UI는 전부 MainForm.cs에서 BuildUI()로 구성되므로
        /// Designer에서는 최소한의 설정만 유지해야 함
        /// </summary>
        private void InitializeComponent()
        {
            this.SuspendLayout();
            // 
            // MainForm
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(7F, 12F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(1600, 900);
            this.Name = "MainForm";
            this.Text = "SemiToolHMI";
            this.ResumeLayout(false);

        }

        #endregion
    }
}
