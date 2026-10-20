package com.example.content.service;

import com.example.content.common.BizException;
import com.example.content.dao.ContentDao;
import com.example.content.dao.TaskDao;
import com.example.content.model.ContentTask;
import com.example.content.model.PageResult;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Map;
import java.util.Set;

@Service
public class TaskService {

    private static final Set<String> STATUSES = Set.of("PENDING", "RUNNING", "SUCCESS", "FAILED");
    private static final Map<String, Set<String>> TRANSITIONS = Map.of(
            "PENDING", Set.of("RUNNING"),
            "RUNNING", Set.of("SUCCESS", "FAILED"),
            "SUCCESS", Set.of(),
            "FAILED", Set.of()
    );

    private final TaskDao taskDao;
    private final ContentDao contentDao;

    public TaskService(TaskDao taskDao, ContentDao contentDao) {
        this.taskDao = taskDao;
        this.contentDao = contentDao;
    }

    public PageResult<ContentTask> page(String status, int page, int size) {
        if (page < 1 || size < 1 || size > 50) {
            throw new BizException(400, 4001, "分页参数不合法：page >= 1 且 1 <= size <= 50");
        }
        if (status != null && !status.isEmpty() && !STATUSES.contains(status)) {
            throw new BizException(400, 5002, "非法的任务状态：" + status);
        }
        long total = taskDao.count(status);
        List<ContentTask> list = taskDao.findPage(status, (page - 1) * size, size);
        return new PageResult<>(total, page, size, list);
    }

    public List<ContentTask> findByContentId(long contentId) {
        if (contentDao.findById(contentId) == null) {
            throw new BizException(404, 4002, "内容不存在");
        }
        return taskDao.findByContentId(contentId);
    }

    public ContentTask updateStatus(long id, String target) {
        if (target == null || !STATUSES.contains(target)) {
            throw new BizException(400, 5002, "非法的任务状态：" + target);
        }
        ContentTask task = taskDao.findById(id);
        if (task == null) {
            throw new BizException(404, 5001, "任务不存在");
        }
        if (!TRANSITIONS.getOrDefault(task.getStatus(), Set.of()).contains(target)) {
            throw new BizException(400, 5003,
                    "任务状态不允许从 " + task.getStatus() + " 变更为 " + target);
        }
        taskDao.updateStatus(id, target);
        return taskDao.findById(id);
    }
}
