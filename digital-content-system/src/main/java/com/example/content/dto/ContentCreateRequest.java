package com.example.content.dto;

import javax.validation.constraints.NotBlank;
import javax.validation.constraints.Pattern;
import javax.validation.constraints.Size;

public class ContentCreateRequest {

    @NotBlank(message = "标题不能为空")
    @Size(max = 100, message = "标题长度不能超过 100")
    private String title;

    @NotBlank(message = "内容类型不能为空")
    @Pattern(regexp = "NEWS|ARTICLE|VIDEO", message = "内容类型只能是 NEWS/ARTICLE/VIDEO")
    private String contentType;

    @NotBlank(message = "正文不能为空")
    @Size(max = 5000, message = "正文长度不能超过 5000")
    private String body;

    public String getTitle() {
        return title;
    }

    public void setTitle(String title) {
        this.title = title;
    }

    public String getContentType() {
        return contentType;
    }

    public void setContentType(String contentType) {
        this.contentType = contentType;
    }

    public String getBody() {
        return body;
    }

    public void setBody(String body) {
        this.body = body;
    }
}
