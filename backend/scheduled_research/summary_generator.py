"""
动态摘要生成器 - 生成AI驱动的智能摘要
Dynamic Summary Generator - Generates AI-driven intelligent summaries
"""
import logging
import json
from datetime import datetime
from typing import Dict, List, Any, Optional

from .prompts import ScheduledResearchPrompts
import asyncio

logger = logging.getLogger(__name__)


class DynamicSummaryGenerator:
    """
    动态摘要生成器
    Generates dynamic summaries based on research results and trend analysis
    """
    
    def __init__(self):
        """初始化摘要生成器"""
        self.summary_templates = {
            "trending_up": "📈 {topic} 呈现上升趋势，活跃度显著提升",
            "trending_down": "📉 {topic} 活跃度有所下降，需要关注发展动向", 
            "stable": "📊 {topic} 保持稳定发展，无明显波动",
            "emerging": "🚀 {topic} 出现新的发展方向，值得重点关注",
            "anomaly": "⚠️ {topic} 检测到异常变化，建议深入分析"
        }
    
    async def generate_dynamic_summary(self, task, research_result: Dict[str, Any], trend_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成动态摘要
        
        Args:
            task: 任务对象
            research_result: 研究结果
            trend_result: 趋势分析结果
            
        Returns:
            Dict包含生成的摘要和相关信息
        """
        try:
            logger.info(f"Generating dynamic summary for: {task.topic}")
            
            # 简化分类，增加具体内容
            summary_data = {
                "summary": "",
                "key_findings": [],
                "key_changes": []
            }
            
            # 生成综合性详细摘要（包含趋势、分析、建议等所有内容）
            summary_data["summary"] = await self._generate_comprehensive_summary(task, research_result, trend_result)
            
            # 生成详细的关键发现（包含具体内容和分析）
            summary_data["key_findings"] = self._extract_detailed_findings(research_result, trend_result)
            
            # 生成详细的变化分析（包含趋势变化和具体数据）
            summary_data["key_changes"] = self._identify_detailed_changes(trend_result)
            
            logger.info(f"Dynamic summary generated successfully")
            
            return summary_data
            
        except Exception as e:
            logger.error(f"Dynamic summary generation failed: {e}")
            return self._create_fallback_summary(research_result, task)
    
    async def _generate_comprehensive_summary(self, task, research_result: Dict[str, Any], trend_result: Dict[str, Any]) -> str:
        """生成综合性详细摘要"""
        try:
            # 获取趋势分数和状态
            trend_score = trend_result.get("trend_score", 5.0)
            activity_level = trend_result.get("activity_level", 5.0)
            anomaly_detected = trend_result.get("anomaly_detected", False)
            
            # 确定趋势状态
            if anomaly_detected:
                trend_status = "anomaly"
            elif trend_score > 7.5:
                trend_status = "trending_up"
            elif trend_score < 3.5:
                trend_status = "trending_down"
            elif len(trend_result.get("new_topics", [])) > 3:
                trend_status = "emerging"
            else:
                trend_status = "stable"
            
            # 基础摘要模板
            base_summary = self.summary_templates.get(trend_status, "").format(topic=task.topic)
            
            # 添加详细信息
            details = []
            
            # 添加活跃度信息
            if activity_level > 7.0:
                details.append(f"当前活跃度较高 (评分: {activity_level:.1f}/10)")
            elif activity_level < 4.0:
                details.append(f"当前活跃度较低 (评分: {activity_level:.1f}/10)")
            
            # 添加新发现信息
            new_topics = trend_result.get("new_topics", [])
            if new_topics:
                details.append(f"发现 {len(new_topics)} 个新相关话题")
            
            # 添加关键词趋势
            keyword_trends = trend_result.get("keyword_trends", {})
            trending_keywords = [k for k, v in keyword_trends.items() if v > 7.0]
            if trending_keywords:
                details.append(f"热门关键词: {', '.join(trending_keywords[:3])}")
            
            # 添加情感变化
            sentiment_changes = trend_result.get("sentiment_changes", {})
            for sentiment_type, data in sentiment_changes.items():
                if isinstance(data, dict) and data.get("trend") in ["up", "down"]:
                    if sentiment_type == "positive" and data.get("trend") == "up":
                        details.append("正面情绪呈上升趋势")
                    elif sentiment_type == "negative" and data.get("trend") == "up":
                        details.append("负面情绪有所增加")
            
            # 构建详细的综合摘要
            summary_parts = [base_summary]
            
            # 添加详细的数据分析
            if details:
                summary_parts.append(f"详细分析：{' '.join(details)}。")
            
            # 添加具体的研究内容摘录
            report_content = research_result.get("report", "")
            if report_content and len(report_content) > 100:
                # 提取报告的关键段落
                key_paragraphs = self._extract_key_paragraphs(report_content)
                if key_paragraphs:
                    summary_parts.append(f"\n\n**主要发现：**\n{key_paragraphs}")
            
            # 添加趋势分析详情
            trend_details = self._generate_detailed_trend_analysis(trend_result)
            if trend_details:
                summary_parts.append(f"\n\n**趋势分析：**\n{trend_details}")
            
            # 添加行动建议和后续关注重点
            recommendations = self._generate_comprehensive_recommendations(task, trend_result)
            if recommendations:
                summary_parts.append(f"\n\n**建议与后续关注：**\n{recommendations}")
            
            # 添加时间戳
            timestamp = datetime.now().strftime("%Y年%m月%d日 %H:%M")
            summary_parts.append(f"\n\n*数据更新时间: {timestamp}*")
            
            return '\n'.join(summary_parts)
            
        except Exception as e:
            logger.error(f"Main summary generation failed: {e}")
            return f"关于 {task.topic} 的最新分析报告已生成。数据更新时间: {datetime.now().strftime('%Y年%m月%d日 %H:%M')}"
    
    def _extract_key_paragraphs(self, report_content: str) -> str:
        """从报告中提取关键段落"""
        try:
            # 分割成段落
            paragraphs = [p.strip() for p in report_content.split('\n\n') if p.strip()]
            if not paragraphs:
                paragraphs = [p.strip() for p in report_content.split('\n') if p.strip() and len(p.strip()) > 50]
            
            # 选择最有价值的段落（长度适中，包含关键词）
            key_paragraphs = []
            important_keywords = ["突破", "创新", "发展", "增长", "变化", "趋势", "影响", "重要", "关键", "显著", "主要", "核心", "新兴"]
            
            for paragraph in paragraphs[:10]:  # 检查前10个段落
                if 50 <= len(paragraph) <= 300:  # 长度适中
                    keyword_count = sum(1 for keyword in important_keywords if keyword in paragraph)
                    if keyword_count >= 1:  # 包含至少一个关键词
                        key_paragraphs.append(paragraph)
                        if len(key_paragraphs) >= 3:  # 最多选择3个段落
                            break
            
            # 如果没有找到合适的段落，选择前几个较长的段落
            if not key_paragraphs:
                key_paragraphs = [p for p in paragraphs[:3] if len(p) > 30]
            
            return '\n\n'.join(key_paragraphs[:3])
            
        except Exception as e:
            logger.error(f"Key paragraphs extraction failed: {e}")
            return ""

    def _generate_detailed_trend_analysis(self, trend_result: Dict[str, Any]) -> str:
        """生成详细的趋势分析"""
        try:
            analysis_parts = []
            
            # 基础指标分析
            trend_score = trend_result.get("trend_score", 5.0)
            activity_level = trend_result.get("activity_level", 5.0)
            change_magnitude = trend_result.get("change_magnitude", 0.0)
            confidence_score = trend_result.get("confidence_score", 0.5)
            
            # 趋势分析
            if trend_score > 7.5:
                analysis_parts.append(f"**趋势强度：** 当前呈现强劲上升趋势 (评分: {trend_score:.1f}/10)，表明该话题正获得越来越多的关注和讨论。")
            elif trend_score > 6.0:
                analysis_parts.append(f"**趋势强度：** 表现出温和的上升趋势 (评分: {trend_score:.1f}/10)，相关活动和讨论有所增加。")
            elif trend_score < 3.5:
                analysis_parts.append(f"**趋势强度：** 出现下降趋势 (评分: {trend_score:.1f}/10)，关注度和活跃程度有所减少。")
            else:
                analysis_parts.append(f"**趋势强度：** 保持相对稳定的发展态势 (评分: {trend_score:.1f}/10)，没有明显的波动变化。")
            
            # 活跃度分析
            if activity_level > 7.0:
                analysis_parts.append(f"**活跃程度：** 当前处于高度活跃状态 (评分: {activity_level:.1f}/10)，信息更新频繁，讨论热烈。")
            elif activity_level > 5.0:
                analysis_parts.append(f"**活跃程度：** 维持中等活跃水平 (评分: {activity_level:.1f}/10)，有稳定的信息产出和关注。")
            else:
                analysis_parts.append(f"**活跃程度：** 活跃度相对较低 (评分: {activity_level:.1f}/10)，可能需要寻找新的信息源或调整关键词。")
            
            # 变化程度分析
            if change_magnitude > 6.0:
                analysis_parts.append(f"**变化程度：** 发生了显著变化 (评分: {change_magnitude:.1f}/10)，出现了值得关注的新动向或转折点。")
            elif change_magnitude > 3.0:
                analysis_parts.append(f"**变化程度：** 出现了一定程度的变化 (评分: {change_magnitude:.1f}/10)，趋势正在逐步演进。")
            else:
                analysis_parts.append(f"**变化程度：** 变化相对平缓 (评分: {change_magnitude:.1f}/10)，保持了相对稳定的发展模式。")
            
            # 关键词趋势详情
            keyword_trends = trend_result.get("keyword_trends", {})
            if keyword_trends:
                trending_up = [(k, v) for k, v in keyword_trends.items() if v > 7.0]
                trending_down = [(k, v) for k, v in keyword_trends.items() if v < 4.0]
                
                if trending_up:
                    trending_keywords = ', '.join([f"{k}({v:.1f})" for k, v in trending_up[:3]])
                    analysis_parts.append(f"**热门关键词：** {trending_keywords} - 这些关键词显示出强劲的上升趋势，值得重点关注。")
                
                if trending_down:
                    declining_keywords = ', '.join([f"{k}({v:.1f})" for k, v in trending_down[:3]])
                    analysis_parts.append(f"**热度下降：** {declining_keywords} - 这些关键词的关注度有所下降，可能反映了话题重点的转移。")
            
            # 新兴内容分析
            new_topics = trend_result.get("new_topics", [])
            emerging_keywords = trend_result.get("emerging_keywords", [])
            
            if new_topics or emerging_keywords:
                emerging_content = []
                if new_topics:
                    emerging_content.append(f"新话题: {', '.join(new_topics[:3])}")
                if emerging_keywords:
                    emerging_content.append(f"新关键词: {', '.join(emerging_keywords[:3])}")
                
                analysis_parts.append(f"**新兴内容：** {'; '.join(emerging_content)} - 这些新出现的元素可能代表了该领域的最新发展方向。")
            
            # 数据可靠性
            if confidence_score > 0.8:
                analysis_parts.append(f"**数据可靠性：** 高置信度 ({confidence_score:.1%}) - 基于充足的历史数据和高质量的信息源。")
            elif confidence_score > 0.5:
                analysis_parts.append(f"**数据可靠性：** 中等置信度 ({confidence_score:.1%}) - 有一定的历史数据支撑，结论较为可靠。")
            else:
                analysis_parts.append(f"**数据可靠性：** 低置信度 ({confidence_score:.1%}) - 历史数据有限，建议积累更多数据后再做判断。")
            
            return '\n\n'.join(analysis_parts)
            
        except Exception as e:
            logger.error(f"Detailed trend analysis generation failed: {e}")
            return "趋势分析正在进行中，请稍后查看详细结果。"

    def _generate_comprehensive_recommendations(self, task, trend_result: Dict[str, Any]) -> str:
        """生成综合性建议和后续关注重点"""
        try:
            recommendations = []
            
            trend_score = trend_result.get("trend_score", 5.0)
            activity_level = trend_result.get("activity_level", 5.0)
            new_topics = trend_result.get("new_topics", [])
            emerging_keywords = trend_result.get("emerging_keywords", [])
            anomaly_detected = trend_result.get("anomaly_detected", False)
            
            # 基于趋势的建议
            if trend_score > 8.0:
                recommendations.append("**立即行动建议：** 当前趋势非常强劲，建议密切关注最新发展，考虑加大投入或提高关注优先级。这可能是一个重要的发展窗口期。")
            elif trend_score > 6.0:
                recommendations.append("**持续关注建议：** 趋势向好，建议保持当前的监测频率，及时跟进相关动态，适时调整策略方向。")
            elif trend_score < 3.0:
                recommendations.append("**策略调整建议：** 当前趋势走低，建议评估是否需要调整研究方向或重新定位关注重点，可能需要寻找新的切入角度。")
            else:
                recommendations.append("**稳定监测建议：** 趋势相对稳定，建议继续定期监测，关注潜在的变化信号和新兴发展方向。")
            
            # 基于活跃度的建议
            if activity_level > 8.0:
                recommendations.append("**实时跟进：** 当前活跃度极高，信息更新频繁，建议启用实时监测模式，确保不错过重要信息和发展动向。")
            elif activity_level < 3.0:
                recommendations.append("**信息源优化：** 活跃度较低，建议扩展信息源范围，调整搜索关键词组合，或缩短监测间隔以捕获更多动态。")
            
            # 基于新内容的建议
            if len(new_topics) > 2 or len(emerging_keywords) > 3:
                focus_areas = []
                if new_topics:
                    focus_areas.extend(new_topics[:3])
                if emerging_keywords:
                    focus_areas.extend(emerging_keywords[:3])
                
                unique_areas = list(dict.fromkeys(focus_areas))[:4]
                recommendations.append(f"**新兴领域关注：** 发现了多个新的发展方向，建议重点关注以下领域：{', '.join(unique_areas)}。这些可能代表了未来的重要发展趋势。")
            
            # 基于异常的建议
            if anomaly_detected:
                anomaly_desc = trend_result.get("anomaly_description", "")
                recommendations.append(f"**异常情况处理：** 检测到异常变化模式 - {anomaly_desc}。建议立即进行深度分析，了解变化原因，评估对整体趋势的影响。")
            
            # 监测优化建议
            if task.interval_hours > 24:
                recommendations.append("**监测频率优化：** 考虑将监测间隔从当前的{}小时缩短至12-24小时，以获取更及时的信息和趋势变化。".format(task.interval_hours))
            
            # 关键词优化建议
            keyword_trends = trend_result.get("keyword_trends", {})
            if keyword_trends:
                low_performing = [k for k, v in keyword_trends.items() if v < 3.0]
                if low_performing and len(low_performing) > 1:
                    recommendations.append(f"**关键词优化：** 以下关键词表现较差：{', '.join(low_performing[:2])}。建议考虑替换为更相关或更具时效性的关键词。")
            
            # 默认建议
            if not recommendations:
                recommendations.append("**持续优化：** 继续保持当前的监测策略，定期评估和调整关键词设置，关注行业发展趋势和新兴话题。")
            
            return '\n\n'.join(recommendations[:4])  # 最多返回4个详细建议
            
        except Exception as e:
            logger.error(f"Comprehensive recommendations generation failed: {e}")
            return "正在生成个性化建议，请稍后查看详细内容。"

    def _extract_detailed_findings(self, research_result: Dict[str, Any], trend_result: Dict[str, Any]) -> List[str]:
        """提取详细的关键发现"""
        try:
            findings = []
            
            # 从研究结果中提取详细发现
            report = research_result.get("report", "")
            if report:
                # 寻找包含关键信息的完整段落或句群
                paragraphs = [p.strip() for p in report.split('\n\n') if p.strip()]
                if not paragraphs:
                    # 如果没有段落分割，尝试按句号分割
                    sentences = [s.strip() for s in report.split("。") if s.strip()]
                    paragraphs = []
                    temp_paragraph = []
                    for sentence in sentences:
                        temp_paragraph.append(sentence)
                        if len("。".join(temp_paragraph)) > 150:  # 组合成段落
                            paragraphs.append("。".join(temp_paragraph) + "。")
                            temp_paragraph = []
                    if temp_paragraph:  # 添加剩余内容
                        paragraphs.append("。".join(temp_paragraph) + "。")
                
                # 筛选重要的发现
                important_keywords = ["突破", "创新", "发展", "增长", "下降", "变化", "趋势", "影响", "重要", "关键", "显著", "主要", "新兴", "提升", "改善", "挑战"]
                
                for paragraph in paragraphs[:15]:  # 检查前15个段落
                    if 30 <= len(paragraph) <= 200:  # 长度适中
                        keyword_count = sum(1 for keyword in important_keywords if keyword in paragraph)
                        if keyword_count >= 1:  # 包含关键词
                            findings.append(f"**研究发现：** {paragraph}")
                        if len(findings) >= 3:  # 限制研究发现数量
                            break
            
            # 从趋势分析中提取详细信息
            trend_score = trend_result.get("trend_score", 5.0)
            activity_level = trend_result.get("activity_level", 5.0)
            
            # 添加趋势发现
            if trend_score > 7.5:
                findings.append(f"**趋势发现：** 该话题呈现强劲上升趋势（评分: {trend_score:.1f}/10），表明正在获得越来越多的关注和讨论，可能正处于重要的发展节点。")
            elif trend_score < 3.5:
                findings.append(f"**趋势发现：** 该话题出现下降趋势（评分: {trend_score:.1f}/10），关注度和讨论热度有所减少，可能需要重新评估其发展前景或寻找新的关注角度。")
            
            # 添加新内容发现
            new_topics = trend_result.get("new_topics", [])
            emerging_keywords = trend_result.get("emerging_keywords", [])
            
            if new_topics or emerging_keywords:
                new_content = []
                if new_topics:
                    new_content.append(f"新话题: {', '.join(new_topics[:3])}")
                if emerging_keywords:
                    new_content.append(f"新关键词: {', '.join(emerging_keywords[:3])}")
                
                findings.append(f"**新兴内容发现：** {'; '.join(new_content)}。这些新出现的内容可能代表了该领域的最新发展方向和创新点，值得深入关注和分析。")
            
            # 添加异常发现
            if trend_result.get("anomaly_detected"):
                anomaly_desc = trend_result.get("anomaly_description", "检测到异常变化模式")
                findings.append(f"**异常现象发现：** {anomaly_desc}。这种异常变化可能意味着重要的转折点或突发事件，建议进行深入分析以了解其影响和意义。")
            
            # 添加情感趋势发现
            sentiment_changes = trend_result.get("sentiment_changes", {})
            significant_sentiment_changes = []
            for sentiment_type, data in sentiment_changes.items():
                if isinstance(data, dict) and abs(data.get("change", 0.0)) > 0.15:
                    direction = "上升" if data.get("change", 0) > 0 else "下降"
                    change_percent = abs(data.get("change", 0.0)) * 100
                    significant_sentiment_changes.append(f"{sentiment_type}情感{direction}{change_percent:.1f}%")
            
            if significant_sentiment_changes:
                findings.append(f"**情感趋势发现：** {', '.join(significant_sentiment_changes)}。这些情感变化反映了公众对该话题态度的转变，可能影响其未来发展轨迹。")
            
            return findings[:4]  # 最多返回4个详细发现
            
        except Exception as e:
            logger.error(f"Detailed findings extraction failed: {e}")
            return ["正在深入分析最新数据和发展趋势，详细发现即将生成。"]
    
    def _identify_detailed_changes(self, trend_result: Dict[str, Any]) -> List[str]:
        """识别详细的关键变化"""
        try:
            changes = []
            
            # 详细的情感变化分析
            sentiment_changes = trend_result.get("sentiment_changes", {})
            significant_sentiment_changes = []
            for sentiment_type, data in sentiment_changes.items():
                if isinstance(data, dict):
                    change = data.get("change", 0.0)
                    current = data.get("current", 0.0)
                    historical_avg = data.get("historical_avg", 0.0)
                    trend = data.get("trend", "stable")
                    
                    if abs(change) > 0.1:  # 显著变化阈值
                        direction = "上升" if change > 0 else "下降"
                        change_desc = f"{sentiment_type}情感{direction}{abs(change):.1%}"
                        
                        # 添加更详细的分析
                        if sentiment_type == "positive" and change > 0:
                            analysis = f"正面情绪显著上升（从{historical_avg:.1%}提升至{current:.1%}），表明公众对该话题的态度趋向积极，可能反映了好消息或积极发展。"
                        elif sentiment_type == "negative" and change > 0:
                            analysis = f"负面情绪有所增加（从{historical_avg:.1%}上升至{current:.1%}），需要关注可能存在的问题或争议，建议深入了解负面情绪的来源。"
                        elif sentiment_type == "positive" and change < 0:
                            analysis = f"正面情绪出现下滑（从{historical_avg:.1%}降至{current:.1%}），可能表明热度减退或出现了一些不利因素。"
                        elif sentiment_type == "negative" and change < 0:
                            analysis = f"负面情绪有所缓解（从{historical_avg:.1%}降至{current:.1%}），表明争议或问题得到一定程度的解决或关注度下降。"
                        else:
                            analysis = f"{sentiment_type}情绪发生了{abs(change):.1%}的变化，从{historical_avg:.1%}变化至{current:.1%}。"
                        
                        changes.append(f"**情感变化：** {analysis}")
            
            # 详细的话题演变分析  
            topic_evolution = trend_result.get("topic_evolution", {})
            new_topics = topic_evolution.get("new_topics", [])
            disappeared_topics = topic_evolution.get("disappeared_topics", [])
            persistent_topics = topic_evolution.get("persistent_topics", [])
            evolution_rate = topic_evolution.get("evolution_rate", 0.0)
            
            if new_topics or disappeared_topics:
                evolution_analysis = []
                if new_topics:
                    evolution_analysis.append(f"新出现{len(new_topics)}个相关话题：{', '.join(new_topics[:3])}")
                if disappeared_topics:
                    evolution_analysis.append(f"有{len(disappeared_topics)}个话题热度消退：{', '.join(disappeared_topics[:2])}")
                
                evolution_desc = f"话题演变率为{evolution_rate:.1%}，"
                if evolution_rate > 0.3:
                    evolution_desc += "表明该领域正经历快速变化，新的发展方向不断涌现。"
                elif evolution_rate > 0.1:
                    evolution_desc += "表明该领域在稳步发展，有新的关注点出现。"
                else:
                    evolution_desc += "表明该领域相对稳定，核心话题保持一致。"
                
                changes.append(f"**话题演变：** {'; '.join(evolution_analysis)}。{evolution_desc}")
            
            # 详细的关键词趋势变化分析
            keyword_trends = trend_result.get("keyword_trends", {})
            if keyword_trends:
                trending_up = [(k, v) for k, v in keyword_trends.items() if v > 7.5]
                trending_down = [(k, v) for k, v in keyword_trends.items() if v < 3.5]
                stable_keywords = [(k, v) for k, v in keyword_trends.items() if 4.0 <= v <= 7.0]
                
                if trending_up or trending_down:
                    trend_analysis = []
                    if trending_up:
                        up_keywords = ', '.join([f"{k}({v:.1f})" for k, v in trending_up[:3]])
                        trend_analysis.append(f"热度上升的关键词：{up_keywords}，这些关键词正获得更多关注")
                    
                    if trending_down:
                        down_keywords = ', '.join([f"{k}({v:.1f})" for k, v in trending_down[:3]])
                        trend_analysis.append(f"热度下降的关键词：{down_keywords}，可能反映了关注点的转移")
                    
                    stability_desc = ""
                    if stable_keywords:
                        stability_desc = f"同时有{len(stable_keywords)}个关键词保持稳定表现。"
                    
                    changes.append(f"**关键词趋势：** {'; '.join(trend_analysis)}。{stability_desc}")
            
            # 详细的活跃度变化分析
            activity_level = trend_result.get("activity_level", 5.0)
            change_magnitude = trend_result.get("change_magnitude", 0.0)
            
            if activity_level > 8.0 or change_magnitude > 6.0:
                if activity_level > 8.0:
                    activity_desc = f"整体活跃度达到高水平（{activity_level:.1f}/10），信息更新频繁，讨论热度很高"
                else:
                    activity_desc = f"虽然活跃度为{activity_level:.1f}/10，但变化幅度较大（{change_magnitude:.1f}/10）"
                
                impact_analysis = "这种高活跃度通常意味着该话题正处于关键发展期，建议密切关注后续动态。"
                changes.append(f"**活跃度变化：** {activity_desc}。{impact_analysis}")
                
            elif activity_level < 3.0:
                activity_desc = f"整体活跃度较低（{activity_level:.1f}/10），相关讨论和信息更新不够频繁"
                suggestion = "建议考虑调整监测关键词或扩大信息源范围，以获取更多相关动态。"
                changes.append(f"**活跃度变化：** {activity_desc}。{suggestion}")
            
            return changes[:3]  # 最多返回3个详细变化分析
            
        except Exception as e:
            logger.error(f"Detailed changes identification failed: {e}")
            return ["正在深入分析变化趋势，详细分析即将完成。"]
    
    def _generate_trend_summary(self, trend_result: Dict[str, Any]) -> str:
        """生成趋势摘要"""
        try:
            trend_score = trend_result.get("trend_score", 5.0)
            activity_level = trend_result.get("activity_level", 5.0)
            change_magnitude = trend_result.get("change_magnitude", 0.0)
            confidence_score = trend_result.get("confidence_score", 0.5)
            
            # 趋势描述
            if trend_score > 7.5:
                trend_desc = "强劲上升趋势"
            elif trend_score > 6.0:
                trend_desc = "温和上升趋势"
            elif trend_score < 3.5:
                trend_desc = "下降趋势"
            elif trend_score < 4.5:
                trend_desc = "温和下降趋势"
            else:
                trend_desc = "稳定趋势"
            
            # 活跃度描述
            if activity_level > 7.0:
                activity_desc = "高度活跃"
            elif activity_level > 5.5:
                activity_desc = "中等活跃"
            else:
                activity_desc = "活跃度一般"
            
            # 变化程度描述
            if change_magnitude > 7.0:
                change_desc = "剧烈变化"
            elif change_magnitude > 4.0:
                change_desc = "明显变化"
            else:
                change_desc = "轻微变化"
            
            # 置信度描述
            if confidence_score > 0.8:
                confidence_desc = "高置信度"
            elif confidence_score > 0.5:
                confidence_desc = "中等置信度"
            else:
                confidence_desc = "低置信度"
            
            summary = f"趋势评估: {trend_desc} | 活跃程度: {activity_desc} | 变化程度: {change_desc} | 数据可靠性: {confidence_desc}"
            
            # 添加评分
            summary += f"\n评分详情: 趋势 {trend_score:.1f}/10, 活跃度 {activity_level:.1f}/10, 变化幅度 {change_magnitude:.1f}/10"
            
            return summary
            
        except Exception as e:
            logger.error(f"Trend summary generation failed: {e}")
            return "趋势分析: 数据分析中，请稍后查看详细结果"
    
    def _determine_priority_level(self, trend_result: Dict[str, Any]) -> str:
        """确定优先级级别"""
        try:
            trend_score = trend_result.get("trend_score", 5.0)
            change_magnitude = trend_result.get("change_magnitude", 0.0)
            anomaly_detected = trend_result.get("anomaly_detected", False)
            
            # 异常检测到，高优先级
            if anomaly_detected:
                return "high"
            
            # 高趋势分数或大变化幅度
            if trend_score > 8.0 or change_magnitude > 7.0:
                return "high"
            
            # 低趋势分数，中优先级
            if trend_score < 3.0:
                return "medium"
            
            # 有一定变化，中优先级
            if change_magnitude > 4.0:
                return "medium"
            
            # 其他情况，低优先级
            return "low"
            
        except Exception as e:
            logger.error(f"Priority level determination failed: {e}")
            return "medium"
    
    def _generate_action_recommendations(self, task, trend_result: Dict[str, Any]) -> List[str]:
        """生成行动建议"""
        try:
            recommendations = []
            
            trend_score = trend_result.get("trend_score", 5.0)
            activity_level = trend_result.get("activity_level", 5.0)
            new_topics = trend_result.get("new_topics", [])
            anomaly_detected = trend_result.get("anomaly_detected", False)
            
            # 基于趋势分数的建议
            if trend_score > 8.0:
                recommendations.append("密切关注当前发展，考虑加大投入或关注力度")
            elif trend_score < 3.0:
                recommendations.append("评估是否需要调整策略或重新定位关注重点")
            
            # 基于活跃度的建议
            if activity_level > 8.0:
                recommendations.append("当前活跃度很高，建议及时跟进最新动态")
            elif activity_level < 3.0:
                recommendations.append("活跃度较低，可能需要寻找新的信息源或调整关键词")
            
            # 基于新话题的建议
            if len(new_topics) > 3:
                recommendations.append(f"出现多个新话题，建议深入研究: {', '.join(new_topics[:2])}")
            
            # 基于异常的建议
            if anomaly_detected:
                recommendations.append("检测到异常变化，建议立即进行深度分析")
            
            # 基于任务配置的建议
            if task.interval_hours > 24:
                recommendations.append("考虑缩短监测间隔以获取更及时的信息")
            
            # 默认建议
            if not recommendations:
                recommendations.append("继续定期监测，关注趋势变化")
            
            return recommendations[:3]  # 最多返回3个建议
            
        except Exception as e:
            logger.error(f"Action recommendations generation failed: {e}")
            return ["继续监测话题发展趋势"]
    
    def _suggest_next_focus_areas(self, trend_result: Dict[str, Any]) -> List[str]:
        """推荐下一步关注领域"""
        try:
            focus_areas = []
            
            # 基于新话题
            new_topics = trend_result.get("new_topics", [])
            if new_topics:
                focus_areas.extend(new_topics[:2])
            
            # 基于新兴关键词
            emerging_keywords = trend_result.get("emerging_keywords", [])
            if emerging_keywords:
                focus_areas.extend(emerging_keywords[:2])
            
            # 基于趋势上升的关键词
            keyword_trends = trend_result.get("keyword_trends", {})
            trending_keywords = [k for k, v in keyword_trends.items() if v > 7.5]
            if trending_keywords:
                focus_areas.extend(trending_keywords[:2])
            
            # 去重并限制数量
            unique_focus_areas = list(dict.fromkeys(focus_areas))  # 保持顺序的去重
            
            return unique_focus_areas[:4]  # 最多返回4个关注领域
            
        except Exception as e:
            logger.error(f"Next focus areas suggestion failed: {e}")
            return ["相关技术发展", "市场动态变化"]
    
    def _create_fallback_summary(self, research_result: Dict[str, Any], task) -> Dict[str, Any]:
        """创建后备摘要（出错时）"""
        report = research_result.get("report", "")
        
        # 简单提取前几句作为摘要
        sentences = report.split("。")[:3]
        simple_summary = "。".join(sentences) + "。" if sentences else f"关于 {task.topic} 的研究分析已完成。"
        
        return {
            "summary": simple_summary,
            "key_findings": ["正在深入分析最新数据，详细发现即将生成"],
            "key_changes": ["正在监测和分析关键变化趋势"]
        }
