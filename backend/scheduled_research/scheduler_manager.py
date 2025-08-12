"""
定时任务管理器 - 管理和调度研究任务
Scheduler Manager - Manages and schedules research tasks
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Callable
import threading
import json

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.cron import CronTrigger
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.asyncio import AsyncIOExecutor
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR, EVENT_JOB_MISSED

from ..database import ScheduledTaskDAO, ResearchHistoryDAO, TaskExecutionLogDAO
from .task_executor import ResearchTaskExecutor
from .quick_executor import QuickResearchExecutor, StreamingQuickExecutor

logger = logging.getLogger(__name__)


class ScheduledResearchManager:
    """
    定时研究管理器
    Manages scheduled research tasks using APScheduler
    """
    
    def __init__(self, websocket_manager=None):
        """
        初始化调度器管理器
        
        Args:
            websocket_manager: WebSocket管理器，用于实时推送结果
        """
        self.websocket_manager = websocket_manager
        self.scheduler = None
        self.task_executor = ResearchTaskExecutor(websocket_manager=websocket_manager)
        self.quick_executor = QuickResearchExecutor()
        self.streaming_executor = StreamingQuickExecutor(websocket_manager=websocket_manager)
        self.running_tasks = {}  # 正在运行的任务记录
        self._is_initialized = False
        
        # 配置调度器
        self._setup_scheduler()
    
    def _setup_scheduler(self):
        """配置APScheduler调度器"""
        jobstores = {
            'default': MemoryJobStore()
        }
        
        executors = {
            'default': AsyncIOExecutor()
        }
        
        job_defaults = {
            'coalesce': True,  # 合并多个相同的任务
            'max_instances': 1,  # 每个任务最多只能有一个实例运行
            'misfire_grace_time': 300  # 任务错过执行时间的容忍度（秒）
        }
        
        self.scheduler = AsyncIOScheduler(
            jobstores=jobstores,
            executors=executors,
            job_defaults=job_defaults,
            timezone='Asia/Shanghai'  # 设置时区
        )
        
        # 添加事件监听器
        self.scheduler.add_listener(self._job_executed_listener, EVENT_JOB_EXECUTED)
        self.scheduler.add_listener(self._job_error_listener, EVENT_JOB_ERROR)
        self.scheduler.add_listener(self._job_missed_listener, EVENT_JOB_MISSED)
    
    async def initialize(self):
        """初始化调度器和加载现有任务"""
        if self._is_initialized:
            return
        
        try:
            logger.info("Initializing scheduled research manager...")
            
            # 启动调度器
            if not self.scheduler.running:
                self.scheduler.start()
                logger.info("APScheduler started successfully")
            
            # 加载数据库中的活跃任务
            await self._load_existing_tasks()
            
            self._is_initialized = True
            logger.info("Scheduled research manager initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize scheduled research manager: {e}")
            raise
    
    async def _load_existing_tasks(self):
        """从数据库加载现有的活跃任务"""
        try:
            active_tasks = ScheduledTaskDAO.get_all_active_tasks()
            logger.info(f"Loading {len(active_tasks)} active tasks from database")
            
            for task in active_tasks:
                await self._schedule_task(task)
                
            logger.info(f"Successfully loaded {len(active_tasks)} scheduled tasks")
            
        except Exception as e:
            logger.error(f"Failed to load existing tasks: {e}")
            raise
    
    async def _schedule_task(self, task):
        """调度单个任务"""
        try:
            job_id = f"research_task_{task.id}"
            
            # 如果任务已存在，先移除
            if self.scheduler.get_job(job_id):
                self.scheduler.remove_job(job_id)
            
            # 创建间隔触发器
            trigger = IntervalTrigger(
                hours=task.interval_hours,
                start_date=task.next_run or datetime.now()
            )
            
            # 添加任务到调度器
            self.scheduler.add_job(
                func=self._execute_research_task,
                trigger=trigger,
                id=job_id,
                args=[task.id],
                name=f"Research: {task.topic}",
                replace_existing=True
            )
            
            logger.info(f"Scheduled task {task.id}: {task.topic} (every {task.interval_hours}h)")
            
        except Exception as e:
            logger.error(f"Failed to schedule task {task.id}: {e}")
            raise
    
    async def _execute_research_task(self, task_id: str):
        """执行研究任务"""
        execution_log_id = None
        
        try:
            # 获取任务详情
            task = ScheduledTaskDAO.get_task_by_id(task_id)
            if not task or not task.is_active:
                logger.warning(f"Task {task_id} not found or inactive, skipping execution")
                return
            
            # 检查是否已在运行
            if task_id in self.running_tasks:
                logger.warning(f"Task {task_id} is already running, skipping this execution")
                return
            
            # 记录任务开始执行
            self.running_tasks[task_id] = datetime.now()
            
            # 创建执行日志
            log_data = {
                "task_id": task_id,
                "status": "running",
                "execution_step": "initializing",
                "progress_percentage": 0.0,
                "log_messages": [{"timestamp": datetime.now().isoformat(), "message": "Task execution started"}]
            }
            execution_log = TaskExecutionLogDAO.create_log(log_data)
            execution_log_id = execution_log.id
            
            logger.info(f"Starting execution of task {task_id}: {task.topic}")
            
            # 执行研究任务
            result = await self.task_executor.execute_task(task, execution_log_id)
            
            # 更新任务执行状态
            ScheduledTaskDAO.update_task_execution_status(
                task_id=task_id,
                success=result.get("success", False),
                execution_time=result.get("execution_time")
            )
            
            # 更新执行日志
            if execution_log_id:
                TaskExecutionLogDAO.update_log(execution_log_id, {
                    "status": "completed" if result.get("success") else "failed",
                    "completed_at": datetime.now(),
                    "progress_percentage": 100.0,
                    "log_messages": result.get("log_messages", [])
                })
            
            # 推送结果到前端（如果有WebSocket连接）
            if self.websocket_manager and result.get("success"):
                await self._push_result_to_frontend(task, result)
            
            logger.info(f"Task {task_id} executed successfully: {result.get('summary', 'No summary')}")
            
        except Exception as e:
            logger.error(f"Error executing task {task_id}: {e}")
            
            # 更新失败状态
            ScheduledTaskDAO.update_task_execution_status(task_id=task_id, success=False)
            
            if execution_log_id:
                TaskExecutionLogDAO.update_log(execution_log_id, {
                    "status": "failed",
                    "completed_at": datetime.now(),
                    "log_messages": [{"timestamp": datetime.now().isoformat(), "message": f"Error: {str(e)}"}]
                })
            
        finally:
            # 移除运行记录
            self.running_tasks.pop(task_id, None)
    
    async def _push_result_to_frontend(self, task, result):
        """推送结果到前端"""
        try:
            message = {
                "type": "scheduled_result",
                "task_id": task.id,
                "topic": task.topic,
                "timestamp": datetime.now().isoformat(),
                "summary": result.get("summary", ""),
                "key_changes": result.get("key_changes", []),
                "trend_score": result.get("trend_score", 0.0),
                "sources_count": result.get("sources_count", 0)
            }
            
            # 这里需要实现WebSocket推送逻辑
            # 暂时记录日志
            logger.info(f"Would push result to frontend: {json.dumps(message, ensure_ascii=False)}")
            
        except Exception as e:
            logger.error(f"Failed to push result to frontend: {e}")
    
    def _job_executed_listener(self, event):
        """任务执行完成监听器"""
        logger.debug(f"Job {event.job_id} executed successfully")
    
    def _job_error_listener(self, event):
        """任务执行错误监听器"""
        logger.error(f"Job {event.job_id} crashed: {event.exception}")
    
    def _job_missed_listener(self, event):
        """任务错过执行监听器"""
        logger.warning(f"Job {event.job_id} missed its scheduled time")
    
    # 公共API方法
    
    async def add_task(self, task_data: Dict) -> str:
        """添加新的定时任务"""
        try:
            # 创建任务记录
            task = ScheduledTaskDAO.create_task(task_data)
            
            # 调度任务
            await self._schedule_task(task)
            
            logger.info(f"Added new scheduled task: {task.id} - {task.topic}")
            return task.id
            
        except Exception as e:
            logger.error(f"Failed to add scheduled task: {e}")
            raise
    
    async def update_task(self, task_id: str, update_data: Dict) -> bool:
        """更新定时任务"""
        try:
            # 更新数据库记录
            updated_task = ScheduledTaskDAO.update_task(task_id, update_data)
            if not updated_task:
                return False
            
            # 重新调度任务
            if updated_task.is_active:
                await self._schedule_task(updated_task)
            else:
                # 如果任务被禁用，移除调度
                job_id = f"research_task_{task_id}"
                if self.scheduler.get_job(job_id):
                    self.scheduler.remove_job(job_id)
            
            logger.info(f"Updated scheduled task: {task_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update scheduled task {task_id}: {e}")
            raise
    
    async def remove_task(self, task_id: str) -> bool:
        """移除定时任务"""
        try:
            # 从调度器移除
            job_id = f"research_task_{task_id}"
            if self.scheduler.get_job(job_id):
                self.scheduler.remove_job(job_id)
            
            # 从数据库删除
            success = ScheduledTaskDAO.delete_task(task_id)
            
            if success:
                logger.info(f"Removed scheduled task: {task_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to remove scheduled task {task_id}: {e}")
            raise
    
    async def pause_task(self, task_id: str) -> bool:
        """暂停任务（改进版）"""
        try:
            job_id = f"research_task_{task_id}"
            job = self.scheduler.get_job(job_id)
            
            # 移除job而不是暂停，避免重启后状态不一致
            if job:
                self.scheduler.remove_job(job_id)
                logger.info(f"Removed job for paused task: {task_id}")
            
            # 更新数据库状态
            ScheduledTaskDAO.update_task(task_id, {
                "is_active": False,
                "updated_at": datetime.now()
            })
            logger.info(f"Paused scheduled task: {task_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to pause scheduled task {task_id}: {e}")
            raise
    
    async def resume_task(self, task_id: str) -> bool:
        """恢复任务（改进版）"""
        try:
            # 1. 更新数据库状态
            ScheduledTaskDAO.update_task(task_id, {
                "is_active": True,
                "updated_at": datetime.now()
            })
            
            # 2. 获取更新后的任务信息
            task = ScheduledTaskDAO.get_task_by_id(task_id)
            if not task:
                logger.error(f"Task not found: {task_id}")
                return False
            
            # 3. 重新调度任务（确保job正确创建）
            await self._schedule_task(task)
            logger.info(f"Resumed scheduled task: {task_id}")
            return True
                
        except Exception as e:
            logger.error(f"Failed to resume scheduled task {task_id}: {e}")
            raise
    
    async def trigger_task_now(self, task_id: str, quick_mode: bool = False) -> bool:
        """立即触发任务执行"""
        try:
            # 获取任务
            task = ScheduledTaskDAO.get_task_by_id(task_id)
            if not task:
                return False
            
            if quick_mode:
                # 使用快速执行器直接执行
                logger.info(f"Quick triggering task: {task_id}")
                asyncio.create_task(self._execute_quick_task(task_id))
            else:
                # 创建一次性任务
                job_id = f"manual_trigger_{task_id}_{int(datetime.now().timestamp())}"
                
                self.scheduler.add_job(
                    func=self._execute_research_task,
                    trigger=DateTrigger(run_date=datetime.now()),
                    id=job_id,
                    args=[task_id],
                    name=f"Manual Trigger: {task.topic}"
                )
            
            logger.info(f"Triggered task: {task_id} (quick_mode={quick_mode})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to trigger task {task_id}: {e}")
            raise
    
    async def _execute_quick_task(self, task_id: str):
        """执行快速任务"""
        try:
            task = ScheduledTaskDAO.get_task_by_id(task_id)
            if not task:
                logger.warning(f"Task {task_id} not found for quick execution")
                return
            
            # 使用快速执行器
            result = await self.quick_executor.execute_quick_research(task)
            
            # 保存结果到数据库
            if result["success"]:
                await self._save_quick_result(task, result)
                
                # 广播结果
                if self.websocket_manager:
                    await self._broadcast_quick_result(task, result)
            else:
                logger.error(f"Quick execution failed for task {task_id}: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"Quick task execution failed: {e}")
    
    async def _save_quick_result(self, task, result):
        """保存快速执行结果"""
        try:
            # 创建研究历史记录
            history_data = {
                "task_id": task.id,
                "executed_at": datetime.now(),
                "execution_duration": result.get("execution_time", 0),
                "status": "success",
                "raw_result": result.get("report", ""),
                "summary": result.get("summary", ""),
                "key_findings": [],  # 快速模式暂不分析
                "key_changes": [],   # 快速模式暂不分析
                "sources_count": result.get("sources_count", 0),
                "tokens_used": 0,    # 快速模式暂不统计
                "trend_score": 5.0,  # 默认中等分数
                "sentiment_score": 0.0,
                "research_config": {
                    "mode": "quick",
                    "analysis_depth": task.analysis_depth,
                    "query_used": result.get("query_used", "")
                },
                "sources_used": []
            }
            
            ResearchHistoryDAO.create_history(history_data)
            
            # 更新任务执行统计
            ScheduledTaskDAO.update_task_execution_status(
                task_id=task.id,
                success=True,
                execution_time=result.get("execution_time", 0)
            )
            
        except Exception as e:
            logger.error(f"Failed to save quick result: {e}")
    
    async def _broadcast_quick_result(self, task, result):
        """广播快速执行结果"""
        try:
            message = {
                "type": "quick_research_completed",
                "task_id": task.id,
                "task_topic": task.topic,
                "summary": result.get("summary", ""),
                "sources_count": result.get("sources_count", 0),
                "execution_time": result.get("execution_time", 0),
                "timestamp": datetime.now().isoformat(),
                "trend_score": 5.0
            }
            
            await self.websocket_manager.broadcast_scheduled_result(message)
            
        except Exception as e:
            logger.error(f"Failed to broadcast quick result: {e}")
    
    def get_scheduler_status(self) -> Dict:
        """获取调度器状态"""
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                "id": job.id,
                "name": job.name,
                "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
                "trigger": str(job.trigger)
            })
        
        return {
            "running": self.scheduler.running,
            "total_jobs": len(jobs),
            "jobs": jobs,
            "running_tasks": list(self.running_tasks.keys())
        }
    
    async def shutdown(self):
        """关闭调度器"""
        try:
            if self.scheduler and self.scheduler.running:
                self.scheduler.shutdown(wait=True)
                logger.info("Scheduled research manager shutdown successfully")
                
        except Exception as e:
            logger.error(f"Error during scheduler shutdown: {e}")


# 全局调度器实例
_scheduler_manager_instance = None

def get_scheduler_manager(websocket_manager=None) -> ScheduledResearchManager:
    """获取全局调度器管理器实例"""
    global _scheduler_manager_instance
    
    if _scheduler_manager_instance is None:
        _scheduler_manager_instance = ScheduledResearchManager(websocket_manager=websocket_manager)
    
    return _scheduler_manager_instance

async def initialize_scheduler(websocket_manager=None):
    """初始化全局调度器"""
    manager = get_scheduler_manager(websocket_manager)
    await manager.initialize()
    return manager
