// 中文本地化配置
export const zhCN = {
  // 通用
  common: {
    loading: "加载中...",
    search: "搜索",
    submit: "提交",
    cancel: "取消",
    save: "保存",
    delete: "删除",
    edit: "编辑",
    back: "返回",
    next: "下一步",
    previous: "上一步",
    confirm: "确认",
    close: "关闭",
  },

  // 导航
  nav: {
    research: "研究",
    scheduledResearch: "定时研究",
    settings: "设置",
    history: "历史记录",
    home: "首页",
  },

  // 页面标题和描述
  meta: {
    title: "GPT Researcher - AI智能研究助手",
    description: "基于大语言模型的自主研究代理，能够进行本地和网络研究，生成包含引用的全面报告。",
    keywords: "AI研究,智能助手,研究报告,GPT,人工智能",
  },

  // 主页英雄区域
  hero: {
    mainTitle: "告别漫长的",
    highlightTitle: "研究时光",
    subtitle: "欢迎使用GPT Researcher，您的AI研究伙伴，提供即时洞察和全面研究",
    placeholder: "您希望我研究什么主题？",
    chatPlaceholder: "对这份报告有什么问题吗？",
    poweredBy: "由以下技术驱动",
    suggestions: {
      title: "热门研究主题",
      items: [
        "人工智能的最新发展趋势",
        "可持续能源技术现状",
        "区块链技术应用前景",
        "量子计算发展现状",
        "生物技术创新突破"
      ]
    }
  },

  // 研究相关
  research: {
    newResearch: "新研究",
    stopResearch: "停止研究",
    researchInProgress: "研究进行中...",
    researchCompleted: "研究完成",
    researchStopped: "研究已停止",
    generateReport: "生成报告",
    downloadReport: "下载报告",
    shareReport: "分享报告",
    reportGenerated: "报告已生成",
    noResults: "暂无研究结果",
    searchSources: "搜索来源",
    analyzingData: "分析数据中...",
    compilingReport: "编译报告中...",
    sources: "来源",
    references: "参考文献",
  },

  // 侧边栏
  sidebar: {
    researchHistory: "研究历史",
    recentResearches: "最近研究",
    noHistory: "暂无研究历史",
    deleteConfirm: "确定要删除这项研究吗？",
    lastUpdated: "最后更新",
    toggleSidebar: "切换侧边栏",
  },

  // 设置
  settings: {
    title: "设置",
    apiKeys: "API密钥",
    reportSettings: "报告设置",
    language: "语言",
    theme: "主题",
    reportType: "报告类型",
    reportSource: "报告来源",
    tone: "语调",
    maxSources: "最大来源数",
    domains: "指定域名",
    save: "保存设置",
    reset: "重置设置",
    openaiApiKey: "OpenAI API密钥",
    tavilyApiKey: "Tavily API密钥",
    anthropicApiKey: "Anthropic API密钥",
    reportTypes: {
      research_report: "研究报告",
      resource_report: "资源报告",
      outline_report: "大纲报告",
      custom_report: "自定义报告",
    },
    reportSources: {
      web: "网络",
      local: "本地文档",
      hybrid: "混合模式",
    },
    tones: {
      objective: "客观",
      formal: "正式",
      analytical: "分析性",
      persuasive: "说服性",
      informative: "信息性",
    }
  },

  // 定时研究
  scheduled: {
    title: "定时研究",
    createTask: "创建任务",
    editTask: "编辑任务",
    taskName: "任务名称",
    description: "描述",
    schedule: "调度",
    frequency: "频率",
    nextRun: "下次运行",
    status: "状态",
    actions: "操作",
    active: "活跃",
    inactive: "非活跃",
    completed: "已完成",
    failed: "失败",
    running: "运行中",
    daily: "每日",
    weekly: "每周",
    monthly: "每月",
    custom: "自定义",
  },

  // 错误和消息
  messages: {
    error: "发生错误",
    success: "操作成功",
    warning: "警告",
    info: "信息",
    networkError: "网络连接错误",
    serverError: "服务器错误",
    invalidInput: "输入无效",
    operationFailed: "操作失败",
    operationSuccess: "操作成功",
    saveFailed: "保存失败",
    saveSuccess: "保存成功",
    deleteFailed: "删除失败",
    deleteSuccess: "删除成功",
  },

  // 报告导出
  export: {
    title: "导出报告",
    formats: "格式",
    pdf: "PDF",
    word: "Word文档",
    markdown: "Markdown",
    html: "HTML",
    downloading: "下载中...",
    downloadComplete: "下载完成",
    downloadFailed: "下载失败",
  },

  // 页脚
  footer: {
    copyright: "版权所有",
    allRightsReserved: "保留所有权利",
    links: {
      github: "GitHub",
      discord: "Discord",
      documentation: "文档",
      website: "官网",
    }
  },

  // 人工反馈
  humanFeedback: {
    title: "需要您的反馈",
    prompt: "请提供您的反馈以改进研究质量：",
    placeholder: "请输入您的反馈...",
    submit: "提交反馈",
    skip: "跳过",
    thankYou: "感谢您的反馈！",
  },

  // 时间格式
  time: {
    justNow: "刚刚",
    minutesAgo: "分钟前",
    hoursAgo: "小时前",
    daysAgo: "天前",
    weeksAgo: "周前",
    monthsAgo: "个月前",
    yearsAgo: "年前",
  }
};

export default zhCN;
