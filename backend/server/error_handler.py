"""
错误处理工具模块
Error handling utilities for API errors
"""
import re
from typing import Dict, Tuple
from .content_safety import ContentSafetyChecker


def classify_api_error(error_message: str) -> Tuple[str, str, list]:
    """
    分类API错误并提供对应的解决方案
    Classify API errors and provide corresponding solutions
    
    Args:
        error_message: 原始错误信息
        
    Returns:
        Tuple[用户友好的错误信息, 错误类型, 解决方案列表]
    """
    error_message_lower = error_message.lower()
    
    # DeepSeek API特定错误
    if "content exists risk" in error_message_lower:
        return (
            "内容安全检查失败：搜索内容可能包含敏感信息",
            "content_safety",
            [
                "尝试使用更中性的搜索关键词",
                "避免政治、宗教、暴力等敏感话题",
                "使用学术或技术相关的术语",
                "考虑将复合查询拆分为简单查询",
                "推荐安全话题：科技发展趋势、学术研究进展、商业模式创新"
            ]
        )
    
    # 认证相关错误
    elif any(keyword in error_message_lower for keyword in ["authentication", "api key", "unauthorized", "401"]):
        return (
            "API密钥验证失败",
            "authentication",
            [
                "检查 .env 文件中的 DEEPSEEK_API_KEY 是否正确",
                "确认API密钥没有过期",
                "检查API密钥格式（应以 sk- 开头）",
                "重新生成API密钥"
            ]
        )
    
    # 频率限制错误
    elif any(keyword in error_message_lower for keyword in ["rate limit", "quota", "429"]):
        return (
            "API请求频率限制",
            "rate_limit",
            [
                "等待几分钟后重试",
                "检查API账户的使用配额",
                "考虑升级API计划",
                "减少并发请求数量"
            ]
        )
    
    # 请求格式错误
    elif any(keyword in error_message_lower for keyword in ["invalid_request", "bad request", "400"]):
        return (
            "API请求格式错误",
            "invalid_request",
            [
                "检查请求参数格式",
                "确认模型名称配置正确",
                "验证请求数据结构",
                "查看API文档确认正确用法"
            ]
        )
    
    # 网络连接错误
    elif any(keyword in error_message_lower for keyword in ["connection", "timeout", "network", "dns"]):
        return (
            "网络连接问题",
            "network",
            [
                "检查网络连接状态",
                "确认是否需要代理设置",
                "尝试重新连接",
                "检查防火墙设置"
            ]
        )
    
    # 服务器错误
    elif any(keyword in error_message_lower for keyword in ["500", "502", "503", "internal server"]):
        return (
            "服务器内部错误",
            "server_error",
            [
                "稍后重试",
                "检查API服务状态",
                "尝试使用备用端点",
                "联系API提供商"
            ]
        )
    
    # 未知错误
    else:
        return (
            f"未知错误: {error_message[:100]}...",
            "unknown",
            [
                "检查错误日志详情",
                "验证配置文件",
                "尝试重启服务",
                "如问题持续请联系支持"
            ]
        )


def create_error_response(error: Exception, task: str = "", report_type: str = "") -> Dict:
    """
    创建标准化的错误响应
    Create standardized error response
    
    Args:
        error: 异常对象
        task: 任务描述
        report_type: 报告类型
        
    Returns:
        Dict: 错误响应字典
    """
    error_message = str(error)
    friendly_message, error_type, solutions = classify_api_error(error_message)
    
    response = {
        "type": "error",
        "content": friendly_message,
        "error_type": error_type,
        "details": {
            "original_error": error_message,
            "task": task,
            "report_type": report_type,
            "solutions": solutions
        }
    }
    
    # 如果是内容安全错误，添加智能建议
    if error_type == "content_safety" and task:
        try:
            safety_suggestion = ContentSafetyChecker.format_safety_suggestion(task)
            response["details"]["safety_suggestion"] = safety_suggestion
        except Exception as e:
            # 如果安全检查失败，不影响主要错误响应
            pass
    
    return response


def generate_error_report(error: Exception, task: str, report_type: str) -> str:
    """
    生成错误报告文档
    Generate error report document
    
    Args:
        error: 异常对象
        task: 任务描述
        report_type: 报告类型
        
    Returns:
        str: Markdown格式的错误报告
    """
    from datetime import datetime
    
    friendly_message, error_type, solutions = classify_api_error(str(error))
    
    return f"""# 研究任务执行失败报告

## 基本信息
- **任务描述**: {task}
- **报告类型**: {report_type}
- **错误时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **错误类型**: {error_type}

## 错误详情
{friendly_message}

## 技术详情
```
{str(error)}
```

## 建议解决方案
{chr(10).join([f"{i+1}. {solution}" for i, solution in enumerate(solutions)])}

## 常见问题排查
1. **检查网络连接**: 确保能正常访问互联网
2. **验证API配置**: 检查 .env 文件中的API密钥
3. **查看日志**: 检查应用日志获取更多详细信息
4. **重试机制**: 某些错误可能是临时的，可以稍后重试

---
*此报告由GPT-Researcher自动生成*
"""


def should_retry_error(error_message: str, retry_count: int = 0, max_retries: int = 3) -> bool:
    """
    判断是否应该重试该错误
    Determine if the error should be retried
    
    Args:
        error_message: 错误信息
        retry_count: 当前重试次数
        max_retries: 最大重试次数
        
    Returns:
        bool: 是否应该重试
    """
    if retry_count >= max_retries:
        return False
    
    error_message_lower = error_message.lower()
    
    # 这些错误可以重试
    retriable_errors = [
        "timeout",
        "connection",
        "network",
        "500",
        "502", 
        "503",
        "rate limit",
        "quota exceeded"
    ]
    
    # 这些错误不应该重试
    non_retriable_errors = [
        "content exists risk",
        "authentication",
        "unauthorized",
        "invalid_request",
        "400",
        "401",
        "403"
    ]
    
    # 检查不可重试的错误
    if any(keyword in error_message_lower for keyword in non_retriable_errors):
        return False
    
    # 检查可重试的错误
    if any(keyword in error_message_lower for keyword in retriable_errors):
        return True
    
    # 未知错误默认不重试
    return False
