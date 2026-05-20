USE equipmentdb;

-- equipment 테이블에 누락된 컬럼 추가
-- (이미 존재한다는 에러가 나면 무시하셔도 됩니다, 혹은 워크벤치에서 확인 후 없으면 실행하세요)

ALTER TABLE equipment
ADD COLUMN due_date DATETIME DEFAULT NULL COMMENT '반납 예정일',
ADD COLUMN repair_estimate DATETIME DEFAULT NULL COMMENT '수리 완료 예정일';

-- 확인용: 테이블 구조 조회
DESCRIBE equipment;
