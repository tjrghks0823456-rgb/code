using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Xml.Linq;



    namespace 수강신청시스템
    {
        public class Subject
        {
            public string SubjectCode { get; set; }
            public string SubjectName { get; set; }
            public string Department { get; set; }
            public string ProfessorId { get; set; }

            public Subject(string subjectCode, string subjectName, string department, string professorId)
            {
                SubjectCode = subjectCode;
                SubjectName = subjectName;
                Department = department;
                ProfessorId = professorId;
            }

            public void DisplayInfo()
            {
                Console.WriteLine($"과목코드: {SubjectCode}, 과목명: {SubjectName}, 학과: {Department}, 담당교수번호: {ProfessorId}");
            }
        }
    }

