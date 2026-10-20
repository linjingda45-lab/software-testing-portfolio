-- 数字内容管理系统初始化脚本（MySQL 8.0）
-- 执行方式：mysql --no-defaults -h127.0.0.1 -P3307 -uroot content_manage < sql/init.sql

DROP TABLE IF EXISTS content_task;
DROP TABLE IF EXISTS content;
DROP TABLE IF EXISTS sys_user;

CREATE TABLE sys_user (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE COMMENT '登录名',
    password VARCHAR(100) NOT NULL COMMENT '演示项目使用明文，生产环境应加密',
    nickname VARCHAR(50) NOT NULL DEFAULT '' COMMENT '昵称',
    role VARCHAR(20) NOT NULL DEFAULT 'EDITOR' COMMENT 'ADMIN/EDITOR',
    status TINYINT NOT NULL DEFAULT 1 COMMENT '1-正常 0-禁用',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='系统用户表';

CREATE TABLE content (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(100) NOT NULL COMMENT '内容标题',
    content_type VARCHAR(20) NOT NULL COMMENT 'NEWS/ARTICLE/VIDEO',
    author_id BIGINT NOT NULL COMMENT '创建人',
    body TEXT NOT NULL COMMENT '正文',
    status VARCHAR(20) NOT NULL DEFAULT 'DRAFT' COMMENT 'DRAFT/PENDING/PUBLISHED/REJECTED/OFFLINE',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    KEY idx_content_status (status),
    KEY idx_content_author (author_id),
    CONSTRAINT fk_content_user FOREIGN KEY (author_id) REFERENCES sys_user (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='内容表';

CREATE TABLE content_task (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    content_id BIGINT NOT NULL COMMENT '关联内容',
    task_type VARCHAR(20) NOT NULL COMMENT 'PUBLISH/UPDATE',
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING' COMMENT 'PENDING/RUNNING/SUCCESS/FAILED',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    KEY idx_task_content (content_id),
    KEY idx_task_status (status),
    CONSTRAINT fk_task_content FOREIGN KEY (content_id) REFERENCES content (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='内容处理任务表';

INSERT INTO sys_user (id, username, password, nickname, role, status) VALUES
(1, 'admin', '123456', '内容管理员', 'ADMIN', 1),
(2, 'editor', '123456', '内容编辑', 'EDITOR', 1);

INSERT INTO content (id, title, content_type, author_id, body, status) VALUES
(1, '产品发布预告', 'NEWS', 2, '下周将发布新一代智能内容管理平台。', 'DRAFT'),
(2, '内容审核规范', 'ARTICLE', 1, '本文介绍内容审核的流程与常见问题。', 'PENDING'),
(3, '平台操作指南', 'ARTICLE', 2, '从登录到发布，快速上手内容管理平台。', 'PUBLISHED');

INSERT INTO content_task (id, content_id, task_type, status) VALUES
(1, 2, 'PUBLISH', 'PENDING'),
(2, 3, 'PUBLISH', 'SUCCESS'),
(3, 1, 'UPDATE', 'PENDING');

ALTER TABLE sys_user AUTO_INCREMENT = 3;
ALTER TABLE content AUTO_INCREMENT = 4;
ALTER TABLE content_task AUTO_INCREMENT = 4;
