# HMI 애플리케이션

`SemiToolHMI`는 장비 상태 표시, 레시피 관리, 웨이퍼 이송 모니터링, EtherCAT IO 제어를 담당하는 Windows Forms 프로젝트입니다.

## 주요 폴더

- `SemiToolHMI/App`: 프로그램 시작점
- `SemiToolHMI/Forms`: 로그인, 메인 화면, 레시피, 모니터링, 장비 제어 화면
- `SemiToolHMI/Panels`: 메인 화면에 조립되는 장비 패널과 상태 패널
- `SemiToolHMI/Hardware`: EtherCAT 컨트롤러, IO 맵, 경광등, 모션 제어
- `SemiToolHMI/Process`: 공정 순서, 로봇 시나리오, 웨이퍼 파이프라인 시뮬레이션
- `SemiToolHMI/Data`: 데이터베이스 초기화와 레시피 저장소
- `SemiToolHMI/Models`: 공정 상태와 레시피 데이터 모델
- `SemiToolHMI/Logging`: 로봇 로그 기록
- `SemiToolHMI/Legacy`: 현재 구조와 겹치지 않게 분리한 이전 구현 코드

## 정리 기준

화면 파일은 `Forms`, 화면 구성 부품은 `Panels`, 장비 통신/IO는 `Hardware`, 공정 흐름은 `Process`로 분리했습니다. 그래서 GitHub에서 열었을 때 어느 코드가 어떤 역할인지 바로 구분할 수 있습니다.