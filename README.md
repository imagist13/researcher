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