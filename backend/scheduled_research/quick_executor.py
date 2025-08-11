"""
快速任务执行器 - 用于立即执行的优化版本
Quick Task Executor - Optimized version for immediate execution
"""
import asyncio
import logging
import time
from datetime import datetime
from typing import Dict, Any, Optional

from gpt_researcher.agent import GPTResearcher
from gpt_researcher.utils.enum import ReportType, ReportSource, Tone

from .config import ScheduledResearchConfig, ScheduledResearchPrompts

logger = logging.getLogger(__name__)


class QuickResearchExecutor:
    """
    快速研究执行器 - 专为立即执行优化
    优化策略：
    1. 简化配置，减少初始化时间
    2. 使用更激进的超时设置
    3. 优先使用快速模型
    4. 减少不必要的中间步骤
    """
    
    def __init__(self):
        self.max_concurrent_tasks = 2  # 限制并发数
        self.running_tasks = set()
    
    async def execute_quick_research(self, task) -> Dict[str, Any]:
        """
        快速执行研究任务
        
        Args:
            task: ScheduledTask对象
            
        Returns:
            Dict包含执行结果
        """
        start_time = time.time()
        task_id = task.id
        
        # 检查并发限制
        if len(self.running_tasks) >= self.max_concurrent_tasks:
            return {
                "success": False,
                "error": "系统繁忙，请稍后再试",
                "execution_time": 0
            }
        
        self.running_tasks.add(task_id)
        
        try:
            logger.info(f"Quick research started: {task.topic}")
            
            # 构建优化的查询
            query = self._build_quick_query(task)
            
            # 创建快速配置
            researcher_config = self._create_quick_config(task, query)
            
            # 创建研究器实例
            researcher = GPTResearcher(**researcher_config)
            
            # 应用快速优化
            self._apply_quick_optimizations(researcher, task)
            
            # 执行研究 - 使用更短的超时
            timeout = self._get_quick_timeout(task.analysis_depth)
            
            try:
                # 并发执行研究和报告生成准备
                research_data = await asyncio.wait_for(
                    researcher.conduct_research(),
                    timeout=timeout
                )
                
                report = await asyncio.wait_for(
                    researcher.write_report(),
                    timeout=30  # 报告生成最多30秒
                )
                
            except asyncio.TimeoutError:
                logger.warning(f"Quick research timeout for task {task_id}")
                # 快速模式下直接返回超时
                return {
                    "success": False,
                    "error": "研究超时，请尝试降低分析深度或稍后重试",
                    "execution_time": time.time() - start_time
                }
            
            # 快速提取结果
            sources_count = len(getattr(researcher, 'visited_urls', set()))
            execution_time = time.time() - start_time
            
            # 生成简化的摘要
            summary = self._generate_quick_summary(task, report)
            
            result = {
                "success": True,
                "report": report,
                "summary": summary,
                "sources_count": sources_count,
                "execution_time": execution_time,
                "query_used": query,
                "mode": "quick"
            }
            
            logger.info(f"Quick research completed in {execution_time:.1f}s: {task.topic}")
            return result
            
        except Exception as e:
            logger.error(f"Quick research failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "execution_time": time.time() - start_time
            }
        finally:
            self.running_tasks.discard(task_id)
    
    def _build_quick_query(self, task) -> str:
        """构建快速查询 - 简化版本"""
        base_query = task.topic
        
        # 快速模式下只使用核心关键词
        if task.keywords:
            key_keywords = task.keywords[:2]  # 最多2个关键词
            return f"{base_query} {' '.join(key_keywords)}"
        
        return base_query
    
    def _create_quick_config(self, task, query) -> Dict[str, Any]:
        """创建快速配置"""
        return {
            "query": query,
            "report_type": "research_report",  # 固定使用最快的报告类型
            "report_source": task.report_source,
            "tone": Tone.Objective,  # 固定使用客观语调
            "max_subtopics": 1,  # 最小子主题数
            "verbose": False,
            "headers": {"User-Agent": "GPT-Researcher-Quick/1.0"}
        }
    
    def _apply_quick_optimizations(self, researcher, task):
        """应用快速优化"""
        try:
            # 最激进的性能配置
            researcher.cfg.max_search_results_per_query = 2
            researcher.cfg.max_subtopics = 1
            researcher.cfg.max_iterations = 1
            researcher.cfg.max_scraper_workers = 4
            researcher.cfg.total_words = 400  # 大幅减少字数
            researcher.cfg.curate_sources = False
            researcher.cfg.verbose = False
            researcher.cfg.temperature = 0.2  # 更低温度，更快响应
            researcher.cfg.summary_token_limit = 300
            researcher.cfg.browse_chunk_max_length = 2048
            researcher.cfg.fast_token_limit = 1500
            researcher.cfg.language = "chinese"
            
        except Exception as e:
            logger.warning(f"Failed to apply quick optimizations: {e}")
    
    def _get_quick_timeout(self, analysis_depth: str) -> int:
        """获取快速模式超时时间 - 比正常模式更短"""
        timeout_map = {
            "basic": 60,       # 1分钟
            "detailed": 120,   # 2分钟  
            "deep": 180        # 3分钟
        }
        return timeout_map.get(analysis_depth, 90)
    
    def _generate_quick_summary(self, task, report: str) -> str:
        """生成快速摘要"""
        # 简单的摘要生成 - 取报告前200字
        if not report:
            return "研究完成，但未能生成有效内容"
        
        # 清理报告内容
        clean_report = report.replace('#', '').replace('*', '').strip()
        
        # 取前200个字符作为摘要
        if len(clean_report) > 200:
            summary = clean_report[:200] + "..."
        else:
            summary = clean_report
        
        return f"快速研究完成。{summary}"
    
    async def get_system_status(self) -> Dict[str, Any]:
        """获取系统状态"""
        return {
            "running_tasks": len(self.running_tasks),
            "max_concurrent": self.max_concurrent_tasks,
            "available_slots": self.max_concurrent_tasks - len(self.running_tasks),
            "mode": "quick_executor"
        }


class StreamingQuickExecutor(QuickResearchExecutor):
    """
    流式快速执行器 - 支持实时进度推送
    """
    
    def __init__(self, websocket_manager=None):
        super().__init__()
        self.websocket_manager = websocket_manager
    
    async def execute_streaming_research(self, task, websocket=None) -> Dict[str, Any]:
        """
        执行流式研究 - 实时推送进度
        """
        start_time = time.time()
        task_id = task.id
        
        # 发送开始消息
        await self._send_progress(task_id, "开始快速研究...", 0, websocket)
        
        if len(self.running_tasks) >= self.max_concurrent_tasks:
            await self._send_progress(task_id, "系统繁忙，请稍后再试", 0, websocket, error=True)
            return {"success": False, "error": "系统繁忙"}
        
        self.running_tasks.add(task_id)
        
        try:
            # 初始化阶段
            await self._send_progress(task_id, "准备研究环境...", 10, websocket)
            
            query = self._build_quick_query(task)
            researcher_config = self._create_quick_config(task, query)
            researcher = GPTResearcher(**researcher_config)
            self._apply_quick_optimizations(researcher, task)
            
            # 研究阶段
            await self._send_progress(task_id, "正在搜索相关信息...", 30, websocket)
            
            timeout = self._get_quick_timeout(task.analysis_depth)
            research_data = await asyncio.wait_for(
                researcher.conduct_research(),
                timeout=timeout
            )
            
            # 生成报告阶段
            await self._send_progress(task_id, "正在生成研究报告...", 70, websocket)
            
            report = await asyncio.wait_for(
                researcher.write_report(),
                timeout=30
            )
            
            # 完成阶段
            await self._send_progress(task_id, "研究完成", 100, websocket)
            
            result = {
                "success": True,
                "report": report,
                "summary": self._generate_quick_summary(task, report),
                "sources_count": len(getattr(researcher, 'visited_urls', set())),
                "execution_time": time.time() - start_time,
                "query_used": query,
                "mode": "streaming_quick"
            }
            
            return result
            
        except asyncio.TimeoutError:
            await self._send_progress(task_id, "研究超时", 0, websocket, error=True)
            return {"success": False, "error": "研究超时"}
        except Exception as e:
            await self._send_progress(task_id, f"研究失败: {str(e)}", 0, websocket, error=True)
            return {"success": False, "error": str(e)}
        finally:
            self.running_tasks.discard(task_id)
    
    async def _send_progress(self, task_id: str, message: str, progress: int, 
                           websocket=None, error: bool = False):
        """发送进度消息"""
        progress_data = {
            "type": "quick_research_progress",
            "task_id": task_id,
            "message": message,
            "progress": progress,
            "timestamp": datetime.now().isoformat(),
            "error": error
        }
        
        if websocket:
            try:
                await websocket.send_json(progress_data)
            except Exception as e:
                logger.warning(f"Failed to send progress: {e}")
        
        if self.websocket_manager:
            try:
                await self.websocket_manager.broadcast_scheduled_result(progress_data)
            except Exception as e:
                logger.warning(f"Failed to broadcast progress: {e}")
