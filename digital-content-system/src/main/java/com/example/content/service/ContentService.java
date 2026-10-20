package com.example.content.service;

import com.example.content.common.BizException;
import com.example.content.dao.ContentDao;
import com.example.content.dao.TaskDao;
import com.example.content.dto.ContentCreateRequest;
import com.example.content.dto.ContentUpdateRequest;
import com.example.content.model.ContentItem;
import com.example.content.model.PageResult;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Map;
import java.util.Set;

@Service
public class ContentService {

    private static final Set<String> STATUSES =
            Set.of("DRAFT", "PENDING", "PUBLISHED", "REJECTED", "OFFLINE");
    private static final Set<String> TYPES = Set.of("NEWS", "ARTICLE", "VIDEO");
    private static final Map<String, Set<String>> TRANSITIONS = Map.of(
            "DRAFT", Set.of("PENDING"),
            "PENDING", Set.of("PUBLISHED", "REJECTED"),
            "REJECTED", Set.of("DRAFT"),
            "PUBLISHED", Set.of("OFFLINE"),
            "OFFLINE", Set.of("PENDING")
    );

    private final ContentDao contentDao;
    private final TaskDao taskDao;

    public ContentService(ContentDao contentDao, TaskDao taskDao) {
        this.contentDao = contentDao;
        this.taskDao = taskDao;
    }

    @Transactional
    public ContentItem create(ContentCreateRequest request, long authorId) {
        long id = contentDao.insert(
                request.getTitle(), request.getContentType(), authorId, request.getBody());
        // 新增内容后同步生成一条待处理任务，便于后续审核/发布跟踪
        taskDao.insert(id, "PUBLISH", "PENDING");
        return contentDao.findById(id);
    }

    public ContentItem findById(long id) {
        ContentItem item = contentDao.findById(id);
        if (item == null) {
            throw new BizException(404, 4002, "内容不存在");
        }
        return item;
    }

    public PageResult<ContentItem> page(String status, String contentType, String keyword,
                                        int page, int size) {
        if (page < 1 || size < 1 || size > 50) {
            throw new BizException(400, 4001, "分页参数不合法：page >= 1 且 1 <= size <= 50");
        }
        if (status != null && !status.isEmpty() && !STATUSES.contains(status)) {
            throw new BizException(400, 4003, "非法的内容状态：" + status);
        }
        if (contentType != null && !contentType.isEmpty() && !TYPES.contains(contentType)) {
            throw new BizException(400, 4003, "非法的内容类型：" + contentType);
        }

        long total = contentDao.count(status, contentType, keyword);
        List<ContentItem> list = contentDao.findPage(
                status, contentType, keyword, (page - 1) * size, size);
        return new PageResult<>(total, page, size, list);
    }

    public ContentItem update(long id, ContentUpdateRequest request) {
        ContentItem item = findById(id);
        if (!"DRAFT".equals(item.getStatus()) && !"REJECTED".equals(item.getStatus())) {
            throw new BizException(400, 4004, "只有草稿或已驳回的内容可以编辑");
        }
        contentDao.updateBasic(id, request.getTitle(), request.getBody());
        return contentDao.findById(id);
    }

    @Transactional
    public ContentItem changeStatus(long id, String target) {
        if (target == null || !STATUSES.contains(target)) {
            throw new BizException(400, 4003, "非法的内容状态：" + target);
        }
        ContentItem item = findById(id);
        String current = item.getStatus();
        if (!TRANSITIONS.getOrDefault(current, Set.of()).contains(target)) {
            throw new BizException(400, 4004,
                    "内容状态不允许从 " + current + " 变更为 " + target);
        }

        contentDao.updateStatus(id, target);
        // 数据一致性：内容发布/驳回后，同步关闭其待处理任务
        if ("PUBLISHED".equals(target)) {
            taskDao.updateStatusByContent(id, "PENDING", "SUCCESS");
        } else if ("REJECTED".equals(target)) {
            taskDao.updateStatusByContent(id, "PENDING", "FAILED");
        }
        return contentDao.findById(id);
    }
}
