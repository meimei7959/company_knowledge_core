# 输入契约

## 1. `.softcopyright/softcopyright.toml`

### software

- `full_name`：不含版本号的软件全称；
- `short_name`：软件简称；
- `version`：例如 `V1.0`；
- `completion_date`：开发完成日期，必须人工提供；
- `publication_status`：`unpublished` 或 `published`；
- `first_publication_date`：已发表时人工填写；
- `copyright_owner`：法定著作权人名称；
- `manual_type`：`user-manual` 或 `design-description`；
- `platforms`、`app_display_name`、`package_id`：与当前冻结版本一致；
- `hardware_environment`、`software_environment`、`technical_characteristics`：人工确认内容。

### application

- `applicant_type`：`enterprise`、`individual` 或 `other`；
- `development_mode`：`independent`、`cooperative`、`commissioned` 或 `task`；
- `rights_acquisition`：`original`、`inherited`、`assigned` 或 `undertaken`；
- `software_category`、`rights_scope`：人工按当前表单填写；
- `has_ownership_contract_or_task`：是否存在应提交的归属合同或任务书；
- `based_on_original_software`：是否基于原软件修改；
- `uses_registration_agent`：是否委托登记代理机构；
- `has_foreign_documents`：证明材料是否含外文；
- `main_function_description`：由人独立撰写；`main_function_min_chars/max_chars` 由负责人按提交当日表单确认，模板默认 500—1300；
- `human_author_name`、`human_confirmed_on`：人工撰写和确认记录。

### source/build/output

- `source.roots`：第一方核心源码目录，顺序决定连续源程序顺序；
- `source.exclude_globs`：排除依赖、构建物、生成文件、密钥和生产配置；
- `source.deposit_mode`：仅支持 `general`；
- `build.*_command`：构建、测试和真实截图采集命令；
- `build.require_clean_git`：默认 true；
- `output.generate_pdf`：正式上报通常需要 PDF 时启用。

## 2. `.softcopyright/authorship-attestation.toml`

只由申请负责人按事实填写。Agent 不得代填。详见 `ai-compliance-gate.md`。

## 3. `.softcopyright/company-materials.json`

每个字段填写实际文件相对路径或路径数组：

```json
{
  "applicant_type": "enterprise",
  "official_application_form": ".softcopyright/company-materials/application-form.pdf",
  "business_license": ".softcopyright/company-materials/business-license.pdf",
  "identity_document": "",
  "ownership_scenario": "independent",
  "development_contract_or_task_documents": [],
  "modified_from_other_software": false,
  "original_software_permission_documents": [],
  "rights_succession": false,
  "succession_or_transfer_documents": [],
  "agent_authorization_documents": [],
  "foreign_document_translations": [],
  "other_documents": []
}
```

Skill 只原样复制，不修改内容。

## 4. `.softcopyright/feature-evidence.json`

每项由人填写：

```json
{
  "name": "用户登录",
  "summary": "人工原创的实际功能说明",
  "status": "verified",
  "code_paths": ["app/src/main/kotlin/.../LoginViewModel.kt"],
  "screenshots": [".softcopyright/screenshots/01-login.png"],
  "operation_steps": ["打开应用", "输入演示账号", "点击登录"],
  "notes": "截图使用虚构演示数据并已脱敏"
}
```

状态：

- `verified`：人已核验代码、运行结果、步骤和截图；
- `needs_review`：证据不完整，不得进入正式说明书；
- `excluded`：本版本不纳入申报材料。

## 5. `.softcopyright/manual.md`

说明书正文必须与当前真实版本对应。可使用：

- Markdown 标题、段落、列表；
- `![图名](相对路径)` 插入真实截图；
- `[[PAGE_BREAK]]` 手动分页。

禁止存在模板提示、TODO、占位图、虚构菜单、不存在的图片或未核验功能。
