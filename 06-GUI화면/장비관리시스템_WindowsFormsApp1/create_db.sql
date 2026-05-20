-- 1. 데이터베이스 생성 및 선택
CREATE DATABASE IF NOT EXISTS equipmentdb;
USE equipmentdb;

-- 2. equipment 테이블 생성 (장비 정보)
CREATE TABLE IF NOT EXISTS equipment (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL COMMENT '장비 이름',
    category VARCHAR(50) COMMENT '장비 카테고리',
    status VARCHAR(20) DEFAULT '정상' COMMENT '상태 (정상, 대여중, 고장)',
    user VARCHAR(50) DEFAULT '-' COMMENT '현재 사용자',
    last_update DATETIME COMMENT '마지막 상태 변경 시간',
    due_date DATETIME DEFAULT NULL COMMENT '반납 예정일 (대여중일 때만 값 있음)',
    repair_estimate DATETIME DEFAULT NULL COMMENT '수리 완료 예정일 (고장일 때만 값 있음)'
);

-- 3. history 테이블 생성 (대여/반납/수리 이력)
CREATE TABLE IF NOT EXISTS history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    action VARCHAR(50) COMMENT '동작 (대여, 반납, 고장신고, 수리완료)',
    user VARCHAR(50) COMMENT '수행한 사용자 혹은 관련 인물',
    equip_name VARCHAR(100) COMMENT '관련 장비 이름',
    time DATETIME COMMENT '이력 발생 시간'
);

-- 4. manager_schedule 테이블 생성 (스케줄 관리)
-- (코드상 ScheduleRepository 생성자에서 자동 생성되지만, 수동 생성을 위해 포함)
CREATE TABLE IF NOT EXISTS manager_schedule (
    id INT AUTO_INCREMENT PRIMARY KEY,
    date DATE COMMENT '스케줄 날짜',
    manager_name VARCHAR(50) COMMENT '담당자 이름'
);

-- 5. (선택사항) 초기 테스트 데이터 삽입
INSERT INTO equipment (name, category, status, user, last_update, due_date) VALUES 
('Samsung Galaxy Book', 'Laptop', '정상', '-', NOW(), NULL),
('LG Gram', 'Laptop', '대여중', '학생1', NOW(), DATE_ADD(NOW(), INTERVAL 7 DAY)),
('IPhone 15', 'Mobile', '고장', '-', NOW(), NULL);

-- 6. users 테이블 생성 (사용자 관리)
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE COMMENT '사용자 아이디',
    password VARCHAR(100) NOT NULL COMMENT '비밀번호',
    created_at DATETIME DEFAULT NOW() COMMENT '생성일'
);

-- 초기 관리자 계정 생성 (존재하지 않을 때만)
-- 아이디: admin, 비밀번호: 1234
INSERT IGNORE INTO users (username, password) VALUES ('admin', '1234');
