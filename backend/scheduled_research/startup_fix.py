"""
启动时自动修复模块
Startup Auto-Fix Module

在系统启动时自动检查和修复定时任务问题
"""

import logging
import asyncio
from datetime import datetime
from typing import Dict, Any

from .scheduler_fix import patch_scheduler_manager, diagnose_scheduler_issues

logger = logging.getLogger(__name__)


async def apply_startup_fixes(scheduler_manager) -> Dict[str, Any]:
    """
    应用启动时修复
    
    Args:
        scheduler_manager: 调度器管理器实例
    
    Returns:
        修复结果字典
    """
    fix_results = {
        "timestamp": datetime.now().isoformat(),
        "patches_applied": False,
        "diagnosis_ran": False,
        "issues_found": 0,
        "fixes_applied": 0,
        "success": False,
        "details": []
    }
    
    try:
        logger.info("🔧 Applying startup fixes for scheduled tasks...")
        
        # 1. 应用补丁
        scheduler_manager = patch_scheduler_manager(scheduler_manager)
        fix_results["patches_applied"] = True
        fix_results["details"].append("Scheduler patches applied successfully")
        logger.info("✅ Scheduler patches applied")
        
        # 2. 运行诊断
        diagnosis = await diagnose_scheduler_issues(scheduler_manager)
        fix_results["diagnosis_ran"] = True
        fix_results["issues_found"] = len(diagnosis.get("issues", []))
        
        if diagnosis.get("issues"):
            logger.warning(f"⚠️  Found {len(diagnosis['issues'])} issues during startup diagnosis")
            
            # 3. 自动修复常见问题
            if hasattr(scheduler_manager, 'health_checker'):
                try:
                    health_result = await scheduler_manager.health_checker.check_and_fix_paused_tasks()
                    fix_results["fixes_applied"] = health_result.get("fixed_tasks", 0)
                    fix_results["details"].append(f"Auto-fixed {fix_results['fixes_applied']} tasks")
                    logger.info(f"✅ Auto-fixed {fix_results['fixes_applied']} tasks")
                    
                except Exception as e:
                    logger.error(f"❌ Auto-fix failed: {e}")
                    fix_results["details"].append(f"Auto-fix failed: {str(e)}")
        else:
            logger.info("✅ No issues found during startup diagnosis")
            fix_results["details"].append("No issues found")
        
        fix_results["success"] = True
        logger.info("🎉 Startup fixes completed successfully")
        
    except Exception as e:
        logger.error(f"❌ Startup fixes failed: {e}")
        fix_results["details"].append(f"Startup fixes failed: {str(e)}")
        fix_results["success"] = False
    
    return fix_results


def setup_startup_fixes(scheduler_manager):
    """
    设置启动时自动修复
    
    Args:
        scheduler_manager: 调度器管理器实例
    """
    
    # 保存原始的初始化方法
    original_initialize = scheduler_manager.initialize
    
    async def enhanced_initialize():
        """增强的初始化方法，包含自动修复"""
        try:
            # 先执行原始初始化
            await original_initialize()
            
            # 然后应用启动修复
            fix_results = await apply_startup_fixes(scheduler_manager)
            
            # 记录修复结果
            if fix_results["success"]:
                logger.info("🎉 Enhanced initialization completed successfully")
            else:
                logger.warning("⚠️  Enhanced initialization completed with issues")
            
            return fix_results
            
        except Exception as e:
            logger.error(f"❌ Enhanced initialization failed: {e}")
            raise
    
    # 替换初始化方法
    scheduler_manager.initialize = enhanced_initialize
    
    logger.info("🔧 Startup fixes configured")
    return scheduler_manager
