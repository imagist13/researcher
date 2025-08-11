"""
定时研究配置 - 优化性能和资源使用
Scheduled Research Configuration - Optimized for performance and resource usage
"""
import os
from typing import Dict, Any

class ScheduledResearchConfig:
    """定时研究专用配置"""
    
    # 基础性能配置
    BASIC_CONFIG = {
        "MAX_SEARCH_RESULTS_PER_QUERY": 3,
        "MAX_SUBTOPICS": 2,
        "MAX_ITERATIONS": 2,
        "MAX_SCRAPER_WORKERS": 6,
        "TOTAL_WORDS": 600,
        "CURATE_SOURCES": False,
        "VERBOSE": False,
        "TEMPERATURE": 0.3,
        "MEMORY_BACKEND": "local",  # 使用本地内存，避免复杂的向量存储
        "BROWSE_CHUNK_MAX_LENGTH": 3072,
        "SUMMARY_TOKEN_LIMIT": 400,
        "FAST_TOKEN_LIMIT": 2000,
        "SMART_TOKEN_LIMIT": 4000,
    }
    
    # 详细分析配置
    DETAILED_CONFIG = {
        "MAX_SEARCH_RESULTS_PER_QUERY": 5,
        "MAX_SUBTOPICS": 3,
        "MAX_ITERATIONS": 3,
        "MAX_SCRAPER_WORKERS": 8,
        "TOTAL_WORDS": 1000,
        "CURATE_SOURCES": True,
        "VERBOSE": False,
        "MEMORY_BACKEND": "local",
        "BROWSE_CHUNK_MAX_LENGTH": 4096,
        "SUMMARY_TOKEN_LIMIT": 600,
        "TEMPERATURE": 0.4,
        "FAST_TOKEN_LIMIT": 3000,
        "SMART_TOKEN_LIMIT": 5000,
    }
    
    # 深度分析配置
    DEEP_CONFIG = {
        "MAX_SEARCH_RESULTS_PER_QUERY": 7,
        "MAX_SUBTOPICS": 4,
        "MAX_ITERATIONS": 4,
        "MAX_SCRAPER_WORKERS": 10,
        "TOTAL_WORDS": 1500,
        "CURATE_SOURCES": True,
        "VERBOSE": False,
        "MEMORY_BACKEND": "local",
        "BROWSE_CHUNK_MAX_LENGTH": 6144,
        "SUMMARY_TOKEN_LIMIT": 800,
        "TEMPERATURE": 0.4,
        "FAST_TOKEN_LIMIT": 3000,
        "SMART_TOKEN_LIMIT": 6000,
    }
    
    @classmethod
    def get_config_by_depth(cls, analysis_depth: str) -> Dict[str, Any]:
        """根据分析深度获取配置"""
        config_map = {
            "basic": cls.BASIC_CONFIG,
            "detailed": cls.DETAILED_CONFIG,
            "deep": cls.DEEP_CONFIG
        }
        return config_map.get(analysis_depth, cls.BASIC_CONFIG).copy()
    
    @classmethod
    def get_optimized_config(cls, task) -> Dict[str, Any]:
        """获取针对任务优化的配置"""
        base_config = cls.get_config_by_depth(task.analysis_depth)
        
        # 根据任务特性进一步优化
        optimizations = {}
        
        # 语言优化
        if task.language == "zh-CN":
            optimizations["LANGUAGE"] = "chinese"
        else:
            optimizations["LANGUAGE"] = "english"
        
        # 源类型优化
        if task.report_source == "local":
            optimizations["MAX_SCRAPER_WORKERS"] = 2  # 本地文档不需要太多worker
            optimizations["MAX_SEARCH_RESULTS_PER_QUERY"] = 1
        
        # 域名限制优化
        if task.query_domains:
            # 有域名限制时减少并发，避免被限制
            optimizations["MAX_SCRAPER_WORKERS"] = min(base_config["MAX_SCRAPER_WORKERS"], 4)
        
        # 关键词数量优化
        keyword_count = len(task.keywords) if task.keywords else 1
        if keyword_count > 5:
            # 关键词较多时减少子主题数量
            optimizations["MAX_SUBTOPICS"] = max(1, base_config["MAX_SUBTOPICS"] - 1)
        
        # 合并配置
        base_config.update(optimizations)
        return base_config
    
    @classmethod
    def get_timeout_by_depth(cls, analysis_depth: str) -> int:
        """根据分析深度获取超时时间"""
        timeout_map = {
            "basic": 120,      # 2分钟 - 快速分析
            "detailed": 300,   # 5分钟 - 详细分析
            "deep": 600        # 10分钟 - 深度分析
        }
        return timeout_map.get(analysis_depth, 180)
    
    @classmethod
    def get_llm_config(cls, analysis_depth: str) -> Dict[str, Any]:
        """获取LLM配置"""
        if analysis_depth == "basic":
            return {
                "model_preference": "fast",  # 优先使用快速模型
                "max_retries": 2,
                "timeout": 30
            }
        elif analysis_depth == "detailed":
            return {
                "model_preference": "smart",  # 使用智能模型
                "max_retries": 3,
                "timeout": 60
            }
        else:  # deep
            return {
                "model_preference": "smart",  # 深度分析也用智能模型
                "max_retries": 3,
                "timeout": 90
            }
    
    @classmethod
    def get_retriever_config(cls, task) -> Dict[str, Any]:
        """获取检索器配置"""
        config = {
            "max_results": cls.get_config_by_depth(task.analysis_depth)["MAX_SEARCH_RESULTS_PER_QUERY"],
            "timeout": 15,  # 单次搜索超时
            "max_concurrent": 3,  # 最大并发搜索数
        }
        
        # 如果有域名限制，调整检索策略
        if task.query_domains:
            config["domain_specific"] = True
            config["max_concurrent"] = 2  # 减少并发避免被限制
        
        return config

class ScheduledResearchPrompts:
    """定时研究专用提示词"""
    
    @staticmethod
    def generate_trend_research_query(task) -> str:
        """生成趋势研究查询"""
        base_query = task.topic
        keywords = task.keywords or []
        
        # 构建增强的查询
        if task.analysis_depth == "basic":
            # 基础查询 - 简洁明了
            query_parts = [base_query]
            if keywords:
                query_parts.extend(keywords[:3])  # 最多3个关键词
            return " ".join(query_parts)
        
        elif task.analysis_depth == "detailed":
            # 详细查询 - 包含趋势分析要求
            trend_terms = ["趋势", "发展", "变化", "现状", "前景"]
            query_parts = [base_query]
            if keywords:
                query_parts.extend(keywords[:5])
            query_parts.extend(trend_terms[:2])
            return " ".join(query_parts)
        
        else:  # deep
            # 深度查询 - 全面的研究方向
            analysis_terms = ["深度分析", "市场趋势", "技术发展", "未来展望", "影响因素"]
            query_parts = [base_query]
            if keywords:
                query_parts.extend(keywords)
            query_parts.extend(analysis_terms[:3])
            return " ".join(query_parts)
    
    @staticmethod
    def get_research_instructions(task) -> str:
        """获取研究指令"""
        instructions = {
            "basic": f"请对'{task.topic}'进行基础研究分析，重点关注当前状态和主要特点。",
            "detailed": f"请对'{task.topic}'进行详细的趋势分析，包括现状、发展趋势、关键变化和影响因素。",
            "deep": f"请对'{task.topic}'进行深度研究，全面分析其发展历程、当前状态、趋势变化、影响因素、未来展望和相关建议。"
        }
        return instructions.get(task.analysis_depth, instructions["basic"])
    
    @staticmethod
    def get_summary_prompt(task, research_result) -> str:
        """获取摘要生成提示词"""
        return f"""
基于以下研究结果，请生成一个简洁的中文摘要：

研究主题：{task.topic}
关键词：{', '.join(task.keywords or [])}
分析深度：{task.analysis_depth}

研究结果：
{research_result.get('report', '')[:2000]}  # 限制长度避免token超限

请生成一个200-300字的摘要，重点突出：
1. 主要发现
2. 关键趋势
3. 重要变化
4. 核心洞察

摘要应该客观、准确、易于理解。
"""

# 环境变量配置
def get_env_config() -> Dict[str, Any]:
    """从环境变量获取配置"""
    return {
        # API配置
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "TAVILY_API_KEY": os.getenv("TAVILY_API_KEY"),
        "GOOGLE_API_KEY": os.getenv("GOOGLE_API_KEY"),
        "GOOGLE_CX_ID": os.getenv("GOOGLE_CX_ID"),
        
        # 性能配置
        "MAX_CONCURRENT_TASKS": int(os.getenv("MAX_CONCURRENT_SCHEDULED_TASKS", "3")),
        "TASK_TIMEOUT": int(os.getenv("SCHEDULED_TASK_TIMEOUT", "600")),
        "ENABLE_CACHING": os.getenv("ENABLE_RESEARCH_CACHING", "true").lower() == "true",
        
        # 调试配置
        "DEBUG_MODE": os.getenv("DEBUG_SCHEDULED_RESEARCH", "false").lower() == "true",
        "LOG_LEVEL": os.getenv("SCHEDULED_LOG_LEVEL", "INFO"),
    }
