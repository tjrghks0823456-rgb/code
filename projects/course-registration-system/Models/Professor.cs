using System;
using System.Xml.Linq;
using 수강신청시스템;

namespace 수강신청시스템
{
    public class Professor : Person
    {
        public string ProfessorId { get; set; }

        public Professor(string professorId, string name, string gender, string department, string birthDate, string phoneNumber, string address)
            : base(name, gender, department, birthDate, phoneNumber, address)
        {
            ProfessorId = professorId;
        }

        public override void DisplayInfo()
        {
            Console.Write($"교수번호: {ProfessorId}, ");
            base.DisplayInfo();
        }

        public void CreateSubject(Subject subject)
        {
            Console.WriteLine($"{Name} 교수가 {subject.SubjectName} 과목을 개설합니다.");
        }
    }
}