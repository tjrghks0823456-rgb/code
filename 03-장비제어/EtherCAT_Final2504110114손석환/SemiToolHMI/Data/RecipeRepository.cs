using System;
using System.Collections.Generic;
using System.Data.SQLite;
using SemiToolHMI.Models;

namespace SemiToolHMI.Data
{
    public class RecipeRepository
    {
        private readonly string connStr = "Data Source=semitoolhmi.db;Version=3;";

        public RecipeRepository()
        {
            InitializeDB();
        }

        // ==========================================
        // DB 및 테이블 생성
        // ==========================================
        private void InitializeDB()
        {
            using (var conn = new SQLiteConnection(connStr))
            {
                conn.Open();

                string sql1 = @"
                CREATE TABLE IF NOT EXISTS recipe_header(
                    recipe_id    INTEGER PRIMARY KEY AUTOINCREMENT,
                    recipe_name  TEXT,
                    chamber_type TEXT,
                    total_steps  INTEGER
                );";

                string sql2 = @"
                CREATE TABLE IF NOT EXISTS recipe_step(
                    step_id     INTEGER PRIMARY KEY AUTOINCREMENT,
                    recipe_id   INTEGER,
                    step_no     INTEGER,
                    mode        TEXT,
                    time_s      INTEGER,
                    o2_sv       REAL,
                    gas_a_sv    REAL,
                    gas_b_sv    REAL,
                    press_sv    REAL,
                    temp_sv     REAL,
                    rf_sv       REAL,
                    liquid_sv   REAL,
                    n2_sv       REAL
                );";

                new SQLiteCommand(sql1, conn).ExecuteNonQuery();
                new SQLiteCommand(sql2, conn).ExecuteNonQuery();

                // ★ 기존 DB 호환성용: 컬럼이 없으면 추가 (간이 마이그레이션)
                try
                {
                    string alterSql = "ALTER TABLE recipe_step ADD COLUMN rf_sv REAL DEFAULT 0;";
                    new SQLiteCommand(alterSql, conn).ExecuteNonQuery();
                }
                catch (Exception)
                {
                    // 이미 컬럼이 존재하면 에러 발생하므로 무시
                }
            }
        }

        // ==========================================
        // 1) 레시피 리스트
        // ==========================================
        public List<(int id, string name)> GetRecipeList()
        {
            var list = new List<(int, string)>();

            using (var conn = new SQLiteConnection(connStr))
            {
                conn.Open();

                string sql =
                    "SELECT recipe_id, recipe_name FROM recipe_header ORDER BY recipe_id;";

                using (var cmd = new SQLiteCommand(sql, conn))
                using (var rd = cmd.ExecuteReader())
                {
                    while (rd.Read())
                    {
                        list.Add((Convert.ToInt32(rd["recipe_id"]),
                                  rd["recipe_name"].ToString()));
                    }
                }
            }
            return list;
        }

        // ==========================================
        // 1-2) 챔버별 레시피 목록
        // ==========================================
        public List<(int id, string name)> GetRecipeListByChamber(string chamber)
        {
            var list = new List<(int, string)>();

            using (var conn = new SQLiteConnection(connStr))
            {
                conn.Open();

                string sql =
                    @"SELECT recipe_id, recipe_name 
                      FROM recipe_header
                      WHERE chamber_type=@chamber
                      ORDER BY recipe_id;";

                using (var cmd = new SQLiteCommand(sql, conn))
                {
                    cmd.Parameters.AddWithValue("@chamber", chamber);

                    using (var rd = cmd.ExecuteReader())
                    {
                        while (rd.Read())
                        {
                            list.Add((Convert.ToInt32(rd["recipe_id"]),
                                      rd["recipe_name"].ToString()));
                        }
                    }
                }
            }
            return list;
        }

        // ==========================================
        // 1-3) 전체 레시피 목록 (ID, Name, Chamber)
        // ==========================================
        public List<(int id, string name, string chamber)> GetFullRecipeList()
        {
            var list = new List<(int, string, string)>();

            using (var conn = new SQLiteConnection(connStr))
            {
                conn.Open();
                string sql =
                    "SELECT recipe_id, recipe_name, chamber_type FROM recipe_header ORDER BY recipe_id;";

                using (var cmd = new SQLiteCommand(sql, conn))
                using (var rd = cmd.ExecuteReader())
                {
                    while (rd.Read())
                    {
                        list.Add((Convert.ToInt32(rd["recipe_id"]),
                                  rd["recipe_name"].ToString(),
                                  rd["chamber_type"].ToString()));
                    }
                }
            }
            return list;
        }

        // ==========================================
        // 2) 레시피 로드 (헤더 + 스텝)
        // ==========================================
        public (string name, string chamber, List<RecipeStep> steps) LoadRecipe(int recipeId)
        {
            string name = "";
            string chamber = "";
            var steps = new List<RecipeStep>();

            using (var conn = new SQLiteConnection(connStr))
            {
                conn.Open();

                // Header
                string sqlHeader =
                    @"SELECT recipe_name, chamber_type 
                      FROM recipe_header 
                      WHERE recipe_id=@id";

                using (var cmd = new SQLiteCommand(sqlHeader, conn))
                {
                    cmd.Parameters.AddWithValue("@id", recipeId);

                    using (var rd = cmd.ExecuteReader())
                    {
                        if (rd.Read())
                        {
                            name = rd["recipe_name"].ToString();
                            chamber = rd["chamber_type"].ToString();
                        }
                    }
                }

                // Steps
                string sqlStep =
                    @"SELECT * 
                      FROM recipe_step 
                      WHERE recipe_id=@id
                      ORDER BY step_no ASC;";

                using (var cmd = new SQLiteCommand(sqlStep, conn))
                {
                    cmd.Parameters.AddWithValue("@id", recipeId);

                    using (var rd = cmd.ExecuteReader())
                    {
                        while (rd.Read())
                        {
                            steps.Add(new RecipeStep
                            {
                                StepId = Convert.ToInt32(rd["step_id"]),
                                RecipeId = recipeId,
                                StepNo = Convert.ToInt32(rd["step_no"]),
                                Mode = rd["mode"].ToString(),
                                Time_s = Convert.ToInt32(rd["time_s"]),
                                O2_SV = GetDoubleSafe(rd, "o2_sv"),
                                NF3_SV = GetDoubleSafe(rd, "gas_a_sv"),
                                CF4_SV = GetDoubleSafe(rd, "gas_b_sv"),
                                Press_SV = GetDoubleSafe(rd, "press_sv"),
                                Temp_SV = GetDoubleSafe(rd, "temp_sv"),
                                RF_SV = GetDoubleSafe(rd, "rf_sv"),
                                Liquid_SV = GetDoubleSafe(rd, "liquid_sv"),
                                N2_SV = GetDoubleSafe(rd, "n2_sv")
                            });
                        }
                    }
                }
            }

            return (name, chamber, steps);
        }

        private double GetDoubleSafe(SQLiteDataReader rd, string colName)
        {
            try
            {
                int ord = rd.GetOrdinal(colName);
                return rd.IsDBNull(ord) ? 0.0 : rd.GetDouble(ord);
            }
            catch (IndexOutOfRangeException)
            {
                return 0.0;
            }
        }

        // ==========================================
        // 3) Insert Header
        // ==========================================
        public int InsertRecipeHeader(string name, string chamber, int totalSteps)
        {
            using (var conn = new SQLiteConnection(connStr))
            {
                conn.Open();

                string sql =
                    @"INSERT INTO recipe_header
                      (recipe_name, chamber_type, total_steps)
                      VALUES (@name, @chamber, @steps);
                      SELECT last_insert_rowid();";

                using (var cmd = new SQLiteCommand(sql, conn))
                {
                    cmd.Parameters.AddWithValue("@name", name);
                    cmd.Parameters.AddWithValue("@chamber", chamber);
                    cmd.Parameters.AddWithValue("@steps", totalSteps);
                    return Convert.ToInt32(cmd.ExecuteScalar());
                }
            }
        }

        // ==========================================
        // 4) Update Header
        // ==========================================
        public void UpdateRecipeHeader(int id, string name, string chamber, int totalSteps)
        {
            using (var conn = new SQLiteConnection(connStr))
            {
                conn.Open();

                string sql =
                    @"UPDATE recipe_header
                      SET recipe_name=@name,
                          chamber_type=@chamber,
                          total_steps=@steps
                      WHERE recipe_id=@id";

                using (var cmd = new SQLiteCommand(sql, conn))
                {
                    cmd.Parameters.AddWithValue("@name", name);
                    cmd.Parameters.AddWithValue("@chamber", chamber);
                    cmd.Parameters.AddWithValue("@steps", totalSteps);
                    cmd.Parameters.AddWithValue("@id", id);
                    cmd.ExecuteNonQuery();
                }
            }
        }

        // ==========================================
        // 5) Step Insert
        // ==========================================
        private void InsertStep(RecipeStep s)
        {
            using (var conn = new SQLiteConnection(connStr))
            {
                conn.Open();

                string sql =
                    @"INSERT INTO recipe_step
                      (recipe_id, step_no, mode, time_s,
                       o2_sv, gas_a_sv, gas_b_sv, press_sv, temp_sv, rf_sv, liquid_sv, n2_sv)
                      VALUES
                      (@rid, @no, @mode, @time,
                       @o2, @nf3, @cf4, @press, @temp, @rf, @liquid, @n2)";

                using (var cmd = new SQLiteCommand(sql, conn))
                {
                    cmd.Parameters.AddWithValue("@rid", s.RecipeId);
                    cmd.Parameters.AddWithValue("@no", s.StepNo);
                    cmd.Parameters.AddWithValue("@mode", s.Mode);
                    cmd.Parameters.AddWithValue("@time", s.Time_s);
                    cmd.Parameters.AddWithValue("@o2", s.O2_SV);
                    cmd.Parameters.AddWithValue("@nf3", s.NF3_SV);
                    cmd.Parameters.AddWithValue("@cf4", s.CF4_SV);
                    cmd.Parameters.AddWithValue("@press", s.Press_SV);
                    cmd.Parameters.AddWithValue("@temp", s.Temp_SV);
                    cmd.Parameters.AddWithValue("@rf", s.RF_SV);
                    cmd.Parameters.AddWithValue("@liquid", s.Liquid_SV);
                    cmd.Parameters.AddWithValue("@n2", s.N2_SV);

                    cmd.ExecuteNonQuery();
                }
            }
        }

        // ==========================================
        // 6) Replace Steps + 챔버 반영
        // ==========================================
        public void ReplaceSteps(int recipeId, List<RecipeStep> steps, string chamber)
        {
            using (var conn = new SQLiteConnection(connStr))
            {
                conn.Open();

                // Step 전체 삭제
                using (var cmd = new SQLiteCommand("DELETE FROM recipe_step WHERE recipe_id=@id", conn))
                {
                    cmd.Parameters.AddWithValue("@id", recipeId);
                    cmd.ExecuteNonQuery();
                }

                // Step 재삽입
                foreach (var s in steps)
                {
                    s.RecipeId = recipeId;
                    InsertStep(s);
                }

                // Header 업데이트 (total_steps / chamber)
                string sql =
                    @"UPDATE recipe_header
                      SET total_steps=@cnt,
                          chamber_type=@chamber
                      WHERE recipe_id=@id";

                using (var cmd = new SQLiteCommand(sql, conn))
                {
                    cmd.Parameters.AddWithValue("@cnt", steps.Count);
                    cmd.Parameters.AddWithValue("@chamber", chamber);
                    cmd.Parameters.AddWithValue("@id", recipeId);
                    cmd.ExecuteNonQuery();
                }
            }
        }

        // ==========================================
        // 7) RecipeEditorForm 용 래퍼 메서드
        //    (InsertRecipe / UpdateRecipe)
        // ==========================================

        /// <summary>
        /// 새 레시피 저장 (Header + Step 전체)
        /// </summary>
        public int InsertRecipe(string name, string chamber, List<RecipeStep> steps)
        {
            if (steps == null) steps = new List<RecipeStep>();

            // 1) Header 저장 (총 Step 수)
            int recipeId = InsertRecipeHeader(name, chamber, steps.Count);

            // 2) Step 전체 저장 + Header total_steps/chamber 동기화
            ReplaceSteps(recipeId, steps, chamber);

            return recipeId;
        }

        /// <summary>
        /// 기존 레시피 수정 (Header + Step 전체 교체)
        /// </summary>
        public void UpdateRecipe(int recipeId, string name, string chamber, List<RecipeStep> steps)
        {
            if (steps == null) steps = new List<RecipeStep>();

            // 1) Header(이름, 챔버, 총 Step 수) 갱신
            UpdateRecipeHeader(recipeId, name, chamber, steps.Count);

            // 2) Step 전체 교체 + Header total_steps/chamber 동기화
            ReplaceSteps(recipeId, steps, chamber);
        }
    }
}
