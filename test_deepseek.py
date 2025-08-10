#!/usr/bin/env python3
"""
GPT Researcher + DeepSeek API 配置测试脚本
"""
import os
import asyncio
from dotenv import load_dotenv
from gpt_researcher import GPTResearcher

def test_environment():
    """测试环境变量配置"""
    print("🔍 检查环境变量配置...")
    
    # 加载环境变量
    load_dotenv()
    
    # 检查必要的环境变量
    required_vars = {
        'DEEPSEEK_API_KEY': os.getenv('DEEPSEEK_API_KEY'),
        'FAST_LLM': os.getenv('FAST_LLM'),
        'SMART_LLM': os.getenv('SMART_LLM'),
    }
    
    missing_vars = []
    for var_name, var_value in required_vars.items():
        if not var_value or var_value == f'your_{var_name.lower()}_here':
            missing_vars.append(var_name)
        else:
            print(f"✅ {var_name}: {var_value[:20]}...")
    
    if missing_vars:
        print(f"❌ 缺少以下环境变量: {', '.join(missing_vars)}")
        print("请编辑 .env 文件并填入正确的值")
        return False
    
    return True

async def test_deepseek_connection():
    """测试 DeepSeek API 连接"""
    print("\n🤖 测试 DeepSeek API 连接...")
    
    try:
        # 创建一个简单的研究实例
        researcher = GPTResearcher(
            query="什么是人工智能？",
            report_type="research_report",
            verbose=True
        )
        
        print("✅ GPTResearcher 实例创建成功")
        print(f"✅ 使用的快速 LLM: {researcher.cfg.fast_llm}")
        print(f"✅ 使用的智能 LLM: {researcher.cfg.smart_llm}")
        
        return True
        
    except Exception as e:
        print(f"❌ DeepSeek API 连接测试失败: {str(e)}")
        return False

async def test_simple_research():
    """测试简单的研究功能"""
    print("\n📚 测试简单研究功能...")
    
    try:
        researcher = GPTResearcher(
            query="GPT 是什么的缩写？",
            report_type="research_report",
            verbose=False
        )
        
        print("🔍 开始进行研究...")
        research_result = await researcher.conduct_research()
        
        print("📝 生成研究报告...")
        report = await researcher.write_report()
        
        print("✅ 研究完成！")
        print(f"📊 研究上下文数量: {len(research_result)}")
        print(f"📄 报告长度: {len(report)} 字符")
        print(f"💰 总成本: ${researcher.get_costs():.4f}")
        
        # 保存测试报告
        with open("test_report.md", "w", encoding="utf-8") as f:
            f.write(report)
        print("💾 测试报告已保存到 test_report.md")
        
        return True
        
    except Exception as e:
        print(f"❌ 研究测试失败: {str(e)}")
        return False

async def main():
    """主测试函数"""
    print("=" * 60)
    print("🧪 GPT Researcher + DeepSeek API 配置测试")
    print("=" * 60)
    
    # 测试环境变量
    if not test_environment():
        return
    
    # 测试 DeepSeek 连接
    if not await test_deepseek_connection():
        return
    
    # 询问是否进行完整测试
    print("\n" + "=" * 60)
    choice = input("🤔 是否进行完整的研究功能测试？(y/n): ").strip().lower()
    
    if choice in ['y', 'yes', '是']:
        await test_simple_research()
    
    print("\n" + "=" * 60)
    print("🎉 测试完成！如果所有测试通过，您可以开始使用 GPT Researcher 了。")
    print("🚀 启动开发服务器: python -m uvicorn main:app --reload")
    print("🌐 访问地址: http://localhost:8000")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
