from __future__ import annotations

from pathlib import Path
from urllib.parse import urlparse

from zhenzhi_knowledge.core import safe_slug


WORKSPACE_DIRS = [
    "00_原始资料",
    "01_产品需求",
    "02_架构方案",
    "03_研发实现",
    "04_测试验收",
    "05_运营上线",
    "99_项目管理",
]

WORKSPACE_PROFILES = {
    "delivery": WORKSPACE_DIRS,
    "development": [
        "00_项目管理",
        "01_产品需求",
        "02_设计交互",
        "03_架构方案",
        "04_研发工程/apps",
        "04_研发工程/services",
        "04_研发工程/skills",
        "04_研发工程/packages",
        "05_测试验收",
        "06_发布运维",
        "07_运营素材",
        "08_交付归档",
    ],
    "operations": [
        "00_项目管理",
        "01_资料来源",
        "02_运营素材/01_产品介绍",
        "02_运营素材/02_官网素材",
        "02_运营素材/03_发布说明",
        "03_内容生产",
        "04_投放发布",
        "05_数据复盘",
        "06_交付归档",
    ],
    "copyright": [
        "00_项目管理",
        "01_源码镜像",
        "02_软著材料/01_产品说明",
        "02_软著材料/02_技术说明",
        "02_软著材料/03_源代码整理",
        "02_软著材料/04_截图证据",
        "02_软著材料/05_申请提交包",
        "03_运营素材/01_产品介绍",
        "03_运营素材/02_官网素材",
        "03_运营素材/03_发布说明",
        "04_过程记录",
        "05_交付归档",
    ],
}

RAW_MATERIAL_DIR_BY_PROFILE = {
    "delivery": "00_原始资料",
    "development": "01_产品需求",
    "operations": "01_资料来源",
    "copyright": "02_软著材料/01_产品说明",
}

SOURCE_MIRROR_DIR_BY_PROFILE = {
    "delivery": "00_原始资料/源码镜像",
    "development": "04_研发工程/source",
    "operations": "01_资料来源/源码镜像",
    "copyright": "01_源码镜像",
}

PROFILE_KEYWORDS = {
    "copyright": ["软著", "软件著作权", "著作权", "申报", "copyright"],
    "operations": ["运营", "素材", "官网", "发布", "营销", "投放", "内容"],
    "development": ["开发", "研发", "新产品", "应用", "客户端", "页面", "服务", "代码"],
}

PROFILE_INITIAL_TASKS = {
    "delivery": [
        ("product-scope", "产品经理梳理项目目标和交付范围", "agent.company.product-manager", "product_requirement", "Product scope, role route, and acceptance boundary are ready for PM review."),
        ("architecture-route", "架构师评审交付路径和技术约束", "agent.company.architect", "project_management", "Architecture review confirms downstream implementation route and blockers."),
        ("test-checklist", "测试 Agent 制定交付验收清单", "agent.company.test", "testing", "Test checklist covers acceptance criteria and regression route."),
    ],
    "development": [
        ("product-requirements", "产品经理结构化新项目需求和 V1 范围", "agent.company.product-manager", "product_requirement", "Requirement tree, V1 scope, and acceptance criteria are ready."),
        ("design-spec", "设计 Agent 输出界面体验和交互规范", "agent.company.design", "design_spec", "Human-readable UI/UX design spec is ready when the product has user-facing screens."),
        ("architecture-solution", "架构师输出技术方案和工程边界", "agent.company.architect", "project_management", "Technical solution, boundaries, risks, and implementation slices are ready."),
        ("development-plan", "研发 Agent 制定实现计划并等待上游评审", "agent.company.development", "development", "Development plan links to product/design/architecture inputs before coding."),
        ("test-strategy", "测试 Agent 制定测试策略和验收路径", "agent.company.test", "testing", "Test strategy, regression scope, and acceptance gate are ready."),
    ],
    "operations": [
        ("product-positioning", "产品经理确认运营目标和用户表达", "agent.company.product-manager", "product_requirement", "Operational positioning, target readers, and material scope are ready."),
        ("content-plan", "运营 Agent 制定素材生产和发布计划", "agent.company.operations", "operations_feedback", "Content plan, publishing route, and review checkpoints are ready."),
        ("quality-checklist", "测试 Agent 制定运营素材验收清单", "agent.company.test", "testing", "Material quality checklist covers facts, links, screenshots, and release evidence."),
    ],
    "copyright": [
        ("copyright-scope", "产品经理确认软著申报范围和材料清单", "agent.company.product-manager", "product_requirement", "Software copyright scope, product description, and material checklist are ready."),
        ("code-structure-review", "研发 Agent 只读分析源码结构和可申报代码范围", "agent.company.development", "development", "Read-only source structure review identifies copyright code range without modifying source."),
        ("screenshot-evidence-plan", "测试 Agent 制定截图和证据验收清单", "agent.company.test", "testing", "Screenshot and evidence checklist is ready for submission package review."),
    ],
}


def material_dir_for_profile(profile: str) -> str:
    return RAW_MATERIAL_DIR_BY_PROFILE.get(profile, RAW_MATERIAL_DIR_BY_PROFILE["delivery"])


def source_mirror_dir_for_profile(profile: str) -> str:
    return SOURCE_MIRROR_DIR_BY_PROFILE.get(profile, SOURCE_MIRROR_DIR_BY_PROFILE["delivery"])


def repo_name_from_url(source_repo_url: str, fallback: str) -> str:
    if not source_repo_url.strip():
        return fallback
    parsed = urlparse(source_repo_url)
    tail = Path(parsed.path or source_repo_url).name or fallback
    if tail.endswith(".git"):
        tail = tail[:-4]
    return tail or fallback


def infer_workspace_profile(request: str, explicit_profile: str = "") -> str:
    if explicit_profile:
        return explicit_profile
    lowered = request.lower()
    for profile, keywords in PROFILE_KEYWORDS.items():
        if any(keyword.lower() in lowered for keyword in keywords):
            return profile
    return "delivery"


def default_project_id(name: str, source_repo_url: str) -> str:
    if source_repo_url.strip():
        return safe_slug(repo_name_from_url(source_repo_url, "project"), "project")
    return safe_slug(name, "project")
