---
type: NotificationRecord
title: task_finished kt-v1-workbench-user-copy-polish
description: Task lifecycle notification trace.
timestamp: "2026-06-22T09:20:12Z"
notificationId: notification.20260622T092012433949Z
taskId: kt-v1-workbench-user-copy-polish
projectId: company-knowledge-core
recipient: agent.company.project-manager
channel: feishu
messageType: task_finished
status: pending
sentAt: ""
sourceMessageRef: ""
failureReason: ""
retryCount: 0
lastAttemptAt: ""
deadLetterAt: ""
---

## Message Summary

任务已完成：修复 V1 工作台用户可读中文文案。结果：第3轮返修完成：工作台顶部改为用户视角项目选择器，当前项目显示为真知公司知识核心；运行说明改为本机运行、只读状态、数据来自中央状态记录；渲染层隐藏或中文化 runtimeMetrics、deviceId、session.v1、company-knowledge-core、英文能力值等内部字段；路由链路明确展示路由已建好并覆盖项目、主 Agent、岗位 Agent、本机设备、执行器 Runner、任务结果记录、审批/权限、异常恢复；validator 和 unittest 已加入项目选择器、路由链路和 raw DOM 禁止项回归检查。。结果记录：task-results/tr-kt-v1-workbench-user-copy-polish.md。

## Task

- taskId: kt-v1-workbench-user-copy-polish
- projectId: company-knowledge-core
- status: waiting_acceptance
- taskRef: projects/company-knowledge-core/tasks/kt-v1-workbench-user-copy-polish.md

## Delivery

- channel: feishu
- status: pending
- failureReason: none
