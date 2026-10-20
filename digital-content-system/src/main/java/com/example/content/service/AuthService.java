package com.example.content.service;

import com.example.content.common.BizException;
import com.example.content.dao.UserDao;
import com.example.content.dto.LoginRequest;
import com.example.content.model.User;
import com.example.content.model.UserProfile;
import org.springframework.stereotype.Service;

import java.util.LinkedHashMap;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;

@Service
public class AuthService {

    // 演示项目使用进程内令牌；生产环境应替换为 Redis + JWT
    private final Map<String, UserProfile> tokens = new ConcurrentHashMap<>();
    private final UserDao userDao;

    public AuthService(UserDao userDao) {
        this.userDao = userDao;
    }

    public Map<String, Object> login(LoginRequest request) {
        User user = userDao.findByUsername(request.getUsername());
        if (user == null || !user.getPassword().equals(request.getPassword())) {
            throw new BizException(401, 1002, "用户名或密码错误");
        }
        if (user.getStatus() == null || user.getStatus() != 1) {
            throw new BizException(403, 1004, "账号已被禁用");
        }

        String token = UUID.randomUUID().toString().replace("-", "");
        UserProfile profile = new UserProfile(
                user.getId(), user.getUsername(), user.getNickname(), user.getRole());
        tokens.put(token, profile);

        Map<String, Object> data = new LinkedHashMap<>();
        data.put("token", token);
        data.put("userId", user.getId());
        data.put("username", user.getUsername());
        data.put("nickname", user.getNickname());
        data.put("role", user.getRole());
        return data;
    }

    public UserProfile resolve(String token) {
        return tokens.get(token);
    }
}
