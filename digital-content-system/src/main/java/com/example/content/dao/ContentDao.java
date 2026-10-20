package com.example.content.dao;

import com.example.content.model.ContentItem;
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
public class ContentDao {

    private static final String BASE_SQL = "SELECT c.id, c.title, c.content_type, c.author_id, "
            + "u.nickname AS author_name, c.body, c.status, c.created_at, c.updated_at "
            + "FROM content c JOIN sys_user u ON u.id = c.author_id ";

    private static final RowMapper<ContentItem> ROW_MAPPER = (rs, rowNum) -> {
        ContentItem item = new ContentItem();
        item.setId(rs.getLong("id"));
        item.setTitle(rs.getString("title"));
        item.setContentType(rs.getString("content_type"));
        item.setAuthorId(rs.getLong("author_id"));
        item.setAuthorName(rs.getString("author_name"));
        item.setBody(rs.getString("body"));
        item.setStatus(rs.getString("status"));
        item.setCreatedAt(rs.getTimestamp("created_at").toLocalDateTime());
        item.setUpdatedAt(rs.getTimestamp("updated_at").toLocalDateTime());
        return item;
    };

    private final JdbcTemplate jdbcTemplate;

    public ContentDao(JdbcTemplate jdbcTemplate) {
        this.jdbcTemplate = jdbcTemplate;
    }

    public long insert(String title, String contentType, Long authorId, String body) {
        String sql = "INSERT INTO content (title, content_type, author_id, body, status) "
                + "VALUES (?, ?, ?, ?, 'DRAFT')";
        KeyHolder keyHolder = new GeneratedKeyHolder();
        jdbcTemplate.update(connection -> {
            PreparedStatement ps = connection.prepareStatement(sql, Statement.RETURN_GENERATED_KEYS);
            ps.setString(1, title);
            ps.setString(2, contentType);
            ps.setLong(3, authorId);
            ps.setString(4, body);
            return ps;
        }, keyHolder);
        Number key = keyHolder.getKey();
        if (key == null) {
            throw new IllegalStateException("内容新增失败，未获取到主键");
        }
        return key.longValue();
    }

    public ContentItem findById(long id) {
        return jdbcTemplate.query(BASE_SQL + "WHERE c.id = ?", ROW_MAPPER, id)
                .stream().findFirst().orElse(null);
    }

    public List<ContentItem> findPage(String status, String contentType, String keyword,
                                      int offset, int size) {
        List<Object> args = new ArrayList<>();
        String where = buildWhere(status, contentType, keyword, args);
        args.add(size);
        args.add(offset);
        String sql = BASE_SQL + where + "ORDER BY c.id DESC LIMIT ? OFFSET ?";
        return jdbcTemplate.query(sql, ROW_MAPPER, args.toArray());
    }

    public long count(String status, String contentType, String keyword) {
        List<Object> args = new ArrayList<>();
        String where = buildWhere(status, contentType, keyword, args);
        Long total = jdbcTemplate.queryForObject(
                "SELECT COUNT(*) FROM content c " + where, Long.class, args.toArray());
        return total == null ? 0L : total;
    }

    public int updateBasic(long id, String title, String body) {
        return jdbcTemplate.update(
                "UPDATE content SET title = ?, body = ? WHERE id = ?", title, body, id);
    }

    public int updateStatus(long id, String status) {
        return jdbcTemplate.update("UPDATE content SET status = ? WHERE id = ?", status, id);
    }

    private String buildWhere(String status, String contentType, String keyword, List<Object> args) {
        StringBuilder where = new StringBuilder("WHERE 1 = 1");
        if (status != null && !status.isEmpty()) {
            where.append(" AND c.status = ?");
            args.add(status);
        }
        if (contentType != null && !contentType.isEmpty()) {
            where.append(" AND c.content_type = ?");
            args.add(contentType);
        }
        if (keyword != null && !keyword.isEmpty()) {
            where.append(" AND c.title LIKE ?");
            args.add("%" + keyword + "%");
        }
        return where.append(" ").toString();
    }
}
