# WinForms GUI Portfolio

C# Windows Forms의 기본 UI 구성과 이벤트 처리 방식을 연습하기 위해 만든 미니 앱 모음입니다.

`MainForm`이 런처 역할을 하며, 버튼을 눌러 텍스트 입력, 로그인, 숫자 맞추기, 계산기, Todo List 화면을 각각 실행할 수 있습니다. 하나의 큰 업무 시스템이라기보다 WinForms에서 자주 쓰는 폼, 버튼, 텍스트박스, 리스트, 다이얼로그, 파일 입출력을 작게 나누어 실습한 포트폴리오 프로젝트입니다.

## Screens

| Screen | Description |
| --- | --- |
| `MainForm` | 4개의 예제 화면을 여는 런처 화면 |
| `TextLoginForm` | 텍스트 입력, RichTextBox 출력, 간단한 로그인 검증 |
| `NumberGuessingForm` | 난수 생성, 입력값 비교, 남은 기회 표시 |
| `CalculatorForm` | 숫자 버튼과 사칙연산 이벤트 처리 |
| `TodoListForm` | Todo 추가/수정/삭제, 텍스트 파일 저장/불러오기 |

## Practiced Concepts

- Windows Forms 화면 구성
- 버튼 클릭 이벤트와 키보드 입력 이벤트
- TextBox, RichTextBox, ListBox/ListView 계열 컨트롤 사용
- `OpenFileDialog`, `SaveFileDialog` 기반 파일 입출력
- 여러 Form을 런처 화면에서 여는 구조
- 간단한 상태값 관리와 입력 검증

## Environment

- Visual Studio 2022
- .NET Framework 4.7.2
- C# Windows Forms

## Run

1. Visual Studio에서 `WinForms-GUI-Portfolio.sln`을 엽니다.
2. 시작 프로젝트가 `WinForms-GUI-Portfolio`인지 확인합니다.
3. 실행하면 런처 화면이 열리고, 각 버튼으로 예제 화면을 실행할 수 있습니다.

## Portfolio Point

이 프로젝트는 WinForms 기초 화면을 여러 개로 나누어 구현한 연습 결과물입니다. `equipment-management-winforms`처럼 DB가 붙은 관리 앱으로 넘어가기 전에, 화면 이벤트와 컨트롤 사용법을 익힌 단계로 설명하면 자연스럽습니다.
