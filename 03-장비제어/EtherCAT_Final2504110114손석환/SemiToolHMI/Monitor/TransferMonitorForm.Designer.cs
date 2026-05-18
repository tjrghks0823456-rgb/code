using System;
using System.ComponentModel;
using System.Drawing;
using System.Windows.Forms;

namespace SemiToolHMI.Monitor
{
    partial class TransferMonitorForm
    {
        private IContainer components = null;
        private Label lblRobotJob;
        private DataGridView grid;

        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
            {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        #region Windows Form Designer generated code

        private void InitializeComponent()
        {
            this.components = new System.ComponentModel.Container();
            this.lblRobotJob = new System.Windows.Forms.Label();
            this.grid = new System.Windows.Forms.DataGridView();
            ((System.ComponentModel.ISupportInitialize)(this.grid)).BeginInit();
            this.SuspendLayout();
            // 
            // lblRobotJob
            // 
            this.lblRobotJob.BackColor = System.Drawing.Color.FromArgb(40, 42, 50);
            this.lblRobotJob.Dock = System.Windows.Forms.DockStyle.Top;
            this.lblRobotJob.Font = new System.Drawing.Font("Malgun Gothic", 9F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(129)));
            this.lblRobotJob.ForeColor = System.Drawing.Color.White;
            this.lblRobotJob.Location = new System.Drawing.Point(0, 0);
            this.lblRobotJob.Name = "lblRobotJob";
            this.lblRobotJob.Padding = new System.Windows.Forms.Padding(10, 0, 0, 0);
            this.lblRobotJob.Size = new System.Drawing.Size(640, 28);
            this.lblRobotJob.TabIndex = 0;
            this.lblRobotJob.Text = "TM: Idle";
            this.lblRobotJob.TextAlign = System.Drawing.ContentAlignment.MiddleLeft;
            // 
            // grid
            // 
            this.grid.AllowUserToAddRows = false;
            this.grid.AllowUserToDeleteRows = false;
            this.grid.AllowUserToResizeRows = false;
            this.grid.BackgroundColor = System.Drawing.Color.White;
            this.grid.BorderStyle = System.Windows.Forms.BorderStyle.None;
            this.grid.Dock = System.Windows.Forms.DockStyle.Fill;
            this.grid.EnableHeadersVisualStyles = false;
            this.grid.Location = new System.Drawing.Point(0, 28);
            this.grid.MultiSelect = false;
            this.grid.Name = "grid";
            this.grid.ReadOnly = true;
            this.grid.RowHeadersVisible = false;
            this.grid.SelectionMode = System.Windows.Forms.DataGridViewSelectionMode.FullRowSelect;
            this.grid.TabIndex = 1;

            // ===== 헤더 스타일 =====
            DataGridViewCellStyle headerStyle = new DataGridViewCellStyle();
            headerStyle.Alignment = DataGridViewContentAlignment.MiddleCenter;
            headerStyle.BackColor = Color.FromArgb(45, 47, 60);
            headerStyle.ForeColor = Color.White;
            headerStyle.Font = new Font("Malgun Gothic", 9F, FontStyle.Bold);
            headerStyle.SelectionBackColor = Color.FromArgb(45, 47, 60);
            headerStyle.SelectionForeColor = Color.White;
            this.grid.ColumnHeadersDefaultCellStyle = headerStyle;

            // ===== 공통 셀 스타일 (검은 글씨) =====
            DataGridViewCellStyle baseCellStyle = new DataGridViewCellStyle();
            baseCellStyle.BackColor = Color.White;                    // 평상시 흰 배경
            baseCellStyle.ForeColor = Color.Black;                    // 평상시 검은 글씨
            baseCellStyle.SelectionBackColor = Color.FromArgb(0, 120, 215); // 선택 파란 배경
            baseCellStyle.SelectionForeColor = Color.Black;           // 선택 시에도 검은 글씨
            baseCellStyle.Font = new Font("Malgun Gothic", 9F, FontStyle.Regular);

            this.grid.DefaultCellStyle = baseCellStyle;
            this.grid.RowsDefaultCellStyle = baseCellStyle;

            // 교차 행(Alt row)도 흰 배경 + 검은 글씨
            DataGridViewCellStyle altStyle = baseCellStyle.Clone() as DataGridViewCellStyle;
            altStyle.BackColor = Color.FromArgb(240, 240, 240);
            this.grid.AlternatingRowsDefaultCellStyle = altStyle;

            // ===== 컬럼 추가 (컬럼에도 같은 스타일 강제) =====
            this.grid.Columns.Clear();

            DataGridViewTextBoxColumn colLoc = new DataGridViewTextBoxColumn();
            colLoc.HeaderText = "Location";
            colLoc.Name = "colLoc";
            colLoc.ReadOnly = true;
            colLoc.Width = 220;
            colLoc.DefaultCellStyle = baseCellStyle;   // ← 여기 중요

            DataGridViewTextBoxColumn colStatus = new DataGridViewTextBoxColumn();
            colStatus.HeaderText = "Status";
            colStatus.Name = "colStatus";
            colStatus.ReadOnly = true;
            colStatus.AutoSizeMode = DataGridViewAutoSizeColumnMode.Fill;
            colStatus.DefaultCellStyle = baseCellStyle; // ← 여기도

            this.grid.Columns.AddRange(new DataGridViewColumn[] { colLoc, colStatus });

            // 
            // TransferMonitorForm
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(7F, 12F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.BackColor = System.Drawing.Color.FromArgb(24, 26, 32);
            this.ClientSize = new System.Drawing.Size(640, 360);
            this.Controls.Add(this.grid);
            this.Controls.Add(this.lblRobotJob);
            this.Name = "TransferMonitorForm";
            this.Text = "Transfer Monitor";
            ((System.ComponentModel.ISupportInitialize)(this.grid)).EndInit();
            this.ResumeLayout(false);
        }

        #endregion
    }
}
