using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using MySql.Data.MySqlClient;

namespace SemiToolHMI.Data
{
    public class DatabaseInitializer
    {
        private string baseConnStr = "Server=localhost;Uid=root;Pwd=YOUR_PASSWORD;";
        private string dbName = "semitoolhmi_db";

        public void Initialize()
        {
            CreateDatabase();
            CreateTables();
        }

        private void CreateDatabase()
        {
            using (var conn = new MySqlConnection(baseConnStr))
            {
                conn.Open();

                string sql = $"CREATE DATABASE IF NOT EXISTS {dbName} " +
                             "DEFAULT CHARACTER SET utf8mb4 DEFAULT COLLATE utf8mb4_unicode_ci;";

                using (var cmd = new MySqlCommand(sql, conn))
                {
                    cmd.ExecuteNonQuery();
                }

                Console.WriteLine("[DB] Database OK");
            }
        }

        private void CreateTables()
        {
            string connStr = $"{baseConnStr}Database={dbName};";

            using (var conn = new MySqlConnection(connStr))
            {
                conn.Open();

                string[] tableSqls =
                {
                    // recipe_header
                    @"
                    CREATE TABLE IF NOT EXISTS recipe_header (
                        recipe_id      INT AUTO_INCREMENT PRIMARY KEY,
                        recipe_name    VARCHAR(100) NOT NULL,
                        description    TEXT,
                        chamber_type   ENUM('A','B','C') NOT NULL,
                        total_steps    INT NOT NULL,
                        created_at     DATETIME DEFAULT CURRENT_TIMESTAMP
                    );
                    ",

                    // recipe_step
                    @"
                    CREATE TABLE IF NOT EXISTS recipe_step (
                        step_id     INT AUTO_INCREMENT PRIMARY KEY,
                        recipe_id   INT NOT NULL,
                        step_no     INT NOT NULL,
                        mode        VARCHAR(30),
                        time_s      INT NOT NULL,
                        o2_sv       DOUBLE,
                        gas_a_sv    DOUBLE,
                        gas_b_sv    DOUBLE,
                        press_sv    DOUBLE,
                        temp_sv     DOUBLE,
                        liquid_sv   DOUBLE,
                        n2_sv       DOUBLE,
                        FOREIGN KEY (recipe_id) REFERENCES recipe_header(recipe_id)
                            ON DELETE CASCADE ON UPDATE CASCADE
                    );
                    ",

                    // wafer_lot
                    @"
                    CREATE TABLE IF NOT EXISTS wafer_lot (
                        lot_id        INT AUTO_INCREMENT PRIMARY KEY,
                        lot_name      VARCHAR(50),
                        total_wafers  INT DEFAULT 25,
                        start_time    DATETIME,
                        end_time      DATETIME,
                        status        ENUM('WAIT','RUN','DONE','ERROR') DEFAULT 'WAIT'
                    );
                    ",

                    // wafer_position
                    @"
                    CREATE TABLE IF NOT EXISTS wafer_position (
                        pos_id      INT AUTO_INCREMENT PRIMARY KEY,
                        foup_id     ENUM('A','B') NOT NULL,
                        slot_no     INT NOT NULL,
                        lot_id      INT,
                        wafer_id    INT,
                        present     BOOLEAN DEFAULT FALSE,
                        updated_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (lot_id) REFERENCES wafer_lot(lot_id)
                            ON DELETE SET NULL ON UPDATE CASCADE
                    );
                    ",

                    // wafer_process
                    @"
                    CREATE TABLE IF NOT EXISTS wafer_process (
                        process_id   INT AUTO_INCREMENT PRIMARY KEY,
                        wafer_id     INT NOT NULL,
                        chamber      ENUM('A','B','C'),
                        step_name    VARCHAR(50),
                        start_time   DATETIME,
                        end_time     DATETIME,
                        status       ENUM('WAIT','RUN','DONE','ERROR'),
                        message      TEXT
                    );
                    ",

                    // sensor_log
                    @"
                    CREATE TABLE IF NOT EXISTS equipment_sensor_log (
                        log_id        BIGINT AUTO_INCREMENT PRIMARY KEY,
                        chamber       ENUM('A','B','C') NOT NULL,
                        timestamp     DATETIME NOT NULL,
                        press_pv      DOUBLE,
                        temp_pv       DOUBLE,
                        gas_a_pv      DOUBLE,
                        gas_b_pv      DOUBLE,
                        liquid_pv     DOUBLE,
                        wafer_present BOOLEAN,
                        align_sensor  BOOLEAN
                    );
                    ",

                    // alarm_log
                    @"
                    CREATE TABLE IF NOT EXISTS alarm_log (
                        alarm_id     BIGINT AUTO_INCREMENT PRIMARY KEY,
                        timestamp    DATETIME NOT NULL,
                        equipment    VARCHAR(20),
                        alarm_type   VARCHAR(100),
                        description  TEXT,
                        level        ENUM('WARN','ERROR','FATAL') DEFAULT 'ERROR'
                    );
                    "
                };

                foreach (var sql in tableSqls)
                {
                    using (var cmd = new MySqlCommand(sql, conn))
                        cmd.ExecuteNonQuery();
                }

                Console.WriteLine("[DB] Tables OK");
            }
        }
    }
}

