# csharp-course-registration-practice

> C# · Console Application 기반 수강신청 시스템 학습 과제

## 1. 실습 목적

C# 콘솔 앱에서 객체지향 설계(클래스, 상속, 컬렉션)를 활용해 수강신청 시스템의 기본 기능을 구현해보는 수업 과제입니다.

## 2. 실습 내용

- 교수, 학생 초기 데이터 생성
- 강의 개설 기능
- 학생 수강신청 및 삭제
- 개설 강의 목록 출력
- 수강신청 현황 출력

## 3. 사용 기술

| 구분 | 기술 |
|------|------|
| Language | C# |
| 앱 타입 | Console Application |
| 프레임워크 | .NET Framework 4.7.2 |
| 개발 환경 | Visual Studio 2022 |

## 4. 프로젝트 구조

```
수강신청시스템/
├── Program.cs
├── Models/
│   ├── Person.cs
│   ├── Professor.cs
│   ├── Student.cs
│   ├── Subject.cs
│   └── Course.cs
├── 수강신청시스템.csproj
└── 수강신청시스템.sln
```

## 5. 실행 방법

Visual Studio에서 `수강신청시스템.sln` 파일을 열고 실행합니다.

## 6. 배운 점

- C#에서 클래스 상속과 다형성 구조 설계
- 컬렉션(List)을 활용한 데이터 관리
- Console 앱에서 메뉴 기반 사용자 인터페이스 구성
