# winforms-gui-practice

> C# · WinForms 기초 UI 구성과 이벤트 처리 학습 실습 모음

## 1. 실습 목적

C# Windows Forms에서 자주 쓰는 화면 구성, 이벤트 처리, 파일 입출력 패턴을 직접 만들어보며 익히기 위한 실습 모음입니다.

실제 업무용 시스템이 아니라 WinForms 기초를 연습하기 위한 목적으로 만들었습니다.

## 2. 실습 내용

`MainForm`이 런처 역할을 하며, 버튼을 눌러 각 예제 화면을 실행할 수 있습니다.

| 화면 | 실습 내용 |
|------|----------|
| `TextLoginForm` | 텍스트 입력, RichTextBox 출력, 간단한 로그인 검증 |
| `NumberGuessingForm` | 난수 생성, 입력값 비교, 남은 기회 표시 |
| `CalculatorForm` | 숫자 버튼과 사칙연산 이벤트 처리 |
| `TodoListForm` | Todo 추가/수정/삭제, 텍스트 파일 저장/불러오기 |

## 3. 학습한 내용

- Windows Forms 화면 구성
- 버튼 클릭 이벤트와 키보드 입력 이벤트
- TextBox, RichTextBox, ListBox/ListView 계열 컨트롤 사용
- `OpenFileDialog`, `SaveFileDialog` 기반 파일 입출력
- 여러 Form을 런처 화면에서 여는 구조
- 간단한 상태값 관리와 입력 검증

## 4. 사용 기술

| 구분 | 기술 |
|------|------|
| Language | C# |
| UI | WinForms (.NET Framework 4.7.2) |
| 개발 환경 | Visual Studio 2022 |

## 5. 실행 방법

1. Visual Studio에서 `WinForms-GUI-Portfolio.sln` 열기
2. 시작 프로젝트가 `WinForms-GUI-Portfolio`인지 확인
3. 실행하면 런처 화면이 열리고, 각 버튼으로 예제 화면 실행 가능

## 6. 배운 점

WinForms 기초 화면 구성과 이벤트 처리 방식을 여러 작은 예제로 나누어 익혔습니다.  
이후 `equipment-management-winforms`처럼 DB가 연동된 관리 앱으로 넘어가기 전 단계로 활용했습니다.
