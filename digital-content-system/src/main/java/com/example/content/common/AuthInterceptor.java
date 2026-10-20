package com.example.content.common;

import com.example.content.model.UserProfile;
import com.example.content.service.AuthService;
import org.springframework.stereotype.Component;
import org.springframework.web.servlet.HandlerInterceptor;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

@Component
public class AuthInterceptor implements HandlerInterceptor {

    private final AuthService authService;

    public AuthInterceptor(AuthService authService) {
        this.authService = authService;
    }

    @Override
    public boolean preHandle(HttpServletRequest request, HttpServletResponse response, Object handler) {
        String authorization = request.getHeader("Authorization");
        if (authorization == null || authorization.trim().isEmpty()) {
            throw new BizException(401, 1003, "未登录或缺少访问令牌");
        }
        String token = authorization.startsWith("Bearer ")
                ? authorization.substring(7) : authorization;
        UserProfile profile = authService.resolve(token.trim());
        if (profile == null) {
            throw new BizException(401, 1003, "登录状态已失效，请重新登录");
        }
        request.setAttribute("currentUser", profile);
        return true;
    }
}
