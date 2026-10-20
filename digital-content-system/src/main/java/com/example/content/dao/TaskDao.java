package com.example.content.dao;

import com.example.content.model.ContentTask;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.core.RowMapper;
import org.springframework.jdbc.support.GeneratedKeyHolder;
import org.springframework.jdbc.support.KeyHolder;
import org.springframework.stereotype.Repository;

import java.sql.PreparedStatement;
import java.sql.Statement;
import java.util.ArrayList;
import java.util.List;

@Repository
public class TaskDao {

    private static final String BASE_SQL = "SELECT t.id, t.content_id, c.title AS content_title, "
            + "t.task_type, t.status, t.created_at, t.updated_at "
            + "FROM content_task t JOIN content c ON c.id = t.content_id ";

    private static final RowMapper<ContentTask> ROW_MAPPER = (rs, rowNum) -> {
        ContentTask task = new ContentTask();
        task.setId(rs.getLong("id"));
        task.setContentId(rs.getLong("content_id"));
        task.setContentTitle(rs.getString("content_title"));
        task.setTaskType(rs.getString("task_type"));
        task.setStatus(rs.getString("status"));
        task.setCreatedAt(rs.getTimestamp("created_at").toLocalDateTime());
        task.setUpdatedAt(rs.getTimestamp("updated_at").toLocalDateTime());
        return task;
    };

    private final JdbcTemplate jdbcTemplate;

    public TaskDao(JdbcTemplate jdbcTemplate) {
        this.jdbcTemplate = jdbcTemplate;
    }

    public long insert(long contentId, String taskType, String status) {
        String sql = "INSERT INTO content_task (content_id, task_type, status) VALUES (?, ?, ?)";
        KeyHolder keyHolder = new GeneratedKeyHolder();
        jdbcTemplate.update(connection -> {
            PreparedStatement ps = connection.prepareStatement(sql, Statement.RETURN_GENERATED_KEYS);
            ps.setLong(1, contentId);
            ps.setString(2, taskType);
            ps.setString(3, status);
            return ps;
        }, keyHolder);
        Number key = keyHolder.getKey();
        if (key == null) {
            throw new IllegalStateException("任务创建失败，未获取到主键");
        }
        return key.longValue();
    }

    public ContentTask findById(long id) {
        return jdbcTemplate.query(BASE_SQL + "WHERE t.id = ?", ROW_MAPPER, id)
                .stream().findFirst().orElse(null);
    }

    public List<ContentTask> findByContentId(long contentId) {
        return jdbcTemplate.query(
                BASE_SQL + "WHERE t.content_id = ? ORDER BY t.id DESC", ROW_MAPPER, contentId);
    }

    public List<ContentTask> findPage(String status, int offset, int size) {
        List<Object> args = new ArrayList<>();
        String where = "WHERE 1 = 1";
        if (status != null && !status.isEmpty()) {
            where += " AND t.status = ?";
            args.add(status);
        }
        args.add(size);
        args.add(offset);
        return jdbcTemplate.query(
                BASE_SQL + where + " ORDER BY t.id DESC LIMIT ? OFFSET ?",
                ROW_MAPPER, args.toArray());
    }

    public long count(String status) {
        List<Object> args = new ArrayList<>();
        String where = "WHERE 1 = 1";
        if (status != null && !status.isEmpty()) {
            where += " AND status = ?";
            args.add(status);
        }
        Long total = jdbcTemplate.queryForObject(
                "SELECT COUNT(*) FROM content_task " + where, Long.class, args.toArray());
        return total == null ? 0L : total;
    }

    public int updateStatus(long id, String status) {
        return jdbcTemplate.update("UPDATE content_task SET status = ? WHERE id = ?", status, id);
    }

    public int updateStatusByContent(long contentId, String currentStatus, String newStatus) {
        return jdbcTemplate.update(
                "UPDATE content_task SET status = ? WHERE content_id = ? AND status = ?",
                newStatus, contentId, currentStatus);
    }
}
