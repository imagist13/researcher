/**
 * 模拟AI分析结果数据
 * Mock data for AI analysis results
 */
import { ResearchHistoryRecord } from '@/types/data';

export const generateMockAnalysisData = (taskId: string, count: number = 5): ResearchHistoryRecord[] => {
  const statuses: ('success' | 'failed' | 'partial')[] = ['success', 'success', 'success', 'partial', 'failed'];
  const topics = [
    'AI技术发展趋势',
    '区块链技术应用',
    '量子计算研究进展',
    '新能源汽车市场',
    '生物技术突破'
  ];
  
  const mockData: ResearchHistoryRecord[] = [];
  
  for (let i = 0; i < count; i++) {
    const date = new Date();
    date.setHours(date.getHours() - i * 6); // 每6小时一次执行
    
    const status = statuses[i % statuses.length];
    const isSuccess = status === 'success';
    
    mockData.push({
      id: `history_${taskId}_${i}`,
      task_id: taskId,
      executed_at: date.toISOString(),
      execution_duration: 15.5 + Math.random() * 30,
      status,
      error_message: status === 'failed' ? '网络连接超时，部分数据源无法访问' : undefined,
      raw_result: isSuccess ? JSON.stringify({
        research_topic: topics[i % topics.length],
        findings: [
          '发现了新的技术突破点',
          '市场需求呈现上升趋势',
          '竞争格局发生重要变化'
        ],
        sources: [
          { url: 'https://example.com/source1', title: '技术报告1' },
          { url: 'https://example.com/source2', title: '市场分析2' }
        ],
        analysis: {
          trend: 'positive',
          confidence: 0.85,
          key_metrics: {
            growth_rate: '15.2%',
            market_size: '$2.5B',
            adoption_rate: '68%'
          }
        }
      }, null, 2) : undefined,
      summary: isSuccess ? `本次研究发现${topics[i % topics.length]}领域出现了显著的发展变化，主要体现在技术创新、市场需求和政策支持三个方面。通过分析${3 + i}个主要信息源，识别出了${2 + i}个关键趋势变化。` : '执行失败，无法生成摘要',
      key_findings: isSuccess ? [
        '技术成熟度显著提升',
        '市场接受度持续增长',
        '投资热度保持高位',
        '政策环境日趋完善'
      ].slice(0, 2 + i % 3) : [],
      key_changes: isSuccess ? [
        '相比上次分析，热度上升12%',
        '新增3个重要参与者',
        '政策支持力度加强'
      ].slice(0, 1 + i % 3) : [],
      sources_count: isSuccess ? 5 + i : 0,
      tokens_used: isSuccess ? 2500 + Math.floor(Math.random() * 1000) : 0,
      trend_score: isSuccess ? 6.5 + Math.random() * 3 : undefined,
      sentiment_score: isSuccess ? -0.2 + Math.random() * 1.4 : undefined,
      research_config: {
        analysis_depth: 'detailed',
        source_types: ['web', 'news', 'academic'],
        language: 'zh-CN',
        max_sources: 10,
        keywords: ['AI', '人工智能', '技术趋势']
      },
      sources_used: isSuccess ? [
        {
          url: 'https://tech-news.example.com/ai-trends-2024',
          title: '2024年AI技术发展趋势报告',
          domain: 'tech-news.example.com',
          relevance_score: 0.92,
          publish_date: '2024-01-15',
          summary: '详细分析了当前AI技术的发展现状和未来趋势'
        },
        {
          url: 'https://research.example.com/artificial-intelligence',
          title: '人工智能技术研究前沿',
          domain: 'research.example.com',
          relevance_score: 0.88,
          publish_date: '2024-01-10',
          summary: '学术视角下的AI技术发展分析'
        },
        {
          url: 'https://market.example.com/ai-market-analysis',
          title: 'AI市场分析与投资机会',
          domain: 'market.example.com',
          relevance_score: 0.85,
          publish_date: '2024-01-12',
          summary: '从市场角度分析AI技术的商业价值和投资前景'
        }
      ].slice(0, 2 + i % 2) : []
    });
  }
  
  return mockData;
};

export const mockResearchResult = {
  research_topic: "AI技术发展趋势分析",
  executive_summary: "本次研究深入分析了2024年人工智能技术的发展趋势，发现AI技术在多个领域都呈现出加速发展的态势。",
  key_findings: [
    {
      title: "大模型技术持续演进",
      description: "GPT、Claude等大语言模型在参数规模和能力上都有显著提升",
      impact_level: "high",
      confidence: 0.92
    },
    {
      title: "多模态AI成为新热点",
      description: "结合文本、图像、语音的多模态AI应用快速增长",
      impact_level: "medium",
      confidence: 0.87
    },
    {
      title: "AI基础设施投资激增",
      description: "云计算厂商大幅增加AI芯片和算力投资",
      impact_level: "high",
      confidence: 0.89
    }
  ],
  trend_analysis: {
    overall_trend: "strongly_positive",
    growth_rate: "45%",
    market_size: "$184.5B",
    key_drivers: [
      "技术突破",
      "政策支持",
      "市场需求",
      "投资增长"
    ]
  },
  competitive_landscape: {
    leading_companies: ["OpenAI", "Google", "Microsoft", "Anthropic"],
    emerging_players: ["Stability AI", "Cohere", "Inflection AI"],
    market_concentration: "moderate"
  },
  future_outlook: {
    short_term: "持续快速增长，技术应用场景不断扩展",
    long_term: "AI将深度融入各行各业，成为数字化转型的核心驱动力",
    risks: ["监管不确定性", "技术伦理问题", "人才短缺"]
  },
  methodology: {
    data_sources: 15,
    analysis_period: "2024-01-01 to 2024-01-15",
    keywords_analyzed: ["人工智能", "AI技术", "大模型", "机器学习"],
    confidence_level: 0.88
  }
};
