# 🚀 GPT Researcher 快速启动指南

> 5分钟内完成部署并开始使用！

## ⚡ 一分钟快速体验

```bash
# 1. 进入项目目录
cd researcher

# 2. 安装依赖（如未安装）
pip install -r requirements.txt

# 3. 启动服务
python main.py

# 4. 打开浏览器
# http://localhost:8000
```

## 🔑 首次配置（重要！）

### 获取API密钥

**DeepSeek API密钥（必须）**：
1. 访问：https://platform.deepseek.com/
2. 注册并创建API密钥
3. 复制密钥

**Tavily搜索API（推荐）**：
1. 访问：https://tavily.com/
2. 获取免费密钥
3. 复制密钥

### 编辑配置文件

打开 `config.yaml` 文件，填入您的API密钥：

```yaml
api:
  deepseek:
    api_key: "你的_DeepSeek_密钥"  # 粘贴在这里
    enabled: true
  search:
    tavily:
      api_key: "你的_Tavily_密钥"  # 粘贴在这里（可选）
      enabled: true
```

## 🎯 开始使用

### Web界面使用
1. 浏览器访问：http://localhost:8000
2. 输入研究主题，如："人工智能发展趋势"
3. 点击"开始研究"
4. 等待生成完整报告
5. 下载PDF或DOCX格式

### 命令行使用
```bash
python cli.py --task "人工智能发展趋势" --report_type research_report
```

## ❗ 常见问题

**问题1：API密钥错误**
```
解决：确认密钥正确且有效，检查config.yaml格式
```

**问题2：搜索无结果**
```yaml
# 在config.yaml中设置免费搜索引擎
retrieval:
  primary_retriever: "duckduckgo"  # 免费选项
```

**问题3：启动失败**
```bash
# 重新安装依赖
pip install -r requirements.txt --upgrade
```

## 🎉 成功标志

看到以下信息表示成功：
- ✅ 服务启动：`INFO: Uvicorn running on http://0.0.0.0:8000`
- ✅ 配置加载：`使用配置文件：config.yaml`
- ✅ API访问：浏览器可以打开Web界面

## 📚 下一步

- 阅读完整部署文档：[DEPLOYMENT.md](DEPLOYMENT.md)
- 了解高级配置选项
- 自定义研究主题和参数

**开始您的智能研究之旅！** 🚀
