package com.example.content.dao;

import com.example.content.model.User;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.core.RowMapper;
import org.springframework.stereotype.Repository;

@Repository
public class UserDao {

    private static final RowMapper<User> ROW_MAPPER = (rs, rowNum) -> {
        User user = new User();
        user.setId(rs.getLong("id"));
        user.setUsername(rs.getString("username"));
        user.setPassword(rs.getString("password"));
        user.setNickname(rs.getString("nickname"));
        user.setRole(rs.getString("role"));
        user.setStatus(rs.getInt("status"));
        return user;
    };

    private final JdbcTemplate jdbcTemplate;

    public UserDao(JdbcTemplate jdbcTemplate) {
        this.jdbcTemplate = jdbcTemplate;
    }

    public User findByUsername(String username) {
        String sql = "SELECT id, username, password, nickname, role, status "
                + "FROM sys_user WHERE username = ?";
        return jdbcTemplate.query(sql, ROW_MAPPER, username).stream().findFirst().orElse(null);
    }
}
