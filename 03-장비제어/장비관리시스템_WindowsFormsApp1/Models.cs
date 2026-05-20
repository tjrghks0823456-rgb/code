using System;

namespace WindowsFormsApp1
{
    // 장비 정보를 담는 그릇 (Model)
    public class Equipment
    {
        public int Id { get; set; }
        public string Name { get; set; }
        public string Category { get; set; }
        public string Status { get; set; } // "정상", "대여중", "고장"
        public string User { get; set; }
        public DateTime LastUpdate { get; set; }

        // 추가된 정보: 반납 예정일 / 수리 완료 예정일
        // 물음표(?)는 값이 없을 수도 있다는 뜻입니다 (Null 허용)
        public DateTime? DueDate { get; set; } 
        public DateTime? RepairEstimate { get; set; }

        // 리스트뷰에 보여주기 편하게 배열로 변환하는 함수
        public string[] ToListViewItem()
        {
            // 남은 시간 계산을 위한 변수
            string timeRemaining = "-";
            string scheduledDate = "-";

            if (Status == "대여중" && DueDate != null)
            {
                scheduledDate = DueDate.Value.ToString("MM-dd HH:mm");
                TimeSpan diff = DueDate.Value - DateTime.Now;
                
                if (diff.TotalSeconds < 0)
                    timeRemaining = "연체됨";
                else
                    timeRemaining = $"{diff.Days}일 {diff.Hours}시간 남음";
            }
            else if (Status == "고장" && RepairEstimate != null)
            {
                scheduledDate = RepairEstimate.Value.ToString("MM-dd HH:mm");
                TimeSpan diff = RepairEstimate.Value - DateTime.Now;
                
                if (diff.TotalSeconds < 0)
                    timeRemaining = "수리 지연";
                else
                    timeRemaining = $"{diff.Days}일 {diff.Hours}시간 남음";
            }

            return new string[] { Name, Category, Status, User, scheduledDate, timeRemaining };
        }
    }

    // 이력(로그) 정보를 담는 그릇 (Model)
    public class History
    {
        public int Id { get; set; }
        public string Action { get; set; } // "대여", "반납", "고장신고", "수리완료"
        public string EquipmentName { get; set; }
        public string Actor { get; set; } // 수행한 사람
        public DateTime Timestamp { get; set; }

        public string[] ToListViewItem()
        {
            string displayActor = Actor;
            string displayReason = "";

            // '관리자(사유)' 형식인 경우 분리
            if (!string.IsNullOrEmpty(Actor) && Actor.Contains("(") && Actor.EndsWith(")"))
            {
                int start = Actor.IndexOf("(") + 1;
                int end = Actor.LastIndexOf(")"); // Use LastIndexOf just in case
                if (end > start)
                {
                    displayReason = Actor.Substring(start, end - start);
                    displayActor = Actor.Substring(0, start - 1);
                }
            }

            return new string[] { Timestamp.ToString("yyyy-MM-dd HH:mm:ss"), Action, EquipmentName, displayActor, displayReason };
        }
    }

    // 사용자 정보를 담는 그릇 (Model)
    public class User
    {
        public int Id { get; set; }
        public string Username { get; set; }
        public string Password { get; set; }
        public DateTime CreatedAt { get; set; }

        public string[] ToListViewItem()
        {
            return new string[] { Id.ToString(), Username, Password, CreatedAt.ToString("yyyy-MM-dd HH:mm") };
        }
    }
}
