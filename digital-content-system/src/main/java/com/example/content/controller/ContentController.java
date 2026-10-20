package com.example.content.controller;

import com.example.content.common.ApiResponse;
import com.example.content.dto.ContentCreateRequest;
import com.example.content.dto.ContentUpdateRequest;
import com.example.content.dto.StatusRequest;
import com.example.content.model.ContentItem;
import com.example.content.model.ContentTask;
import com.example.content.model.PageResult;
import com.example.content.model.UserProfile;
import com.example.content.service.ContentService;
import com.example.content.service.TaskService;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestAttribute;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import javax.validation.Valid;
import java.util.List;

@RestController
@RequestMapping("/api/contents")
public class ContentController {

    private final ContentService contentService;
    private final TaskService taskService;

    public ContentController(ContentService contentService, TaskService taskService) {
        this.contentService = contentService;
        this.taskService = taskService;
    }

    @PostMapping
    public ApiResponse<ContentItem> create(
            @Valid @RequestBody ContentCreateRequest request,
            @RequestAttribute("currentUser") UserProfile user) {
        return ApiResponse.ok(contentService.create(request, user.getId()), "内容新增成功");
    }

    @GetMapping
    public ApiResponse<PageResult<ContentItem>> page(
            @RequestParam(defaultValue = "") String status,
            @RequestParam(defaultValue = "") String contentType,
            @RequestParam(defaultValue = "") String keyword,
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "10") int size) {
        return ApiResponse.ok(contentService.page(status, contentType, keyword, page, size));
    }

    @GetMapping("/{id}")
    public ApiResponse<ContentItem> detail(@PathVariable long id) {
        return ApiResponse.ok(contentService.findById(id));
    }

    @PutMapping("/{id}")
    public ApiResponse<ContentItem> update(
            @PathVariable long id,
            @Valid @RequestBody ContentUpdateRequest request) {
        return ApiResponse.ok(contentService.update(id, request), "内容修改成功");
    }

    @PutMapping("/{id}/status")
    public ApiResponse<ContentItem> changeStatus(
            @PathVariable long id,
            @Valid @RequestBody StatusRequest request) {
        return ApiResponse.ok(contentService.changeStatus(id, request.getStatus()), "状态更新成功");
    }

    @GetMapping("/{id}/tasks")
    public ApiResponse<List<ContentTask>> tasks(@PathVariable long id) {
        return ApiResponse.ok(taskService.findByContentId(id));
    }
}
