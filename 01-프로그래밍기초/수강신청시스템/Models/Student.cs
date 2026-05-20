using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Xml.Linq;


    namespace 수강신청시스템
    {
        public class Student : Person
        {
            public string StudentId { get; set; }

            public Student(string studentId, string name, string gender, string department, string birthDate, string phoneNumber, string address)
                : base(name, gender, department, birthDate, phoneNumber, address)
            {
                StudentId = studentId;
            }

            public override void DisplayInfo()
            {
                Console.Write($"학번: {StudentId}, ");
                base.DisplayInfo();
            }

            public void EnrollCourse(Course course)
            {
                Console.WriteLine($"{Name} 학생이 {course.SubjectName} 과목을 수강 신청했습니다.");
            }

            public void DropCourse(Course course)
            {
                Console.WriteLine($"{Name} 학생이 {course.SubjectName} 과목 수강 신청을 취소했습니다.");
            }
        }
    }
