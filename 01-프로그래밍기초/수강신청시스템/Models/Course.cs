using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Xml.Linq;

namespace 수강신청시스템
{
    public class Course
    {
        public string CourseCode { get; set; }
        public string SubjectName { get; set; }
        public string ProfessorId { get; set; }
        public string ProfessorName { get; set; } // 교수 이름을 저장할 속성
        public string StudentId { get; set; }
        public string StudentName { get; set; }

        public Course(string courseCode, string subjectName, string professorId, string professorName, string studentId, string studentName)
        {
            CourseCode = courseCode;
            SubjectName = subjectName;
            ProfessorId = professorId;
            ProfessorName = professorName; // 생성자에서 교수 이름을 할당합니다.
            StudentId = studentId;
            StudentName = studentName;
        }

        public void DisplayInfo()
        {
            // 출력 시 교수 이름을 사용합니다.
            Console.WriteLine($"수강코드: {CourseCode}, 과목명: {SubjectName}, 교수: {ProfessorName}({ProfessorId}), 학생: {StudentName}({StudentId})");
        }
    }
}