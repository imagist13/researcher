"""
定时研究API路由
Scheduled Research API Routes
"""
import logging
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.responses import JSONResponse

from ..database import (
    ScheduledTaskDAO, ResearchHistoryDAO, TrendDataDAO, 
    TaskExecutionLogDAO, AnalyticsDAO
)
from ..scheduled_research import ScheduledResearchManager, initialize_scheduler
from .api_models import (
    CreateScheduledTaskRequest, UpdateScheduledTaskRequest, TestTaskConfigRequest,
    ScheduledTaskResponse, ResearchHistoryResponse, TrendDataResponse,
    TaskStatisticsResponse, UserStatisticsResponse, SchedulerStatusResponse,
    ApiResponse, PaginatedResponse, TaskExecutionResponse, TestConfigResponse
)

logger = logging.getLogger(__name__)

# 创建路由器
router = APIRouter(prefix="/api/scheduled", tags=["scheduled-research"])

# 全局调度器管理器实例
_scheduler_manager = None

async def get_scheduler_manager() -> ScheduledResearchManager:
    """获取调度器管理器实例"""
    global _scheduler_manager
    if _scheduler_manager is None:
        _scheduler_manager = await initialize_scheduler()
    return _scheduler_manager


# 任务管理端点
@router.post("/tasks", response_model=ApiResponse)
async def create_scheduled_task(
    request: CreateScheduledTaskRequest,
    manager: ScheduledResearchManager = Depends(get_scheduler_manager)
):
    """创建新的定时任务"""
    try:
        logger.info(f"Creating scheduled task: {request.topic}")
        
        # 转换请求数据
        task_data = request.model_dump()
        
        # 创建任务
        task_id = await manager.add_task(task_data)
        
        # 获取创建的任务详情
        task = ScheduledTaskDAO.get_task_by_id(task_id)
        
        return ApiResponse(
            success=True,
            message="定时任务创建成功",
            data=ScheduledTaskResponse.model_validate(task.to_dict())
        )
        
    except Exception as e:
        logger.error(f"Failed to create scheduled task: {e}")
        raise HTTPException(status_code=500, detail=f"创建定时任务失败: {str(e)}")


@router.get("/tasks", response_model=PaginatedResponse)
async def get_scheduled_tasks(
    user_id: str = Query("default_user", description="用户ID"),
    active_only: bool = Query(False, description="仅获取激活的任务"),
    page: int = Query(1, description="页码", ge=1),
    per_page: int = Query(20, description="每页数量", ge=1, le=100)
):
    """获取定时任务列表"""
    try:
        logger.info(f"Getting scheduled tasks for user: {user_id}")
        
        # 获取任务列表
        tasks = ScheduledTaskDAO.get_tasks_by_user(user_id, active_only)
        
        # 分页处理
        total = len(tasks)
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_tasks = tasks[start_idx:end_idx]
        
        # 转换为响应格式
        task_responses = [
            ScheduledTaskResponse.model_validate(task.to_dict()) 
            for task in paginated_tasks
        ]
        
        return PaginatedResponse(
            items=task_responses,
            total=total,
            page=page,
            per_page=per_page,
            total_pages=(total + per_page - 1) // per_page
        )
        
    except Exception as e:
        logger.error(f"Failed to get scheduled tasks: {e}")
        raise HTTPException(status_code=500, detail=f"获取任务列表失败: {str(e)}")


@router.get("/tasks/{task_id}", response_model=ApiResponse)
async def get_scheduled_task(task_id: str):
    """获取单个定时任务详情"""
    try:
        task = ScheduledTaskDAO.get_task_by_id(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="任务不存在")
        
        return ApiResponse(
            success=True,
            message="获取任务详情成功",
            data=ScheduledTaskResponse.model_validate(task.to_dict())
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get scheduled task: {e}")
        raise HTTPException(status_code=500, detail=f"获取任务详情失败: {str(e)}")


@router.put("/tasks/{task_id}", response_model=ApiResponse)
async def update_scheduled_task(
    task_id: str,
    request: UpdateScheduledTaskRequest,
    manager: ScheduledResearchManager = Depends(get_scheduler_manager)
):
    """更新定时任务"""
    try:
        logger.info(f"Updating scheduled task: {task_id}")
        
        # 只包含非None的字段
        update_data = {k: v for k, v in request.model_dump().items() if v is not None}
        
        # 更新任务
        success = await manager.update_task(task_id, update_data)
        if not success:
            raise HTTPException(status_code=404, detail="任务不存在")
        
        # 获取更新后的任务
        task = ScheduledTaskDAO.get_task_by_id(task_id)
        
        return ApiResponse(
            success=True,
            message="任务更新成功",
            data=ScheduledTaskResponse.model_validate(task.to_dict())
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update scheduled task: {e}")
        raise HTTPException(status_code=500, detail=f"更新任务失败: {str(e)}")


@router.delete("/tasks/{task_id}", response_model=ApiResponse)
async def delete_scheduled_task(
    task_id: str,
    manager: ScheduledResearchManager = Depends(get_scheduler_manager)
):
    """删除定时任务"""
    try:
        logger.info(f"Deleting scheduled task: {task_id}")
        
        success = await manager.remove_task(task_id)
        if not success:
            raise HTTPException(status_code=404, detail="任务不存在")
        
        return ApiResponse(
            success=True,
            message="任务删除成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete scheduled task: {e}")
        raise HTTPException(status_code=500, detail=f"删除任务失败: {str(e)}")


# 任务控制端点
@router.post("/tasks/{task_id}/pause", response_model=ApiResponse)
async def pause_scheduled_task(
    task_id: str,
    manager: ScheduledResearchManager = Depends(get_scheduler_manager)
):
    """暂停定时任务"""
    try:
        success = await manager.pause_task(task_id)
        if not success:
            raise HTTPException(status_code=404, detail="任务不存在")
        
        return ApiResponse(
            success=True,
            message="任务已暂停"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to pause scheduled task: {e}")
        raise HTTPException(status_code=500, detail=f"暂停任务失败: {str(e)}")


@router.post("/tasks/{task_id}/resume", response_model=ApiResponse)
async def resume_scheduled_task(
    task_id: str,
    manager: ScheduledResearchManager = Depends(get_scheduler_manager)
):
    """恢复定时任务"""
    try:
        success = await manager.resume_task(task_id)
        if not success:
            raise HTTPException(status_code=404, detail="任务不存在")
        
        return ApiResponse(
            success=True,
            message="任务已恢复"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to resume scheduled task: {e}")
        raise HTTPException(status_code=500, detail=f"恢复任务失败: {str(e)}")


@router.post("/tasks/{task_id}/trigger", response_model=ApiResponse)
async def trigger_task_now(
    task_id: str,
    quick_mode: bool = Query(False, description="是否使用快速模式"),
    manager: ScheduledResearchManager = Depends(get_scheduler_manager)
):
    """立即触发任务执行"""
    try:
        success = await manager.trigger_task_now(task_id, quick_mode=quick_mode)
        if not success:
            raise HTTPException(status_code=404, detail="任务不存在")
        
        message = "任务已触发快速执行" if quick_mode else "任务已触发执行"
        return ApiResponse(
            success=True,
            message=message,
            data={"quick_mode": quick_mode, "task_id": task_id}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to trigger scheduled task: {e}")
        raise HTTPException(status_code=500, detail=f"触发任务失败: {str(e)}")


@router.get("/system/performance", response_model=ApiResponse)
async def get_system_performance(
    manager: ScheduledResearchManager = Depends(get_scheduler_manager)
):
    """获取系统性能状态"""
    try:
        scheduler_status = manager.get_scheduler_status()
        quick_executor_status = await manager.quick_executor.get_system_status()
        
        return ApiResponse(
            success=True,
            message="系统状态获取成功",
            data={
                "scheduler": scheduler_status,
                "quick_executor": quick_executor_status,
                "timestamp": datetime.now().isoformat()
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to get system performance: {e}")
        raise HTTPException(status_code=500, detail=f"获取系统状态失败: {str(e)}")


# 历史记录和趋势分析端点
@router.get("/tasks/{task_id}/history", response_model=PaginatedResponse)
async def get_task_history(
    task_id: str,
    page: int = Query(1, description="页码", ge=1),
    per_page: int = Query(10, description="每页数量", ge=1, le=50)
):
    """获取任务执行历史"""
    try:
        # 验证任务存在
        task = ScheduledTaskDAO.get_task_by_id(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="任务不存在")
        
        # 获取历史记录
        histories = ResearchHistoryDAO.get_history_by_task(task_id, limit=per_page * 10)
        
        # 分页处理
        total = len(histories)
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_histories = histories[start_idx:end_idx]
        
        # 转换为响应格式
        history_responses = [
            ResearchHistoryResponse.model_validate(history.to_dict())
            for history in paginated_histories
        ]
        
        return PaginatedResponse(
            items=history_responses,
            total=total,
            page=page,
            per_page=per_page,
            total_pages=(total + per_page - 1) // per_page
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get task history: {e}")
        raise HTTPException(status_code=500, detail=f"获取历史记录失败: {str(e)}")


@router.get("/tasks/{task_id}/trends", response_model=PaginatedResponse)
async def get_task_trends(
    task_id: str,
    days: int = Query(30, description="获取最近几天的趋势数据", ge=1, le=365),
    page: int = Query(1, description="页码", ge=1),
    per_page: int = Query(10, description="每页数量", ge=1, le=50)
):
    """获取任务趋势分析数据"""
    try:
        # 验证任务存在
        task = ScheduledTaskDAO.get_task_by_id(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="任务不存在")
        
        # 获取趋势数据
        trends = TrendDataDAO.get_trend_data_by_period(task_id, days)
        
        # 分页处理
        total = len(trends)
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_trends = trends[start_idx:end_idx]
        
        # 转换为响应格式
        trend_responses = [
            TrendDataResponse.model_validate(trend.to_dict())
            for trend in paginated_trends
        ]
        
        return PaginatedResponse(
            items=trend_responses,
            total=total,
            page=page,
            per_page=per_page,
            total_pages=(total + per_page - 1) // per_page
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get task trends: {e}")
        raise HTTPException(status_code=500, detail=f"获取趋势数据失败: {str(e)}")


# 统计和分析端点
@router.get("/tasks/{task_id}/statistics", response_model=TaskStatisticsResponse)
async def get_task_statistics(task_id: str):
    """获取任务统计信息"""
    try:
        # 验证任务存在
        task = ScheduledTaskDAO.get_task_by_id(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="任务不存在")
        
        # 获取统计数据
        stats = AnalyticsDAO.get_task_statistics(task_id)
        
        return TaskStatisticsResponse.model_validate(stats)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get task statistics: {e}")
        raise HTTPException(status_code=500, detail=f"获取任务统计失败: {str(e)}")


@router.get("/users/{user_id}/statistics", response_model=UserStatisticsResponse)
async def get_user_statistics(user_id: str = "default_user"):
    """获取用户统计信息"""
    try:
        stats = AnalyticsDAO.get_user_statistics(user_id)
        return UserStatisticsResponse.model_validate(stats)
        
    except Exception as e:
        logger.error(f"Failed to get user statistics: {e}")
        raise HTTPException(status_code=500, detail=f"获取用户统计失败: {str(e)}")


@router.get("/scheduler/status", response_model=SchedulerStatusResponse)
async def get_scheduler_status(
    manager: ScheduledResearchManager = Depends(get_scheduler_manager)
):
    """获取调度器状态"""
    try:
        status = manager.get_scheduler_status()
        return SchedulerStatusResponse.model_validate(status)
        
    except Exception as e:
        logger.error(f"Failed to get scheduler status: {e}")
        raise HTTPException(status_code=500, detail=f"获取调度器状态失败: {str(e)}")


# 测试和配置端点
@router.post("/test-config", response_model=TestConfigResponse)
async def test_task_configuration(request: TestTaskConfigRequest):
    """测试任务配置"""
    try:
        from ..scheduled_research.task_executor import ResearchTaskExecutor
        
        executor = ResearchTaskExecutor()
        test_data = request.model_dump()
        
        # 执行配置测试
        result = await executor.test_research_configuration(test_data)
        
        return TestConfigResponse.model_validate(result)
        
    except Exception as e:
        logger.error(f"Failed to test task configuration: {e}")
        raise HTTPException(status_code=500, detail=f"测试配置失败: {str(e)}")


@router.get("/health", response_model=ApiResponse)
async def health_check():
    """健康检查端点"""
    try:
        from ..database import check_database_connection
        
        # 检查数据库连接
        db_healthy = check_database_connection()
        
        # 检查调度器状态
        scheduler_healthy = True
        try:
            manager = await get_scheduler_manager()
            status = manager.get_scheduler_status()
            scheduler_healthy = status["running"]
        except Exception:
            scheduler_healthy = False
        
        health_status = {
            "database": "healthy" if db_healthy else "unhealthy",
            "scheduler": "healthy" if scheduler_healthy else "unhealthy",
            "overall": "healthy" if (db_healthy and scheduler_healthy) else "unhealthy"
        }
        
        return ApiResponse(
            success=db_healthy and scheduler_healthy,
            message="健康检查完成",
            data=health_status
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return ApiResponse(
            success=False,
            message=f"健康检查失败: {str(e)}",
            data={"overall": "unhealthy"}
        )
