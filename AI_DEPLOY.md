# AI 功能部署指南

本文档说明如何在 SoulMatch 项目中部署和启用 AI 功能。

## 快速开始

### 方式一：使用 Ollama（推荐，完全免费）

#### 1. 安装 Ollama

**macOS / Linux:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**Windows:**
从 [https://ollama.ai/download](https://ollama.ai/download) 下载安装包

#### 2. 拉取模型

```bash
# 推荐模型（7B 参数，约 4GB，需 8GB+ RAM）
ollama pull qwen2.5:7b

# 或者更轻量的模型（3GB，，适合低配置机器）
ollama pull qwen2.5:3b

# 如需更强的语义理解能力（需 GPU）
ollama pull qwen2.5:14b
```

#### 3. 验证 Ollama 运行

```bash
curl http://localhost:11434/api/tags
```

#### 4. 启动 SoulMatch

```bash
docker-compose up -d
```

---

### 方式二：使用 Google Gemini API

1. 获取 API Key: [Google AI Studio](https://makersuite.google.com/app/apikey)

2. 配置环境变量:
```bash
export AI_PROVIDER=gemini
export GEMINI_API_KEY=your-api-key
```

---

### 方式三：使用硅基流动（国内推荐）

1. 注册账号: [https://cloud.siliconflow.cn](https://cloud.siliconflow.cn)
2. 获取 API Key
3. 配置:
```bash
export AI_PROVIDER=siliconflow
export SILICONFLOW_API_KEY=your-api-key
```

---

## API 端点说明

部署成功后，以下 API 端点可用：

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/ai/health` | GET | 检查 AI 服务状态 |
| `/api/ai/chat-suggestion` | POST | 获取聊天建议 |
| `/api/ai/match-tags` | POST | 智能标签语义匹配 |
| `/api/ai/assistant` | POST | AI 私人助理 |

### 聊天建议 API 示例

```bash
curl -X POST http://localhost:8000/api/ai/chat-suggestion \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "targetUserId": "uuid-of-match",
    "chatHistory": [
      {"role": "user", "content": "你好呀"},
      {"role": "assistant", "content": "嗨，你好！"}
    ]
  }'
```

### 标签匹配 API 示例

```bash
curl -X POST http://localhost:8000/api/ai/match-tags \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "myTags": ["原神", "篮球"],
    "candidateTags": ["Genshin", "NBA"]
  }'
```

---

## 硬件要求

| 模型 | 最低 RAM | 推荐 RAM | GPU |
|------|----------|----------|-----|
| qwen2.5:3b | 6GB | 8GB | 可选 |
| qwen2.5:7b | 8GB | 16GB | 推荐 |
| qwen2.5:14b | 16GB | 32GB | 推荐 |

---

## 常见问题

### Q: Ollama 启动失败？
```bash
# 检查状态
ollama list

# 手动启动
ollama serve
```

### Q: 响应很慢？
- 使用更小的模型 (qwen2.5:3b)
- 确保有足够内存
- 考虑使用 GPU

### Q: API 返回错误？
```bash
# 检查 AI 服务健康状态
curl http://localhost:8000/api/ai/health
```
