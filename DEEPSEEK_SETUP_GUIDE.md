# 🚀 GPT Researcher + DeepSeek API 开发环境配置指南

## 📋 前置要求

- Python 3.11 或更高版本
- DeepSeek API Key ([申请地址](https://platform.deepseek.com/))
- Tavily API Key ([申请地址](https://app.tavily.com)) 或使用免费的 DuckDuckGo

## ⚡ 快速开始

### 1. 自动化安装 (推荐)

```bash
# 运行自动安装脚本
./setup_dev.bat

# 或者手动执行以下步骤
```

### 2. 手动安装步骤

```bash
# 1. 创建虚拟环境
python -m venv venv

# 2. 激活虚拟环境 (Windows)
venv\Scripts\activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 复制环境配置文件
copy config.env .env
```

### 3. 配置 API 密钥

编辑 `.env` 文件，填入您的 API 密钥：

```env
# 必填：DeepSeek API Key
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxx

# 推荐：Tavily 搜索 API (免费额度)
TAVILY_API_KEY=tvly-xxxxxxxxxxxxxxxx

# 可选：OpenAI API Key (仅用于嵌入模型，性能更好)
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxx
```

## 🔧 配置说明

### LLM 模型配置

```env
# 使用 DeepSeek 模型
FAST_LLM=deepseek:deepseek-chat       # 快速模型
SMART_LLM=deepseek:deepseek-chat      # 智能模型  
STRATEGIC_LLM=deepseek:deepseek-chat  # 策略模型
```

### 搜索引擎配置

```env
# 方案1: Tavily (推荐，AI优化搜索)
RETRIEVER=tavily
TAVILY_API_KEY=your_tavily_api_key

# 方案2: 免费 DuckDuckGo (无需API密钥)
RETRIEVER=duckduckgo

# 方案3: 多搜索引擎组合
RETRIEVER=tavily,duckduckgo
```

### 嵌入模型配置

```env
# 方案1: OpenAI 嵌入 (推荐，质量高)
EMBEDDING=openai:text-embedding-3-small
OPENAI_API_KEY=your_openai_key

# 方案2: 本地嵌入 (免费)
EMBEDDING=huggingface:sentence-transformers/all-MiniLM-L6-v2
```

## 🧪 测试配置

```bash
# 运行配置测试
python test_deepseek.py
```

测试将验证：
- ✅ 环境变量配置
- ✅ DeepSeek API 连接
- ✅ 简单研究功能

## 🚀 启动开发服务器

```bash
# 激活虚拟环境
venv\Scripts\activate

# 启动开发服务器
python -m uvicorn main:app --reload

# 或使用 CLI 测试
python cli.py "人工智能的发展历史" --report_type research_report --tone objective
```

## 🌐 访问应用

- **Web 界面**: http://localhost:8000
- **API 文档**: http://localhost:8000/docs

## 📝 使用示例

### Python API 使用

```python
from gpt_researcher import GPTResearcher
import asyncio

async def main():
    # 创建研究实例
    researcher = GPTResearcher(
        query="人工智能在医疗领域的应用",
        report_type="research_report"
    )
    
    # 进行研究
    await researcher.conduct_research()
    
    # 生成报告
    report = await researcher.write_report()
    
    print(report)

# 运行
asyncio.run(main())
```

### 命令行使用

```bash
# 基础研究报告
python cli.py "区块链技术原理" --report_type research_report --tone objective

# 详细研究报告
python cli.py "量子计算发展现状" --report_type detailed_report --tone analytical

# 指定语言
python cli.py "机器学习算法" --report_type research_report --language chinese
```

## 🎛️ 高级配置

### 报告定制

```env
TOTAL_WORDS=2000           # 报告字数
LANGUAGE=chinese           # 报告语言
REPORT_FORMAT=APA          # 报告格式
TEMPERATURE=0.7            # 创造性程度
```

### 性能优化

```env
MAX_SEARCH_RESULTS_PER_QUERY=8    # 每次搜索结果数
MAX_SCRAPER_WORKERS=20            # 爬虫并发数
FAST_TOKEN_LIMIT=4000             # 快速模型token限制
SMART_TOKEN_LIMIT=8000            # 智能模型token限制
```

### 本地文档研究

```env
DOC_PATH=./my-docs         # 本地文档路径
REPORT_SOURCE=local        # 使用本地文档
```

## 🔍 支持的文件格式

- PDF 文档
- Word 文档 (.docx)
- Excel 表格 (.xlsx)
- Markdown 文件 (.md)
- 纯文本文件 (.txt)
- CSV 文件
- PowerPoint 演示文稿 (.pptx)

## 🛠️ 故障排除

### 常见问题

1. **DeepSeek API 错误**
   ```
   检查 DEEPSEEK_API_KEY 是否正确
   确认 API 余额充足
   检查网络连接
   ```

2. **搜索失败**
   ```
   检查 TAVILY_API_KEY 或切换到 duckduckgo
   检查网络代理设置
   ```

3. **依赖安装失败**
   ```
   pip install --upgrade pip
   pip install -r requirements.txt --no-cache-dir
   ```

### 代理配置

如果需要使用代理：

```env
HTTP_PROXY=http://127.0.0.1:7890
HTTPS_PROXY=http://127.0.0.1:7890
```

## 💡 最佳实践

1. **API 成本控制**
   - 使用 DeepSeek 可大幅降低成本
   - 合理设置 token 限制
   - 优先使用免费搜索引擎

2. **性能优化**
   - 根据需求选择合适的报告类型
   - 调整并发数和搜索结果数
   - 使用本地嵌入模型节省成本

3. **研究质量**
   - 使用多搜索引擎提高覆盖面
   - 设置合适的 temperature 值
   - 根据任务选择合适的语言模型

## 📚 参考资源

- [GPT Researcher 官方文档](https://docs.gptr.dev)
- [DeepSeek API 文档](https://platform.deepseek.com/api-docs)
- [Tavily 搜索 API](https://docs.tavily.com)
- [项目 GitHub 仓库](https://github.com/assafelovic/gpt-researcher)

---

🎉 **配置完成后，您就可以开始使用 GPT Researcher 进行高质量的 AI 研究了！**
