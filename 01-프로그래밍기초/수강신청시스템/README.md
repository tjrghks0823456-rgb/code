# 수강신청 시스템

C# 콘솔 기반 수강신청 실습 프로젝트입니다.

## 주요 기능

- 교수, 학생 초기 데이터 생성
- 강의 개설
- 학생 수강신청
- 수강신청 삭제
- 개설 강의 목록 출력
- 수강신청 현황 출력

## 프로젝트 구조

```text
수강신청시스템/
├─ Program.cs
├─ Models/
│  ├─ Person.cs
│  ├─ Professor.cs
│  ├─ Student.cs
│  ├─ Subject.cs
│  └─ Course.cs
├─ Properties/
├─ App.config
├─ 수강신청시스템.csproj
└─ 수강신청시스템.sln
```

## 실행 방법

Visual Studio에서 `수강신청시스템.sln` 파일을 열고 실행합니다.

또는 .NET Framework 빌드 환경에서 다음 명령으로 빌드할 수 있습니다.

```powershell
dotnet build 수강신청시스템.csproj
```

## 사용 기술

- C#
- .NET Framework 4.7.2
- Console Application
