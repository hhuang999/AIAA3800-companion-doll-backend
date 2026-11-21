(() => {
  const EVIDENCE_AUTHOR_YEAR = {
    E01: "Ye et al., 2019",
    E02: "Wang et al., 2025",
    E03: "Dickerson & Kemeny, 2004",
    E04: "Zhao & Hu, 2022",
    E05: "Gulliver et al., 2010",
    E06: "Leigh et al., 2025",
    E07: "Lunn et al., 2023",
    E08: "WHO & UNICEF, 2023",
    E09: "Bluth et al., 2024",
    E10: "Filia et al., 2021",
    E11: "Chen et al., 2022",
    E12: "Scullin et al., 2018",
    E13: "WHO, 2011",
    E14: "Liu et al., 2021",
    E15: "Deng et al., 2024",
    E16: "Dunning et al., 2022",
    E17: "Yeager et al., 2022",
    E18: "Megalokonomou & Zhang, 2024",
    E19: "Ding et al., 2026"
  };

  function formatEvidence(ids) {
    return (ids || []).map((id) => EVIDENCE_AUTHOR_YEAR[id] || "Academic Source").join("; ");
  }

  function escapeHtml(str) {
    return String(str ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  const SCENARIOS = [
    {
      id: "exam",
      label: "考前手抖心慌",
      userPrompt: "明早就要一模进考场了，想到发卷我就心跳直飙、手心出汗，脑子发紧，怎么办？",
      turns: {
        initial: {
          stage: "permission",
          objective: "invite_action",
          card: "-",
          pending: "exam_steadying (awaiting_consent)",
          boundary: "none",
          bot: "考前心里发紧挺折磨人的，想不想花半分钟把身体信号和待会儿第一步先稳住？",
          meta: "STATE: permission · PendingOffer(exam_steadying)"
        },
        agree: {
          stage: "action",
          objective: "invite_action",
          card: "exam_steadying (step 1/3)",
          pending: "none (consented)",
          boundary: "none",
          bot: "心跳快、手心出汗不是要垮掉了，而是身体在悄悄帮你提神集中注意力。拿卷头一分钟先圈两道最有把握的基础小题就行，你看稳得住吗？",
          meta: "STAGE: action · card=exam_steadying · Yeager et al., 2022"
        },
        refuse: {
          stage: "explore",
          objective: "attuned_listen",
          card: "-",
          pending: "none (cards_refused += exam_steadying)",
          boundary: "no_advice (turn)",
          bot: "好，那先不讲考前方法。手心直出汗肯定特别难受，我在这儿陪你听你说会儿。",
          meta: "STAGE: explore · explicit_refusal -> L1 attuned_listen"
        },
        quiet: {
          stage: "quiet",
          objective: "quiet_presence",
          card: "-",
          pending: "none (resume cleared)",
          boundary: "no_topic_probe (session)",
          bot: "好，我就在这儿陪着你，先不问了。",
          meta: "STAGE: quiet · zero questions"
        }
      }
    },
    {
      id: "parent",
      label: "父母拿排名唠叨",
      userPrompt: "爸妈又拿月考排名跟表哥比，我暂时不想跟他们吵架，就是胸口堵得慌，怎么办？",
      turns: {
        initial: {
          stage: "permission",
          objective: "invite_action",
          card: "-",
          pending: "expectation_boundary (awaiting_consent)",
          boundary: "excluded: unsafe_relationship -> context safe",
          bot: "家里总拿分数和别人家孩子念叨挺憋屈的，要不要先把爸妈的焦虑和你自己的节奏分清楚？",
          meta: "STATE: permission · PendingOffer(expectation_boundary)"
        },
        agree: {
          stage: "action",
          objective: "invite_action",
          card: "expectation_boundary (step 1/3)",
          pending: "none (consented)",
          boundary: "never_say: 父母都是为你好",
          bot: "被一遍遍拿表哥来比，换谁心里都堵得慌。爸妈的焦急归他们担心，今晚十一点前你手头这页错题怎么走，听你自己的步调就好。",
          meta: "STAGE: action · card=expectation_boundary · Ding et al., 2026"
        },
        refuse: {
          stage: "explore",
          objective: "tentative_reflect",
          card: "-",
          pending: "none (cards_refused += expectation_boundary)",
          boundary: "no_advice (turn)",
          bot: "明白，先不理什么节奏了。听着他们叹气，是不是觉得怎么努力都还差点意思？",
          meta: "STAGE: explore · L1 tentative_reflect"
        },
        quiet: {
          stage: "quiet",
          objective: "quiet_presence",
          card: "-",
          pending: "none",
          boundary: "no_topic_probe (current_topic)",
          bot: "嗯，那先不说家里的事了，你安心喘口气，我陪着你。",
          meta: "STAGE: quiet · topic isolated"
        }
      }
    },
    {
      id: "burnout",
      label: "晚自习散架疲惫",
      userPrompt: "十点半刚下晚自习回来，彻底刷不动题了，可坐着歇十分钟我就内疚得像在犯罪，一点办法也不想要。",
      turns: {
        initial: {
          stage: "explore",
          objective: "low_energy_companionship",
          card: "-",
          pending: "none (L1 empathy only)",
          boundary: "no_advice (readiness=low)",
          bot: "十点半了，身体和脑子都该喊停了。坐着喘口气真不是偷懒，只是连轴转之后该歇了。",
          meta: "STAGE: explore · L1 low_energy_companionship (fast_path)"
        },
        agree: {
          stage: "explore",
          objective: "low_energy_companionship",
          card: "-",
          pending: "none (no task assigned)",
          boundary: "no_advice (readiness=low)",
          bot: "嗯，今天就不再碰题了，把书包合上安心坐会儿，明天再说。",
          meta: "L1 guard: readiness=low blocks action clutter"
        },
        refuse: {
          stage: "explore",
          objective: "low_energy_companionship",
          card: "-",
          pending: "none",
          boundary: "no_advice (session)",
          bot: "绝对不给你排任何任务。累成这样，能躺平十分钟已经很好了。",
          meta: "STAGE: explore · no-advice honored"
        },
        quiet: {
          stage: "quiet",
          objective: "quiet_presence",
          card: "-",
          pending: "none",
          boundary: "no_topic_probe",
          bot: "晚安，今晚好好歇着。",
          meta: "STAGE: quiet · sleep safe"
        }
      }
    },
    {
      id: "memory",
      label: "榜单与边界记忆",
      userPrompt: "我叫小琳（双木林王字旁），以后别主动问数学成绩；另：我现在不想定死未来，只想知道选科手册怎么看。",
      turns: {
        initial: {
          stage: "explore",
          objective: "attuned_listen",
          card: "-",
          pending: "scoped negative lookahead check",
          boundary: "no_topic_probe:数学成绩 | allow: values_exploration",
          bot: "记牢了小琳，以后绝不主动提数学成绩。至于“不想定死未来”——选科本来就能先从一页小问题慢慢摸底。",
          meta: "scoped lookahead regex + identity_name cluster saved"
        },
        agree: {
          stage: "action",
          objective: "invite_action",
          card: "values_exploration",
          pending: "none (consented)",
          boundary: "no_topic_probe:数学成绩 preserved",
          bot: "那今晚只挑一个不涉分数排名的小好奇点——比如翻翻学校选科手册里某个专业的真实选考科目，行吗？",
          meta: "STAGE: action · scoped boundary isolated from values_exploration"
        },
        refuse: {
          stage: "explore",
          objective: "attuned_listen",
          card: "-",
          pending: "none",
          boundary: "no_topic_probe:数学成绩 preserved",
          bot: "好，选科手册也先不聊。刚才心里堵着的那股烦躁，想说说哪里最难受吗？",
          meta: "STAGE: explore · zero policy leakage"
        },
        quiet: {
          stage: "quiet",
          objective: "quiet_presence",
          card: "-",
          pending: "none",
          boundary: "persistent identity + boundary kept",
          bot: "小琳，我就在这儿陪着，想说时再喊我。",
          meta: "reconnect-safe: skips duplicate onboarding"
        }
      }
    }
  ];

  const LANES = [
    {
      id: "talker",
      code: "LANE 01",
      title: "实时表达线 (Talker)",
      summary: "仅消费 Core 已冻结的 TurnPolicyFrame，永不阻塞等待后台思考；首个 >=8 字语义子句即送流式 Opus 合成与 60ms 内存打包，保留闭合中文引号完整性并结合 64 项短语 LRU 热缓存与动态表情映射。",
      nodes: ["TurnContext", "Talker (qwen-flash)", "OutputRail + 闭合引号保护", "First-Clause -> In-Memory Opus"],
      metric: "400ms Concurrent Safe Gate · 64-Entry LRU · Zero Disk WAV I/O"
    },
    {
      id: "cognition",
      code: "LANE 02",
      title: "有界后台协作 (Bounded Cognition)",
      summary: "并行执行独立盲审 Brief（qwen-flash）与情境分析 Analysis（gpt-4.1-mini），经 Catalog 确定性过滤后由 Planner 制定候选；携带行动或边界疑点时必经跨家族 Critic 评审，纯共情倾诉则走 fast_path_non_action 且受 protects_active_offer 保护。",
      nodes: ["Brief // Analysis", "Catalog 前置过滤", "Planner (9 卡 / 3 练)", "Cross-Family Critic / Fast-Path"],
      metric: "8 Calls / 20s Cap · Single-User Serial · Cross-User Fair Queue"
    },
    {
      id: "safety",
      code: "LANE 03",
      title: "静默安全与来源蕴含记忆",
      summary: "风险词表与并发分类器在后台静默兜底，日常顺畅表达不受干扰；会话结束及记忆梳理共享 2-Call / 20s 预算，由 ConsolidationGrounder 对用户原话逐句检验前提蕴含，并借助 8 组校园升学概念簇支持跨会话召唤。",
      nodes: ["L1/L2 Silent Safety", "Extraction (Call #1)", "ConsolidationGrounder (Call #2)", "8 Concept Clusters + SQLite"],
      metric: "2 Calls / 20s Budget · Verbatim Quote Summary · 8 Domain Clusters"
    },
    {
      id: "cas",
      code: "CAS GATE",
      title: "Core 权威与四重版本号 CAS 提交",
      summary: "CompanionCore 与 StateMachine 独占对话阶段、PendingOffer 单步许可与 generation 代次；若后台推理期间用户插话，先由 DeltaChecker 在 120s / 4 轮窗内单次复核，再在锁内比对 4 项基线版本一致方可激活下轮策略。",
      nodes: ["generation 递增闸", "PendingOffer 许可态", "DeltaGuard 兼容复核", "4-Revision Atomic CAS Commit"],
      metric: "120s / <=4 Turns Window · Partial Memory Commit · WriterLease"
    }
  ];

  const DIAGRAMS = [
    {
      id: "01",
      tab: "01 压力情境",
      title: "Fig 01 · 中国初高中升学日常压力情境、共同通路与求助障碍图谱",
      desc: "梳理五类日常压力源、四条心理放大通路、青少年求助顾虑，以及通用聊天机器人的三项典型失配。",
      src: "assets/diagrams/01-context-and-stressors.png",
      svg: "assets/diagrams/01-context-and-stressors.svg"
    },
    {
      id: "02",
      tab: "02 文献转译",
      title: "Fig 02 · 心理学与人机交互文献向可执行对话约束与工程模块的转译链",
      desc: "展示实证研究发现如何转译为具体化拆步、协同压力重评、排名基线解耦、父母期待边界与分句策略解耦。",
      src: "assets/diagrams/02-evidence-to-design.png",
      svg: "assets/diagrams/02-evidence-to-design.svg"
    },
    {
      id: "03",
      tab: "03 能力全景",
      title: "Fig 03 · 分层陪伴能力全景图：主动共情四态、单步许可门与九卡三练",
      desc: "呈现 L1 非行动默认共情、PendingOffer 许可门控、L2 九张支持策略卡、三段固定短练习及静默安全底层。",
      src: "assets/diagrams/03-strategy-taxonomy.png",
      svg: "assets/diagrams/03-strategy-taxonomy.svg"
    },
    {
      id: "04",
      tab: "04 策略卡结构",
      title: "Fig 04 · 单张支持策略卡内部结构解剖（targets / reasoner / protocol / talker）",
      desc: "以父母期待边界策略为例，解剖适用靶点、排除前提、单步邀请、三轮聚焦限制、刚性禁语及反馈归因边界。",
      src: "assets/diagrams/04-strategy-card-anatomy.png",
      svg: "assets/diagrams/04-strategy-card-anatomy.svg"
    },
    {
      id: "05",
      tab: "05 许可与边界",
      title: "Fig 05 · 确定性交互状态机、负向瞻前作用域边界与随时喊停控制",
      desc: "呈现单步许可转移闭环、并列否定防误杀负向瞻前模式、跨话题边界隔离以及口语意图仲裁逻辑。",
      src: "assets/diagrams/05-consent-boundary-fsm.png",
      svg: "assets/diagrams/05-consent-boundary-fsm.svg"
    },
    {
      id: "06",
      tab: "06 三线架构",
      title: "Fig 06 · 三线解耦系统总图：Core 权威控制、三线分工与持久化架构",
      desc: "展示小智 ESP32 终端接入、CompanionCore 唯一权威内核、实时快线、有界后台协作池与静默安全存储。",
      src: "assets/diagrams/06-system-architecture.png",
      svg: "assets/diagrams/06-system-architecture.svg"
    },
    {
      id: "07",
      tab: "07 多Agent协作",
      title: "Fig 07 · 有界多 Agent 后台协作：并行理解、目录过滤、快慢分流与跨家族互审",
      desc: "阐明 Brief // Analysis 并行执行、Catalog 前置筛选、非行动 Fast-Path（兼顾活跃邀约保护）与 Critic 单次修复。",
      src: "assets/diagrams/07-multiagent-deliberation.png",
      svg: "assets/diagrams/07-multiagent-deliberation.svg"
    },
    {
      id: "08",
      tab: "08 CAS并发",
      title: "Fig 08 · 四重版本号 CAS 事务发布、DeltaGuard 复核与代次防串音控制",
      desc: "刻画连续打断输入下 generation 代次取消、DeltaChecker 窗口兼容性复核、四项版本号原子比较及部分提交语义。",
      src: "assets/diagrams/08-cas-concurrency.png",
      svg: "assets/diagrams/08-cas-concurrency.svg"
    },
    {
      id: "09",
      tab: "09 蕴含记忆",
      title: "Fig 09 · 跨家族来源蕴含记忆核对、逐字原话摘要与八组概念簇跨会话召回架构",
      desc: "呈现两阶段 2-Call / 20s 抽取与文本蕴含校验管线、八组升学领域概念簇以及按需唤醒与更名废止机制。",
      src: "assets/diagrams/09-grounded-memory.png",
      svg: "assets/diagrams/09-grounded-memory.svg"
    },
    {
      id: "10",
      tab: "10 语音管线",
      title: "Fig 10 · 实时分句流式 TTS、内存 60ms Opus 打包、短语缓存与固定音频切管流水线",
      desc: "拆解 Talker 分句切片、OutputRail 审查、64 项短语 LRU 缓存、PyAV/opuslib_next 纯内存编码与静态练习分段播控。",
      src: "assets/diagrams/10-voice-opus-pipeline.png",
      svg: "assets/diagrams/10-voice-opus-pipeline.svg"
    },
    {
      id: "11",
      tab: "11 场景走查",
      title: "Fig 11 · 三幕典型高中日常交互过程走查：许可进入、疲惫喊停与跨会话边界记忆",
      desc: "全景跟踪三个完整交互样例：父母比较单步进入、晚自习疲惫拒建议与随时安静、更名记忆与成绩边界不误伤。",
      src: "assets/diagrams/11-interaction-walkthroughs.png",
      svg: "assets/diagrams/11-interaction-walkthroughs.svg"
    }
  ];

  let activeScenario = 0;
  let activeOutcome = "initial";
  let activeLane = 0;
  let activeDiagram = 0;
  let siteData = null;
  let catalogFilter = "all";
  let selectedStrategyKey = null;

  function el(id) {
    return document.getElementById(id);
  }

  function renderScenario() {
    const s = SCENARIOS[activeScenario];
    const outcome = s.turns[activeOutcome];
    document.querySelectorAll("[data-scenario-idx]").forEach((btn) => {
      btn.setAttribute("aria-pressed", Number(btn.dataset.scenarioIdx) === activeScenario ? "true" : "false");
    });
    document.querySelectorAll("[data-outcome]").forEach((btn) => {
      btn.setAttribute("aria-pressed", btn.dataset.outcome === activeOutcome ? "true" : "false");
    });
    const chat = el("sim-chat-log");
    if (chat) {
      chat.innerHTML = `
        <div class="msg msg-user">
          <span class="msg-meta">学生输入 · 合成高中日常情境示例</span>
          ${escapeHtml(s.userPrompt)}
        </div>
        <div class="msg msg-bot">
          <span class="msg-meta">${escapeHtml(outcome.meta)}</span>
          ${escapeHtml(outcome.bot)}
        </div>
      `;
    }
    if (el("tel-stage")) el("tel-stage").textContent = outcome.stage;
    if (el("tel-obj")) el("tel-obj").textContent = outcome.objective;
    if (el("tel-card")) el("tel-card").textContent = outcome.card;
    if (el("tel-offer")) el("tel-offer").textContent = outcome.pending;
    if (el("tel-bound")) el("tel-bound").textContent = outcome.boundary;
  }

  function renderLane(pulse = false) {
    const lane = LANES[activeLane];
    document.querySelectorAll("[data-lane-idx]").forEach((btn) => {
      btn.setAttribute("aria-pressed", Number(btn.dataset.laneIdx) === activeLane ? "true" : "false");
    });
    if (el("lane-title")) el("lane-title").textContent = `${lane.code} · ${lane.title}`;
    if (el("lane-summary")) el("lane-summary").textContent = lane.summary;
    if (el("lane-metric")) el("lane-metric").textContent = lane.metric;
    const nodeBox = el("lane-nodes");
    if (nodeBox) {
      nodeBox.innerHTML = lane.nodes
        .map(
          (n, i) =>
            `<span class="sig-node ${pulse || i === 0 ? "is-pulsed" : ""}">${escapeHtml(n)}</span>` +
            (i < lane.nodes.length - 1 ? `<span class="sig-arrow" aria-hidden="true">-&gt;</span>` : "")
        )
        .join("");
      if (pulse && !window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
        const spans = nodeBox.querySelectorAll(".sig-node");
        spans.forEach((sp, i) => {
          sp.classList.remove("is-pulsed");
          setTimeout(() => sp.classList.add("is-pulsed"), i * 160);
        });
      }
    }
  }

  function renderDiagramTabs() {
    const strip = el("diagram-tabs");
    if (!strip) return;
    strip.innerHTML = DIAGRAMS.map(
      (d, idx) =>
        `<button type="button" class="pill-btn" data-diag-idx="${idx}" aria-pressed="${idx === activeDiagram}">${escapeHtml(d.tab)}</button>`
    ).join("");
    strip.querySelectorAll("[data-diag-idx]").forEach((btn) =>
      btn.addEventListener("click", () => {
        activeDiagram = Number(btn.dataset.diagIdx);
        renderDiagram();
      })
    );
  }

  function renderDiagram() {
    const d = DIAGRAMS[activeDiagram];
    document.querySelectorAll("[data-diag-idx]").forEach((btn) => {
      btn.setAttribute("aria-pressed", Number(btn.dataset.diagIdx) === activeDiagram ? "true" : "false");
    });
    if (el("diagram-img")) {
      el("diagram-img").src = d.src;
      el("diagram-img").alt = d.title;
    }
    if (el("diagram-title-line")) el("diagram-title-line").textContent = d.title;
    if (el("diagram-desc")) el("diagram-desc").textContent = d.desc;
    if (el("diagram-svg-link")) el("diagram-svg-link").href = d.svg;
    if (el("diagram-png-link")) el("diagram-png-link").href = d.src;
  }

  function categoryMatch(item, filter) {
    if (filter === "all") return true;
    if (filter === "exercise") return item._kind === "exercise";
    if (item._kind === "exercise") return false;
    const pts = item.targets?.pressure_types || [];
    const pws = item.targets?.pathways || [];
    if (filter === "academic") return pts.includes("academic") || pws.includes("rumination");
    if (filter === "evaluative") return pts.includes("social_evaluative") || pts.includes("self");
    if (filter === "relationship") return pts.includes("relationship");
    if (filter === "future_sleep") return pts.includes("future") || pws.includes("sleep") || item.id === "worry_parking";
    return true;
  }

  function renderCatalog() {
    if (!siteData) return;
    const all = [
      ...(siteData.cards || []).map((c) => ({ ...c, _kind: "card" })),
      ...(siteData.exercises || []).map((e) => ({ ...e, _kind: "exercise" }))
    ];
    const filtered = all.filter((item) => categoryMatch(item, catalogFilter));
    document.querySelectorAll("[data-cat-filter]").forEach((btn) => {
      btn.setAttribute("aria-pressed", btn.dataset.catFilter === catalogFilter ? "true" : "false");
    });
    if (!filtered.some((i) => `${i._kind}:${i.id}` === selectedStrategyKey)) {
      selectedStrategyKey = filtered[0] ? `${filtered[0]._kind}:${filtered[0].id}` : null;
    }
    const grid = el("cards-matrix");
    if (grid) {
      grid.innerHTML = filtered
        .map((item) => {
          const key = `${item._kind}:${item.id}`;
          const active = key === selectedStrategyKey;
          const citeLabel = formatEvidence(item.protocol?.evidence_ids);
          const tag = item._kind === "exercise" ? `EXERCISE · ${citeLabel}` : `CARD · ${citeLabel}`;
          return `<button type="button" class="strat-btn" data-strat-key="${escapeHtml(key)}" aria-pressed="${active}">
            <span class="strat-meta">${escapeHtml(item.id)} · ${escapeHtml(tag)}</span>
            <span class="strat-title">${escapeHtml(item.name)}</span>
            <span class="strat-sub">${escapeHtml(item.protocol?.invitation || item.protocol?.goal || "")}</span>
          </button>`;
        })
        .join("");
      grid.querySelectorAll("[data-strat-key]").forEach((btn) => {
        btn.addEventListener("click", () => {
          selectedStrategyKey = btn.dataset.stratKey;
          renderCatalog();
        });
      });
    }
    const insp = el("proto-inspector");
    const activeItem = filtered.find((i) => `${i._kind}:${i.id}` === selectedStrategyKey);
    if (insp && activeItem) {
      const p = activeItem.protocol || {};
      const sourcesById = Object.fromEntries((siteData.sources || []).map((s) => [s.id, s]));
      const citeLinks = (p.evidence_ids || [])
        .map((id) => {
          const label = EVIDENCE_AUTHOR_YEAR[id] || "Source";
          const url = sourcesById[id]?.url;
          return url
            ? `<a href="${escapeHtml(url)}" target="_blank" rel="noreferrer">${escapeHtml(label)}</a>`
            : escapeHtml(label);
        })
        .join(" · ");

      insp.innerHTML = `
        <span class="kicker" style="margin-bottom:4px;">${escapeHtml(activeItem._kind.toUpperCase())} · ${escapeHtml(activeItem.id)}</span>
        <h3>${escapeHtml(activeItem.name)}</h3>
        <div class="proto-row"><span class="pk">情境化邀请 (invitation)</span><p class="pv">${escapeHtml(p.invitation || "-")}</p></div>
        <div class="proto-row"><span class="pk">${activeItem._kind === "card" ? "作用机制 (mechanism)" : "练习目标 (goal)"}</span><p class="pv">${escapeHtml(p.mechanism || p.goal || "-")}</p></div>
        ${activeItem.steps ? `<div class="proto-row"><span class="pk">短步骤重点</span><p class="pv">${escapeHtml(activeItem.steps.join(" / "))}</p></div>` : ""}
        <div class="proto-row"><span class="pk">停止规则与禁忌边界</span><p class="pv">${escapeHtml(p.stop || "-")} ${activeItem.not_when?.length ? "｜ 禁用：" + escapeHtml(activeItem.not_when.join("；")) : ""}</p></div>
        <div class="proto-row"><span class="pk">研究来源与适用限制</span><p class="pv">${citeLinks || "-"}${p.adaptation || p.feedback_limits ? " · " + escapeHtml(p.adaptation || p.feedback_limits) : ""}</p></div>
      `;
    }
  }

  document.addEventListener("DOMContentLoaded", async () => {
    document.querySelectorAll("[data-scenario-idx]").forEach((btn) =>
      btn.addEventListener("click", () => {
        activeScenario = Number(btn.dataset.scenarioIdx);
        activeOutcome = "initial";
        renderScenario();
      })
    );
    document.querySelectorAll("[data-outcome]").forEach((btn) =>
      btn.addEventListener("click", () => {
        activeOutcome = btn.dataset.outcome;
        renderScenario();
      })
    );
    document.querySelectorAll("[data-lane-idx]").forEach((btn) =>
      btn.addEventListener("click", () => {
        activeLane = Number(btn.dataset.laneIdx);
        renderLane(true);
      })
    );
    document.querySelectorAll("[data-cat-filter]").forEach((btn) =>
      btn.addEventListener("click", () => {
        catalogFilter = btn.dataset.catFilter;
        renderCatalog();
      })
    );

    renderDiagramTabs();
    renderScenario();
    renderLane(false);
    renderDiagram();

    try {
      const resp = await fetch("assets/project-data.json");
      if (resp.ok) {
        siteData = await resp.json();
        renderCatalog();
      }
    } catch (err) {
      console.error("Failed to load project-data.json", err);
    }
  });
})();
