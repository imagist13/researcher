"""
研究任务执行器 - 执行具体的研究任务
Research Task Executor - Executes specific research tasks
"""
import asyncio
import logging
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

from gpt_researcher.agent import GPTResearcher
from gpt_researcher.utils.enum import ReportType, ReportSource, Tone

from ..database import ResearchHistoryDAO, TrendDataDAO, TaskExecutionLogDAO
from ..server.content_safety import ContentSafetyChecker
from .trend_analyzer import TopicTrendAnalyzer
from .summary_generator import DynamicSummaryGenerator
from .config import ScheduledResearchConfig, ScheduledResearchPrompts

logger = logging.getLogger(__name__)


class ResearchTaskExecutor:
    """
    研究任务执行器
    Executes research tasks and manages the research workflow
    """
    
    def __init__(self, websocket_manager=None):
        """
        初始化任务执行器
        
        Args:
            websocket_manager: WebSocket管理器，用于实时推送进度
        """
        self.websocket_manager = websocket_manager
        self.trend_analyzer = TopicTrendAnalyzer()
        self.summary_generator = DynamicSummaryGenerator()
    
    async def execute_task(self, task, execution_log_id: Optional[str] = None) -> Dict[str, Any]:
        """
        执行研究任务
        
        Args:
            task: ScheduledTask对象
            execution_log_id: 执行日志ID
            
        Returns:
            Dict包含执行结果
        """
        start_time = time.time()
        result = {
            "success": False,
            "task_id": task.id,
            "execution_time": 0.0,
            "summary": "",
            "key_changes": [],
            "trend_score": 0.0,
            "sources_count": 0,
            "log_messages": []
        }
        
        try:
            logger.info(f"Starting research task execution: {task.topic}")
            
            # 更新执行日志
            await self._update_execution_log(execution_log_id, {
                "execution_step": "research_phase",
                "progress_percentage": 10.0,
                "log_messages": [{"timestamp": datetime.now().isoformat(), "message": "Starting research phase"}]
            })
            
            # 第一阶段：执行研究
            research_result = await self._conduct_research(task)
            if not research_result["success"]:
                result["error"] = research_result.get("error", "Research failed")
                return result
            
            # 更新执行日志
            await self._update_execution_log(execution_log_id, {
                "execution_step": "analysis_phase",
                "progress_percentage": 60.0,
                "log_messages": [{"timestamp": datetime.now().isoformat(), "message": "Research completed, starting analysis"}]
            })
            
            # 第二阶段：趋势分析
            trend_result = await self._analyze_trends(task, research_result)
            
            # 更新执行日志
            await self._update_execution_log(execution_log_id, {
                "execution_step": "summary_phase", 
                "progress_percentage": 80.0,
                "log_messages": [{"timestamp": datetime.now().isoformat(), "message": "Trend analysis completed, generating summary"}]
            })
            
            # 第三阶段：生成摘要
            summary_result = await self._generate_summary(task, research_result, trend_result)
            
            # 第四阶段：保存结果
            await self._save_results(task, research_result, trend_result, summary_result)
            
            # 更新执行日志
            await self._update_execution_log(execution_log_id, {
                "execution_step": "completed",
                "progress_percentage": 100.0,
                "log_messages": [{"timestamp": datetime.now().isoformat(), "message": "Task execution completed successfully"}]
            })
            
            # 组装最终结果
            result.update({
                "success": True,
                "execution_time": time.time() - start_time,
                "summary": summary_result.get("summary", ""),
                "key_changes": summary_result.get("key_changes", []),
                "trend_score": trend_result.get("trend_score", 0.0),
                "sources_count": research_result.get("sources_count", 0),
                "raw_result": research_result.get("report", ""),
                "trend_data": trend_result,
                "log_messages": result["log_messages"]
            })
            
            logger.info(f"Task execution completed successfully: {task.topic}")
            
            # 通过WebSocket广播研究结果
            if self.websocket_manager:
                await self._broadcast_result(task, result)
            
        except Exception as e:
            logger.error(f"Task execution failed: {e}")
            result["error"] = str(e)
            result["execution_time"] = time.time() - start_time
            
            # 更新执行日志
            await self._update_execution_log(execution_log_id, {
                "execution_step": "failed",
                "progress_percentage": 0.0,
                "log_messages": [{"timestamp": datetime.now().isoformat(), "message": f"Task execution failed: {str(e)}"}]
            })
        
        return result
    
    async def _conduct_research(self, task) -> Dict[str, Any]:
        """执行GPT研究 - 优化版本"""
        try:
            logger.info(f"Conducting research for topic: {task.topic}")
            
            # 构建查询字符串
            query = self._build_research_query(task)
            
            # 优化的研究参数配置
            researcher_config = {
                "query": query,
                "report_type": self._get_report_type(task.report_type),
                "report_source": self._get_report_source(task.report_source),
                "tone": self._get_tone(task.tone),
                "max_subtopics": min(task.max_sources or 3, 5),  # 限制子主题数量提升速度
                "verbose": False,  # 关闭详细日志提升性能
                "headers": {"User-Agent": "GPT-Researcher-Scheduled/1.0"}
            }
            
            # 如果指定了查询域名
            if task.query_domains:
                researcher_config["query_domains"] = task.query_domains[:5]  # 限制域名数量
            
            # 创建自定义配置来优化性能
            custom_config = self._create_optimized_config(task)
            researcher_config["config_path"] = None  # 使用默认配置但会被下面的设置覆盖
            
            # 创建研究器实例
            researcher = GPTResearcher(**researcher_config)
            
            # 应用性能优化配置
            self._apply_performance_optimizations(researcher, custom_config)
            
            # 执行研究 - 使用超时控制
            start_time = time.time()
            try:
                # 设置研究超时（根据分析深度调整）
                timeout = self._get_research_timeout(task.analysis_depth)
                
                research_data = await asyncio.wait_for(
                    researcher.conduct_research(), 
                    timeout=timeout
                )
                report = await asyncio.wait_for(
                    researcher.write_report(), 
                    timeout=60  # 报告生成最多1分钟
                )
                
            except asyncio.TimeoutError:
                logger.warning(f"Research timeout for task {task.id}, using partial results")
                # 尝试获取部分结果
                report = await researcher.write_report() if hasattr(researcher, 'context') else "研究超时，无法生成完整报告"
                research_data = getattr(researcher, 'context', [])
            
            # 提取研究结果信息
            sources_count = len(getattr(researcher, 'visited_urls', set()))
            research_sources = getattr(researcher, 'research_sources', [])
            
            # 提取更详细的研究信息
            research_costs = getattr(researcher, 'research_costs', 0.0)
            execution_time = time.time() - start_time
            
            return {
                "success": True,
                "report": report,
                "research_data": research_data,
                "research_sources": research_sources,
                "sources_count": sources_count,
                "query_used": query,
                "execution_time": execution_time,
                "research_costs": research_costs,
                "researcher_instance": researcher  # 保留实例以便后续分析
            }
            
        except Exception as e:
            logger.error(f"Research failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _get_report_type(self, report_type_str: str) -> str:
        """获取报告类型"""
        type_mapping = {
            "research_report": ReportType.ResearchReport.value,
            "detailed_report": ReportType.DetailedReport.value,
            "multi_agents": "multi_agents",
            "deep": ReportType.DetailedReport.value
        }
        return type_mapping.get(report_type_str, ReportType.ResearchReport.value)
    
    def _get_report_source(self, source_str: str) -> str:
        """获取报告来源"""
        source_mapping = {
            "web": ReportSource.Web.value,
            "local": ReportSource.Local.value,
            "hybrid": ReportSource.Hybrid.value
        }
        return source_mapping.get(source_str, ReportSource.Web.value)
    
    def _get_tone(self, tone_str: str) -> Tone:
        """获取语调"""
        tone_mapping = {
            "objective": Tone.Objective,
            "formal": Tone.Formal,
            "analytical": Tone.Analytical,
            "persuasive": Tone.Persuasive,
            "informative": Tone.Informative,
            "explanatory": Tone.Explanatory,
            "descriptive": Tone.Descriptive,
            "critical": Tone.Critical,
            "comparative": Tone.Comparative,
            "speculative": Tone.Speculative,
            "reflective": Tone.Reflective,
            "narrative": Tone.Narrative,
            "humorous": Tone.Humorous,
            "optimistic": Tone.Optimistic,
            "pessimistic": Tone.Pessimistic,
            "simple": Tone.Simple,
            "casual": Tone.Casual
        }
        return tone_mapping.get(tone_str, Tone.Objective)
    
    def _get_research_timeout(self, analysis_depth: str) -> int:
        """根据分析深度获取研究超时时间"""
        timeout_mapping = {
            "basic": 120,      # 2分钟
            "detailed": 300,   # 5分钟
            "deep": 600        # 10分钟
        }
        return timeout_mapping.get(analysis_depth, 180)  # 默认3分钟
    
    def _create_optimized_config(self, task) -> Dict[str, Any]:
        """创建优化的配置"""
        return ScheduledResearchConfig.get_optimized_config(task)
    
    def _apply_performance_optimizations(self, researcher, custom_config):
        """应用性能优化配置到研究器"""
        try:
            # 更新配置
            for key, value in custom_config.items():
                if hasattr(researcher.cfg, key.lower()):
                    setattr(researcher.cfg, key.lower(), value)
            
            # 优化内存使用
            researcher.cfg.browse_chunk_max_length = 4096  # 减少chunk大小
            researcher.cfg.summary_token_limit = 500      # 减少摘要token
            
        except Exception as e:
            logger.warning(f"Failed to apply some optimizations: {e}")
    
    def _build_research_query(self, task) -> str:
        """构建研究查询字符串（包含内容安全处理）"""
        try:
            # 生成基础查询
            base_query = ScheduledResearchPrompts.generate_trend_research_query(task)
            
            # 进行内容安全预处理
            processed_query = ContentSafetyChecker.preprocess_query_for_safety(base_query)
            
            # 检查处理后的查询安全性
            is_safe, risky_words, suggestions = ContentSafetyChecker.check_query_safety(processed_query)
            
            if not is_safe and risky_words:
                logger.warning(f"Detected potentially sensitive content in query for task {task.id}: {risky_words}")
                
                # 如果仍有敏感词，使用建议的安全查询
                if suggestions:
                    safe_query = ContentSafetyChecker.suggest_safe_query(processed_query)
                    logger.info(f"Using safe alternative query for task {task.id}: {safe_query}")
                    return safe_query
            
            return processed_query
            
        except Exception as e:
            logger.error(f"Error in query safety processing: {e}")
            # 如果安全处理失败，回退到基础查询
            return ScheduledResearchPrompts.generate_trend_research_query(task)
    
    async def _analyze_trends(self, task, research_result) -> Dict[str, Any]:
        """分析趋势变化"""
        try:
            logger.info(f"Analyzing trends for task: {task.topic}")
            
            # 获取历史数据进行对比
            historical_data = await self._get_historical_data(task.id)
            
            # 使用趋势分析器
            trend_analysis = await self.trend_analyzer.analyze_trends(
                task=task,
                current_result=research_result,
                historical_data=historical_data
            )
            
            return trend_analysis
            
        except Exception as e:
            logger.error(f"Trend analysis failed: {e}")
            return {
                "trend_score": 5.0,  # 默认中等趋势分数
                "keyword_trends": {},
                "sentiment_changes": {},
                "new_topics": [],
                "error": str(e)
            }
    
    async def _generate_summary(self, task, research_result, trend_result) -> Dict[str, Any]:
        """生成动态摘要"""
        try:
            logger.info(f"Generating summary for task: {task.topic}")
            
            # 使用摘要生成器
            summary_data = await self.summary_generator.generate_dynamic_summary(
                task=task,
                research_result=research_result,
                trend_result=trend_result
            )
            
            return summary_data
            
        except Exception as e:
            logger.error(f"Summary generation failed: {e}")
            return {
                "summary": research_result.get("report", "")[:500] + "...",  # 截取前500字符作为摘要
                "key_changes": [],
                "key_findings": [],
                "error": str(e)
            }
    
    async def _get_historical_data(self, task_id: str) -> List[Dict]:
        """获取历史数据用于趋势对比"""
        try:
            # 获取最近的成功记录
            histories = ResearchHistoryDAO.get_successful_histories(task_id, limit=5)
            
            historical_data = []
            for history in histories:
                historical_data.append({
                    "executed_at": history.executed_at,
                    "summary": history.summary,
                    "key_findings": history.key_findings,
                    "trend_score": history.trend_score,
                    "sentiment_score": history.sentiment_score
                })
            
            return historical_data
            
        except Exception as e:
            logger.error(f"Failed to get historical data: {e}")
            return []
    
    async def _save_results(self, task, research_result, trend_result, summary_result):
        """保存执行结果到数据库"""
        try:
            # 保存研究历史记录
            history_data = {
                "task_id": task.id,
                "raw_result": research_result.get("report", ""),
                "summary": summary_result.get("summary", ""),
                "key_findings": summary_result.get("key_findings", []),
                "key_changes": summary_result.get("key_changes", []),
                "sources_count": research_result.get("sources_count", 0),
                "trend_score": trend_result.get("trend_score", 0.0),
                "sentiment_score": trend_result.get("sentiment_score", 0.0),
                "status": "success",
                "research_config": {
                    "query": research_result.get("query_used", ""),
                    "analysis_depth": task.analysis_depth,
                    "source_types": task.source_types
                }
            }
            
            history = ResearchHistoryDAO.create_history(history_data)
            logger.info(f"Saved research history: {history.id}")
            
            # 保存趋势数据
            if trend_result and not trend_result.get("error"):
                trend_data = {
                    "task_id": task.id,
                    "period_start": datetime.now() - timedelta(hours=task.interval_hours),
                    "period_end": datetime.now(),
                    "keyword_trends": trend_result.get("keyword_trends", {}),
                    "sentiment_changes": trend_result.get("sentiment_changes", {}),
                    "new_topics": trend_result.get("new_topics", []),
                    "emerging_keywords": trend_result.get("emerging_keywords", []),
                    "activity_level": trend_result.get("activity_level", 0.0),
                    "change_magnitude": trend_result.get("change_magnitude", 0.0),
                    "confidence_score": trend_result.get("confidence_score", 0.0),
                    "comparison_data": trend_result.get("comparison_data", {}),
                    "anomaly_detected": trend_result.get("anomaly_detected", False),
                    "anomaly_description": trend_result.get("anomaly_description", "")
                }
                
                trend = TrendDataDAO.create_trend_data(trend_data)
                logger.info(f"Saved trend data: {trend.id}")
            
        except Exception as e:
            logger.error(f"Failed to save results: {e}")
            # 这里不抛出异常，因为研究已经完成，只是保存失败
    
    async def _update_execution_log(self, log_id: Optional[str], update_data: Dict):
        """更新执行日志"""
        if not log_id:
            return
        
        try:
            TaskExecutionLogDAO.update_log(log_id, update_data)
        except Exception as e:
            logger.error(f"Failed to update execution log: {e}")
    
    async def test_research_configuration(self, task_data: Dict) -> Dict[str, Any]:
        """测试研究配置（不保存结果）"""
        try:
            logger.info("Testing research configuration...")
            
            # 创建临时任务对象
            from types import SimpleNamespace
            temp_task = SimpleNamespace(**task_data)
            
            # 构建查询
            query = self._build_research_query(temp_task)
            
            # 执行简化的研究（限制时间和资源）
            researcher_config = {
                "query": query,
                "report_type": "research_report",
                "report_source": "web",
                "tone": Tone.Objective,
                "max_subtopics": 3,  # 限制子话题数量
                "verbose": False
            }
            
            researcher = GPTResearcher(**researcher_config)
            
            # 只进行初步研究，不生成完整报告
            research_data = await researcher.conduct_research()
            
            return {
                "success": True,
                "query_generated": query,
                "sources_found": len(getattr(researcher, 'visited_urls', set())),
                "research_preview": str(research_data)[:200] + "..."
            }
            
        except Exception as e:
            logger.error(f"Research configuration test failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _broadcast_result(self, task, result):
        """通过WebSocket广播研究结果"""
        try:
            # 准备广播数据
            broadcast_data = {
                "task_id": task.id,
                "topic": task.topic,
                "timestamp": datetime.now().isoformat(),
                "summary": result.get("summary", ""),
                "key_changes": result.get("key_changes", []),
                "trend_score": result.get("trend_score", 0.0),
                "sources_count": result.get("sources_count", 0),
                "status": "completed" if result.get("success") else "failed",
                "execution_time": result.get("execution_time", 0.0)
            }
            
            # 广播结果
            await self.websocket_manager.broadcast_scheduled_result(broadcast_data)
            
            # 如果趋势分数超过通知阈值，发送通知
            if (result.get("trend_score", 0) >= task.notification_threshold and 
                task.enable_notifications):
                
                notification_data = {
                    "title": f"🔥 重要趋势变化检测",
                    "message": f"话题 '{task.topic}' 出现重要变化，趋势分数: {result.get('trend_score', 0):.1f}",
                    "level": "warning" if result.get("trend_score", 0) >= 8 else "info",
                    "task_id": task.id,
                    "timestamp": datetime.now().isoformat()
                }
                
                await self.websocket_manager.send_scheduled_notification(notification_data)
            
            logger.info(f"Successfully broadcasted result for task: {task.id}")
            
        except Exception as e:
            logger.error(f"Failed to broadcast result: {e}")
