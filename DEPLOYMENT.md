# GPT Researcher 部署运行文档 📚

> **版本**: 2.0.0  
> **更新时间**: 2025年8月  
> **配置系统**: YAML格式（已升级）  

## 🚀 快速开始

### 系统要求

- **Python**: 3.9 或以上版本
- **操作系统**: Windows / macOS / Linux
- **内存**: 建议 4GB 以上
- **网络**: 稳定的互联网连接

### ⚡ 一键部署

```bash
# 1. 克隆项目
git clone <your-repo-url>
cd researcher

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置API密钥（见下方配置章节）
# 编辑 config.yaml 文件

# 4. 启动服务
python main.py
```

服务启动后访问：[http://localhost:8000](http://localhost:8000)

---

## 📋 详细部署指南

### 1. 环境准备

#### Python环境安装

**Windows用户：**
```powershell
# 下载并安装 Python 3.9+
# 验证安装
python --version
pip --version
```

**macOS/Linux用户：**
```bash
# 使用系统包管理器或pyenv安装Python
python3 --version
pip3 --version
```

#### 虚拟环境（推荐）

```bash
# 创建虚拟环境
python -m venv gpt_researcher_env

# 激活虚拟环境
# Windows:
gpt_researcher_env\Scripts\activate
# macOS/Linux:
source gpt_researcher_env/bin/activate
```

### 2. 项目安装

```bash
# 克隆项目
git clone <your-repo-url>
cd researcher

# 安装依赖
pip install -r requirements.txt

# 验证安装
python -c "import yaml; print('YAML支持正常')"
```

### 3. 配置系统（⭐ 重要）

#### 🆕 YAML配置文件

项目已升级到YAML配置系统，配置文件为 `config.yaml`。

#### 基础配置

编辑 `config.yaml` 文件：

```yaml
# 核心API配置
api:
  # DeepSeek API（主要LLM提供商）
  deepseek:
    api_key: "your_deepseek_api_key_here"  # 必填
    enabled: true
  
  # 搜索引擎配置
  search:
    tavily:
      api_key: "your_tavily_api_key_here"  # 可选，但推荐
      enabled: true

# LLM模型配置
llm:
  fast_model: "deepseek:deepseek-chat"
  smart_model: "deepseek:deepseek-chat"
  strategic_model: "deepseek:deepseek-chat"
  temperature: 0.7

# 搜索配置
retrieval:
  primary_retriever: "duckduckgo"  # 免费搜索引擎
  max_search_results_per_query: 5
  embedding:
    provider: "none"  # 禁用嵌入以获得最佳性能
    model: "none"

# 报告配置
report:
  total_words: 1500
  format: "APA"
  language: "chinese"
  default_source: "web"
```

#### 🔑 API密钥获取

**1. DeepSeek API密钥（必需）**
- 访问：[DeepSeek开放平台](https://platform.deepseek.com/)
- 注册账户并创建API密钥
- 复制密钥到 `api.deepseek.api_key`

**2. Tavily搜索API（推荐）**
- 访问：[Tavily API](https://tavily.com/)
- 获取免费API密钥
- 复制到 `api.search.tavily.api_key`

**3. 其他API密钥（可选）**
- Google Search API
- Bing Search API
- OpenAI API（仅用于嵌入）

#### 配置验证

```bash
# 运行配置验证
python -c "from config_manager import ConfigManager; c=ConfigManager(); print('✅ 配置验证成功')"
```

### 4. 启动服务

#### 开发模式启动

```bash
# 前台启动（可以看到日志）
python main.py

# 看到以下信息表示启动成功：
# INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

#### 生产模式启动

```bash
# 后台启动
nohup python main.py > gpt_researcher.log 2>&1 &

# 查看日志
tail -f gpt_researcher.log
```

#### Docker部署（推荐生产环境）

```bash
# 构建镜像
docker build -t gpt-researcher .

# 运行容器
docker run -d \
  --name gpt-researcher \
  -p 8000:8000 \
  -v $(pwd)/config.yaml:/app/config.yaml \
  -v $(pwd)/outputs:/app/outputs \
  gpt-researcher

# 查看容器状态
docker ps
docker logs gpt-researcher
```

---

## 🛠️ 功能使用指南

### Web界面使用

1. **访问界面**：打开浏览器访问 [http://localhost:8000](http://localhost:8000)

2. **研究任务**：
   - 在文本框中输入研究主题
   - 选择报告类型（研究报告/详细分析等）
   - 选择信息来源（网络/本地文档/混合）
   - 点击"开始研究"

3. **结果查看**：
   - 实时查看研究进度
   - 下载PDF/DOCX格式报告
   - 查看引用来源

### API调用

#### 基础研究API

```bash
# POST /report/
curl -X POST "http://localhost:8000/report/" \
-H "Content-Type: application/json" \
-d '{
  "task": "人工智能技术发展趋势",
  "report_type": "research_report",
  "report_source": "web",
  "tone": "Objective",
  "headers": {},
  "repo_name": "",
  "branch_name": "",
  "generate_in_background": false
}'
```

#### WebSocket实时通信

```javascript
// 连接WebSocket
const ws = new WebSocket('ws://localhost:8000/ws');

// 发送研究任务
ws.send(JSON.stringify({
  type: "start_research",
  task: "研究主题",
  report_type: "research_report"
}));

// 接收实时更新
ws.onmessage = function(event) {
  const data = JSON.parse(event.data);
  console.log('研究进度:', data);
};
```

### 命令行使用

```bash
# 使用CLI工具
python cli.py --task "研究主题" --report_type research_report

# 查看帮助
python cli.py --help
```

---

## ⚙️ 高级配置

### 多搜索引擎配置

```yaml
api:
  search:
    # 启用多个搜索引擎
    tavily:
      api_key: "your_tavily_key"
      enabled: true
    google:
      api_key: "your_google_key"
      cx_key: "your_cx_key"
      enabled: true
    bing:
      api_key: "your_bing_key"
      enabled: true

retrieval:
  primary_retriever: "tavily"  # 主要搜索引擎
  # 系统会自动回退到其他可用的搜索引擎
```

### 代理配置

```yaml
network:
  proxy:
    http: "http://127.0.0.1:7890"
    https: "http://127.0.0.1:7890"
    enabled: true
```

### 自定义路径

```yaml
paths:
  documents: "/path/to/your/documents"  # 本地文档路径
  outputs: "/path/to/outputs"           # 报告输出路径
  logs: "/path/to/logs"                 # 日志路径
```

### 日志配置

```yaml
logging:
  level: "DEBUG"          # DEBUG/INFO/WARNING/ERROR
  verbose: true           # 详细日志
  modules:
    fontTools: "WARNING"  # 抑制特定模块日志
    transformers: "ERROR"
```

### 性能优化

```yaml
retrieval:
  max_search_results_per_query: 10  # 增加搜索结果数量
  embedding:
    provider: "openai"              # 启用高质量嵌入
    model: "text-embedding-3-small"

llm:
  temperature: 0.3  # 降低温度提高准确性

report:
  total_words: 3000  # 生成更详细的报告
```

---

## 🐛 故障排除

### 常见问题

#### 1. 服务启动失败

**问题**：`ImportError: No module named 'yaml'`

**解决**：
```bash
pip install pyyaml
# 或重新安装所有依赖
pip install -r requirements.txt
```

#### 2. API密钥错误

**问题**：`Authentication failed`

**解决**：
1. 检查 `config.yaml` 中的API密钥是否正确
2. 确认API密钥有效期
3. 查看API使用配额是否用完

#### 3. 搜索功能失效

**问题**：`No search results found`

**解决**：
1. 检查网络连接
2. 验证搜索API密钥
3. 尝试切换搜索引擎：
```yaml
retrieval:
  primary_retriever: "duckduckgo"  # 免费搜索引擎
```

#### 4. 嵌入模型错误

**问题**：`'NoneType' object has no attribute 'embed_documents'`

**解决**：
```yaml
retrieval:
  embedding:
    provider: "none"  # 禁用嵌入模型
    model: "none"
```

#### 5. 权限问题

**问题**：`Permission denied`

**解决**：
```bash
# Windows
icacls outputs /grant Users:F /T
# Linux/macOS
chmod -R 755 outputs logs
```

### 日志分析

```bash
# 查看详细日志
tail -f logs/app.log

# 过滤错误日志
grep "ERROR" logs/app.log

# 查看特定模块日志
grep "research" logs/app.log
```

### 性能监控

```bash
# 查看系统资源使用
# Windows
tasklist | findstr python
# Linux/macOS
ps aux | grep python

# 查看端口使用
netstat -an | findstr 8000
```

---

## 📊 监控和维护

### 健康检查

```bash
# API健康检查
curl http://localhost:8000/

# 功能测试
python -c "
from config_manager import ConfigManager
import requests

# 配置检查
config = ConfigManager()
print('✅ 配置系统正常')

# API检查
response = requests.get('http://localhost:8000/')
print(f'✅ API服务正常: {response.status_code}')
"
```

### 定期维护

```bash
# 清理旧日志（保留最近30天）
find logs/ -name "*.log" -mtime +30 -delete

# 清理临时输出文件
find outputs/ -name "*.tmp" -delete

# 更新依赖
pip install --upgrade -r requirements.txt
```

### 备份配置

```bash
# 备份配置文件
cp config.yaml config.yaml.backup.$(date +%Y%m%d)

# 备份输出文件
tar -czf outputs_backup_$(date +%Y%m%d).tar.gz outputs/
```

---

## 🔧 开发和自定义

### 开发环境设置

```yaml
# 开发配置
development:
  debug: true
  test_mode: true
  mock_responses: false

logging:
  level: "DEBUG"
  verbose: true
```

### 自定义搜索引擎

1. 创建自定义检索器：
```python
# gpt_researcher/retrievers/custom/my_retriever.py
class MyCustomRetriever:
    def search(self, query):
        # 实现自定义搜索逻辑
        return results
```

2. 注册检索器：
```yaml
retrieval:
  primary_retriever: "my_custom"
```

### 插件开发

参考 `gpt_researcher/` 目录结构开发自定义插件。

---

## 🆘 技术支持

### 获取帮助

1. **文档**: 查看项目Wiki和README
2. **日志**: 检查 `logs/app.log` 获取详细错误信息
3. **配置验证**: 运行配置测试脚本
4. **社区支持**: 提交Issue到项目仓库

### 问题报告

提交Issue时请包含：

1. 系统信息（操作系统、Python版本）
2. 配置文件内容（隐藏API密钥）
3. 完整错误日志
4. 复现步骤

### 性能优化建议

1. **服务器配置**：
   - CPU: 2核心以上
   - 内存: 4GB以上
   - 存储: SSD推荐

2. **网络优化**：
   - 稳定的网络连接
   - 考虑使用代理加速API访问
   - 选择就近的API服务节点

3. **配置优化**：
   - 合理设置搜索结果数量
   - 根据需要启用/禁用功能
   - 定期清理日志和缓存

---

## 📝 更新日志

### v2.0.0 (2025-08)
- ✨ 全新YAML配置系统
- 🔧 改进的配置管理器
- 📚 完整的部署文档
- 🛠️ 一键迁移工具
- 🐛 修复嵌入模型问题
- ⚡ 性能优化

### 配置迁移

如果您有旧的 `.env` 配置文件：

```bash
# 自动迁移到YAML格式
python migrate_config.py

# 验证迁移结果
python -c "from config_manager import ConfigManager; ConfigManager()"
```

---

## 🎯 下一步

部署完成后，您可以：

1. 🔍 **开始研究**：访问 Web界面进行首次研究
2. 📖 **阅读文档**：了解更多高级功能
3. 🛠️ **自定义配置**：根据需求调整配置参数
4. 🔧 **开发扩展**：基于API开发自定义应用
5. 📊 **监控运行**：设置监控和日志分析

**祝您使用愉快！** 🚀

---

> 📞 **需要帮助？**  
> 如果在部署过程中遇到任何问题，请查看故障排除章节或提交Issue。

> 💡 **提示**  
> 建议定期备份配置文件和重要数据，保持系统更新。
