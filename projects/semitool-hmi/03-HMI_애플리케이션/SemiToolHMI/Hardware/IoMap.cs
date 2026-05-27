namespace SemiToolHMI.EtherCAT
{
    public static class IoMap
    {
        // ============================
        // Stack Light (P100~P102)
        // ============================
        public const int RED = 0;
        public const int YELLOW = 1;
        public const int GREEN = 2;

        // ============================
        // Chamber A (P103~P105)
        // ============================
        public const int A_LAMP = 3;
        public const int A_DOOR_OPEN = 4;   // 상승 = OPEN
        public const int A_DOOR_CLOSE = 5;   // 하강 = CLOSE

        // ============================
        // Chamber B (P106~P108)
        // ============================
        public const int B_LAMP = 6;
        public const int B_DOOR_OPEN = 7;
        public const int B_DOOR_CLOSE = 8;

        // ============================
        // Chamber C (P109~P111)
        // ============================
        public const int C_LAMP = 9;
        public const int C_DOOR_OPEN = 10;
        public const int C_DOOR_CLOSE = 11;

        // ============================
        // Robot Move
        // ============================
        public const int ROBOT_MOVE_FRONT = 12;
        public const int ROBOT_MOVE_A = 13;
        public const int ROBOT_MOVE_B = 14;
        public const int ROBOT_MOVE_C = 15;

        // ============================
        // FOUP Lock
        // ============================
        public const int FOUP_LOCK = 20;

        // ============================
        // Vacuum / Vent
        // ============================
        public const int VACUUM_ON = 21;
        public const int VENT_ON = 22;

        // ============================
        // Gas (UI Only)
        // ============================
        public const int VALVE_NF3 = -1;
        public const int VALVE_O2 = -1;
        public const int VALVE_CF4 = -1;
    }
}
