package com.example.content.controller;

import com.example.content.common.ApiResponse;
import com.example.content.dto.StatusRequest;
import com.example.content.model.ContentTask;
import com.example.content.model.PageResult;
import com.example.content.service.TaskService;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import javax.validation.Valid;

@RestController
@RequestMapping("/api/tasks")
public class TaskController {

    private final TaskService taskService;

    public TaskController(TaskService taskService) {
        this.taskService = taskService;
    }

    @GetMapping
    public ApiResponse<PageResult<ContentTask>> page(
            @RequestParam(defaultValue = "") String status,
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "10") int size) {
        return ApiResponse.ok(taskService.page(status, page, size));
    }

    @PutMapping("/{id}/status")
    public ApiResponse<ContentTask> updateStatus(
            @PathVariable long id,
            @Valid @RequestBody StatusRequest request) {
        return ApiResponse.ok(taskService.updateStatus(id, request.getStatus()), "任务状态更新成功");
    }
}
