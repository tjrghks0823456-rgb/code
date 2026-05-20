CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE COMMENT '사용자 아이디',
    password VARCHAR(100) NOT NULL COMMENT '비밀번호',
    created_at DATETIME DEFAULT NOW() COMMENT '생성일'
);

INSERT IGNORE INTO users (username, password) VALUES ('admin', '1234');
