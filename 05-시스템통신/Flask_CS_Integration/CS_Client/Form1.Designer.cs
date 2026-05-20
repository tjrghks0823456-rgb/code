using System;
using System.Windows.Forms;
using System.Windows.Forms.DataVisualization.Charting;

namespace flaskConnect
{
    partial class Form1
    {
        private System.ComponentModel.IContainer components = null;

        private Label lblModeTitle;
        private Label lblTempVal;
        private Label lblHumVal;
        private Label lblVibVal;
        private Label lblPresVal;

        private Label lblDoorState;
        private Label lblAlarmState;

        private Button btnToggleDoor;
        private Button btnToggleCooler;
        private Button btnToggleAlarm;

        private Button btnModeNormal;
        private Button btnModeCold;
        private Button btnModeFreeze;

        private Chart chartTemp;


        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
                components.Dispose();
            base.Dispose(disposing);
        }

        private void InitializeComponent()
        {
            this.components = new System.ComponentModel.Container();
            System.Windows.Forms.DataVisualization.Charting.ChartArea chartArea1 = new System.Windows.Forms.DataVisualization.Charting.ChartArea();
            System.Windows.Forms.DataVisualization.Charting.Series series1 = new System.Windows.Forms.DataVisualization.Charting.Series();
            this.lblModeTitle = new System.Windows.Forms.Label();
            this.lblTempVal = new System.Windows.Forms.Label();
            this.lblHumVal = new System.Windows.Forms.Label();
            this.lblVibVal = new System.Windows.Forms.Label();
            this.lblPresVal = new System.Windows.Forms.Label();
            this.lblDoorState = new System.Windows.Forms.Label();
            this.lblAlarmState = new System.Windows.Forms.Label();
            this.btnToggleDoor = new System.Windows.Forms.Button();
            this.btnToggleCooler = new System.Windows.Forms.Button();
            this.btnToggleAlarm = new System.Windows.Forms.Button();
            this.btnModeNormal = new System.Windows.Forms.Button();
            this.btnModeCold = new System.Windows.Forms.Button();
            this.btnModeFreeze = new System.Windows.Forms.Button();
            this.chartTemp = new System.Windows.Forms.DataVisualization.Charting.Chart();
            this.timerBlink = new System.Windows.Forms.Timer(this.components);
            this.lblTempCaption = new System.Windows.Forms.Label();
            this.lblHumCaption = new System.Windows.Forms.Label();
            this.lblVibCaption = new System.Windows.Forms.Label();
            this.lblPresCaption = new System.Windows.Forms.Label();
            this.lblDoorCaption = new System.Windows.Forms.Label();
            this.lblAlarmCaption = new System.Windows.Forms.Label();
            ((System.ComponentModel.ISupportInitialize)(this.chartTemp)).BeginInit();
            this.SuspendLayout();
            // 
            // lblModeTitle
            // 
            this.lblModeTitle.AutoSize = true;
            this.lblModeTitle.Font = new System.Drawing.Font("맑은 고딕", 14F, System.Drawing.FontStyle.Bold);
            this.lblModeTitle.Location = new System.Drawing.Point(20, 55);
            this.lblModeTitle.Name = "lblModeTitle";
            this.lblModeTitle.Size = new System.Drawing.Size(95, 25);
            this.lblModeTitle.TabIndex = 3;
            this.lblModeTitle.Text = "일반 모드";
            // 
            // lblTempVal
            // 
            this.lblTempVal.AutoSize = true;
            this.lblTempVal.Location = new System.Drawing.Point(120, 90);
            this.lblTempVal.Name = "lblTempVal";
            this.lblTempVal.Size = new System.Drawing.Size(33, 12);
            this.lblTempVal.TabIndex = 8;
            this.lblTempVal.Text = "-- ℃";
            // 
            // lblHumVal
            // 
            this.lblHumVal.AutoSize = true;
            this.lblHumVal.Location = new System.Drawing.Point(120, 115);
            this.lblHumVal.Name = "lblHumVal";
            this.lblHumVal.Size = new System.Drawing.Size(31, 12);
            this.lblHumVal.TabIndex = 9;
            this.lblHumVal.Text = "-- %";
            // 
            // lblVibVal
            // 
            this.lblVibVal.AutoSize = true;
            this.lblVibVal.Location = new System.Drawing.Point(120, 140);
            this.lblVibVal.Name = "lblVibVal";
            this.lblVibVal.Size = new System.Drawing.Size(17, 12);
            this.lblVibVal.TabIndex = 10;
            this.lblVibVal.Text = "--";
            // 
            // lblPresVal
            // 
            this.lblPresVal.AutoSize = true;
            this.lblPresVal.Location = new System.Drawing.Point(120, 165);
            this.lblPresVal.Name = "lblPresVal";
            this.lblPresVal.Size = new System.Drawing.Size(42, 12);
            this.lblPresVal.TabIndex = 11;
            this.lblPresVal.Text = "-- kW";
            // 
            // lblDoorState
            // 
            this.lblDoorState.AutoSize = true;
            this.lblDoorState.Location = new System.Drawing.Point(120, 195);
            this.lblDoorState.Name = "lblDoorState";
            this.lblDoorState.Size = new System.Drawing.Size(60, 12);
            this.lblDoorState.TabIndex = 15;
            this.lblDoorState.Text = "전원: OFF";
            // 
            // lblAlarmState
            // 
            this.lblAlarmState.AutoSize = true;
            this.lblAlarmState.Location = new System.Drawing.Point(120, 222);
            this.lblAlarmState.Name = "lblAlarmState";
            this.lblAlarmState.Size = new System.Drawing.Size(74, 12);
            this.lblAlarmState.TabIndex = 17;
            this.lblAlarmState.Text = "ALARM OFF";
            // 
            // btnToggleDoor
            // 
            this.btnToggleDoor.Location = new System.Drawing.Point(30, 280);
            this.btnToggleDoor.Name = "btnToggleDoor";
            this.btnToggleDoor.Size = new System.Drawing.Size(90, 30);
            this.btnToggleDoor.TabIndex = 18;
            this.btnToggleDoor.Text = "전원 토글";
            // 
            // btnToggleCooler
            // 
            this.btnToggleCooler.Location = new System.Drawing.Point(130, 280);
            this.btnToggleCooler.Name = "btnToggleCooler";
            this.btnToggleCooler.Size = new System.Drawing.Size(90, 30);
            this.btnToggleCooler.TabIndex = 19;
            this.btnToggleCooler.Text = "냉각기";
            // 
            // btnToggleAlarm
            // 
            this.btnToggleAlarm.Location = new System.Drawing.Point(230, 280);
            this.btnToggleAlarm.Name = "btnToggleAlarm";
            this.btnToggleAlarm.Size = new System.Drawing.Size(90, 30);
            this.btnToggleAlarm.TabIndex = 20;
            this.btnToggleAlarm.Text = "알람";
            // 
            // btnModeNormal
            // 
            this.btnModeNormal.Location = new System.Drawing.Point(20, 10);
            this.btnModeNormal.Name = "btnModeNormal";
            this.btnModeNormal.Size = new System.Drawing.Size(100, 30);
            this.btnModeNormal.TabIndex = 0;
            this.btnModeNormal.Text = "일반 모드";
            this.btnModeNormal.Click += new System.EventHandler(this.btnModeNormal_Click);
            // 
            // btnModeCold
            // 
            this.btnModeCold.Location = new System.Drawing.Point(130, 10);
            this.btnModeCold.Name = "btnModeCold";
            this.btnModeCold.Size = new System.Drawing.Size(100, 30);
            this.btnModeCold.TabIndex = 1;
            this.btnModeCold.Text = "냉장 모드";
            this.btnModeCold.Click += new System.EventHandler(this.btnModeCold_Click);
            // 
            // btnModeFreeze
            // 
            this.btnModeFreeze.Location = new System.Drawing.Point(240, 10);
            this.btnModeFreeze.Name = "btnModeFreeze";
            this.btnModeFreeze.Size = new System.Drawing.Size(100, 30);
            this.btnModeFreeze.TabIndex = 2;
            this.btnModeFreeze.Text = "냉동 모드";
            this.btnModeFreeze.Click += new System.EventHandler(this.btnModeFreeze_Click);
            // 
            // chartTemp
            // 
            chartArea1.Name = "ChartArea1";
            this.chartTemp.ChartAreas.Add(chartArea1);
            this.chartTemp.Location = new System.Drawing.Point(350, 20);
            this.chartTemp.Name = "chartTemp";
            series1.ChartArea = "ChartArea1";
            series1.ChartType = System.Windows.Forms.DataVisualization.Charting.SeriesChartType.FastLine;
            series1.Name = "온도";
            this.chartTemp.Series.Add(series1);
            this.chartTemp.Size = new System.Drawing.Size(500, 290);
            this.chartTemp.TabIndex = 21;
            // 
            // timerBlink
            // 
            this.timerBlink.Interval = 500;
            this.timerBlink.Tick += new System.EventHandler(this.timerBlink_Tick);
            // 
            // lblTempCaption
            // 
            this.lblTempCaption.AutoSize = true;
            this.lblTempCaption.Location = new System.Drawing.Point(30, 90);
            this.lblTempCaption.Name = "lblTempCaption";
            this.lblTempCaption.Size = new System.Drawing.Size(29, 12);
            this.lblTempCaption.TabIndex = 4;
            this.lblTempCaption.Text = "온도";
            // 
            // lblHumCaption
            // 
            this.lblHumCaption.AutoSize = true;
            this.lblHumCaption.Location = new System.Drawing.Point(30, 115);
            this.lblHumCaption.Name = "lblHumCaption";
            this.lblHumCaption.Size = new System.Drawing.Size(29, 12);
            this.lblHumCaption.TabIndex = 5;
            this.lblHumCaption.Text = "습도";
            // 
            // lblVibCaption
            // 
            this.lblVibCaption.AutoSize = true;
            this.lblVibCaption.Location = new System.Drawing.Point(30, 140);
            this.lblVibCaption.Name = "lblVibCaption";
            this.lblVibCaption.Size = new System.Drawing.Size(29, 12);
            this.lblVibCaption.TabIndex = 6;
            this.lblVibCaption.Text = "진동";
            // 
            // lblPresCaption
            // 
            this.lblPresCaption.AutoSize = true;
            this.lblPresCaption.Location = new System.Drawing.Point(30, 165);
            this.lblPresCaption.Name = "lblPresCaption";
            this.lblPresCaption.Size = new System.Drawing.Size(29, 12);
            this.lblPresCaption.TabIndex = 7;
            this.lblPresCaption.Text = "전력";
            // 
            // lblDoorCaption
            // 
            this.lblDoorCaption.AutoSize = true;
            this.lblDoorCaption.Location = new System.Drawing.Point(30, 195);
            this.lblDoorCaption.Name = "lblDoorCaption";
            this.lblDoorCaption.Size = new System.Drawing.Size(57, 12);
            this.lblDoorCaption.TabIndex = 12;
            this.lblDoorCaption.Text = "전원 상태";
            // 
            // lblAlarmCaption
            // 
            this.lblAlarmCaption.AutoSize = true;
            this.lblAlarmCaption.Location = new System.Drawing.Point(30, 222);
            this.lblAlarmCaption.Name = "lblAlarmCaption";
            this.lblAlarmCaption.Size = new System.Drawing.Size(57, 12);
            this.lblAlarmCaption.TabIndex = 14;
            this.lblAlarmCaption.Text = "알람 상태";
            // 
            // Form1
            // 
            this.ClientSize = new System.Drawing.Size(880, 330);
            this.Controls.Add(this.btnModeNormal);
            this.Controls.Add(this.btnModeCold);
            this.Controls.Add(this.btnModeFreeze);
            this.Controls.Add(this.lblModeTitle);
            this.Controls.Add(this.lblTempCaption);
            this.Controls.Add(this.lblHumCaption);
            this.Controls.Add(this.lblVibCaption);
            this.Controls.Add(this.lblPresCaption);
            this.Controls.Add(this.lblTempVal);
            this.Controls.Add(this.lblHumVal);
            this.Controls.Add(this.lblVibVal);
            this.Controls.Add(this.lblPresVal);
            this.Controls.Add(this.lblDoorCaption);
            this.Controls.Add(this.lblAlarmCaption);
            this.Controls.Add(this.lblDoorState);
            this.Controls.Add(this.lblAlarmState);
            this.Controls.Add(this.btnToggleDoor);
            this.Controls.Add(this.btnToggleCooler);
            this.Controls.Add(this.btnToggleAlarm);
            this.Controls.Add(this.chartTemp);
            this.Name = "Form1";
            this.Text = "PLC 센서 모니터링";
            this.Load += new System.EventHandler(this.Form1_Load);
            ((System.ComponentModel.ISupportInitialize)(this.chartTemp)).EndInit();
            this.ResumeLayout(false);
            this.PerformLayout();

        }

        private Label lblTempCaption;
        private Label lblHumCaption;
        private Label lblVibCaption;
        private Label lblPresCaption;
        private Label lblDoorCaption;
        private Label lblAlarmCaption;
    }
}
