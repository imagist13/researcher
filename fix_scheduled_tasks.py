#!/usr/bin/env python3
"""
定时任务修复工具
Scheduled Tasks Fix Tool

这个工具可以诊断和修复定时任务的各种问题，包括：
1. 暂停后无法恢复的任务
2. 调度器与数据库状态不一致
3. 丢失的任务
4. 重复的任务

使用方法：
    python fix_scheduled_tasks.py [options]
"""

import asyncio
import logging
import argparse
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from backend.database import init_database, ScheduledTaskDAO
from backend.scheduled_research import get_scheduler_manager, initialize_scheduler
from backend.scheduled_research.scheduler_fix import (
    patch_scheduler_manager, 
    diagnose_scheduler_issues,
    ImprovedSchedulerManager
)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ScheduledTasksDoctor:
    """定时任务医生 - 诊断和修复工具"""
    
    def __init__(self):
        self.scheduler_manager = None
        self.enhanced_manager = None
    
    async def initialize(self):
        """初始化工具"""
        try:
            # 初始化数据库
            init_database()
            logger.info("✅ Database initialized")
            
            # 初始化调度器
            self.scheduler_manager = await initialize_scheduler()
            logger.info("✅ Scheduler initialized")
            
            # 应用补丁
            self.scheduler_manager = patch_scheduler_manager(self.scheduler_manager)
            logger.info("✅ Scheduler patches applied")
            
        except Exception as e:
            logger.error(f"❌ Initialization failed: {e}")
            raise
    
    async def diagnose(self) -> Dict[str, Any]:
        """诊断问题"""
        logger.info("🔍 Diagnosing scheduled tasks...")
        
        try:
            # 运行诊断
            diagnosis = await diagnose_scheduler_issues(self.scheduler_manager)
            
            # 打印诊断结果
            print("\n" + "="*60)
            print("🏥 定时任务诊断报告")
            print("="*60)
            print(f"诊断时间: {diagnosis['timestamp']}")
            print(f"调度器运行状态: {'✅ 运行中' if diagnosis['scheduler_running'] else '❌ 停止'}")
            print(f"调度器中的任务数: {diagnosis['total_jobs']}")
            print(f"数据库中活跃任务数: {diagnosis['active_tasks_in_db']}")
            print(f"数据库中暂停任务数: {diagnosis['inactive_tasks_in_db']}")
            
            if diagnosis['issues']:
                print(f"\n⚠️  发现 {len(diagnosis['issues'])} 个问题:")
                for i, issue in enumerate(diagnosis['issues'], 1):
                    print(f"  {i}. [{issue['type']}] {issue['description']}")
                    if 'task_id' in issue:
                        print(f"     任务ID: {issue['task_id']}")
                    if 'topic' in issue:
                        print(f"     主题: {issue['topic']}")
            else:
                print("\n✅ 未发现问题")
            
            if diagnosis['recommendations']:
                print(f"\n💡 建议:")
                for i, rec in enumerate(diagnosis['recommendations'], 1):
                    print(f"  {i}. {rec}")
            
            print("="*60)
            
            return diagnosis
            
        except Exception as e:
            logger.error(f"❌ Diagnosis failed: {e}")
            raise
    
    async def fix_all(self) -> Dict[str, Any]:
        """修复所有问题"""
        logger.info("🔧 Fixing all issues...")
        
        try:
            # 先诊断问题
            diagnosis = await self.diagnose()
            
            if not diagnosis['issues']:
                print("✅ 未发现需要修复的问题")
                return {"status": "no_issues"}
            
            # 执行自动修复
            print("\n🔧 开始修复...")
            
            # 1. 运行健康检查和修复
            health_result = await self.scheduler_manager.health_checker.check_and_fix_paused_tasks()
            
            # 2. 强制重新同步所有任务
            resync_result = await self.scheduler_manager.force_resync_all_tasks()
            
            print(f"\n✅ 修复完成:")
            print(f"  - 检查任务数: {health_result['checked_tasks']}")
            print(f"  - 修复任务数: {health_result['fixed_tasks']}")
            print(f"  - 失败任务数: {health_result['failed_tasks']}")
            print(f"  - 重新调度任务数: {resync_result['successfully_scheduled']}")
            
            # 再次诊断验证修复结果
            print("\n🔍 验证修复结果...")
            post_fix_diagnosis = await diagnose_scheduler_issues(self.scheduler_manager)
            
            if post_fix_diagnosis['issues']:
                print(f"⚠️  仍有 {len(post_fix_diagnosis['issues'])} 个问题未解决")
                for issue in post_fix_diagnosis['issues']:
                    print(f"  - {issue['description']}")
            else:
                print("✅ 所有问题已修复")
            
            return {
                "status": "completed",
                "health_result": health_result,
                "resync_result": resync_result,
                "remaining_issues": len(post_fix_diagnosis['issues'])
            }
            
        except Exception as e:
            logger.error(f"❌ Fix failed: {e}")
            raise
    
    async def list_tasks(self):
        """列出所有任务"""
        logger.info("📋 Listing all scheduled tasks...")
        
        try:
            # 获取所有任务
            all_tasks = ScheduledTaskDAO.get_tasks_by_user("default_user")
            
            print("\n" + "="*80)
            print("📋 定时任务列表")
            print("="*80)
            
            if not all_tasks:
                print("未找到任何定时任务")
                return
            
            for i, task in enumerate(all_tasks, 1):
                status = "✅ 活跃" if task.is_active else "⏸️ 暂停"
                job_id = f"research_task_{task.id}"
                job = self.scheduler_manager.scheduler.get_job(job_id)
                scheduler_status = "✅ 已调度" if job else "❌ 未调度"
                
                print(f"\n{i}. 【{status}】 {task.topic}")
                print(f"   ID: {task.id}")
                print(f"   创建时间: {task.created_at}")
                print(f"   间隔: {task.interval_hours} 小时")
                print(f"   下次执行: {task.next_run}")
                print(f"   调度器状态: {scheduler_status}")
                print(f"   执行统计: 总计 {task.total_runs} 次，成功 {task.success_runs} 次")
                
                if not task.is_active and job:
                    print("   ⚠️  警告: 任务已暂停但仍在调度器中")
                elif task.is_active and not job:
                    print("   ⚠️  警告: 任务已激活但不在调度器中")
            
            print("="*80)
            
        except Exception as e:
            logger.error(f"❌ List tasks failed: {e}")
            raise
    
    async def force_resume_all_paused(self):
        """强制恢复所有暂停的任务"""
        logger.info("🔄 Force resuming all paused tasks...")
        
        try:
            # 获取所有暂停的任务
            all_tasks = ScheduledTaskDAO.get_tasks_by_user("default_user")
            paused_tasks = [t for t in all_tasks if not t.is_active]
            
            if not paused_tasks:
                print("✅ 未找到暂停的任务")
                return
            
            print(f"🔄 找到 {len(paused_tasks)} 个暂停的任务，开始恢复...")
            
            resumed_count = 0
            failed_count = 0
            
            for task in paused_tasks:
                try:
                    success = await self.scheduler_manager.resume_task(task.id)
                    if success:
                        resumed_count += 1
                        print(f"  ✅ 恢复成功: {task.topic}")
                    else:
                        failed_count += 1
                        print(f"  ❌ 恢复失败: {task.topic}")
                except Exception as e:
                    failed_count += 1
                    print(f"  ❌ 恢复失败: {task.topic} - {str(e)}")
            
            print(f"\n📊 恢复结果: 成功 {resumed_count} 个，失败 {failed_count} 个")
            
        except Exception as e:
            logger.error(f"❌ Force resume failed: {e}")
            raise
    
    async def cleanup_orphaned_jobs(self):
        """清理孤立的调度器任务"""
        logger.info("🧹 Cleaning up orphaned scheduler jobs...")
        
        try:
            jobs = self.scheduler_manager.scheduler.get_jobs()
            research_jobs = [job for job in jobs if job.id.startswith("research_task_")]
            
            if not research_jobs:
                print("✅ 未找到研究相关的调度器任务")
                return
            
            print(f"🧹 检查 {len(research_jobs)} 个调度器任务...")
            
            removed_count = 0
            
            for job in research_jobs:
                task_id = job.id.replace("research_task_", "")
                task = ScheduledTaskDAO.get_task_by_id(task_id)
                
                if not task:
                    # 孤立的job，没有对应的数据库记录
                    self.scheduler_manager.scheduler.remove_job(job.id)
                    removed_count += 1
                    print(f"  🗑️  删除孤立任务: {job.id}")
            
            print(f"📊 清理结果: 删除 {removed_count} 个孤立任务")
            
        except Exception as e:
            logger.error(f"❌ Cleanup failed: {e}")
            raise
    
    async def shutdown(self):
        """关闭工具"""
        if self.scheduler_manager:
            await self.scheduler_manager.shutdown()
            logger.info("✅ Scheduler shutdown")


async def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="定时任务修复工具")
    parser.add_argument("command", choices=[
        "diagnose", "fix", "list", "resume-all", "cleanup"
    ], help="执行的命令")
    
    args = parser.parse_args()
    
    doctor = ScheduledTasksDoctor()
    
    try:
        await doctor.initialize()
        
        if args.command == "diagnose":
            await doctor.diagnose()
        elif args.command == "fix":
            await doctor.fix_all()
        elif args.command == "list":
            await doctor.list_tasks()
        elif args.command == "resume-all":
            await doctor.force_resume_all_paused()
        elif args.command == "cleanup":
            await doctor.cleanup_orphaned_jobs()
            
    except KeyboardInterrupt:
        print("\n⏹️  操作已取消")
    except Exception as e:
        logger.error(f"❌ 执行失败: {e}")
        sys.exit(1)
    finally:
        await doctor.shutdown()


if __name__ == "__main__":
    print("🏥 定时任务修复工具 v1.0")
    print("用途：诊断和修复定时任务暂停后无法恢复的问题\n")
    
    asyncio.run(main())
