"""
话题趋势分析器 - 分析话题发展趋势和变化
Topic Trend Analyzer - Analyzes topic development trends and changes
"""
import re
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import Counter
import asyncio

from .prompts import ScheduledResearchPrompts

logger = logging.getLogger(__name__)


class TopicTrendAnalyzer:
    """
    话题趋势分析器
    Analyzes trends in research topics and content
    """
    
    def __init__(self):
        """初始化趋势分析器"""
        self.sentiment_keywords = {
            "positive": ["增长", "上升", "改善", "突破", "成功", "创新", "发展", "进步", "优化", "提升"],
            "negative": ["下降", "减少", "衰退", "问题", "挑战", "困难", "风险", "危机", "失败", "下滑"],
            "neutral": ["保持", "稳定", "持续", "维持", "不变", "平稳", "类似", "相同", "常规", "普通"]
        }
    
    async def analyze_trends(self, task, current_result: Dict[str, Any], historical_data: List[Dict]) -> Dict[str, Any]:
        """
        分析趋势变化
        
        Args:
            task: 任务对象
            current_result: 当前研究结果
            historical_data: 历史数据列表
            
        Returns:
            Dict包含趋势分析结果
        """
        try:
            logger.info(f"Analyzing trends for topic: {task.topic}")
            
            # 提取当前结果的关键信息
            current_data = self._extract_analysis_data(current_result)
            
            # 如果没有历史数据，返回基础分析
            if not historical_data:
                return self._create_baseline_analysis(current_data, task)
            
            # 进行趋势对比分析
            trend_analysis = {
                "trend_score": 0.0,
                "activity_level": 0.0,
                "change_magnitude": 0.0,
                "confidence_score": 0.0,
                "keyword_trends": {},
                "sentiment_changes": {},
                "topic_evolution": {},
                "new_topics": [],
                "emerging_keywords": [],
                "comparison_data": {},
                "anomaly_detected": False,
                "anomaly_description": ""
            }
            
            # 分析关键词趋势
            trend_analysis["keyword_trends"] = self._analyze_keyword_trends(
                current_data, historical_data, task.keywords
            )
            
            # 分析情感变化
            trend_analysis["sentiment_changes"] = self._analyze_sentiment_trends(
                current_data, historical_data
            )
            
            # 分析话题演变
            trend_analysis["topic_evolution"] = self._analyze_topic_evolution(
                current_data, historical_data
            )
            
            # 检测新话题和关键词
            new_content = self._detect_new_content(current_data, historical_data)
            trend_analysis["new_topics"] = new_content["topics"]
            trend_analysis["emerging_keywords"] = new_content["keywords"]
            
            # 计算综合趋势分数
            trend_analysis["trend_score"] = self._calculate_trend_score(trend_analysis)
            
            # 计算活跃度和变化幅度
            trend_analysis["activity_level"] = self._calculate_activity_level(current_data, historical_data)
            trend_analysis["change_magnitude"] = self._calculate_change_magnitude(trend_analysis)
            
            # 计算置信度
            trend_analysis["confidence_score"] = self._calculate_confidence_score(
                len(historical_data), current_data
            )
            
            # 异常检测
            anomaly_result = self._detect_anomalies(trend_analysis, historical_data)
            trend_analysis["anomaly_detected"] = anomaly_result["detected"]
            trend_analysis["anomaly_description"] = anomaly_result["description"]
            
            # 生成对比数据
            trend_analysis["comparison_data"] = self._generate_comparison_data(
                current_data, historical_data
            )
            
            logger.info(f"Trend analysis completed: score={trend_analysis['trend_score']:.2f}")
            
            return trend_analysis
            
        except Exception as e:
            logger.error(f"Trend analysis failed: {e}")
            return self._create_fallback_analysis(current_result, task)
    
    def _extract_analysis_data(self, research_result: Dict[str, Any]) -> Dict[str, Any]:
        """从研究结果中提取分析数据"""
        try:
            report = research_result.get("report", "")
            
            # 提取关键词
            keywords = self._extract_keywords(report)
            
            # 分析情感倾向
            sentiment = self._analyze_sentiment(report)
            
            # 提取主要话题
            topics = self._extract_topics(report)
            
            # 统计信息
            stats = {
                "word_count": len(report.split()),
                "sources_count": research_result.get("sources_count", 0),
                "report_length": len(report)
            }
            
            return {
                "keywords": keywords,
                "sentiment": sentiment,
                "topics": topics,
                "stats": stats,
                "content": report
            }
            
        except Exception as e:
            logger.error(f"Failed to extract analysis data: {e}")
            return {
                "keywords": [],
                "sentiment": {"positive": 0.3, "negative": 0.2, "neutral": 0.5},
                "topics": [],
                "stats": {"word_count": 0, "sources_count": 0, "report_length": 0},
                "content": ""
            }
    
    def _extract_keywords(self, text: str, top_k: int = 20) -> List[str]:
        """提取关键词"""
        try:
            # 简单的关键词提取（基于词频）
            # 移除标点符号和停用词
            import jieba
            
            words = jieba.lcut(text)
            
            # 停用词列表（简化版）
            stop_words = {"的", "是", "在", "了", "和", "有", "与", "等", "及", "或", "但", "而", "也", "将", "可", "能", "更", "这", "那", "一个", "一些", "如果", "因为", "所以", "然后", "但是", "然而", "此外", "另外", "首先", "其次", "最后", "总之", "总的来说"}
            
            # 过滤词长和停用词
            filtered_words = [
                word for word in words 
                if len(word) >= 2 and word not in stop_words and word.strip()
            ]
            
            # 统计词频
            word_freq = Counter(filtered_words)
            
            # 返回前top_k个关键词
            return [word for word, freq in word_freq.most_common(top_k)]
            
        except Exception as e:
            logger.error(f"Keyword extraction failed: {e}")
            # 如果jieba不可用，使用简单的方法
            words = text.split()
            return list(set(words))[:20]
    
    def _analyze_sentiment(self, text: str) -> Dict[str, float]:
        """分析情感倾向"""
        try:
            total_score = {"positive": 0, "negative": 0, "neutral": 0}
            
            # 统计情感关键词
            for sentiment_type, keywords in self.sentiment_keywords.items():
                for keyword in keywords:
                    count = text.count(keyword)
                    total_score[sentiment_type] += count
            
            # 计算总数
            total = sum(total_score.values())
            
            if total == 0:
                return {"positive": 0.3, "negative": 0.2, "neutral": 0.5}
            
            # 归一化
            return {
                sentiment: score / total 
                for sentiment, score in total_score.items()
            }
            
        except Exception as e:
            logger.error(f"Sentiment analysis failed: {e}")
            return {"positive": 0.3, "negative": 0.2, "neutral": 0.5}
    
    def _extract_topics(self, text: str, max_topics: int = 10) -> List[str]:
        """提取主要话题"""
        try:
            # 简单的话题提取：寻找名词短语
            sentences = re.split(r'[。！？\n]', text)
            
            topics = []
            for sentence in sentences[:50]:  # 限制处理的句子数量
                # 寻找可能的话题短语（长度2-6个字符的中文词汇）
                topic_matches = re.findall(r'[\u4e00-\u9fff]{2,6}', sentence)
                topics.extend(topic_matches)
            
            # 去重并返回
            unique_topics = list(set(topics))
            return unique_topics[:max_topics]
            
        except Exception as e:
            logger.error(f"Topic extraction failed: {e}")
            return []
    
    def _analyze_keyword_trends(self, current_data: Dict, historical_data: List[Dict], task_keywords: List[str]) -> Dict[str, float]:
        """分析关键词趋势"""
        try:
            keyword_trends = {}
            current_keywords = set(current_data.get("keywords", []))
            
            # 分析任务关键词的趋势
            for keyword in task_keywords:
                trend_score = self._calculate_keyword_trend(keyword, current_data, historical_data)
                keyword_trends[keyword] = trend_score
            
            # 分析当前发现的新关键词
            for keyword in list(current_keywords)[:10]:  # 限制数量
                if keyword not in task_keywords:
                    trend_score = self._calculate_keyword_trend(keyword, current_data, historical_data)
                    keyword_trends[keyword] = trend_score
            
            return keyword_trends
            
        except Exception as e:
            logger.error(f"Keyword trend analysis failed: {e}")
            return {}
    
    def _calculate_keyword_trend(self, keyword: str, current_data: Dict, historical_data: List[Dict]) -> float:
        """计算单个关键词的趋势分数"""
        try:
            current_content = current_data.get("content", "")
            current_count = current_content.count(keyword)
            
            # 计算历史平均出现次数
            historical_counts = []
            for hist_data in historical_data:
                if "content" in hist_data:
                    count = hist_data["content"].count(keyword)
                    historical_counts.append(count)
            
            if not historical_counts:
                return 5.0  # 默认中等分数
            
            avg_historical = sum(historical_counts) / len(historical_counts)
            
            if avg_historical == 0:
                return 8.0 if current_count > 0 else 5.0
            
            # 计算增长率
            growth_rate = (current_count - avg_historical) / avg_historical
            
            # 转换为1-10分数
            if growth_rate > 0.5:
                return min(10.0, 8.0 + growth_rate * 2)
            elif growth_rate < -0.5:
                return max(1.0, 3.0 + growth_rate * 2)
            else:
                return 5.0 + growth_rate * 2
                
        except Exception as e:
            logger.error(f"Keyword trend calculation failed: {e}")
            return 5.0
    
    def _analyze_sentiment_trends(self, current_data: Dict, historical_data: List[Dict]) -> Dict[str, Any]:
        """分析情感趋势变化"""
        try:
            current_sentiment = current_data.get("sentiment", {})
            
            # 计算历史情感平均值
            historical_sentiments = {"positive": [], "negative": [], "neutral": []}
            
            for hist_data in historical_data:
                if "sentiment" in hist_data:
                    hist_sentiment = hist_data["sentiment"]
                    for key in historical_sentiments:
                        if key in hist_sentiment:
                            historical_sentiments[key].append(hist_sentiment[key])
            
            # 计算变化
            sentiment_changes = {}
            for sentiment_type in ["positive", "negative", "neutral"]:
                current_val = current_sentiment.get(sentiment_type, 0.0)
                
                if historical_sentiments[sentiment_type]:
                    avg_historical = sum(historical_sentiments[sentiment_type]) / len(historical_sentiments[sentiment_type])
                    change = current_val - avg_historical
                    sentiment_changes[sentiment_type] = {
                        "current": current_val,
                        "historical_avg": avg_historical,
                        "change": change,
                        "trend": "up" if change > 0.05 else "down" if change < -0.05 else "stable"
                    }
                else:
                    sentiment_changes[sentiment_type] = {
                        "current": current_val,
                        "historical_avg": 0.0,
                        "change": 0.0,
                        "trend": "stable"
                    }
            
            return sentiment_changes
            
        except Exception as e:
            logger.error(f"Sentiment trend analysis failed: {e}")
            return {}
    
    def _analyze_topic_evolution(self, current_data: Dict, historical_data: List[Dict]) -> Dict[str, Any]:
        """分析话题演变"""
        try:
            current_topics = set(current_data.get("topics", []))
            
            # 收集历史话题
            all_historical_topics = set()
            for hist_data in historical_data:
                historical_topics = hist_data.get("topics", [])
                all_historical_topics.update(historical_topics)
            
            # 分析话题变化
            new_topics = current_topics - all_historical_topics
            disappeared_topics = all_historical_topics - current_topics
            persistent_topics = current_topics & all_historical_topics
            
            return {
                "new_topics": list(new_topics),
                "disappeared_topics": list(disappeared_topics),
                "persistent_topics": list(persistent_topics),
                "evolution_rate": len(new_topics) / max(len(current_topics), 1)
            }
            
        except Exception as e:
            logger.error(f"Topic evolution analysis failed: {e}")
            return {"new_topics": [], "disappeared_topics": [], "persistent_topics": [], "evolution_rate": 0.0}
    
    def _detect_new_content(self, current_data: Dict, historical_data: List[Dict]) -> Dict[str, List[str]]:
        """检测新内容（话题和关键词）"""
        try:
            current_keywords = set(current_data.get("keywords", []))
            current_topics = set(current_data.get("topics", []))
            
            # 收集历史内容
            historical_keywords = set()
            historical_topics = set()
            
            for hist_data in historical_data:
                historical_keywords.update(hist_data.get("keywords", []))
                historical_topics.update(hist_data.get("topics", []))
            
            # 识别新内容
            new_keywords = list(current_keywords - historical_keywords)
            new_topics = list(current_topics - historical_topics)
            
            return {
                "keywords": new_keywords[:10],  # 限制数量
                "topics": new_topics[:10]
            }
            
        except Exception as e:
            logger.error(f"New content detection failed: {e}")
            return {"keywords": [], "topics": []}
    
    def _calculate_trend_score(self, trend_analysis: Dict) -> float:
        """计算综合趋势分数（1-10分）"""
        try:
            scores = []
            
            # 关键词趋势分数
            keyword_trends = trend_analysis.get("keyword_trends", {})
            if keyword_trends:
                avg_keyword_score = sum(keyword_trends.values()) / len(keyword_trends)
                scores.append(avg_keyword_score)
            
            # 新内容分数
            new_topics_count = len(trend_analysis.get("new_topics", []))
            new_keywords_count = len(trend_analysis.get("emerging_keywords", []))
            new_content_score = min(10.0, 5.0 + (new_topics_count + new_keywords_count) * 0.5)
            scores.append(new_content_score)
            
            # 话题演变分数
            topic_evolution = trend_analysis.get("topic_evolution", {})
            evolution_rate = topic_evolution.get("evolution_rate", 0.0)
            evolution_score = min(10.0, 5.0 + evolution_rate * 10)
            scores.append(evolution_score)
            
            # 计算加权平均
            if scores:
                return sum(scores) / len(scores)
            else:
                return 5.0
                
        except Exception as e:
            logger.error(f"Trend score calculation failed: {e}")
            return 5.0
    
    def _calculate_activity_level(self, current_data: Dict, historical_data: List[Dict]) -> float:
        """计算活跃度分数"""
        try:
            current_stats = current_data.get("stats", {})
            current_word_count = current_stats.get("word_count", 0)
            current_sources = current_stats.get("sources_count", 0)
            
            if not historical_data:
                return 5.0
            
            # 计算历史平均
            historical_words = []
            historical_sources = []
            
            for hist_data in historical_data:
                stats = hist_data.get("stats", {})
                historical_words.append(stats.get("word_count", 0))
                historical_sources.append(stats.get("sources_count", 0))
            
            avg_words = sum(historical_words) / len(historical_words) if historical_words else 1
            avg_sources = sum(historical_sources) / len(historical_sources) if historical_sources else 1
            
            # 计算活跃度
            word_ratio = current_word_count / max(avg_words, 1)
            source_ratio = current_sources / max(avg_sources, 1)
            
            activity_score = (word_ratio + source_ratio) / 2 * 5
            return min(10.0, max(1.0, activity_score))
            
        except Exception as e:
            logger.error(f"Activity level calculation failed: {e}")
            return 5.0
    
    def _calculate_change_magnitude(self, trend_analysis: Dict) -> float:
        """计算变化幅度"""
        try:
            changes = []
            
            # 基于新内容数量
            new_topics = len(trend_analysis.get("new_topics", []))
            new_keywords = len(trend_analysis.get("emerging_keywords", []))
            content_change = (new_topics + new_keywords) / 10.0  # 归一化
            changes.append(content_change)
            
            # 基于情感变化
            sentiment_changes = trend_analysis.get("sentiment_changes", {})
            sentiment_change = 0.0
            for sentiment_data in sentiment_changes.values():
                if isinstance(sentiment_data, dict):
                    change = abs(sentiment_data.get("change", 0.0))
                    sentiment_change += change
            changes.append(sentiment_change * 10)  # 放大
            
            # 基于话题演变率
            topic_evolution = trend_analysis.get("topic_evolution", {})
            evolution_rate = topic_evolution.get("evolution_rate", 0.0)
            changes.append(evolution_rate * 10)
            
            avg_change = sum(changes) / len(changes) if changes else 0.0
            return min(10.0, max(0.0, avg_change))
            
        except Exception as e:
            logger.error(f"Change magnitude calculation failed: {e}")
            return 5.0
    
    def _calculate_confidence_score(self, history_count: int, current_data: Dict) -> float:
        """计算置信度分数"""
        try:
            # 基于历史数据量
            history_score = min(1.0, history_count / 10.0)
            
            # 基于当前数据质量
            stats = current_data.get("stats", {})
            word_count = stats.get("word_count", 0)
            sources_count = stats.get("sources_count", 0)
            
            data_quality = min(1.0, (word_count / 1000.0 + sources_count / 10.0) / 2)
            
            # 综合置信度
            confidence = (history_score * 0.6 + data_quality * 0.4)
            return confidence
            
        except Exception as e:
            logger.error(f"Confidence score calculation failed: {e}")
            return 0.5
    
    def _detect_anomalies(self, trend_analysis: Dict, historical_data: List[Dict]) -> Dict[str, Any]:
        """检测异常"""
        try:
            anomalies = []
            
            # 检查趋势分数异常
            trend_score = trend_analysis.get("trend_score", 5.0)
            if trend_score > 8.5:
                anomalies.append("检测到异常高的趋势活跃度")
            elif trend_score < 2.0:
                anomalies.append("检测到异常低的趋势活跃度")
            
            # 检查新内容异常
            new_topics_count = len(trend_analysis.get("new_topics", []))
            if new_topics_count > 5:
                anomalies.append(f"发现异常多的新话题 ({new_topics_count}个)")
            
            # 检查情感变化异常
            sentiment_changes = trend_analysis.get("sentiment_changes", {})
            for sentiment_type, data in sentiment_changes.items():
                if isinstance(data, dict) and abs(data.get("change", 0.0)) > 0.3:
                    anomalies.append(f"检测到{sentiment_type}情感的大幅变化")
            
            return {
                "detected": len(anomalies) > 0,
                "description": "; ".join(anomalies) if anomalies else ""
            }
            
        except Exception as e:
            logger.error(f"Anomaly detection failed: {e}")
            return {"detected": False, "description": ""}
    
    def _generate_comparison_data(self, current_data: Dict, historical_data: List[Dict]) -> Dict[str, Any]:
        """生成对比数据"""
        try:
            if not historical_data:
                return {}
            
            # 最近一次的对比
            latest_data = historical_data[0] if historical_data else {}
            
            comparison = {
                "vs_latest": {},
                "vs_average": {},
                "trend_direction": {}
            }
            
            # 与最新记录对比
            current_stats = current_data.get("stats", {})
            latest_stats = latest_data.get("stats", {})
            
            comparison["vs_latest"] = {
                "word_count_change": current_stats.get("word_count", 0) - latest_stats.get("word_count", 0),
                "sources_count_change": current_stats.get("sources_count", 0) - latest_stats.get("sources_count", 0)
            }
            
            # 与平均值对比
            avg_stats = self._calculate_average_stats(historical_data)
            comparison["vs_average"] = {
                "word_count_vs_avg": current_stats.get("word_count", 0) - avg_stats.get("word_count", 0),
                "sources_count_vs_avg": current_stats.get("sources_count", 0) - avg_stats.get("sources_count", 0)
            }
            
            return comparison
            
        except Exception as e:
            logger.error(f"Comparison data generation failed: {e}")
            return {}
    
    def _calculate_average_stats(self, historical_data: List[Dict]) -> Dict[str, float]:
        """计算历史数据的平均统计"""
        try:
            total_stats = {"word_count": 0, "sources_count": 0, "report_length": 0}
            count = len(historical_data)
            
            for data in historical_data:
                stats = data.get("stats", {})
                for key in total_stats:
                    total_stats[key] += stats.get(key, 0)
            
            return {key: value / count for key, value in total_stats.items()} if count > 0 else total_stats
            
        except Exception as e:
            logger.error(f"Average stats calculation failed: {e}")
            return {"word_count": 0, "sources_count": 0, "report_length": 0}
    
    def _create_baseline_analysis(self, current_data: Dict, task) -> Dict[str, Any]:
        """创建基线分析（没有历史数据时）"""
        return {
            "trend_score": 5.0,
            "activity_level": 5.0,
            "change_magnitude": 5.0,
            "confidence_score": 0.3,  # 低置信度，因为没有历史数据
            "keyword_trends": {keyword: 5.0 for keyword in task.keywords},
            "sentiment_changes": current_data.get("sentiment", {}),
            "topic_evolution": {"new_topics": current_data.get("topics", []), "disappeared_topics": [], "persistent_topics": [], "evolution_rate": 1.0},
            "new_topics": current_data.get("topics", [])[:5],
            "emerging_keywords": current_data.get("keywords", [])[:10],
            "comparison_data": {},
            "anomaly_detected": False,
            "anomaly_description": "首次分析，无历史数据对比"
        }
    
    def _create_fallback_analysis(self, research_result: Dict, task) -> Dict[str, Any]:
        """创建后备分析（出错时）"""
        return {
            "trend_score": 5.0,
            "activity_level": 5.0,
            "change_magnitude": 0.0,
            "confidence_score": 0.1,
            "keyword_trends": {keyword: 5.0 for keyword in task.keywords},
            "sentiment_changes": {"positive": 0.3, "negative": 0.2, "neutral": 0.5},
            "topic_evolution": {"new_topics": [], "disappeared_topics": [], "persistent_topics": [], "evolution_rate": 0.0},
            "new_topics": [],
            "emerging_keywords": [],
            "comparison_data": {},
            "anomaly_detected": False,
            "anomaly_description": "分析过程中出现错误，使用默认值"
        }
