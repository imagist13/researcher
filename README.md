## 📋 项目概述

本项目是一个完整的全栈AI应用，完全满足以下核心功能：**前端对话式交互** + **后端定时任务** + **AI模型数据分析和总结**。

### 🎯 主要功能以及实现

| 具体功能 | 实现情况 | 技术实现 | 文件位置 |
|---------|----------|----------|----------|
| ✅ 前端对话式交互 | **完全实现** | Next.js + WebSocket实时通信 | `frontend/nextjs/` |
| ✅ 后端AI处理 | **完全实现** | Python FastAPI  | `backend/server/` |
| ✅ 定时任务 | **完全实现** | APScheduler + 数据库持久化 | `backend/scheduled_research/` |
| ✅ 结构化结果 | **完全实现** | JSON API + 多种报告格式 | `backend/report_type/` |
| ✅ 用户参数调整 | **完全实现** | 实时配置界面 + 任务管理 | `frontend/nextjs/app/scheduled/` |
| ✅ DeepSeek支持 | **完全实现** | 支持deepseek-chat | `gpt_researcher/llm_provider/` |

---

## 🏗️ 技术架构

### 前端技术栈
- **框架**: Next.js 14 (React 18) + TypeScript
- **样式**: Tailwind CSS + 自定义组件库
- **状态管理**: React Hooks + Context API
- **实时通信**: WebSocket + Socket.IO
- **动画效果**: Framer Motion
- **构建工具**: Webpack 5 + ESBuild

### 后端技术栈
- **API框架**: Python FastAPI 0.104+
- **任务调度**: APScheduler (异步任务调度器)
- **数据库**: SQLite (开发) / PostgreSQL (生产)
- **WebSocket**: FastAPI WebSocket
- **AI集成**: LangChain 
- **异步处理**: asyncio + uvloop

### AI模型支持矩阵
```yaml
核心AI提供商:
  - DeepSeek: deepseek-chat
  - 本地模型: HuggingFace 
  
搜索引擎集成:
  - Tavily API 
```


## 🛠️ 本地运行指南

### 环境要求
```bash
# Python 环境
Python 3.9+
Node.js 18+

# API密钥 (任选其一)
OPENAI_API_KEY=your_openai_key
DEEPSEEK_API_KEY=your_deepseek_key
```

### 快速启动

#### 方式一：使用 Docker
```bash
# 克隆项目
git clone https://github.com/your-repo/gpt-researcher.git
cd gpt-researcher

# 配置环境变量
cp config.env.example config.env
# 编辑 config.env 添加你的API密钥

# 启动完整服务
docker-compose up -d

# 访问应用
open http://localhost:3000
```

#### 方式二：手动启动
```bash
# 后端启动
cd backend
pip install -r requirements.txt
python -m uvicorn server.main:app --host 0.0.0.0 --port 8000

# 前端启动 (新终端)
cd frontend/nextjs
npm install
npm run dev

# 访问 http://localhost:3000
```


## 🤖 AI任务逻辑架构

### 核心组件

#### 1. GPTResearcher 主代理
- **智能研究规划**: 根据查询自动分解为子任务和研究步骤
- **多源信息收集**: 支持Web搜索、学术论文、新闻、文档等多种信息源
- **上下文管理**: 智能管理研究过程中的上下文信息和记忆
- **动态报告生成**: 根据研究深度和类型生成相应格式的报告

#### 2. 研究技能模块
- **ResearchConductor**: 研究流程控制和协调
- **ReportGenerator**: 报告生成和格式化
- **ContextManager**: 上下文信息管理和压缩
- **BrowserManager**: 网页浏览和数据提取
- **SourceCurator**: 信息源筛选和质量评估
- **DeepResearchSkill**: 深度研究和分析

#### 3. 定时研究系统
- **SchedulerManager**: 任务调度和时间管理
- **TaskExecutor**: 研究任务执行引擎
- **TrendAnalyzer**: 趋势分析和变化检测
- **SummaryGenerator**: 动态摘要生成

### 研究流程

```
用户查询 → 任务分解 → 信息收集 → 内容分析 → 趋势检测 → 报告生成 → 结果存储
    ↓           ↓         ↓         ↓         ↓         ↓         ↓
  智能解析   子任务规划   多源搜索   深度分析   变化追踪   格式输出   历史记录
```

#### 详细流程说明

1. **查询解析阶段**
   - 分析用户查询意图
   - 识别研究主题和关键词
   - 确定研究深度和范围

2. **信息收集阶段**
   - 执行Web搜索获取最新信息
   - 访问学术数据库获取专业资料
   - 提取网页内容和文档信息
   - 过滤和验证信息质量

3. **内容分析阶段**
   - 使用LLM进行内容理解和分析
   - 提取关键信息和洞察
   - 识别信息间的关联性
   - 生成初步研究结果

4. **趋势检测阶段**
   - 对比历史数据识别变化
   - 计算趋势分数和情感分析
   - 检测异常和重要变化
   - 生成趋势报告

5. **报告生成阶段**
   - 根据研究类型选择报告模板
   - 整合所有研究结果
   - 生成结构化报告
   - 支持多种输出格式

---

## 🔌 API交互方式

### 基础配置

```bash
# 本地开发环境
BASE_URL=http://localhost:8000
WEBSOCKET_URL=ws://localhost:8000/ws

### 核心API端点

#### 1. 研究任务管理

**启动研究任务**
```bash
POST /api/research/start
Content-Type: application/json

{
  "query": "人工智能在医疗领域的应用",
  "report_type": "research_report",
  "analysis_depth": "detailed",
  "language": "zh-CN",
  "source_types": ["news", "academic"],
  "max_sources": 15
}
```

**获取任务状态**
```bash
GET /api/research/status/{task_id}
```

**取消任务**
```bash
POST /api/research/cancel/{task_id}
```

#### 2. 定时任务管理

**创建定时任务**
```bash
POST /api/scheduled/tasks
Content-Type: application/json

{
  "topic": "AI技术趋势追踪",
  "keywords": ["人工智能", "机器学习", "深度学习"],
  "interval_hours": 24,
  "analysis_depth": "detailed",
  "max_sources": 15,
  "enable_notifications": true,
  "notification_threshold": 7.0
}
```

**任务控制操作**
```bash
# 暂停任务
POST /api/scheduled/tasks/{task_id}/pause

# 恢复任务
POST /api/scheduled/tasks/{task_id}/resume

# 立即执行
POST /api/scheduled/tasks/{task_id}/trigger

# 删除任务
DELETE /api/scheduled/tasks/{task_id}
```

#### 3. 聊天对话接口

**发送消息**
```bash
POST /api/chat/send
Content-Type: application/json

{
  "message": "请分析一下特斯拉的最新财报",
  "research_mode": true,
  "stream": false,
  "context": "previous_conversation_id"
}
```

**获取对话历史**
```bash
GET /api/chat/history?conversation_id={id}&limit=50
```

#### 4. WebSocket实时通信

**连接WebSocket**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onopen = () => {
  console.log('WebSocket连接已建立');
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('收到消息:', data);
  
  // 处理不同类型的消息
  switch(data.type) {
    case 'progress':
      updateProgress(data.progress);
      break;
    case 'result':
      displayResult(data.result);
      break;
    case 'error':
      handleError(data.error);
      break;
  }
};
```

**发送研究请求**
```javascript
ws.send(JSON.stringify({
  type: 'research_request',
  query: '人工智能发展趋势',
  report_type: 'detailed_report',
  stream: true
}));
```

### 响应格式

#### 标准响应结构
```json
{
  "success": true,
  "data": {
    "task_id": "research_uuid_12345",
    "status": "running",
    "progress": 45.5,
    "estimated_time": 180,
    "websocket_url": "ws://localhost:8000/ws/research/research_uuid_12345"
  },
  "message": "研究任务正在执行中",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### 错误响应格式
```json
{
  "success": false,
  "error": {
    "code": "INVALID_QUERY",
    "message": "查询内容不能为空",
    "details": "query field is required"
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### 使用示例

#### Python客户端示例
```python
import requests
import json
import websockets
import asyncio

class GPTResearcherClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def start_research(self, query, report_type="research_report"):
        """启动研究任务"""
        url = f"{self.base_url}/api/research/start"
        data = {
            "query": query,
            "report_type": report_type,
            "analysis_depth": "detailed"
        }
        
        response = self.session.post(url, json=data)
        return response.json()
    
    async def monitor_progress(self, task_id):
        """监控任务进度"""
        url = f"ws://localhost:8000/ws/research/{task_id}"
        
        async with websockets.connect(url) as websocket:
            while True:
                message = await websocket.recv()
                data = json.loads(message)
                
                if data["type"] == "progress":
                    print(f"进度: {data['progress']}%")
                elif data["type"] == "complete":
                    print("研究完成!")
                    return data["result"]
                elif data["type"] == "error":
                    print(f"错误: {data['error']}")
                    break

# 使用示例
client = GPTResearcherClient()
result = client.start_research("量子计算最新进展")
print(f"任务ID: {result['data']['task_id']}")

# 异步监控进度
asyncio.run(client.monitor_progress(result['data']['task_id']))
```

#### JavaScript/Node.js客户端示例
```javascript
const axios = require('axios');
const WebSocket = require('ws');

class GPTResearcherClient {
  constructor(baseUrl = 'http://localhost:8000') {
    this.baseUrl = baseUrl;
    this.axios = axios.create({ baseURL: baseUrl });
  }

  async startResearch(query, reportType = 'research_report') {
    try {
      const response = await this.axios.post('/api/research/start', {
        query,
        report_type: reportType,
        analysis_depth: 'detailed'
      });
      return response.data;
    } catch (error) {
      console.error('启动研究失败:', error.response?.data || error.message);
      throw error;
    }
  }

  async createScheduledTask(taskConfig) {
    try {
      const response = await this.axios.post('/api/scheduled/tasks', taskConfig);
      return response.data;
    } catch (error) {
      console.error('创建定时任务失败:', error.response?.data || error.message);
      throw error;
    }
  }

  async getTaskStatus(taskId) {
    try {
      const response = await this.axios.get(`/api/research/status/${taskId}`);
      return response.data;
    } catch (error) {
      console.error('获取任务状态失败:', error.response?.data || error.message);
      throw error;
    }
  }
}

// 使用示例
async function main() {
  const client = new GPTResearcherClient();
  
  try {
    // 启动研究任务
    const researchResult = await client.startResearch('人工智能在医疗领域的应用');
    console.log('研究任务已启动:', researchResult.data.task_id);
    
    // 创建定时任务
    const scheduledTask = await client.createScheduledTask({
      topic: 'AI技术趋势追踪',
      keywords: ['人工智能', '机器学习'],
      interval_hours: 24
    });
    console.log('定时任务已创建:', scheduledTask.data.id);
    
  } catch (error) {
    console.error('操作失败:', error.message);
  }
}

main();
```

---

## ⏰ 定时任务设计架构

### 系统架构概览

```
用户配置 → 任务调度器 → 任务执行器 → 趋势分析器 → 摘要生成器 → 结果存储
    ↓           ↓          ↓          ↓          ↓          ↓
  任务参数   时间管理   研究执行   变化检测   内容总结   历史记录
```

### 核心组件设计

#### 1. 任务调度管理器 (SchedulerManager)
- **APScheduler集成**: 基于APScheduler的异步任务调度系统
- **多触发器支持**: 支持间隔触发、定时触发、Cron表达式等
- **任务去重**: 智能合并相同任务，避免重复执行
- **容错机制**: 任务错过执行时间的容忍度和重试策略

#### 2. 任务执行引擎 (TaskExecutor)
- **分层执行**: 研究阶段 → 分析阶段 → 摘要阶段 → 存储阶段
- **实时进度**: WebSocket推送执行进度和状态更新
- **资源优化**: 根据任务类型动态调整资源配置
- **异常处理**: 完善的错误处理和恢复机制

#### 3. 趋势分析引擎 (TrendAnalyzer)
- **多维度分析**: 关键词趋势、情感变化、话题演变
- **异常检测**: 智能识别重要变化和异常情况
- **趋势评分**: 综合计算趋势分数和置信度
- **历史对比**: 与历史数据进行深度对比分析

#### 4. 动态摘要生成器 (SummaryGenerator)
- **智能摘要**: 根据变化程度生成不同深度的摘要
- **关键信息提取**: 自动识别和突出重要变化
- **多格式输出**: 支持Markdown、JSON等多种格式

### 配置系统设计

#### 性能配置分层
```python
# 基础配置 (快速执行)
BASIC_CONFIG = {
    "MAX_SEARCH_RESULTS_PER_QUERY": 3,
    "MAX_SUBTOPICS": 2,
    "MAX_ITERATIONS": 2,
    "TOTAL_WORDS": 600,
    "TEMPERATURE": 0.3
}

# 详细配置 (平衡性能)
DETAILED_CONFIG = {
    "MAX_SEARCH_RESULTS_PER_QUERY": 5,
    "MAX_SUBTOPICS": 3,
    "MAX_ITERATIONS": 3,
    "TOTAL_WORDS": 1000,
    "TEMPERATURE": 0.4
}

# 深度配置 (全面分析)
DEEP_CONFIG = {
    "MAX_SEARCH_RESULTS_PER_QUERY": 7,
    "MAX_SUBTOPICS": 4,
    "MAX_ITERATIONS": 4,
    "TOTAL_WORDS": 1500,
    "TEMPERATURE": 0.4
}
```

#### 智能配置优化
- **语言优化**: 中英文不同的处理策略
- **源类型优化**: 根据信息源类型调整并发数
- **域名限制优化**: 有域名限制时减少并发避免被限制
- **关键词优化**: 根据关键词数量动态调整子主题数量

### 调度策略设计

#### 时间调度策略
```python
# 间隔调度
IntervalTrigger(hours=24)  # 每24小时执行一次

# 定时调度  
DateTrigger(run_date=datetime(2024, 1, 15, 9, 0))  # 指定时间执行

# Cron调度
CronTrigger(hour=9, minute=0)  # 每天上午9点执行
```

#### 任务优先级管理
- **高优先级**: 重要话题、紧急监控任务
- **中优先级**: 常规趋势追踪任务
- **低优先级**: 背景研究、历史数据分析

#### 资源调度优化
- **并发控制**: 限制同时运行的任务数量
- **内存管理**: 智能释放已完成任务的内存
- **CPU优化**: 根据系统负载调整任务执行频率

### 趋势分析算法

#### 1. 关键词趋势分析
```python
def analyze_keyword_trends(self, current_data, historical_data, keywords):
    """分析关键词趋势变化"""
    trends = {}
    for keyword in keywords:
        # 计算关键词出现频率变化
        current_freq = self._calculate_keyword_frequency(current_data, keyword)
        historical_freq = self._calculate_historical_frequency(historical_data, keyword)
        
        # 计算趋势分数
        trend_score = (current_freq - historical_freq) / max(historical_freq, 1)
        trends[keyword] = {
            "current_frequency": current_freq,
            "historical_frequency": historical_freq,
            "trend_score": trend_score,
            "trend_direction": "up" if trend_score > 0 else "down"
        }
    return trends
```

#### 2. 情感变化分析
```python
def analyze_sentiment_trends(self, current_data, historical_data):
    """分析情感变化趋势"""
    sentiment_keywords = {
        "positive": ["增长", "上升", "改善", "突破", "成功"],
        "negative": ["下降", "减少", "衰退", "问题", "挑战"],
        "neutral": ["保持", "稳定", "持续", "维持", "不变"]
    }
    
    # 计算各情感类别的得分变化
    current_sentiment = self._calculate_sentiment_score(current_data, sentiment_keywords)
    historical_sentiment = self._calculate_sentiment_score(historical_data, sentiment_keywords)
    
    return {
        "current_sentiment": current_sentiment,
        "historical_sentiment": historical_sentiment,
        "sentiment_change": current_sentiment - historical_sentiment
    }
```

#### 3. 异常检测算法
```python
def detect_anomalies(self, trend_analysis):
    """检测异常变化"""
    anomalies = []
    
    # 趋势分数异常检测
    if abs(trend_analysis["trend_score"]) > 5.0:
        anomalies.append({
            "type": "trend_anomaly",
            "severity": "high",
            "description": f"趋势分数异常: {trend_analysis['trend_score']}"
        })
    
    # 活跃度异常检测
    if trend_analysis["activity_level"] > 8.0:
        anomalies.append({
            "type": "activity_anomaly", 
            "severity": "medium",
            "description": "话题活跃度异常高"
        })
    
    return anomalies
```

### 通知系统设计

#### 通知触发条件
- **趋势分数阈值**: 当趋势分数超过设定阈值时触发
- **异常检测**: 检测到重要变化或异常时触发
- **定期摘要**: 按设定时间间隔发送定期摘要

#### 通知内容结构
```json
{
  "notification_type": "trend_alert",
  "topic": "AI技术趋势追踪",
  "trend_score": 8.5,
  "key_changes": [
    "新发现重要技术突破",
    "市场反应显著变化",
    "专家观点出现分歧"
  ],
  "anomaly_detected": true,
  "recommended_actions": [
    "深入分析技术突破细节",
    "关注市场后续反应",
    "收集更多专家观点"
  ]
}
```

### 数据存储设计

#### 历史数据管理
- **分层存储**: 原始数据、分析结果、趋势数据分层存储
- **数据压缩**: 智能压缩历史数据，节省存储空间
- **快速检索**: 建立索引支持快速历史数据查询

#### 数据备份策略
- **增量备份**: 定期增量备份重要数据
- **版本控制**: 支持数据版本回滚
- **异地备份**: 重要数据异地备份确保安全

### 性能优化策略

#### 1. 并发优化
- **异步执行**: 全异步架构，提高并发处理能力
- **任务队列**: 智能任务队列管理，避免资源竞争
- **负载均衡**: 根据系统负载动态调整任务执行

#### 2. 内存优化
- **对象池**: 重用常用对象，减少内存分配
- **缓存策略**: 智能缓存热点数据
- **垃圾回收**: 及时释放无用对象内存

#### 3. 网络优化
- **连接池**: 复用网络连接，减少连接开销
- **请求合并**: 合并相似请求，减少网络调用
- **超时控制**: 智能超时设置，避免长时间等待

### 监控和日志

#### 系统监控指标
- **任务执行统计**: 成功/失败次数、平均执行时间
- **资源使用情况**: CPU、内存、网络使用率
- **趋势分析质量**: 趋势分数分布、异常检测准确率

#### 日志记录策略
- **分级日志**: DEBUG、INFO、WARNING、ERROR分级记录
- **结构化日志**: JSON格式结构化日志，便于分析
- **日志轮转**: 自动日志轮转，避免日志文件过大

---

