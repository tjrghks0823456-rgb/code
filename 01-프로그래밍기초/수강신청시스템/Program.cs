using System;
using System.Collections.Generic;
using System.Linq; // 정렬 기능을 위해 추가
using 수강신청시스템; // 정의한 클래스들을 사용하기 위해 네임스페이스 추가

namespace 수강신청시스템
{
    class Program
    {
        // 데이터 저장용 리스트 (전역 변수로 선언하여 모든 메서드에서 접근 가능하도록)
        static List<Professor> professors = new List<Professor>();
        static List<Student> students = new List<Student>();
        static List<Subject> subjects = new List<Subject>();
        static List<Course> courses = new List<Course>();

        // 메뉴를 딕셔너리로 관리
        static Dictionary<int, string> menu = new Dictionary<int, string>()
        {
            {0, "종료"},
            {1, "강의개설"},
            {2, "수강신청"},
            {3, "수강신청 삭제"},
            {4, "개설강의 출력"},
            {5, "수강신청 출력"}
        };

        static void Main(string[] args)
        {
            // 1. 초기 데이터 생성 (교수 3명, 학생 3명)
            InitializeData();

            while (true)
            {
                DisplayMenu();
                Console.Write("메뉴를 선택하세요: ");
                string input = Console.ReadLine();

                if (int.TryParse(input, out int choice))
                {
                    switch (choice)
                    {
                        case 0:
                            Console.WriteLine("수강신청 시스템을 종료합니다.");
                            return;
                        case 1:
                            CreateNewSubject();
                            break;
                        case 2:
                            EnrollCourse();
                            break;
                        case 3:
                            DropCourse();
                            break;
                        case 4:
                            PrintOpenedSubjects();
                            break;
                        case 5:
                            PrintEnrolledCourses();
                            break;
                        default:
                            Console.WriteLine("잘못된 메뉴 선택입니다. 다시 입력해주세요.");
                            break;
                    }
                }
                else
                {
                    Console.WriteLine("유효하지 않은 입력입니다. 숫자를 입력해주세요.");
                }
                Console.WriteLine("\n--------------------\n");
            }
        }

        // 초기 데이터 생성 메서드
        static void InitializeData()
        {
            Console.WriteLine("초기 데이터를 생성 중...");
            // 교수 3명
            professors.Add(new Professor("A1", "장문수", "남", "반도체장비SW과", "1999-99-99", "010-1111-1111", "서울시"));
            professors.Add(new Professor("A2", "최인석", "남", "반도체과", "2000-00-00", "010-2222-2222", "경기도"));
            professors.Add(new Professor("A3", "이혁", "여", "기계공학과", "2111-11-11", "010-3333-3333", "인천시"));

            // 학생 3명
            students.Add(new Student("B1", "손석환", "남", "반도체장비SW과", "2000-01-01", "010-4444-4444", "부산시"));
            students.Add(new Student("B2", "최현수", "여", "전자공학과", "2001-02-02", "010-5555-5555", "대구시"));
            students.Add(new Student("B3", "장준영", "남", "기계공학과", "2002-03-03", "010-6666-6666", "광주시"));

            Console.WriteLine("교수 및 학생 데이터가 생성되었습니다.\n");
        }

        // 메뉴 출력 메서드
        static void DisplayMenu()
        {
            Console.WriteLine("[수강신청 시스템 메뉴]");
            foreach (var item in menu)
            {
                Console.WriteLine($"{item.Key}. {item.Value}");
            }
        }

        // 1. 강의 개설 메서드
        static void CreateNewSubject()
        {
            Console.WriteLine("--- [강의 개설] ---");
            Console.Write("새로운 과목 코드를 입력하세요: ");
            string subjectCode = Console.ReadLine();
            Console.Write("교과목명을 입력하세요: ");
            string subjectName = Console.ReadLine();
            Console.Write("학과명을 입력하세요: ");
            string department = Console.ReadLine();

            Console.Write("담당 교수번호를 입력하세요 : ");
            string professorId = Console.ReadLine();

            // 해당 교수번호를 가진 교수가 있는지 확인
            Professor professor = professors.FirstOrDefault(p => p.ProfessorId == professorId);
            if (professor == null)
            {
                Console.WriteLine("해당 교수번호를 가진 교수가 없습니다. 다시 확인해주세요.");
                return;
            }

            Subject newSubject = new Subject(subjectCode, subjectName, department, professorId);
            subjects.Add(newSubject);
            professor.CreateSubject(newSubject); // 교수의 강의 개설 메서드 호출
            Console.WriteLine($"{newSubject.SubjectName} 과목이 성공적으로 개설되었습니다.");
        }

        // 2. 수강신청 메서드
        static void EnrollCourse()
        {
            Console.WriteLine("--- [수강 신청] ---");
            Console.Write("수강 신청할 학생 학번을 입력하세요 ");
            string studentId = Console.ReadLine();

            Student student = students.FirstOrDefault(s => s.StudentId == studentId);
            if (student == null)
            {
                Console.WriteLine("해당 학번을 가진 학생이 없습니다. 다시 확인해주세요.");
                return;
            }

            Console.Write("수강 신청할 과목 코드를 입력하세요 ");
            string subjectCode = Console.ReadLine();

            Subject subject = subjects.FirstOrDefault(sub => sub.SubjectCode == subjectCode);
            if (subject == null)
            {
                Console.WriteLine("해당 과목 코드를 가진 개설된 강의가 없습니다. 다시 확인해주세요.");
                return;
            }

            // 이미 수강 신청한 과목인지 확인
            if (courses.Any(c => c.StudentId == studentId && c.SubjectName == subject.SubjectName))
            {
                Console.WriteLine("이미 해당 과목을 수강 신청했습니다.");
                return;
            }

            // 교수 이름 찾기
            Professor professor = professors.FirstOrDefault(p => p.ProfessorId == subject.ProfessorId);
            string professorName = professor != null ? professor.Name : "알 수 없음";

            // 간단하게 수강코드 생성 (예: CS_학번_과목코드)
            string courseCode = $"CS_{student.StudentId}_{subject.SubjectCode}";

            Course newCourse = new Course(courseCode, subject.SubjectName, subject.ProfessorId, professorName, student.StudentId, student.Name);
            courses.Add(newCourse);
            student.EnrollCourse(newCourse); // 학생의 수강신청 메서드 호출
            Console.WriteLine($"{student.Name} 학생이 {subject.SubjectName} 과목을 수강 신청했습니다.");
        }

        // 3. 수강신청 삭제 메서드
        static void DropCourse()
        {
            Console.WriteLine("--- [수강 신청 삭제] ---");
            Console.Write("수강 신청을 삭제할 학생 학번을 입력하세요 : ");
            string studentId = Console.ReadLine();

            Student foundStudent = null;
            foreach (Student s in students)
            {
                if (s.StudentId == studentId)
                {
                    foundStudent = s;
                    break;
                }
            }

            if (foundStudent == null)
            {
                Console.WriteLine("해당 학번을 가진 학생이 없습니다. 다시 확인해주세요.");
                return;
            }

            Console.Write("삭제할 수강 과목 코드를 입력하세요 : ");
            string subjectCodeToRemove = Console.ReadLine();

            string subjectNameToRemove = null;
            foreach (Subject sub in subjects)
            {
                if (sub.SubjectCode == subjectCodeToRemove)
                {
                    subjectNameToRemove = sub.SubjectName;
                    break;
                }
            }

            if (subjectNameToRemove == null)
            {
                Console.WriteLine("해당 과목 코드를 가진 개설된 강의가 없습니다. 다시 확인해주세요.");
                return;
            }

            Course courseToRemove = null;
            foreach (Course c in courses)
            {
                if (c.StudentId == studentId && c.SubjectName == subjectNameToRemove)
                {
                    courseToRemove = c;
                    break;
                }
            }

            if (courseToRemove == null)
            {
                Console.WriteLine("해당 학생이 해당 과목을 수강 신청한 기록이 없습니다.");
                return;
            }

            courses.Remove(courseToRemove);
            foundStudent.DropCourse(courseToRemove);
            Console.WriteLine($"{foundStudent.Name} 학생이 {courseToRemove.SubjectName} 과목 수강 신청을 취소했습니다.");
        }
        // 4. 개설 강의 출력 메서드
        static void PrintOpenedSubjects()
        {
            Console.WriteLine("--- [개설 강의 현황] ---");
            if (subjects.Count == 0)
            {
                Console.WriteLine("현재 개설된 강의가 없습니다.");
                return;
            }

            // SubjectName 기준으로 오름차순 정렬
            subjects.Sort((s1, s2) => s1.SubjectName.CompareTo(s2.SubjectName));

            foreach (var subject in subjects)
            {
                subject.DisplayInfo();
            }
        }

        // 5. 수강 신청 현황 출력 메서드
        static void PrintEnrolledCourses()
        {
            Console.WriteLine("--- [수강 신청 현황] ---");
            if (courses.Count == 0)
            {
                Console.WriteLine("현재 수강 신청된 강의가 없습니다.");
                return;
            }

            // StudentName 기준으로 오름차순 정렬
            courses.Sort((c1, c2) => c1.StudentName.CompareTo(c2.StudentName));

            foreach (var course in courses)
            {
                course.DisplayInfo();
            }
        }
    }
}