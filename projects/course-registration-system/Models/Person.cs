using System;
using System.Collections.Generic;
using System.Linq;

namespace 수강신청시스템
{
    public class Person
    {
        public string Name { get; set; }
        public string Gender { get; set; }
        public string Department { get; set; }
        public string BirthDate { get; set; }
        public string PhoneNumber { get; set; }
        public string Address { get; set; }

        public Person(string name, string gender, string department, string birthDate, string phoneNumber, string address)
        {
            Name = name;
            Gender = gender;
            Department = department;
            BirthDate = birthDate;
            PhoneNumber = phoneNumber;
            Address = address;
        }

        public virtual void DisplayInfo()
        {
            Console.WriteLine($"이름: {Name}, 성별: {Gender}, 학과: {Department}, 생년월일: {BirthDate}, 전화번호: {PhoneNumber}, 주소: {Address}");
        }
    }
}