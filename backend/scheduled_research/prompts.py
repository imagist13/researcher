"""
定时研究专用提示词系统
Scheduled Research Prompts System
"""
from datetime import datetime
from typing import List, Dict, Any, Optional


class ScheduledResearchPrompts:
    """定时研究和趋势分析专用提示词"""
    
    @staticmethod
    def generate_trend_research_query(topic: str, keywords: List[str], analysis_depth: str = "basic") -> str:
        """
        生成趋势研究查询提示词
        
        Args:
            topic: 研究主题
            keywords: 关键词列表  
            analysis_depth: 分析深度（basic/detailed/deep）
            
        Returns:
            优化的研究查询
        """
        
        # 根据分析深度调整查询策略
        depth_modifiers = {
            "basic": "最新发展和主要趋势",
            "detailed": "详细趋势分析、影响因素和市场变化",
            "deep": "深度趋势研究、预测分析、行业影响和未来展望"
        }
        
        modifier = depth_modifiers.get(analysis_depth, depth_modifiers["basic"])
        keywords_str = "、".join(keywords)
        
        query = f"""
研究主题: {topic}
关键词: {keywords_str}
研究重点: {modifier}

请重点关注以下方面:
1. 最新发展动态和变化趋势
2. 关键事件和重要节点
3. 市场反应和影响评估
4. 专家观点和分析报告
5. 数据指标和量化趋势

时间范围: 近期至当前（优先最新信息）
信息来源: 权威媒体、官方发布、专业分析
        """.strip()
        
        return query

    @staticmethod 
    def generate_trend_analysis_prompt(
        topic: str,
        current_data: str,
        historical_data: Optional[List[Dict]] = None,
        keywords: Optional[List[str]] = None
    ) -> str:
        """
        生成趋势分析提示词
        
        Args:
            topic: 研究主题
            current_data: 当前研究数据
            historical_data: 历史数据记录
            keywords: 关键词列表
            
        Returns:
            趋势分析提示词
        """
        
        historical_context = ""
        if historical_data:
            historical_context = "\n### 历史数据参考:\n"
            for i, record in enumerate(historical_data[-3:], 1):  # 最近3条记录
                date = record.get('executed_at', '未知时间')
                summary = record.get('summary', '无摘要')[:200]
                historical_context += f"{i}. {date}: {summary}...\n"
        
        keywords_context = ""
        if keywords:
            keywords_context = f"\n### 关键监控词汇: {', '.join(keywords)}\n"
        
        prompt = f"""
你是一位专业的趋势分析专家，请对以下主题进行深度趋势分析：

### 研究主题: {topic}
{keywords_context}
### 当前研究数据:
{current_data}
{historical_context}

请按照以下结构进行分析：

## 1. 趋势概览
- 总体发展方向和变化态势
- 主要驱动因素识别
- 关键转折点分析

## 2. 关键变化识别
- 与历史数据的对比分析
- 新出现的重要信息
- 显著变化的指标或事件
- 异常或突破性发展

## 3. 关键词热度分析
- 各关键词的当前活跃度
- 热度变化趋势对比
- 新兴相关词汇识别

## 4. 情感倾向分析
- 整体舆论和市场情感
- 正面/负面/中性比例
- 情感变化趋势

## 5. 影响评估
- 短期影响预测
- 中长期趋势判断
- 潜在风险和机会

## 6. 趋势评分
请给出一个1-10的趋势活跃度评分，其中：
- 1-3: 低活跃度，变化较小
- 4-6: 中等活跃度，有明显变化
- 7-8: 高活跃度，重要变化
- 9-10: 极高活跃度，突破性变化

请确保分析客观、准确，并重点突出与历史数据的差异和新发现。
        """.strip()
        
        return prompt

    @staticmethod
    def generate_summary_prompt(
        topic: str,
        research_data: str,
        trend_analysis: str,
        focus_on_changes: bool = True
    ) -> str:
        """
        生成动态摘要提示词
        
        Args:
            topic: 研究主题
            research_data: 研究数据
            trend_analysis: 趋势分析结果
            focus_on_changes: 是否重点关注变化
            
        Returns:
            摘要生成提示词
        """
        
        focus_instruction = ""
        if focus_on_changes:
            focus_instruction = """
特别要求：请重点突出以下内容
- 最新发生的重要变化
- 与之前状态的显著差异
- 新出现的趋势和信号
- 关键转折点和突破
            """
        
        prompt = f"""
你是一位专业的信息摘要专家，请为以下定时研究结果生成简洁而全面的摘要：

### 研究主题: {topic}

### 原始研究数据:
{research_data}

### 趋势分析结果:
{trend_analysis}

{focus_instruction}

请生成一个结构化的摘要，包含：

## 📍 核心发现
- 3-5个最重要的发现点
- 用简洁明了的语言描述

## 🔄 关键变化 
- 列出最重要的变化事项（如有）
- 每个变化用一句话描述

## 📈 趋势信号
- 主要的发展趋势
- 新兴的关注点

## ⚠️ 重要提醒
- 需要特别关注的事项
- 可能的风险或机会

## 🎯 总结
- 一句话总结整体状况
- 给出发展方向的简要判断

要求：
1. 摘要总长度控制在300-500字
2. 语言简洁、重点突出
3. 突出时效性和变化性
4. 适合快速阅读和理解
        """.strip()
        
        return prompt

    @staticmethod
    def generate_keyword_extraction_prompt(text: str, existing_keywords: List[str]) -> str:
        """
        生成关键词提取提示词
        
        Args:
            text: 源文本
            existing_keywords: 现有关键词
            
        Returns:
            关键词提取提示词
        """
        
        existing_str = "、".join(existing_keywords) if existing_keywords else "无"
        
        prompt = f"""
请从以下文本中提取最重要和最相关的关键词：

### 现有关键词参考: {existing_str}

### 待分析文本:
{text}

请按照以下要求提取关键词：

## 提取标准:
1. 高频出现的重要名词和术语
2. 具有趋势意义的概念词汇
3. 行业专业术语和技术名词
4. 重要人物、机构、产品名称
5. 新兴或热门的概念词汇

## 输出格式:
- 核心关键词: 5-8个最重要的词汇
- 新兴关键词: 3-5个新出现或活跃度上升的词汇
- 相关关键词: 5-10个次要但相关的词汇

## 要求:
1. 关键词应该是名词或名词短语
2. 避免过于通用的词汇
3. 优先选择具有趋势指示意义的词汇
4. 每个关键词用简洁的形式表达
5. 按重要性排序

请确保提取的关键词准确反映文本的核心内容和趋势特征。
        """.strip()
        
        return prompt

    @staticmethod
    def generate_anomaly_detection_prompt(
        current_data: str,
        historical_pattern: str,
        threshold_score: float = 7.0
    ) -> str:
        """
        生成异常检测提示词
        
        Args:
            current_data: 当前数据
            historical_pattern: 历史模式
            threshold_score: 异常阈值
            
        Returns:
            异常检测提示词
        """
        
        prompt = f"""
你是一位专业的数据异常检测分析师，请分析以下数据是否存在异常模式：

### 当前数据:
{current_data}

### 历史模式参考:
{historical_pattern}

### 异常检测阈值: {threshold_score}分（满分10分）

请进行以下分析：

## 1. 模式对比分析
- 当前数据与历史模式的主要差异
- 变化幅度和方向评估
- 偏离程度量化分析

## 2. 异常信号识别
- 突然出现的新现象
- 显著的数值变化
- 异常的时间模式
- 不寻常的关联关系

## 3. 异常类型分类
- 正向异常（积极变化）
- 负向异常（消极变化）
- 中性异常（值得关注的变化）

## 4. 严重程度评估
请给出异常严重程度评分（1-10分）：
- 1-3分: 正常波动范围
- 4-6分: 轻微异常，需观察
- 7-8分: 明显异常，需重点关注
- 9-10分: 严重异常，需立即处理

## 5. 异常原因推测
- 可能的驱动因素
- 外部环境影响
- 内在发展规律

## 6. 建议措施
- 是否需要进一步调查
- 建议的应对策略
- 监控重点调整建议

请基于客观分析给出专业判断，重点识别真正值得关注的异常模式。
        """.strip()
        
        return prompt

    @staticmethod
    def generate_prediction_prompt(
        topic: str,
        current_trends: str,
        historical_data: List[Dict],
        prediction_horizon: str = "1个月"
    ) -> str:
        """
        生成趋势预测提示词
        
        Args:
            topic: 研究主题
            current_trends: 当前趋势
            historical_data: 历史数据
            prediction_horizon: 预测时间范围
            
        Returns:
            趋势预测提示词
        """
        
        historical_summary = ""
        if historical_data:
            historical_summary = "\n### 历史发展轨迹:\n"
            for record in historical_data[-5:]:  # 最近5条记录
                date = record.get('executed_at', '未知时间')
                trend_score = record.get('trend_score', 0)
                summary = record.get('summary', '无摘要')[:100]
                historical_summary += f"- {date}: 趋势分数{trend_score}, {summary}...\n"
        
        prompt = f"""
你是一位专业的趋势预测分析师，请基于以下信息对主题进行前瞻性分析：

### 研究主题: {topic}
### 预测时间范围: {prediction_horizon}

### 当前趋势状况:
{current_trends}
{historical_summary}

请进行以下预测分析：

## 1. 短期发展预测（未来2周）
- 预期的主要发展方向
- 可能出现的重要事件
- 关键指标的变化趋势

## 2. 中期趋势预测（未来1-3个月）
- 主要发展轨迹预判
- 潜在的转折点识别
- 影响因素变化分析

## 3. 关键驱动因素
- 主要推动力量识别
- 阻碍因素分析
- 外部环境影响评估

## 4. 情景分析
- 最可能情景（60-70%概率）
- 乐观情景（15-20%概率）
- 悲观情景（15-20%概率）

## 5. 风险与机会
- 主要风险点识别
- 潜在机会发现
- 不确定性因素

## 6. 监控建议
- 需要重点关注的指标
- 重要时间节点提醒
- 预警信号识别

## 7. 可信度评估
请评估预测的可信度（1-10分）并说明理由：
- 8-10分: 高可信度，基于明确模式
- 5-7分: 中等可信度，存在一定不确定性
- 1-4分: 低可信度，变数较多

请基于数据和逻辑进行客观预测，避免过度主观判断。
        """.strip()
        
        return prompt

    @staticmethod
    def generate_comparative_analysis_prompt(
        topic: str,
        current_data: str,
        comparison_data: List[Dict],
        comparison_timeframe: str = "同期历史数据"
    ) -> str:
        """
        生成对比分析提示词
        
        Args:
            topic: 研究主题
            current_data: 当前数据
            comparison_data: 对比数据
            comparison_timeframe: 对比时间框架
            
        Returns:
            对比分析提示词
        """
        
        comparison_context = ""
        if comparison_data:
            comparison_context = f"\n### {comparison_timeframe}:\n"
            for i, data in enumerate(comparison_data, 1):
                date = data.get('executed_at', '未知时间')
                summary = data.get('summary', '无摘要')[:150]
                trend_score = data.get('trend_score', 0)
                comparison_context += f"{i}. {date} (趋势分数: {trend_score})\n   {summary}...\n\n"
        
        prompt = f"""
你是一位专业的对比分析专家，请对以下数据进行深度对比分析：

### 研究主题: {topic}

### 当前数据:
{current_data}
{comparison_context}

请进行以下对比分析：

## 1. 整体变化趋势
- 总体发展方向对比
- 变化速度和幅度分析
- 发展阶段特征识别

## 2. 关键指标对比
- 重要数据指标的变化
- 量化指标的对比分析
- 关键表现指标(KPI)变化

## 3. 质性变化分析
- 发展质量和特征变化
- 新出现的特征和模式
- 消失或弱化的特征

## 4. 时间维度分析
- 变化的时间节奏
- 周期性模式识别
- 季节性或周期性因素

## 5. 影响因素对比
- 主要驱动因素的变化
- 新出现的影响因素
- 环境因素的变化影响

## 6. 差异化分析
- 最显著的差异点
- 超出预期的变化
- 值得关注的新趋势

## 7. 变化评估
请给出变化程度评分（1-10分）：
- 1-3分: 微小变化，基本稳定
- 4-6分: 中等变化，有明显差异
- 7-8分: 显著变化，重要转变
- 9-10分: 重大变化，根本性转变

## 8. 洞察和发现
- 通过对比发现的关键洞察
- 值得深入研究的问题
- 对未来发展的启示

请确保对比分析客观、全面，突出最有价值的发现和洞察。
        """.strip()
        
        return prompt
