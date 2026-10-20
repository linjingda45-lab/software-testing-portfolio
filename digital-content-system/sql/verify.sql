-- 数据一致性核对 SQL
-- 使用方式：在 MySQL 客户端中执行，核对接口操作后的数据库状态

USE content_manage;

-- 1. 内容状态分布
SELECT status, COUNT(*) AS total
FROM content
GROUP BY status
ORDER BY total DESC;

-- 2. 任务状态分布
SELECT status, COUNT(*) AS total
FROM content_task
GROUP BY status
ORDER BY total DESC;

-- 3. 每条内容与其任务的状态（人工核对新增、修改、发布后的联动结果）
SELECT c.id, c.title, c.status AS content_status,
       t.id AS task_id, t.task_type, t.status AS task_status
FROM content c
LEFT JOIN content_task t ON t.content_id = c.id
ORDER BY c.id DESC, t.id DESC;

-- 4. 一致性异常：已发布内容仍存在待处理/执行中的任务
SELECT c.id, c.title, c.status, t.id AS task_id, t.status AS task_status
FROM content c
JOIN content_task t ON t.content_id = c.id
WHERE c.status = 'PUBLISHED'
  AND t.status IN ('PENDING', 'RUNNING');

-- 5. 一致性异常：待审核内容却没有待处理任务
SELECT c.id, c.title, c.status,
       (SELECT COUNT(*) FROM content_task t
        WHERE t.content_id = c.id AND t.status = 'PENDING') AS pending_tasks
FROM content c
WHERE c.status = 'PENDING'
HAVING pending_tasks = 0;

-- 6. 核对指定内容（把 :content_id 替换为实际 ID）
-- SELECT * FROM content WHERE id = :content_id;
-- SELECT * FROM content_task WHERE content_id = :content_id ORDER BY id;
