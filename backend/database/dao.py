"""
数据访问对象 (DAO) - 提供数据库操作接口
Data Access Objects (DAO) - Provides database operation interfaces
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc, func
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging

from .models import ScheduledTask, ResearchHistory, TrendData, TaskExecutionLog
from .database import SessionLocal

logger = logging.getLogger(__name__)


class ScheduledTaskDAO:
    """定时任务数据访问对象"""

    @staticmethod
    def create_task(task_data: Dict[str, Any]) -> ScheduledTask:
        """创建新的定时任务"""
        with SessionLocal() as db:
            try:
                # 设置下次执行时间
                if 'next_run' not in task_data:
                    task_data['next_run'] = datetime.now() + timedelta(hours=task_data.get('interval_hours', 24))
                
                task = ScheduledTask(**task_data)
                db.add(task)
                db.commit()
                db.refresh(task)
                logger.info(f"Created scheduled task: {task.id}")
                return task
            except Exception as e:
                db.rollback()
                logger.error(f"Failed to create scheduled task: {e}")
                raise

    @staticmethod
    def get_task_by_id(task_id: str) -> Optional[ScheduledTask]:
        """根据ID获取任务"""
        with SessionLocal() as db:
            return db.query(ScheduledTask).filter(ScheduledTask.id == task_id).first()

    @staticmethod
    def get_tasks_by_user(user_id: str, active_only: bool = False) -> List[ScheduledTask]:
        """获取用户的所有任务"""
        with SessionLocal() as db:
            query = db.query(ScheduledTask).filter(ScheduledTask.user_id == user_id)
            if active_only:
                query = query.filter(ScheduledTask.is_active == True)
            return query.order_by(desc(ScheduledTask.created_at)).all()

    @staticmethod
    def get_all_active_tasks() -> List[ScheduledTask]:
        """获取所有激活的任务"""
        with SessionLocal() as db:
            return db.query(ScheduledTask).filter(ScheduledTask.is_active == True).all()

    @staticmethod
    def get_pending_tasks() -> List[ScheduledTask]:
        """获取需要执行的任务"""
        with SessionLocal() as db:
            now = datetime.now()
            return db.query(ScheduledTask).filter(
                and_(
                    ScheduledTask.is_active == True,
                    ScheduledTask.next_run <= now
                )
            ).all()

    @staticmethod
    def update_task(task_id: str, update_data: Dict[str, Any]) -> Optional[ScheduledTask]:
        """更新任务"""
        with SessionLocal() as db:
            try:
                task = db.query(ScheduledTask).filter(ScheduledTask.id == task_id).first()
                if not task:
                    return None
                
                for key, value in update_data.items():
                    if hasattr(task, key):
                        setattr(task, key, value)
                
                task.updated_at = datetime.now()
                db.commit()
                db.refresh(task)
                logger.info(f"Updated scheduled task: {task_id}")
                return task
            except Exception as e:
                db.rollback()
                logger.error(f"Failed to update scheduled task {task_id}: {e}")
                raise

    @staticmethod
    def delete_task(task_id: str) -> bool:
        """删除任务"""
        with SessionLocal() as db:
            try:
                task = db.query(ScheduledTask).filter(ScheduledTask.id == task_id).first()
                if not task:
                    return False
                
                db.delete(task)
                db.commit()
                logger.info(f"Deleted scheduled task: {task_id}")
                return True
            except Exception as e:
                db.rollback()
                logger.error(f"Failed to delete scheduled task {task_id}: {e}")
                raise

    @staticmethod
    def update_task_execution_status(task_id: str, success: bool, execution_time: Optional[float] = None):
        """更新任务执行状态"""
        with SessionLocal() as db:
            try:
                task = db.query(ScheduledTask).filter(ScheduledTask.id == task_id).first()
                if not task:
                    return False
                
                task.last_run = datetime.now()
                task.total_runs += 1
                
                if success:
                    task.success_runs += 1
                else:
                    task.failed_runs += 1
                
                # 更新下次执行时间
                task.update_next_run()
                
                db.commit()
                logger.info(f"Updated execution status for task {task_id}: success={success}")
                return True
            except Exception as e:
                db.rollback()
                logger.error(f"Failed to update execution status for task {task_id}: {e}")
                raise


class ResearchHistoryDAO:
    """研究历史数据访问对象"""

    @staticmethod
    def create_history(history_data: Dict[str, Any]) -> ResearchHistory:
        """创建研究历史记录"""
        with SessionLocal() as db:
            try:
                history = ResearchHistory(**history_data)
                db.add(history)
                db.commit()
                db.refresh(history)
                logger.info(f"Created research history: {history.id}")
                return history
            except Exception as e:
                db.rollback()
                logger.error(f"Failed to create research history: {e}")
                raise

    @staticmethod
    def get_history_by_task(task_id: str, limit: int = 50) -> List[ResearchHistory]:
        """获取任务的历史记录"""
        with SessionLocal() as db:
            return db.query(ResearchHistory).filter(
                ResearchHistory.task_id == task_id
            ).order_by(desc(ResearchHistory.executed_at)).limit(limit).all()

    @staticmethod
    def get_latest_history(task_id: str) -> Optional[ResearchHistory]:
        """获取任务的最新历史记录"""
        with SessionLocal() as db:
            return db.query(ResearchHistory).filter(
                ResearchHistory.task_id == task_id
            ).order_by(desc(ResearchHistory.executed_at)).first()

    @staticmethod
    def get_successful_histories(task_id: str, limit: int = 10) -> List[ResearchHistory]:
        """获取成功执行的历史记录"""
        with SessionLocal() as db:
            return db.query(ResearchHistory).filter(
                and_(
                    ResearchHistory.task_id == task_id,
                    ResearchHistory.status == "success"
                )
            ).order_by(desc(ResearchHistory.executed_at)).limit(limit).all()

    @staticmethod
    def get_history_by_date_range(task_id: str, start_date: datetime, end_date: datetime) -> List[ResearchHistory]:
        """获取指定时间范围的历史记录"""
        with SessionLocal() as db:
            return db.query(ResearchHistory).filter(
                and_(
                    ResearchHistory.task_id == task_id,
                    ResearchHistory.executed_at >= start_date,
                    ResearchHistory.executed_at <= end_date
                )
            ).order_by(asc(ResearchHistory.executed_at)).all()

    @staticmethod
    def update_history(history_id: str, update_data: Dict[str, Any]) -> Optional[ResearchHistory]:
        """更新历史记录"""
        with SessionLocal() as db:
            try:
                history = db.query(ResearchHistory).filter(ResearchHistory.id == history_id).first()
                if not history:
                    return None
                
                for key, value in update_data.items():
                    if hasattr(history, key):
                        setattr(history, key, value)
                
                db.commit()
                db.refresh(history)
                return history
            except Exception as e:
                db.rollback()
                logger.error(f"Failed to update research history {history_id}: {e}")
                raise


class TrendDataDAO:
    """趋势数据访问对象"""

    @staticmethod
    def create_trend_data(trend_data: Dict[str, Any]) -> TrendData:
        """创建趋势数据"""
        with SessionLocal() as db:
            try:
                trend = TrendData(**trend_data)
                db.add(trend)
                db.commit()
                db.refresh(trend)
                logger.info(f"Created trend data: {trend.id}")
                return trend
            except Exception as e:
                db.rollback()
                logger.error(f"Failed to create trend data: {e}")
                raise

    @staticmethod
    def get_trend_data_by_task(task_id: str, limit: int = 30) -> List[TrendData]:
        """获取任务的趋势数据"""
        with SessionLocal() as db:
            return db.query(TrendData).filter(
                TrendData.task_id == task_id
            ).order_by(desc(TrendData.analysis_date)).limit(limit).all()

    @staticmethod
    def get_latest_trend_data(task_id: str) -> Optional[TrendData]:
        """获取最新的趋势数据"""
        with SessionLocal() as db:
            return db.query(TrendData).filter(
                TrendData.task_id == task_id
            ).order_by(desc(TrendData.analysis_date)).first()

    @staticmethod
    def get_trend_data_by_period(task_id: str, days: int = 30) -> List[TrendData]:
        """获取指定时期的趋势数据"""
        with SessionLocal() as db:
            start_date = datetime.now() - timedelta(days=days)
            return db.query(TrendData).filter(
                and_(
                    TrendData.task_id == task_id,
                    TrendData.analysis_date >= start_date
                )
            ).order_by(asc(TrendData.analysis_date)).all()


class TaskExecutionLogDAO:
    """任务执行日志数据访问对象"""

    @staticmethod
    def create_log(log_data: Dict[str, Any]) -> TaskExecutionLog:
        """创建执行日志"""
        with SessionLocal() as db:
            try:
                log = TaskExecutionLog(**log_data)
                db.add(log)
                db.commit()
                db.refresh(log)
                return log
            except Exception as e:
                db.rollback()
                logger.error(f"Failed to create execution log: {e}")
                raise

    @staticmethod
    def update_log(log_id: str, update_data: Dict[str, Any]) -> Optional[TaskExecutionLog]:
        """更新执行日志"""
        with SessionLocal() as db:
            try:
                log = db.query(TaskExecutionLog).filter(TaskExecutionLog.id == log_id).first()
                if not log:
                    return None
                
                for key, value in update_data.items():
                    if hasattr(log, key):
                        setattr(log, key, value)
                
                db.commit()
                db.refresh(log)
                return log
            except Exception as e:
                db.rollback()
                logger.error(f"Failed to update execution log {log_id}: {e}")
                raise

    @staticmethod
    def get_logs_by_task(task_id: str, limit: int = 100) -> List[TaskExecutionLog]:
        """获取任务的执行日志"""
        with SessionLocal() as db:
            return db.query(TaskExecutionLog).filter(
                TaskExecutionLog.task_id == task_id
            ).order_by(desc(TaskExecutionLog.started_at)).limit(limit).all()

    @staticmethod
    def get_running_logs() -> List[TaskExecutionLog]:
        """获取正在运行的任务日志"""
        with SessionLocal() as db:
            return db.query(TaskExecutionLog).filter(
                TaskExecutionLog.status == "running"
            ).all()


# 统计和分析函数
class AnalyticsDAO:
    """数据分析和统计访问对象"""

    @staticmethod
    def get_task_statistics(task_id: str) -> Dict[str, Any]:
        """获取任务统计信息"""
        with SessionLocal() as db:
            task = db.query(ScheduledTask).filter(ScheduledTask.id == task_id).first()
            if not task:
                return {}

            # 获取历史记录统计
            total_histories = db.query(ResearchHistory).filter(ResearchHistory.task_id == task_id).count()
            successful_histories = db.query(ResearchHistory).filter(
                and_(ResearchHistory.task_id == task_id, ResearchHistory.status == "success")
            ).count()

            # 获取平均趋势分数
            avg_trend_score = db.query(func.avg(ResearchHistory.trend_score)).filter(
                and_(ResearchHistory.task_id == task_id, ResearchHistory.trend_score.isnot(None))
            ).scalar()

            # 获取最新趋势数据
            latest_trend = db.query(TrendData).filter(
                TrendData.task_id == task_id
            ).order_by(desc(TrendData.analysis_date)).first()

            return {
                "task_info": task.to_dict(),
                "total_executions": total_histories,
                "successful_executions": successful_histories,
                "success_rate": successful_histories / total_histories if total_histories > 0 else 0,
                "average_trend_score": float(avg_trend_score) if avg_trend_score else 0.0,
                "latest_trend_data": latest_trend.to_dict() if latest_trend else None,
                "uptime_days": (datetime.now() - task.created_at).days if task.created_at else 0
            }

    @staticmethod
    def get_user_statistics(user_id: str) -> Dict[str, Any]:
        """获取用户统计信息"""
        with SessionLocal() as db:
            total_tasks = db.query(ScheduledTask).filter(ScheduledTask.user_id == user_id).count()
            active_tasks = db.query(ScheduledTask).filter(
                and_(ScheduledTask.user_id == user_id, ScheduledTask.is_active == True)
            ).count()

            # 获取总执行次数
            total_executions = db.query(func.sum(ScheduledTask.total_runs)).filter(
                ScheduledTask.user_id == user_id
            ).scalar() or 0

            # 获取成功执行次数
            successful_executions = db.query(func.sum(ScheduledTask.success_runs)).filter(
                ScheduledTask.user_id == user_id
            ).scalar() or 0

            return {
                "total_tasks": total_tasks,
                "active_tasks": active_tasks,
                "inactive_tasks": total_tasks - active_tasks,
                "total_executions": int(total_executions),
                "successful_executions": int(successful_executions),
                "overall_success_rate": successful_executions / total_executions if total_executions > 0 else 0
            }
