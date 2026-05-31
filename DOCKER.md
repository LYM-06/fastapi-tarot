# Docker 部署指南

## 前提条件
- Docker Desktop 已安装并正在运行
- 网络连接正常（能访问 Docker Hub 或国内镜像源）

## 构建和运行

### 方法一：使用 Dockerfile（推荐）

```powershell
# 1. 构建镜像
docker build -t tarot-api .

# 2. 运行容器
docker run -d -p 8000:8000 --name tarot-api `
  -e COZE_API_KEY=your_api_key `
  -e COZE_WEBHOOK_TOKEN=your_token `
  -e USE_WEBHOOK=false `
  tarot-api

# 3. 查看运行状态
docker ps

# 4. 查看日志
docker logs tarot-api

# 5. 停止容器
docker stop tarot-api

# 6. 删除容器
docker rm tarot-api
```

### 方法二：使用 docker-compose

创建 `docker-compose.yml`：

```yaml
version: '3.8'

services:
  tarot-api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - COZE_API_KEY=your_api_key
      - COZE_WEBHOOK_TOKEN=your_token
      - USE_WEBHOOK=false
    volumes:
      - tarot-data:/app/data
    restart: unless-stopped

volumes:
  tarot-data:
```

然后运行：

```powershell
# 构建并启动
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止
docker-compose down
```

## 国内镜像源配置

如果无法访问 Docker Hub，可以配置国内镜像加速：

1. 打开 Docker Desktop 设置
2. 进入 Docker Engine
3. 添加镜像加速配置：

```json
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://registry.docker-cn.com"
  ]
}
```

## 环境变量说明

| 变量名 | 说明 | 必填 |
|--------|------|------|
| COZE_API_KEY | Coze API 密钥 | 是 |
| COZE_BOT_ID | Coze Bot ID | 否 |
| COZE_WEBHOOK_TOKEN | Webhook Token | 是 |
| USE_WEBHOOK | 是否使用 Webhook（true/false） | 否，默认 false |

## 数据持久化

占卜记录存储在 SQLite 数据库中。如需持久化数据，可以挂载卷：

```powershell
docker run -d -p 8000:8000 `
  -v ${PWD}/data:/app/data `
  --name tarot-api `
  tarot-api
```

## 常见问题

### 1. Docker Desktop 无法启动
- 确保已启用 WSL 2
- 重启电脑后重试
- 检查 BIOS 中是否启用了虚拟化

### 2. 构建时无法拉取镜像
- 检查网络连接
- 配置国内镜像加速
- 使用代理

### 3. 容器启动后立即退出
```powershell
# 查看容器日志
docker logs tarot-api

# 查看容器详情
docker inspect tarot-api
```

### 4. 端口被占用
修改端口映射：
```powershell
docker run -d -p 8080:8000 --name tarot-api tarot-api
```

## API 测试

```powershell
# 健康检查
curl http://localhost:8000/health

# 塔罗牌解读
curl -X POST http://localhost:8000/tarot `
  -H "Content-Type: application/json" `
  -d '{"card_name": "战车"}'

# 占卜
curl -X POST http://localhost:8000/divination `
  -H "Content-Type: application/json" `
  -d '{"question": "我的未来运势如何？"}'

# 查看记录
curl http://localhost:8000/readings
```
