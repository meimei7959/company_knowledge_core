# Billing Lite Lessons

## 2026-06-23 - New Project Path Must Separate Entity Workspace From Central Records

### What Happened

During Billing Lite intake, the first project folder was created under the central knowledge repository at `projects/billing-lite/`. That path is correct for project management records, but it was not the entity workspace the user expected in Finder under `/Users/meimei/Documents/`.

The correct entity workspace is `/Users/meimei/Documents/统一付费轻服务`.

### Root Cause

The intake flow treated "create project" as "create central project record" and did not first resolve the user's intended physical workspace location. The phrase "文稿里面创建一个新的文件夹" referred to the macOS Documents location, not the central `projects/` registry.

### Prevention Rule

For every new project intake, resolve and record two paths before declaring the project created:

- Entity workspace: the real user-visible project folder or repo on the current computer. This is machine-specific and must not be copied from another user's computer.
- Central record path: the knowledge-core management folder, such as `projects/<project-id>/`.

If the user provides an explicit absolute path, use that path. If the user only says Finder, 文稿, 下载, 桌面, 本地文件, or sends a screenshot of a folder, infer a candidate from the current computer and ask for confirmation before creating or moving files. If confirmation is not available in an unattended flow, record `workspaceRef: pending_confirmation` and do not claim the entity workspace is complete.

For this incident, `/Users/meimei/Documents/统一付费轻服务` is the confirmed entity workspace on 梅晓华's Mac only.

### Required Checks

- Prefer `scripts/init_project.py` over hand-written project Markdown.
- `project.md` must include `workspaceRef`.
- `workspaceRef` must be confirmed by the user or explicitly marked `pending_confirmation`.
- `SourceMaterial.storageRef` must point to the stored copy in the entity workspace when a local project folder is expected.
- TaskResult evidence must include both the entity workspace and central record refs.
- Final response must show the user-visible folder path first, then central record path second.

## 2026-06-23 - Project Start Must Be PM-Led

### Correction

The entity workspace entry originally told the user to start from Product Manager requirement acceptance. That skipped the project management layer.

Correct flow:

1. User starts from the entity project workspace.
2. Project Manager Agent reads central context and takes control.
3. Project Manager Agent verifies workspace, SourceMaterial, task queue, blockers, and acceptance owner.
4. Project Manager Agent records or updates PM action / TaskResult.
5. Project Manager Agent dispatches Product Manager Agent to the requirement acceptance task.

Product Manager requirement acceptance is the first business task, not the owner of project startup.
