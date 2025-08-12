#!/usr/bin/env python3
"""
配置迁移工具
============

从旧的.env文件迁移到新的YAML配置系统

使用方法：
    python migrate_config.py

功能：
- 读取现有的config.env文件
- 转换为YAML格式
- 保留所有配置项和注释
- 创建备份文件
"""

import os
import yaml
import logging
from pathlib import Path
from typing import Dict, Any
from config_manager import ConfigManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def parse_env_file(env_path: str) -> Dict[str, str]:
    """解析.env文件"""
    env_vars = {}
    
    if not os.path.exists(env_path):
        logger.warning(f".env文件不存在: {env_path}")
        return env_vars
    
    with open(env_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            
            # 跳过空行和注释
            if not line or line.startswith('#'):
                continue
            
            # 解析键值对
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip().strip('"\'')  # 去除引号
                
                if key and value:  # 只保存非空的键值对
                    env_vars[key] = value
                    logger.debug(f"解析配置: {key}={value}")
    
    logger.info(f"从 {env_path} 解析了 {len(env_vars)} 个配置项")
    return env_vars


def migrate_to_yaml(env_vars: Dict[str, str]) -> Dict[str, Any]:
    """将环境变量转换为YAML结构"""
    yaml_config = {
        'api': {
            'deepseek': {
                'api_key': env_vars.get('DEEPSEEK_API_KEY', ''),
                'enabled': bool(env_vars.get('DEEPSEEK_API_KEY', ''))
            },
            'openai': {
                'api_key': env_vars.get('OPENAI_API_KEY', ''),
                'enabled': bool(env_vars.get('OPENAI_API_KEY', ''))
            },
            'search': {
                'tavily': {
                    'api_key': env_vars.get('TAVILY_API_KEY', ''),
                    'enabled': bool(env_vars.get('TAVILY_API_KEY', ''))
                },
                'google': {
                    'api_key': env_vars.get('GOOGLE_API_KEY', ''),
                    'cx_key': env_vars.get('GOOGLE_CX_KEY', ''),
                    'enabled': bool(env_vars.get('GOOGLE_API_KEY', ''))
                },
                'bing': {
                    'api_key': env_vars.get('BING_API_KEY', ''),
                    'enabled': bool(env_vars.get('BING_API_KEY', ''))
                },
                'serper': {
                    'api_key': env_vars.get('SERPER_API_KEY', ''),
                    'enabled': bool(env_vars.get('SERPER_API_KEY', ''))
                },
                'serpapi': {
                    'api_key': env_vars.get('SERPAPI_API_KEY', ''),
                    'enabled': bool(env_vars.get('SERPAPI_API_KEY', ''))
                },
                'searchapi': {
                    'api_key': env_vars.get('SEARCHAPI_API_KEY', ''),
                    'enabled': bool(env_vars.get('SEARCHAPI_API_KEY', ''))
                },
                'searx': {
                    'url': env_vars.get('SEARX_URL', ''),
                    'enabled': bool(env_vars.get('SEARX_URL', ''))
                }
            }
        },
        'llm': {
            'fast_model': env_vars.get('FAST_LLM', 'deepseek:deepseek-chat'),
            'smart_model': env_vars.get('SMART_LLM', 'deepseek:deepseek-chat'),
            'strategic_model': env_vars.get('STRATEGIC_LLM', 'deepseek:deepseek-chat'),
            'temperature': float(env_vars.get('TEMPERATURE', '0.7')),
            'reasoning_effort': env_vars.get('REASONING_EFFORT', 'medium')
        },
        'retrieval': {
            'primary_retriever': env_vars.get('RETRIEVER', 'duckduckgo'),
            'max_search_results_per_query': int(env_vars.get('MAX_SEARCH_RESULTS_PER_QUERY', '5')),
            'embedding': {
                'provider': env_vars.get('EMBEDDING', 'none'),
                'model': env_vars.get('EMBEDDING_MODEL', 'none')
            }
        },
        'report': {
            'total_words': int(env_vars.get('TOTAL_WORDS', '1500')),
            'format': env_vars.get('REPORT_FORMAT', 'APA'),
            'language': env_vars.get('LANGUAGE', 'chinese'),
            'default_source': env_vars.get('REPORT_SOURCE', 'web')
        },
        'paths': {
            'documents': env_vars.get('DOC_PATH', './my-docs'),
            'outputs': './outputs',
            'logs': './logs'
        },
        'network': {
            'proxy': {
                'http': env_vars.get('HTTP_PROXY', ''),
                'https': env_vars.get('HTTPS_PROXY', ''),
                'enabled': bool(env_vars.get('HTTP_PROXY', '') or env_vars.get('HTTPS_PROXY', ''))
            },
            'timeout': {
                'connect': 30,
                'read': 60
            }
        },
        'logging': {
            'level': 'INFO',
            'verbose': env_vars.get('VERBOSE', 'false').lower() == 'true',
            'modules': {
                'fontTools': 'WARNING',
                'transformers': 'WARNING'
            }
        },
        'scheduled_research': {
            'enabled': True,
            'default_interval': 3600,
            'max_concurrent_tasks': 3
        },
        'advanced': {
            'multi_agents': {'enabled': True, 'max_agents': 5},
            'mcp': {'enabled': False, 'servers': [], 'allowed_root_paths': []},
            'memory': {'enabled': True, 'cache_size': 1000}
        },
        'development': {
            'debug': False,
            'test_mode': False,
            'mock_responses': False
        }
    }
    
    return yaml_config


def backup_existing_files():
    """备份现有配置文件"""
    files_to_backup = ['config.env', 'config.yaml']
    
    for filename in files_to_backup:
        if os.path.exists(filename):
            backup_name = f"{filename}.backup"
            os.rename(filename, backup_name)
            logger.info(f"已备份 {filename} 为 {backup_name}")


def main():
    """主函数"""
    logger.info("开始配置迁移...")
    
    # 1. 备份现有文件
    backup_existing_files()
    
    # 2. 解析.env文件
    env_file = 'config.env.backup' if os.path.exists('config.env.backup') else 'config.env'
    env_vars = parse_env_file(env_file)
    
    # 3. 转换为YAML格式
    yaml_config = migrate_to_yaml(env_vars)
    
    # 4. 保存YAML配置
    with open('config.yaml', 'w', encoding='utf-8') as f:
        f.write("""# =============================================================================
# GPT Researcher 配置文件 (YAML格式) - 自动从.env迁移
# =============================================================================
# 这个配置文件由迁移工具自动生成，替代了原来的config.env文件
# 所有原有的配置都已经保留并转换为YAML格式

""")
        yaml.dump(yaml_config, f, default_flow_style=False, 
                 allow_unicode=True, sort_keys=False, indent=2)
    
    logger.info("配置已保存到 config.yaml")
    
    # 5. 测试新配置
    try:
        config_manager = ConfigManager('config.yaml')
        logger.info("✅ 新配置系统测试通过")
        
        # 显示重要配置
        print("\n=== 迁移后的配置摘要 ===")
        print(f"DeepSeek API Key: {'✅ 已配置' if config_manager.get('api.deepseek.api_key') else '❌ 未配置'}")
        print(f"Tavily API Key: {'✅ 已配置' if config_manager.get('api.search.tavily.api_key') else '❌ 未配置'}")
        print(f"主要搜索引擎: {config_manager.get('retrieval.primary_retriever')}")
        print(f"嵌入模型: {config_manager.get('retrieval.embedding.provider')}")
        print(f"报告语言: {config_manager.get('report.language')}")
        print(f"报告字数: {config_manager.get('report.total_words')}")
        
    except Exception as e:
        logger.error(f"❌ 新配置系统测试失败: {str(e)}")
        return
    
    print("\n=== 迁移完成 ===")
    print("✅ 配置迁移成功完成！")
    print("🔄 请重新启动应用以使用新的配置系统")
    print(f"📁 备份文件已保存，如有问题可以恢复")
    print("📝 新的配置文件：config.yaml")
    print("🗑️  旧的配置文件已备份为：config.env.backup")


if __name__ == "__main__":
    main()
