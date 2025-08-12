#!/usr/bin/env python3
"""
GPT Researcher 配置管理器
=========================

这个模块提供了统一的配置管理功能，支持YAML格式的配置文件，
替代原来混乱的.env文件配置方式。

功能：
- 加载YAML配置文件
- 环境变量覆盖
- 配置验证
- 配置热重载
- 类型安全

使用方法：
    from config_manager import ConfigManager
    
    config = ConfigManager()
    api_key = config.get('api.deepseek.api_key')
    
作者: GPT Researcher Team
版本: 2.0.0
"""

import os
import yaml
import logging
from pathlib import Path
from typing import Any, Dict, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class APIConfig:
    """API配置类"""
    deepseek_api_key: str = ""
    openai_api_key: str = ""
    tavily_api_key: str = ""
    google_api_key: str = ""
    google_cx_key: str = ""
    bing_api_key: str = ""
    serper_api_key: str = ""
    serpapi_api_key: str = ""
    searchapi_api_key: str = ""
    searx_url: str = ""


@dataclass
class LLMConfig:
    """LLM模型配置类"""
    fast_model: str = "deepseek:deepseek-chat"
    smart_model: str = "deepseek:deepseek-chat"
    strategic_model: str = "deepseek:deepseek-chat"
    temperature: float = 0.7
    reasoning_effort: str = "medium"


@dataclass
class RetrievalConfig:
    """检索配置类"""
    primary_retriever: str = "duckduckgo"
    max_search_results_per_query: int = 5
    embedding_provider: str = "none"
    embedding_model: str = "none"


@dataclass
class ReportConfig:
    """报告配置类"""
    total_words: int = 1500
    format: str = "APA"
    language: str = "chinese"
    default_source: str = "web"


@dataclass
class PathsConfig:
    """路径配置类"""
    documents: str = "./my-docs"
    outputs: str = "./outputs"
    logs: str = "./logs"


@dataclass
class NetworkConfig:
    """网络配置类"""
    http_proxy: str = ""
    https_proxy: str = ""
    proxy_enabled: bool = False
    connect_timeout: int = 30
    read_timeout: int = 60


@dataclass
class LoggingConfig:
    """日志配置类"""
    level: str = "INFO"
    verbose: bool = False
    fonttools_level: str = "WARNING"
    transformers_level: str = "WARNING"


class ConfigManager:
    """
    统一配置管理器
    
    提供YAML配置文件的加载、验证和访问功能。
    支持环境变量覆盖和配置热重载。
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        初始化配置管理器
        
        Args:
            config_path: 配置文件路径，默认为 'config.yaml'
        """
        self.config_path = config_path or "config.yaml"
        self.config_data: Dict[str, Any] = {}
        self.last_modified: Optional[datetime] = None
        
        # 确保配置文件存在
        self._ensure_config_exists()
        
        # 加载配置
        self.reload_config()
        
        # 设置环境变量
        self._set_environment_variables()
        
        logger.info(f"配置管理器初始化完成，配置文件：{self.config_path}")
    
    def _ensure_config_exists(self) -> None:
        """确保配置文件存在，如果不存在则创建默认配置"""
        config_file = Path(self.config_path)
        
        if not config_file.exists():
            logger.warning(f"配置文件 {self.config_path} 不存在，正在创建默认配置...")
            self._create_default_config()
    
    def _create_default_config(self) -> None:
        """创建默认配置文件"""
        default_config = {
            'api': {
                'deepseek': {'api_key': '', 'enabled': True},
                'openai': {'api_key': '', 'enabled': False},
                'search': {
                    'tavily': {'api_key': '', 'enabled': True},
                    'google': {'api_key': '', 'cx_key': '', 'enabled': False},
                    'bing': {'api_key': '', 'enabled': False},
                }
            },
            'llm': {
                'fast_model': 'deepseek:deepseek-chat',
                'smart_model': 'deepseek:deepseek-chat',
                'strategic_model': 'deepseek:deepseek-chat',
                'temperature': 0.7,
                'reasoning_effort': 'medium'
            },
            'retrieval': {
                'primary_retriever': 'duckduckgo',
                'max_search_results_per_query': 5,
                'embedding': {'provider': 'none', 'model': 'none'}
            },
            'report': {
                'total_words': 1500,
                'format': 'APA',
                'language': 'chinese',
                'default_source': 'web'
            },
            'paths': {
                'documents': './my-docs',
                'outputs': './outputs',
                'logs': './logs'
            },
            'network': {
                'proxy': {'http': '', 'https': '', 'enabled': False},
                'timeout': {'connect': 30, 'read': 60}
            },
            'logging': {
                'level': 'INFO',
                'verbose': False,
                'modules': {'fontTools': 'WARNING', 'transformers': 'WARNING'}
            }
        }
        
        with open(self.config_path, 'w', encoding='utf-8') as f:
            yaml.dump(default_config, f, default_flow_style=False, 
                     allow_unicode=True, sort_keys=False)
        
        logger.info(f"已创建默认配置文件：{self.config_path}")
    
    def reload_config(self) -> None:
        """重新加载配置文件"""
        try:
            config_file = Path(self.config_path)
            
            # 检查文件是否被修改
            if config_file.exists():
                modified_time = datetime.fromtimestamp(config_file.stat().st_mtime)
                if self.last_modified and modified_time <= self.last_modified:
                    return  # 文件没有被修改
                
                self.last_modified = modified_time
            
            # 加载YAML配置
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config_data = yaml.safe_load(f) or {}
            
            # 应用环境变量覆盖
            self._apply_env_overrides()
            
            # 验证配置
            self._validate_config()
            
            logger.info("配置文件重新加载成功")
            
        except Exception as e:
            logger.error(f"加载配置文件失败：{str(e)}")
            raise
    
    def _apply_env_overrides(self) -> None:
        """应用环境变量覆盖"""
        env_mappings = {
            # API密钥映射
            'DEEPSEEK_API_KEY': 'api.deepseek.api_key',
            'OPENAI_API_KEY': 'api.openai.api_key',
            'TAVILY_API_KEY': 'api.search.tavily.api_key',
            'GOOGLE_API_KEY': 'api.search.google.api_key',
            'GOOGLE_CX_KEY': 'api.search.google.cx_key',
            'BING_API_KEY': 'api.search.bing.api_key',
            'SERPER_API_KEY': 'api.search.serper.api_key',
            'SERPAPI_API_KEY': 'api.search.serpapi.api_key',
            'SEARCHAPI_API_KEY': 'api.search.searchapi.api_key',
            'SEARX_URL': 'api.search.searx.url',
            
            # LLM配置映射
            'FAST_LLM': 'llm.fast_model',
            'SMART_LLM': 'llm.smart_model',
            'STRATEGIC_LLM': 'llm.strategic_model',
            'TEMPERATURE': 'llm.temperature',
            'REASONING_EFFORT': 'llm.reasoning_effort',
            
            # 检索配置映射
            'RETRIEVER': 'retrieval.primary_retriever',
            'MAX_SEARCH_RESULTS_PER_QUERY': 'retrieval.max_search_results_per_query',
            'EMBEDDING': 'retrieval.embedding.provider',
            'EMBEDDING_MODEL': 'retrieval.embedding.model',
            
            # 报告配置映射
            'TOTAL_WORDS': 'report.total_words',
            'REPORT_FORMAT': 'report.format',
            'LANGUAGE': 'report.language',
            'REPORT_SOURCE': 'report.default_source',
            
            # 路径配置映射
            'DOC_PATH': 'paths.documents',
            
            # 网络配置映射
            'HTTP_PROXY': 'network.proxy.http',
            'HTTPS_PROXY': 'network.proxy.https',
            
            # 日志配置映射
            'VERBOSE': 'logging.verbose',
        }
        
        for env_var, config_path in env_mappings.items():
            env_value = os.getenv(env_var)
            if env_value is not None:
                self._set_nested_value(config_path, env_value)
    
    def _set_nested_value(self, path: str, value: Any) -> None:
        """设置嵌套配置值"""
        keys = path.split('.')
        current = self.config_data
        
        # 创建嵌套结构
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        # 类型转换
        final_key = keys[-1]
        if isinstance(value, str):
            # 尝试转换布尔值
            if value.lower() in ('true', 'false'):
                value = value.lower() == 'true'
            # 尝试转换数字
            elif value.isdigit():
                value = int(value)
            elif value.replace('.', '').isdigit():
                value = float(value)
        
        current[final_key] = value
    
    def _validate_config(self) -> None:
        """验证配置的有效性"""
        required_sections = ['api', 'llm', 'retrieval', 'report']
        
        for section in required_sections:
            if section not in self.config_data:
                raise ValueError(f"缺少必需的配置段：{section}")
        
        # 验证API密钥
        api_config = self.config_data.get('api', {})
        deepseek_config = api_config.get('deepseek', {})
        
        if deepseek_config.get('enabled', True) and not deepseek_config.get('api_key'):
            logger.warning("DeepSeek API密钥未设置，某些功能可能无法使用")
        
        logger.info("配置验证通过")
    
    def _set_environment_variables(self) -> None:
        """将配置设置为环境变量，以兼容现有代码"""
        mappings = {
            'api.deepseek.api_key': 'DEEPSEEK_API_KEY',
            'api.openai.api_key': 'OPENAI_API_KEY',
            'api.search.tavily.api_key': 'TAVILY_API_KEY',
            'api.search.google.api_key': 'GOOGLE_API_KEY',
            'api.search.google.cx_key': 'GOOGLE_CX_KEY',
            'api.search.bing.api_key': 'BING_API_KEY',
            'api.search.serper.api_key': 'SERPER_API_KEY',
            'api.search.serpapi.api_key': 'SERPAPI_API_KEY',
            'api.search.searchapi.api_key': 'SEARCHAPI_API_KEY',
            'api.search.searx.url': 'SEARX_URL',
            
            'llm.fast_model': 'FAST_LLM',
            'llm.smart_model': 'SMART_LLM',
            'llm.strategic_model': 'STRATEGIC_LLM',
            'llm.temperature': 'TEMPERATURE',
            'llm.reasoning_effort': 'REASONING_EFFORT',
            
            'retrieval.primary_retriever': 'RETRIEVER',
            'retrieval.max_search_results_per_query': 'MAX_SEARCH_RESULTS_PER_QUERY',
            'retrieval.embedding.provider': 'EMBEDDING',
            'retrieval.embedding.model': 'EMBEDDING_MODEL',
            
            'report.total_words': 'TOTAL_WORDS',
            'report.format': 'REPORT_FORMAT',
            'report.language': 'LANGUAGE',
            'report.default_source': 'REPORT_SOURCE',
            
            'paths.documents': 'DOC_PATH',
            
            'network.proxy.http': 'HTTP_PROXY',
            'network.proxy.https': 'HTTPS_PROXY',
            
            'logging.verbose': 'VERBOSE',
        }
        
        for config_path, env_var in mappings.items():
            value = self.get(config_path)
            if value is not None:
                os.environ[env_var] = str(value)
    
    def get(self, path: str, default: Any = None) -> Any:
        """
        获取配置值
        
        Args:
            path: 配置路径，用点分隔，如 'api.deepseek.api_key'
            default: 默认值
            
        Returns:
            配置值或默认值
        """
        keys = path.split('.')
        current = self.config_data
        
        try:
            for key in keys:
                current = current[key]
            return current
        except (KeyError, TypeError):
            return default
    
    def set(self, path: str, value: Any) -> None:
        """
        设置配置值
        
        Args:
            path: 配置路径
            value: 配置值
        """
        self._set_nested_value(path, value)
        
        # 同时更新对应的环境变量
        env_mappings = {
            'api.deepseek.api_key': 'DEEPSEEK_API_KEY',
            'api.openai.api_key': 'OPENAI_API_KEY',
            'retrieval.primary_retriever': 'RETRIEVER',
            # ... 可以添加更多映射
        }
        
        if path in env_mappings:
            os.environ[env_mappings[path]] = str(value)
    
    def get_api_config(self) -> APIConfig:
        """获取API配置对象"""
        return APIConfig(
            deepseek_api_key=self.get('api.deepseek.api_key', ''),
            openai_api_key=self.get('api.openai.api_key', ''),
            tavily_api_key=self.get('api.search.tavily.api_key', ''),
            google_api_key=self.get('api.search.google.api_key', ''),
            google_cx_key=self.get('api.search.google.cx_key', ''),
            bing_api_key=self.get('api.search.bing.api_key', ''),
            serper_api_key=self.get('api.search.serper.api_key', ''),
            serpapi_api_key=self.get('api.search.serpapi.api_key', ''),
            searchapi_api_key=self.get('api.search.searchapi.api_key', ''),
            searx_url=self.get('api.search.searx.url', ''),
        )
    
    def get_llm_config(self) -> LLMConfig:
        """获取LLM配置对象"""
        return LLMConfig(
            fast_model=self.get('llm.fast_model', 'deepseek:deepseek-chat'),
            smart_model=self.get('llm.smart_model', 'deepseek:deepseek-chat'),
            strategic_model=self.get('llm.strategic_model', 'deepseek:deepseek-chat'),
            temperature=self.get('llm.temperature', 0.7),
            reasoning_effort=self.get('llm.reasoning_effort', 'medium'),
        )
    
    def get_retrieval_config(self) -> RetrievalConfig:
        """获取检索配置对象"""
        return RetrievalConfig(
            primary_retriever=self.get('retrieval.primary_retriever', 'duckduckgo'),
            max_search_results_per_query=self.get('retrieval.max_search_results_per_query', 5),
            embedding_provider=self.get('retrieval.embedding.provider', 'none'),
            embedding_model=self.get('retrieval.embedding.model', 'none'),
        )
    
    def is_api_enabled(self, api_name: str) -> bool:
        """检查指定API是否启用"""
        return self.get(f'api.{api_name}.enabled', False)
    
    def has_api_key(self, api_name: str) -> bool:
        """检查指定API是否有密钥"""
        api_key = self.get(f'api.{api_name}.api_key', '')
        return bool(api_key and api_key.strip())
    
    def save_config(self) -> None:
        """保存当前配置到文件"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.config_data, f, default_flow_style=False, 
                         allow_unicode=True, sort_keys=False)
            logger.info("配置文件保存成功")
        except Exception as e:
            logger.error(f"保存配置文件失败：{str(e)}")
            raise
    
    def get_all_config(self) -> Dict[str, Any]:
        """获取所有配置数据"""
        return self.config_data.copy()
    
    def __str__(self) -> str:
        """字符串表示"""
        return f"ConfigManager(config_path='{self.config_path}')"
    
    def __repr__(self) -> str:
        """详细字符串表示"""
        return f"ConfigManager(config_path='{self.config_path}', sections={list(self.config_data.keys())})"


# 全局配置实例
_config_manager: Optional[ConfigManager] = None


def get_config_manager(config_path: Optional[str] = None) -> ConfigManager:
    """
    获取全局配置管理器实例
    
    Args:
        config_path: 配置文件路径
        
    Returns:
        ConfigManager实例
    """
    global _config_manager
    
    if _config_manager is None or config_path:
        _config_manager = ConfigManager(config_path)
    
    return _config_manager


# 便捷函数
def get_config(path: str, default: Any = None) -> Any:
    """获取配置值的便捷函数"""
    return get_config_manager().get(path, default)


def set_config(path: str, value: Any) -> None:
    """设置配置值的便捷函数"""
    get_config_manager().set(path, value)


if __name__ == "__main__":
    # 测试代码
    logging.basicConfig(level=logging.INFO)
    
    print("=== 配置管理器测试 ===")
    
    # 创建配置管理器
    config = ConfigManager()
    
    # 测试配置获取
    print(f"DeepSeek API Key: {config.get('api.deepseek.api_key', 'NOT_SET')}")
    print(f"Primary Retriever: {config.get('retrieval.primary_retriever')}")
    print(f"Report Language: {config.get('report.language')}")
    
    # 测试配置对象
    api_config = config.get_api_config()
    llm_config = config.get_llm_config()
    
    print(f"API配置: {api_config}")
    print(f"LLM配置: {llm_config}")
    
    print("=== 测试完成 ===")
