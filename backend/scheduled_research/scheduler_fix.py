"""
定时任务调度器修复补丁
Scheduler Fix Patch - 修复暂停/恢复功能的问题

问题描述：
1. APScheduler使用内存存储，重启后job丢失
2. 暂停任务设置is_active=False，重启后不会重新加载
3. 恢复任务时可能job已不存在，导致恢复失败

解决方案：
1. 改进暂停/恢复逻辑，使用状态标记而非直接暂停job
2. 添加任务恢复检查机制
3. 提供手动修复工具
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any

from ..database import ScheduledTaskDAO, SessionLocal
from ..database.models import ScheduledTask

logger = logging.getLogger(__name__)


class SchedulerHealthChecker:
    """调度器健康检查和修复工具"""
    
    def __init__(self, scheduler_manager):
        self.scheduler_manager = scheduler_manager
    
    async def check_and_fix_paused_tasks(self) -> Dict[str, Any]:
        """检查并修复暂停的任务"""
        results = {
            "checked_tasks": 0,
            "fixed_tasks": 0,
            "failed_tasks": 0,
            "details": []
        }
        
        try:
            # 获取所有任务（包括暂停的）
            with SessionLocal() as db:
                all_tasks = db.query(ScheduledTask).all()
                results["checked_tasks"] = len(all_tasks)
            
            for task in all_tasks:
                try:
                    await self._fix_single_task(task, results)
                except Exception as e:
                    results["failed_tasks"] += 1
                    results["details"].append({
                        "task_id": task.id,
                        "topic": task.topic,
                        "status": "failed",
                        "error": str(e)
                    })
                    logger.error(f"Failed to fix task {task.id}: {e}")
            
            logger.info(f"Health check completed: {results}")
            return results
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            raise
    
    async def _fix_single_task(self, task: ScheduledTask, results: Dict):
        """修复单个任务"""
        job_id = f"research_task_{task.id}"
        job = self.scheduler_manager.scheduler.get_job(job_id)
        
        # 检查任务状态
        if task.is_active and not job:
            # 任务应该是活跃的，但调度器中没有job - 需要重新调度
            await self.scheduler_manager._schedule_task(task)
            results["fixed_tasks"] += 1
            results["details"].append({
                "task_id": task.id,
                "topic": task.topic,
                "status": "rescheduled",
                "action": "Added missing active job"
            })
            logger.info(f"Rescheduled missing active task: {task.id}")
            
        elif not task.is_active and job:
            # 任务应该是暂停的，但调度器中还有job - 需要移除
            self.scheduler_manager.scheduler.remove_job(job_id)
            results["fixed_tasks"] += 1
            results["details"].append({
                "task_id": task.id,
                "topic": task.topic,
                "status": "removed",
                "action": "Removed inactive job"
            })
            logger.info(f"Removed job for inactive task: {task.id}")
            
        elif task.is_active and job:
            # 检查job是否被错误暂停
            if hasattr(job, '_scheduler') and job._scheduler:
                # job存在但可能状态不正确，确保它是运行状态
                results["details"].append({
                    "task_id": task.id,
                    "topic": task.topic,
                    "status": "verified",
                    "action": "Task and job status consistent"
                })


class ImprovedSchedulerManager:
    """改进的调度器管理器，修复暂停/恢复问题"""
    
    def __init__(self, original_manager):
        self.original = original_manager
        self.health_checker = SchedulerHealthChecker(original_manager)
    
    async def enhanced_pause_task(self, task_id: str) -> bool:
        """增强的暂停任务功能"""
        try:
            # 1. 先移除调度器中的job（而不是暂停）
            job_id = f"research_task_{task_id}"
            job = self.original.scheduler.get_job(job_id)
            
            if job:
                self.original.scheduler.remove_job(job_id)
                logger.info(f"Removed job for task: {task_id}")
            
            # 2. 更新数据库状态为暂停
            ScheduledTaskDAO.update_task(task_id, {
                "is_active": False,
                "updated_at": datetime.now()
            })
            
            # 3. 记录暂停操作
            logger.info(f"Enhanced pause completed for task: {task_id}")
            return True
            
        except Exception as e:
            logger.error(f"Enhanced pause failed for task {task_id}: {e}")
            return False
    
    async def enhanced_resume_task(self, task_id: str) -> bool:
        """增强的恢复任务功能"""
        try:
            # 1. 获取任务信息
            task = ScheduledTaskDAO.get_task_by_id(task_id)
            if not task:
                logger.error(f"Task not found: {task_id}")
                return False
            
            # 2. 更新数据库状态为活跃
            ScheduledTaskDAO.update_task(task_id, {
                "is_active": True,
                "updated_at": datetime.now()
            })
            
            # 3. 重新获取更新后的任务
            updated_task = ScheduledTaskDAO.get_task_by_id(task_id)
            
            # 4. 重新调度任务
            await self.original._schedule_task(updated_task)
            
            # 5. 记录恢复操作
            logger.info(f"Enhanced resume completed for task: {task_id}")
            return True
            
        except Exception as e:
            logger.error(f"Enhanced resume failed for task {task_id}: {e}")
            return False
    
    async def force_resync_all_tasks(self) -> Dict[str, Any]:
        """强制重新同步所有任务"""
        try:
            logger.info("Starting force resync of all tasks...")
            
            # 1. 清除所有调度器中的job
            for job in self.original.scheduler.get_jobs():
                if job.id.startswith("research_task_"):
                    self.original.scheduler.remove_job(job.id)
            
            # 2. 重新加载所有活跃任务
            active_tasks = ScheduledTaskDAO.get_all_active_tasks()
            
            # 3. 重新调度所有活跃任务
            scheduled_count = 0
            for task in active_tasks:
                try:
                    await self.original._schedule_task(task)
                    scheduled_count += 1
                except Exception as e:
                    logger.error(f"Failed to reschedule task {task.id}: {e}")
            
            result = {
                "total_active_tasks": len(active_tasks),
                "successfully_scheduled": scheduled_count,
                "failed_count": len(active_tasks) - scheduled_count,
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"Force resync completed: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Force resync failed: {e}")
            raise


def patch_scheduler_manager(scheduler_manager):
    """为现有的调度器管理器打补丁"""
    
    # 保存原始方法
    original_pause_task = scheduler_manager.pause_task
    original_resume_task = scheduler_manager.resume_task
    
    # 创建增强管理器
    enhanced_manager = ImprovedSchedulerManager(scheduler_manager)
    
    # 替换方法
    scheduler_manager.enhanced_pause_task = enhanced_manager.enhanced_pause_task
    scheduler_manager.enhanced_resume_task = enhanced_manager.enhanced_resume_task
    scheduler_manager.force_resync_all_tasks = enhanced_manager.force_resync_all_tasks
    scheduler_manager.health_checker = enhanced_manager.health_checker
    
    # 添加自动修复功能
    async def auto_fix_on_startup():
        """启动时自动修复任务状态"""
        try:
            await enhanced_manager.health_checker.check_and_fix_paused_tasks()
            logger.info("Startup auto-fix completed")
        except Exception as e:
            logger.error(f"Startup auto-fix failed: {e}")
    
    scheduler_manager.auto_fix_on_startup = auto_fix_on_startup
    
    logger.info("Scheduler manager patched successfully")
    return scheduler_manager


async def diagnose_scheduler_issues(scheduler_manager) -> Dict[str, Any]:
    """诊断调度器问题"""
    diagnosis = {
        "timestamp": datetime.now().isoformat(),
        "scheduler_running": scheduler_manager.scheduler.running,
        "total_jobs": 0,
        "active_tasks_in_db": 0,
        "inactive_tasks_in_db": 0,
        "issues": [],
        "recommendations": []
    }
    
    try:
        # 检查调度器状态
        jobs = scheduler_manager.scheduler.get_jobs()
        diagnosis["total_jobs"] = len(jobs)
        
        # 检查数据库任务
        all_tasks = ScheduledTaskDAO.get_tasks_by_user("default_user")
        active_tasks = [t for t in all_tasks if t.is_active]
        inactive_tasks = [t for t in all_tasks if not t.is_active]
        
        diagnosis["active_tasks_in_db"] = len(active_tasks)
        diagnosis["inactive_tasks_in_db"] = len(inactive_tasks)
        
        # 检查不一致性
        for task in active_tasks:
            job_id = f"research_task_{task.id}"
            job = scheduler_manager.scheduler.get_job(job_id)
            
            if not job:
                diagnosis["issues"].append({
                    "type": "missing_job",
                    "task_id": task.id,
                    "topic": task.topic,
                    "description": "Active task missing from scheduler"
                })
        
        for job in jobs:
            if job.id.startswith("research_task_"):
                task_id = job.id.replace("research_task_", "")
                task = ScheduledTaskDAO.get_task_by_id(task_id)
                
                if not task:
                    diagnosis["issues"].append({
                        "type": "orphan_job",
                        "job_id": job.id,
                        "description": "Scheduler job without corresponding database task"
                    })
                elif not task.is_active:
                    diagnosis["issues"].append({
                        "type": "inactive_job",
                        "task_id": task.id,
                        "topic": task.topic,
                        "description": "Inactive task still has scheduler job"
                    })
        
        # 生成建议
        if diagnosis["issues"]:
            diagnosis["recommendations"].append("Run force_resync_all_tasks() to fix all issues")
            diagnosis["recommendations"].append("Consider using enhanced_pause_task/enhanced_resume_task methods")
        else:
            diagnosis["recommendations"].append("No issues detected")
        
        logger.info(f"Diagnosis completed: {len(diagnosis['issues'])} issues found")
        return diagnosis
        
    except Exception as e:
        diagnosis["error"] = str(e)
        logger.error(f"Diagnosis failed: {e}")
        return diagnosis
