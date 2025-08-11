# 🚀 GPT Researcher API使用指南

## 📌 快速开始

### 基础URL
```
本地开发: http://localhost:8000
生产环境: https://your-domain.com
```

### 核心API端点概览

| 功能模块 | 端点 | 描述 |
|---------|------|------|
| **研究任务** | `POST /api/research/start` | 启动新的研究任务 |
| **定时任务** | `POST /api/scheduled/tasks` | 创建定时研究任务 |
| **聊天对话** | `POST /api/chat/send` | AI对话交互 |
| **WebSocket** | `ws://localhost:8000/ws` | 实时通信 |

---

## 🔍 研究API示例

### 启动研究任务
```bash
curl -X POST "http://localhost:8000/api/research/start" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "人工智能在医疗领域的应用",
    "report_type": "research_report",
    "analysis_depth": "detailed",
    "language": "chinese"
  }'
```

### 响应格式
```json
{
  "success": true,
  "data": {
    "task_id": "research_uuid_12345",
    "status": "started",
    "estimated_time": 300,
    "websocket_url": "ws://localhost:8000/ws/research/research_uuid_12345"
  },
  "message": "研究任务已启动"
}
```

---

## ⏰ 定时任务API示例

### 创建定时任务
```bash
curl -X POST "http://localhost:8000/api/scheduled/tasks" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "AI技术趋势追踪",
    "keywords": ["人工智能", "机器学习", "深度学习"],
    "interval_hours": 24,
    "analysis_depth": "detailed",
    "max_sources": 15
  }'
```

### 获取任务列表
```bash
curl "http://localhost:8000/api/scheduled/tasks?active_only=true&page=1&per_page=10"
```

### 任务控制操作
```bash
# 暂停任务
curl -X POST "http://localhost:8000/api/scheduled/tasks/{task_id}/pause"

# 恢复任务  
curl -X POST "http://localhost:8000/api/scheduled/tasks/{task_id}/resume"

# 立即执行
curl -X POST "http://localhost:8000/api/scheduled/tasks/{task_id}/trigger"
```

---

## 💬 聊天API示例

### 发送消息
```bash
curl -X POST "http://localhost:8000/api/chat/send" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "请分析一下特斯拉的最新财报",
    "research_mode": true,
    "stream": false
  }'
```

---

## 🔌 WebSocket使用示例

### JavaScript客户端
```javascript
// 连接WebSocket
const ws = new WebSocket('ws://localhost:8000/ws/research/task_id_123');

// 监听消息
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  switch(data.type) {
    case 'progress_update':
      console.log(`进度: ${data.data.progress}%`);
      break;
    case 'source_found':
      console.log(`找到信息源: ${data.data.title}`);
      break;
    case 'research_complete':
      console.log('研究完成:', data.data.summary);
      break;
  }
};

// 发送消息
ws.send(JSON.stringify({
  type: 'start_research',
  data: {
    query: '人工智能发展趋势',
    config: { analysis_depth: 'detailed' }
  }
}));
```

### Python客户端
```python
import asyncio
import websockets
import json

async def research_client():
    uri = "ws://localhost:8000/ws/research/task_id_123"
    
    async with websockets.connect(uri) as websocket:
        # 发送研究请求
        await websocket.send(json.dumps({
            "type": "start_research", 
            "data": {
                "query": "人工智能发展趋势",
                "config": {"analysis_depth": "detailed"}
            }
        }))
        
        # 监听响应
        async for message in websocket:
            data = json.loads(message)
            print(f"收到消息: {data['type']}")
            
            if data['type'] == 'research_complete':
                print("研究完成!")
                break

asyncio.run(research_client())
```

---

## 📊 响应格式规范

### 成功响应
```json
{
  "success": true,
  "data": { /* 具体数据 */ },
  "message": "操作成功",
  "timestamp": "2025-01-15T10:00:00Z"
}
```

### 错误响应
```json
{
  "success": false,
  "error": {
    "code": "RESEARCH_FAILED",
    "message": "研究任务执行失败",
    "details": "具体错误信息"
  },
  "timestamp": "2025-01-15T10:00:00Z"
}
```

---

## 🛠️ 客户端SDK示例

### Python SDK
```python
class GPTResearcherClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
    
    def start_research(self, query, **kwargs):
        response = requests.post(
            f"{self.base_url}/api/research/start",
            json={"query": query, **kwargs}
        )
        return response.json()
    
    def create_scheduled_task(self, topic, **config):
        response = requests.post(
            f"{self.base_url}/api/scheduled/tasks",
            json={"topic": topic, **config}
        )
        return response.json()

# 使用示例
client = GPTResearcherClient()

# 启动研究
result = client.start_research(
    query="人工智能的未来发展趋势",
    analysis_depth="detailed"
)

# 创建定时任务
task = client.create_scheduled_task(
    topic="AI技术追踪",
    interval_hours=24,
    keywords=["人工智能", "机器学习"]
)
```

---

## 🔧 配置说明

### 分析深度级别
- `basic`: 快速分析 (1-2分钟，600字)
- `detailed`: 详细分析 (3-5分钟，1000字)  
- `deep`: 深度分析 (5-10分钟，1500字)

### 报告类型
- `research_report`: 标准研究报告
- `detailed_report`: 详细研究报告
- `multi_agents`: 多代理协作报告

### 信息源类型
- `web`: 网络搜索
- `local`: 本地文档
- `hybrid`: 混合模式

---

## 📞 技术支持

如有问题，请参考：
- 🏠 **项目主页**: `http://localhost:3000`
- 📖 **完整文档**: `全栈实习生笔试_项目说明书.md`
- 🔍 **健康检查**: `GET /api/scheduled/health`

---

**🎉 开始使用GPT Researcher，让AI为您的研究工作赋能！**
