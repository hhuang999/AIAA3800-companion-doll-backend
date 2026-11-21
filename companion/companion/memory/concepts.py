"""Zero-dependency high-school domain concept clusters and boundary overlap helpers."""

import re

CONCEPT_CLUSTERS: dict[str, tuple[str, ...]] = {
    "parent_family": (
        "爸妈",
        "父母",
        "家长",
        "爸爸",
        "妈妈",
        "家里",
        "家人",
        "亲子",
        "亲戚",
        "别人家孩子",
        "唠叨",
        "表哥",
        "表姐",
        "姑姑",
    ),
    "exam_grade": (
        "月考",
        "期中",
        "期末",
        "模考",
        "一模",
        "二模",
        "三模",
        "中考",
        "高考",
        "测验",
        "考试",
        "考差",
        "考砸",
        "考前",
        "考场",
        "成绩",
        "分数",
        "排名",
        "名次",
        "卷子",
        "试卷",
        "挂科",
        "及格",
        "数学",
        "英语",
        "物理",
        "化学",
        "语文",
        "刷题",
        "作业",
        "补习",
        "学习",
        "进度",
        "备考",
        "复习",
    ),
    "peer_school": (
        "同桌",
        "室友",
        "舍友",
        "同学",
        "闺蜜",
        "朋友",
        "班里",
        "班级",
        "宿舍",
        "老师",
        "班主任",
        "学校",
        "校园",
        "合群",
    ),
    "future_track": (
        "选科",
        "分班",
        "文理",
        "专业",
        "志愿",
        "大学",
        "出路",
        "未来",
        "方向",
        "意义",
        "生涯",
        "职业",
        "动画",
    ),
    "sleep_burnout": (
        "睡不着",
        "失眠",
        "熬夜",
        "晚自习",
        "犯困",
        "睡前",
        "睡觉",
        "睡眠",
        "休息",
        "歇会儿",
        "疲惫",
        "学不动",
        "没力气",
        "好累",
        "很累",
        "心累",
        "累了",
    ),
    "appearance_self": (
        "身材",
        "外貌",
        "体重",
        "长相",
        "长胖",
        "变胖",
        "太胖",
        "颜值",
        "外表",
    ),
    "time_plan": (
        "时间管理",
        "安排时间",
        "时间安排",
        "计划表",
        "日程",
    ),
    "identity_name": (
        "名字",
        "姓名",
        "称呼",
        "叫我",
        "怎么叫",
        "昵称",
        "小名",
        "user_name",
        "nickname",
        "preferred_name",
    ),
}

PRESSURE_DOMAIN_WORDS: dict[str, str] = {
    "academic": "学业 考试 作业 成绩 刷题 学习",
    "social_evaluative": "排名 比较 同伴 评价 面子",
    "relationship": "父母 家庭 同学 同桌 室友 老师 沟通",
    "future": "选科 专业 志愿 未来 方向 意义",
    "self": "自我批评 完美主义 苛责 身材 外貌",
}

PATHWAY_DOMAIN_WORDS: dict[str, str] = {
    "rumination": "反复想 停不下来",
    "self_criticism": "自我否定 苛责",
    "sleep": "睡前 失眠 睡觉 睡眠",
    "loneliness": "孤独 倾诉",
}


def terms(text: str) -> set[str]:
    """Extract lowercase ASCII tokens and Chinese bigrams."""
    words = set(re.findall(r"[a-z0-9_]+", text.lower()))
    for run in re.findall(r"[\u4e00-\u9fff]+", text):
        words.update(run[i : i + 2] for i in range(len(run) - 1))
    return words


def concept_clusters(text: str) -> set[str]:
    """Return high-school stressor domain clusters present in text."""
    lowered = text.lower()
    return {
        cluster
        for cluster, keywords in CONCEPT_CLUSTERS.items()
        if any(word in lowered for word in keywords)
    }


def enriched_terms(text: str) -> set[str]:
    """Combine lexical terms with domain cluster tokens for synonymous retrieval."""
    return terms(text) | {f"cluster:{name}" for name in concept_clusters(text)}


def targets_overlap(target: str | None, text: str) -> bool:
    """Return whether a boundary target semantically overlaps the given text."""
    if target in (None, "all_topics"):
        return True
    if target == "current_topic":
        return False
    if not text:
        return False
    if target in text:
        return True
    if concept_clusters(target) & concept_clusters(text):
        return True
    target_terms = terms(target)
    return bool(target_terms and (target_terms & terms(text)))


def action_domain_text(action_obj: object) -> str:
    """Build representative Chinese domain text for a Card or Exercise config."""
    if action_obj is None:
        return ""
    parts = [getattr(action_obj, "id", ""), getattr(action_obj, "name", "")]
    targets = getattr(action_obj, "targets", None)
    if targets is not None:
        for pressure in getattr(targets, "pressure_types", ()):
            parts.append(PRESSURE_DOMAIN_WORDS.get(pressure, ""))
        for pathway in getattr(targets, "pathways", ()):
            parts.append(PATHWAY_DOMAIN_WORDS.get(pathway, ""))
    protocol = getattr(action_obj, "protocol", None)
    if protocol is not None:
        parts.extend(getattr(protocol, "keywords", ()) or ())
        parts.extend(getattr(protocol, "pathways", ()) or ())
        parts.extend(getattr(protocol, "request_phrases", ()) or ())
        for pathway in getattr(protocol, "pathways", ()) or ():
            parts.append(PATHWAY_DOMAIN_WORDS.get(pathway, ""))
    return " ".join(str(p) for p in parts if p)
