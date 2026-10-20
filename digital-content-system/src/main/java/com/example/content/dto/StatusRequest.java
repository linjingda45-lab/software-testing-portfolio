package com.example.content.dto;

import javax.validation.constraints.NotBlank;

public class StatusRequest {

    @NotBlank(message = "目标状态不能为空")
    private String status;

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }
}
