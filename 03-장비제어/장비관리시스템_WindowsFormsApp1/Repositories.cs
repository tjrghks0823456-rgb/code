using System;
using System.Collections.Generic;

using MySql.Data.MySqlClient;

namespace WindowsFormsApp1
{
    // =====================================================================
    // DbManager
    //  - "문을 여는 열쇠" 역할
    //  - MySQL 데이터베이스에 연결(문 열기)할 때마다 이 클래스를 통해 연결 객체를 만든다.
    // =====================================================================
    public static class DbManager
    {
        // 데이터베이스에 어떻게 접속할지 적어둔 "주소 + 아이디 + 비밀번호" 정보
        // → 전화기로 치면 "전화번호부"에 저장한 한 줄 정보라고 보면 됨.
        //
        // Server=localhost  : 내 컴퓨터(로컬)에 있는 MySQL 서버에 접속
        // Database=equipmentdb : equipmentdb 라는 이름의 데이터베이스에 접속
        // Uid=root           : 접속할 때 사용할 MySQL 계정 아이디
        // Pwd=puppy235**     : 그 계정의 비밀번호
        //
        // ※ 실제로 배포할 때는 코드에 직접 비밀번호를 쓰지 않고, 설정파일로 빼는 것이 좋음
        private static string ConnectionString = "Server=localhost;Database=equipmentdb;Uid=root;Pwd=puppy235**;";

        // 항상 이 함수를 통해서만 MySqlConnection 객체를 만든다.
        // → 이유: 나중에 비밀번호나 서버 주소가 바뀌어도 이 코드 한 줄만 고치면 되기 때문.
        public static MySqlConnection GetConnection()
        {
            // ConnectionString 정보를 사용해서 "연결 객체" 하나 만들어서 돌려준다.
            return new MySqlConnection(ConnectionString);
        }
    }

    // =====================================================================
    // EquipmentRepository
    //  - 장비(equipment) 테이블과 관련된 모든 DB 작업을 여기서 처리
    //  - 예: 전체 조회, 검색, 대여, 반납, 고장 신고, 수리 완료, 상태 통계
    //  - 폼(Form) 쪽에서는 SQL을 직접 쓰지 않고, 이 클래스의 함수만 호출하도록 설계
    // =====================================================================
    public class EquipmentRepository
    {
        // -------------------------------------------------------------
        // AddEquipment
        //  - 신규 장비를 equipment 테이블에 등록
        //  - 새로 등록되는 장비는 바로 사용할 수 있는 상태이므로
        //    기본 상태를 '정상', 사용자를 '-' 로 저장한다.
        // -------------------------------------------------------------
        public void AddEquipment(string equipmentName, string category)
        {
            if (string.IsNullOrWhiteSpace(equipmentName))
                throw new Exception("장비명을 입력하세요.");

            if (string.IsNullOrWhiteSpace(category))
                throw new Exception("장비 종류를 입력하세요.");

            string name = equipmentName.Trim();
            string trimmedCategory = category.Trim();

            using (var conn = DbManager.GetConnection())
            {
                conn.Open();

                string duplicateCheckQuery =
                    "SELECT COUNT(*) FROM equipment WHERE name=@name";

                using (var checkCmd = new MySqlCommand(duplicateCheckQuery, conn))
                {
                    checkCmd.Parameters.AddWithValue("@name", name);

                    int duplicateCount = Convert.ToInt32(checkCmd.ExecuteScalar());
                    if (duplicateCount > 0)
                        throw new Exception("이미 등록된 장비명입니다.");
                }

                string insertQuery =
                    "INSERT INTO equipment " +
                    "(name, category, status, user, last_update, due_date, repair_estimate) " +
                    "VALUES (@name, @category, '정상', '-', NOW(), NULL, NULL)";

                using (var insertCmd = new MySqlCommand(insertQuery, conn))
                {
                    insertCmd.Parameters.AddWithValue("@name", name);
                    insertCmd.Parameters.AddWithValue("@category", trimmedCategory);
                    insertCmd.ExecuteNonQuery();
                }
            }
        }

        // -------------------------------------------------------------
        // SelectAll
        //  - equipment 테이블에 있는 모든 장비를 가져오는 함수
        //  - 결과는 List<Equipment> 형태로 돌려준다.
        // -------------------------------------------------------------
        public List<Equipment> SelectAll()
        {
            // 결과를 담을 리스트
            List<Equipment> list = new List<Equipment>();

            // 모든 컬럼을 선택하고, id 순서대로 정렬해서 가져오는 SQL문
            string query = "SELECT * FROM equipment ORDER BY id ASC";

            // using 블록을 쓰는 이유:
            //  - 데이터베이스 연결과 명령, 리더(reader)는 사용이 끝나면
            //    자동으로 Dispose(정리)되도록 하기 위해서
            using (var conn = DbManager.GetConnection()) // DB 연결 객체 생성
            {
                conn.Open(); // 실제로 DB 문 여는 순간

                // SQL문과 연결 객체를 이용해 명령 객체 생성
                using (var cmd = new MySqlCommand(query, conn))
                // ExecuteReader()로 결과를 "한 줄씩 읽기 모드"로 가져온다.
                using (var reader = cmd.ExecuteReader())
                {
                    // reader.Read()는 한 줄을 읽을 수 있으면 true, 더 이상 없으면 false
                    while (reader.Read())
                    {
                        // 한 줄(한 장비 정보)을 Equipment 객체로 만들어 리스트에 추가
                        list.Add(new Equipment
                        {
                            // DB의 id 컬럼 값을 int로 변환
                            Id = Convert.ToInt32(reader["id"]),
                            // 문자열 컬럼들은 ToString()으로 가져옴
                            Name = reader["name"].ToString(),
                            Category = reader["category"].ToString(),
                            Status = reader["status"].ToString(),
                            User = reader["user"].ToString(),
                            // 마지막 수정 시간은 DateTime으로 변환
                            LastUpdate = Convert.ToDateTime(reader["last_update"]),

                            // -----------------------------
                            // Nullable(DateTime?) 처리
                            //  - DB 값이 비어 있으면(DBNull) C#의 null 로 바꿔줌
                            //  - 비어 있지 않으면 실제 날짜 값으로 변환
                            // -----------------------------
                            DueDate = reader["due_date"] == DBNull.Value
                                ? (DateTime?)null
                                : Convert.ToDateTime(reader["due_date"]),

                            RepairEstimate = reader["repair_estimate"] == DBNull.Value
                                ? (DateTime?)null
                                : Convert.ToDateTime(reader["repair_estimate"])
                        });
                    }
                }
            }

            // 최종적으로 전체 장비 목록 반환
            return list;
        }

        // -------------------------------------------------------------
        // SelectByKeyword
        //  - 사용자가 입력한 키워드가
        //    장비 이름(name) 또는 카테고리(category)에 포함된 장비만 검색
        //  - LIKE와 파라미터(@key)를 사용하여 SQL Injection(해킹) 방지
        // -------------------------------------------------------------
        public List<Equipment> SelectByKeyword(string keyword)
        {
            List<Equipment> list = new List<Equipment>();

            // name 또는 category 컬럼에 키워드가 포함된 것만 찾는 SQL
            string query = "SELECT * FROM equipment WHERE name LIKE @key OR category LIKE @key";

            using (var conn = DbManager.GetConnection())
            {
                conn.Open();
                using (var cmd = new MySqlCommand(query, conn))
                {
                    // 파라미터 @key에 실제 값 설정
                    //  - %키워드% 형태로 넣어서 "포함 검색"이 되도록 함
                    cmd.Parameters.AddWithValue("@key", "%" + keyword + "%");

                    using (var reader = cmd.ExecuteReader())
                    {
                        while (reader.Read())
                        {
                            list.Add(new Equipment
                            {
                                Id = Convert.ToInt32(reader["id"]),
                                Name = reader["name"].ToString(),
                                Category = reader["category"].ToString(),
                                Status = reader["status"].ToString(),
                                User = reader["user"].ToString(),
                                LastUpdate = Convert.ToDateTime(reader["last_update"]),
                                // 여기에서도 예정일/수리예정일은 비어 있을 수 있으므로 DBNull 체크
                                DueDate = reader["due_date"] == DBNull.Value
                                    ? (DateTime?)null
                                    : Convert.ToDateTime(reader["due_date"]),
                                RepairEstimate = reader["repair_estimate"] == DBNull.Value
                                    ? (DateTime?)null
                                    : Convert.ToDateTime(reader["repair_estimate"])
                            });
                        }
                    }
                }
            }
            return list;
        }

        // -------------------------------------------------------------
        // Rent
        //  - 장비 대여 처리
        //  - 파라미터:
        //      equipmentName : 어떤 장비를 빌릴지 (장비 이름)
        //      userName      : 누가 빌리는지 (사용자 이름)
        //      dueDate       : 언제까지 빌릴지 (반납 예정일)
        //  - 기능:
        //      1) status 를 '대여중' 으로 변경
        //      2) user 에 대여자 이름 저장
        //      3) last_update 를 지금 시간(NOW)으로 설정
        //      4) due_date 에 반납 예정일 저장
        //      5) status 가 '정상' 인 장비만 빌릴 수 있게 조건 추가
        // -------------------------------------------------------------
        public void Rent(string equipmentName, string userName, DateTime dueDate)
        {
            string query =
                "UPDATE equipment " +
                "SET status='대여중', user=@user, last_update=NOW(), due_date=@dueDate " +
                "WHERE name=@name AND status='정상'";

            using (var conn = DbManager.GetConnection())
            {
                conn.Open();
                using (var cmd = new MySqlCommand(query, conn))
                {
                    // @user, @name, @dueDate 파라미터에 실제 값 넣기
                    cmd.Parameters.AddWithValue("@user", userName);
                    cmd.Parameters.AddWithValue("@name", equipmentName);
                    cmd.Parameters.AddWithValue("@dueDate", dueDate);

                    // ExecuteNonQuery() 결과: 실제로 영향을 받은 행(row)의 개수
                    int rows = cmd.ExecuteNonQuery();

                    // rows 가 0이면:
                    //  - 조건에 맞는 장비가 없다는 뜻
                    //    (이미 대여중이거나, 이름이 틀렸거나, 존재하지 않거나)
                    if (rows == 0)
                        throw new Exception("대여 실패: 이미 대여 중이거나 존재하지 않는 장비입니다.");
                }
            }
        }

        // -------------------------------------------------------------
        // Return
        //  - 장비 반납 처리
        //  - 파라미터:
        //      equipmentName : 어떤 장비를 반납할지 (장비 이름)
        //  - 기능:
        //      1) status 를 '정상' 으로 변경
        //      2) user 를 '-' 로 초기화 (현재 대여자 없음 표시)
        //      3) last_update 를 지금 시간으로 설정
        //      4) due_date 를 다시 NULL 로 초기화 (더 이상 예약된 반납일 없음)
        //      5) status 가 '대여중' 인 장비만 반납 가능하게 조건 추가
        // -------------------------------------------------------------
        public void Return(string equipmentName)
        {
            string query =
                "UPDATE equipment " +
                "SET status='정상', user='-', last_update=NOW(), due_date=NULL " +
                "WHERE name=@name AND status='대여중'";

            using (var conn = DbManager.GetConnection())
            {
                conn.Open();
                using (var cmd = new MySqlCommand(query, conn))
                {
                    cmd.Parameters.AddWithValue("@name", equipmentName);
                    int rows = cmd.ExecuteNonQuery();

                    // 대여중인 장비가 아니면 rows 가 0 이므로 예외 발생
                    if (rows == 0)
                        throw new Exception("반납 실패: 대여 중인 장비가 아닙니다.");
                }
            }
        }

        // -------------------------------------------------------------
        // ReportFault
        //  - 장비 고장 신고
        //  - 파라미터:
        //      equipmentName : 고장난 장비 이름
        //  - 기능:
        //      1) status 를 '고장' 으로 변경
        //      2) user 를 '-' 로 초기화 (사용자 없음)
        //      3) last_update 를 지금 시간으로 설정
        //      4) repair_estimate 에 "3일 뒤" 시간을 자동으로 계산해서 저장
        // -------------------------------------------------------------
        public void ReportFault(string equipmentName)
        {
            string query =
                "UPDATE equipment " +
                "SET status='고장', user='-', last_update=NOW(), " +
                "    repair_estimate=DATE_ADD(NOW(), INTERVAL 3 DAY) " +
                "WHERE name=@name";

            using (var conn = DbManager.GetConnection())
            {
                conn.Open();
                using (var cmd = new MySqlCommand(query, conn))
                {
                    cmd.Parameters.AddWithValue("@name", equipmentName);
                    cmd.ExecuteNonQuery();
                }
            }
        }

        // -------------------------------------------------------------
        // CompleteRepair
        //  - 장비 수리 완료 처리
        //  - 파라미터:
        //      equipmentName : 수리 완료된 장비 이름
        //  - 기능:
        //      1) status 를 '정상' 으로 변경
        //      2) user 를 '-' 로 초기화
        //      3) last_update 를 지금 시간으로 설정
        //      4) repair_estimate 를 NULL 로 초기화
        // -------------------------------------------------------------
        public void CompleteRepair(string equipmentName)
        {
            string query =
                "UPDATE equipment " +
                "SET status='정상', user='-', last_update=NOW(), repair_estimate=NULL " +
                "WHERE name=@name";

            using (var conn = DbManager.GetConnection())
            {
                conn.Open();
                using (var cmd = new MySqlCommand(query, conn))
                {
                    cmd.Parameters.AddWithValue("@name", equipmentName);
                    cmd.ExecuteNonQuery();
                }
            }
        }

        // -------------------------------------------------------------
        // GetStatusCounts
        //  - 장비 상태 별(정상, 대여중, 고장) 개수를 집계해서 Dictionary 로 반환
        //  - 예:
        //      "정상"   -> 10대
        //      "대여중" -> 3대
        //      "고장"   -> 1대
        //
        //  - UI 대시보드에서 "지금 장비 상태"를 요약해서 보여줄 때 사용
        // -------------------------------------------------------------
        public Dictionary<string, int> GetStatusCounts()
        {
            // 미리 "정상", "대여중", "고장" 키를 0 으로 넣어두는 이유:
            //  - DB에 해당 상태가 하나도 없어서 조회 결과에 안 나와도
            //    Dictionary 에서는 항상 0 이라는 값을 갖도록 하기 위해
            var stats = new Dictionary<string, int>
            {
                { "정상", 0 },
                { "대여중", 0 },
                { "고장", 0 }
            };

            string query = "SELECT status, COUNT(*) as cnt FROM equipment GROUP BY status";

            using (var conn = DbManager.GetConnection())
            {
                conn.Open();
                using (var cmd = new MySqlCommand(query, conn))
                using (var reader = cmd.ExecuteReader())
                {
                    while (reader.Read())
                    {
                        string status = reader["status"].ToString();
                        int count = Convert.ToInt32(reader["cnt"]);

                        // 만약 우리가 미리 준비한 상태 중 하나라면 값 덮어쓰기
                        if (stats.ContainsKey(status))
                            stats[status] = count;
                    }
                }
            }
            return stats;
        }
    }

    // =====================================================================
    // HistoryRepository
    //  - history 테이블(이력) 관리
    //  - 누가, 언제, 어떤 장비에 대해, 어떤 행동을 했는지 기록/조회
    // =====================================================================
    public class HistoryRepository
    {
        // -------------------------------------------------------------
        // AddLog
        //  - 이력(history) 테이블에 한 줄 추가
        //  - 파라미터:
        //      action        : 어떤 행동인지 (예: "대여", "반납", "고장신고")
        //      actor         : 누가 했는지 (사용자 이름)
        //      equipmentName : 어떤 장비에 대해 했는지
        //  - DB 컬럼명:
        //      action      -> action
        //      actor(파라미터) -> user (컬럼)
        //      equipmentName -> equip_name (컬럼)
        //      time       -> NOW() (현재 시간)
        // -------------------------------------------------------------
        public void AddLog(string action, string actor, string equipmentName)
        {
            string query =
                "INSERT INTO history (action, user, equip_name, time) " +
                "VALUES (@action, @actor, @equip, NOW())";

            using (var conn = DbManager.GetConnection())
            {
                conn.Open();
                using (var cmd = new MySqlCommand(query, conn))
                {
                    // 파라미터에 값 채워 넣기
                    cmd.Parameters.AddWithValue("@action", action);
                    cmd.Parameters.AddWithValue("@actor", actor);
                    cmd.Parameters.AddWithValue("@equip", equipmentName);

                    cmd.ExecuteNonQuery();
                }
            }
        }

        // -------------------------------------------------------------
        // SelectAll
        //  - history 테이블의 모든 이력을 "최신 순"으로 가져옴
        //  - ORDER BY time DESC : 시간이 큰(최근) 것이 위로 오게 정렬
        // -------------------------------------------------------------
        public List<History> SelectAll()
        {
            List<History> list = new List<History>();

            string query = "SELECT * FROM history ORDER BY time DESC";

            using (var conn = DbManager.GetConnection())
            {
                conn.Open();
                using (var cmd = new MySqlCommand(query, conn))
                using (var reader = cmd.ExecuteReader())
                {
                    while (reader.Read())
                    {
                        list.Add(new History
                        {
                            Id = Convert.ToInt32(reader["id"]),
                            Action = reader["action"].ToString(),
                            // DB 컬럼 user -> History.Actor
                            Actor = reader["user"].ToString(),
                            // DB 컬럼 equip_name -> History.EquipmentName
                            EquipmentName = reader["equip_name"].ToString(),
                            // DB 컬럼 time -> History.Timestamp
                            Timestamp = Convert.ToDateTime(reader["time"])
                        });
                    }
                }
            }
            return list;
        }

        // -------------------------------------------------------------
        // SelectByPeriod
        //  - 특정 기간(start ~ end) 안에 발생한 이력만 조회
        //  - 파라미터:
        //      start : 시작 날짜/시간
        //      end   : 끝 날짜/시간
        //  - WHERE time >= @start AND time <= @end 으로 기간 필터링
        // -------------------------------------------------------------
        public List<History> SelectByPeriod(DateTime start, DateTime end)
        {
            List<History> list = new List<History>();

            string query =
                "SELECT * FROM history " +
                "WHERE time >= @start AND time <= @end " +
                "ORDER BY time DESC";

            using (var conn = DbManager.GetConnection())
            {
                conn.Open();
                using (var cmd = new MySqlCommand(query, conn))
                {
                    // 기간 검색을 위한 파라미터 바인딩
                    cmd.Parameters.AddWithValue("@start", start);
                    cmd.Parameters.AddWithValue("@end", end);

                    using (var reader = cmd.ExecuteReader())
                    {
                        while (reader.Read())
                        {
                            list.Add(new History
                            {
                                Id = Convert.ToInt32(reader["id"]),
                                Action = reader["action"].ToString(),
                                Actor = reader["user"].ToString(),
                                EquipmentName = reader["equip_name"].ToString(),
                                Timestamp = Convert.ToDateTime(reader["time"])
                            });
                        }
                    }
                }
            }
            return list;
        }
    }

    // =====================================================================
    // ScheduleRepository
    //  - 관리자 당번(스케줄) 관리용 저장소
    //  - 어떤 날짜에 어떤 관리자가 근무/당번인지 저장/조회
    // =====================================================================
    public class ScheduleRepository
    {
        // -------------------------------------------------------------
        // 생성자
        //  - 이 클래스가 처음 만들어질 때, manager_schedule 테이블이
        //    없으면 자동으로 만들어 주는 역할
        //  - 즉, "테이블 존재 확인 + 없으면 생성" 기능
        // -------------------------------------------------------------
        public ScheduleRepository()
        {
            using (var conn = DbManager.GetConnection())
            {
                conn.Open();

                // IF NOT EXISTS:
                //  - 이미 테이블이 있으면 아무 일도 안 함
                //  - 없으면 새로 만든다.
                string query =
                    "CREATE TABLE IF NOT EXISTS manager_schedule (" +
                    "  id INT AUTO_INCREMENT PRIMARY KEY, " +   // 고유번호
                    "  date DATE, " +                           // 날짜
                    "  manager_name VARCHAR(50)" +              // 관리자 이름
                    ")";

                using (var cmd = new MySqlCommand(query, conn))
                {
                    cmd.ExecuteNonQuery();
                }
            }
        }

        // -------------------------------------------------------------
        // AddManager
        //  - 특정 날짜에 특정 관리자를 "당번으로 추가"
        //  - 파라미터:
        //      date : 어떤 날짜에
        //      name : 어떤 관리자를
        // -------------------------------------------------------------
        public void AddManager(DateTime date, string name)
        {
            using (var conn = DbManager.GetConnection())
            {
                conn.Open();

                string query =
                    "INSERT INTO manager_schedule (date, manager_name) " +
                    "VALUES (@date, @name)";

                using (var cmd = new MySqlCommand(query, conn))
                {
                    // date.Date 를 사용하는 이유:
                    //  - 시간 정보는 버리고, 날짜만 저장하고 싶기 때문
                    cmd.Parameters.AddWithValue("@date", date.Date);
                    cmd.Parameters.AddWithValue("@name", name);

                    cmd.ExecuteNonQuery();
                }
            }
        }

        // -------------------------------------------------------------
        // RemoveManager
        //  - 특정 날짜에 특정 관리자를 "당번에서 제거"
        //  - 파라미터:
        //      date : 어떤 날짜에서
        //      name : 어떤 관리자를 제거할지
        // -------------------------------------------------------------
        public void RemoveManager(DateTime date, string name)
        {
            using (var conn = DbManager.GetConnection())
            {
                conn.Open();

                string query =
                    "DELETE FROM manager_schedule " +
                    "WHERE date=@date AND manager_name=@name";

                using (var cmd = new MySqlCommand(query, conn))
                {
                    cmd.Parameters.AddWithValue("@date", date.Date);
                    cmd.Parameters.AddWithValue("@name", name);

                    cmd.ExecuteNonQuery();
                }
            }
        }

        // -------------------------------------------------------------
        // GetManagers
        //  - 특정 날짜에 등록된 "관리자 이름 목록"을 가져온다.
        //  - 예:
        //      2025-12-11 → ["홍길동", "김관리"]
        // -------------------------------------------------------------
        public List<string> GetManagers(DateTime date)
        {
            List<string> list = new List<string>();

            using (var conn = DbManager.GetConnection())
            {
                conn.Open();

                string query =
                    "SELECT manager_name FROM manager_schedule " +
                    "WHERE date=@date";

                using (var cmd = new MySqlCommand(query, conn))
                {
                    cmd.Parameters.AddWithValue("@date", date.Date);

                    using (var reader = cmd.ExecuteReader())
                    {
                        while (reader.Read())
                        {
                            // 한 줄에 한 명씩, manager_name 컬럼에서 이름 읽기
                            list.Add(reader["manager_name"].ToString());
                        }
                    }
                }
            }
            return list;
        }

        // -------------------------------------------------------------
        // GetScheduledDates
        //  - manager_schedule 테이블에서 "당번이 있는 날짜들만" 모아서 반환
        //  - DISTINCT 를 사용하는 이유:
        //      같은 날짜에 여러 명이 있어도 날짜는 한 번만 받고 싶기 때문
        // -------------------------------------------------------------
        public List<DateTime> GetScheduledDates()
        {
            List<DateTime> list = new List<DateTime>();

            using (var conn = DbManager.GetConnection())
            {
                conn.Open();

                string query = "SELECT DISTINCT date FROM manager_schedule";

                using (var cmd = new MySqlCommand(query, conn))
                using (var reader = cmd.ExecuteReader())
                {
                    while (reader.Read())
                    {
                        // date 컬럼을 DateTime 으로 변환해서 리스트에 추가
                        list.Add(Convert.ToDateTime(reader["date"]));
                    }
                }
            }
            return list;
        }
    }
    // =====================================================================
    // UserRepository
    //  - 사용자 정보 관리 (로그인, 추가, 삭제, 목록)
    // =====================================================================
    public class UserRepository
    {
        // -------------------------------------------------------------
        // 생성자
        //  - 테이블이 없으면 자동으로 생성
        //  - 관리자 계정이 없으면 자동으로 생성
        // -------------------------------------------------------------
        public UserRepository()
        {
            using (var conn = DbManager.GetConnection())
            {
                conn.Open();

                // 1. users 테이블 생성
                string createTableQuery =
                    "CREATE TABLE IF NOT EXISTS users (" +
                    "  id INT AUTO_INCREMENT PRIMARY KEY, " +
                    "  username VARCHAR(50) NOT NULL UNIQUE, " +
                    "  password VARCHAR(100) NOT NULL, " +
                    "  created_at DATETIME DEFAULT NOW()" +
                    ")";

                using (var cmd = new MySqlCommand(createTableQuery, conn))
                {
                    cmd.ExecuteNonQuery();
                }

                // 2. 초기 관리자 계정 생성 (존재하지 않을 때만)
                string insertAdminQuery = 
                    "INSERT IGNORE INTO users (username, password) VALUES ('admin', '1234')";
                
                using (var cmd = new MySqlCommand(insertAdminQuery, conn))
                {
                    cmd.ExecuteNonQuery();
                }
            }
        }

        // -------------------------------------------------------------
        // ValidateUser
        //  - 로그인 시 아이디/비밀번호 확인
        //  - 성공 시 true, 실패 시 false
        // -------------------------------------------------------------
        public bool ValidateUser(string username, string password)
        {
            string query = "SELECT COUNT(*) FROM users WHERE username=@id AND password=@pw";
            
            using (var conn = DbManager.GetConnection())
            {
                conn.Open();
                using (var cmd = new MySqlCommand(query, conn))
                {
                    cmd.Parameters.AddWithValue("@id", username);
                    cmd.Parameters.AddWithValue("@pw", password);
                    
                    int count = Convert.ToInt32(cmd.ExecuteScalar());
                    return count > 0;
                }
            }
        }

        // -------------------------------------------------------------
        // AddUser
        //  - 새 사용자 추가
        // -------------------------------------------------------------
        public void AddUser(string username, string password)
        {
            // 중복 체크는 DB의 UNIQUE 제약조건에 맡기거나 여기서 미리 SELECT로 확인 가능
            // 여기서는 심플하게 INSERT 시도하고 실패하면 예외 발생하도록 함
            
            string query = "INSERT INTO users (username, password) VALUES (@id, @pw)";

            using (var conn = DbManager.GetConnection())
            {
                conn.Open();
                using (var cmd = new MySqlCommand(query, conn))
                {
                    cmd.Parameters.AddWithValue("@id", username);
                    cmd.Parameters.AddWithValue("@pw", password);
                    cmd.ExecuteNonQuery();
                }
            }
        }

        // -------------------------------------------------------------
        // DeleteUser
        //  - 사용자 삭제 (admin은 삭제 안되도록 방어 로직 추가 가능)
        // -------------------------------------------------------------
        public void DeleteUser(string username)
        {
            if (username.ToLower() == "admin")
            {
                throw new Exception("관리자 계정은 삭제할 수 없습니다.");
            }

            string query = "DELETE FROM users WHERE username=@id";

            using (var conn = DbManager.GetConnection())
            {
                conn.Open();
                using (var cmd = new MySqlCommand(query, conn))
                {
                    cmd.Parameters.AddWithValue("@id", username);
                    cmd.ExecuteNonQuery();
                }
            }
        }

        // -------------------------------------------------------------
        // SelectAll
        //  - 모든 사용자 목록 반환
        // -------------------------------------------------------------
        public List<User> SelectAll()
        {
            List<User> list = new List<User>();
            string query = "SELECT * FROM users ORDER BY id ASC";

            using (var conn = DbManager.GetConnection())
            {
                conn.Open();
                using (var cmd = new MySqlCommand(query, conn))
                using (var reader = cmd.ExecuteReader())
                {
                    while (reader.Read())
                    {
                        list.Add(new User
                        {
                            Id = Convert.ToInt32(reader["id"]),
                            Username = reader["username"].ToString(),
                            Password = reader["password"].ToString(), // 보안상 뺄 수도 있지만 목록에 필요하다면
                            CreatedAt = Convert.ToDateTime(reader["created_at"])
                        });
                    }
                }
            }
            return list;
        }
    }
}
