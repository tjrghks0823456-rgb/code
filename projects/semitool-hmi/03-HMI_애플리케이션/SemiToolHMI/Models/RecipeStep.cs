namespace SemiToolHMI.Models
{
    public class RecipeStep
    {
        public double TimeSec => Time_s;
        public double O2 => O2_SV;
        public double NF3 => NF3_SV;
        public double CF4 => CF4_SV;
        public double Press => Press_SV;
        public double Temp => Temp_SV;
        public double RF => RF_SV;

        public int StepId { get; set; }
        public int RecipeId { get; set; }
        public int StepNo { get; set; }
        public string Mode { get; set; }
        public int Time_s { get; set; }

        // ====== SV 값 ======
        public double O2_SV { get; set; }       // o2_sv
        public double NF3_SV { get; set; }      // gas_a_sv
        public double CF4_SV { get; set; }      // gas_b_sv
        public double Press_SV { get; set; }    // press_sv
        public double Temp_SV { get; set; }     // temp_sv
        public double RF_SV { get; set; }       // rf_sv

        // 세정 챔버용(필요 시)
        public double Liquid_SV { get; set; }
        public double N2_SV { get; set; }
    }
}
