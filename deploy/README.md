# 本机局域网部署（Windows + Nginx）

面向组内验收的临时部署方式：前端静态文件由 Nginx 托管，后端与领域引擎跑在本机回环地址，通过 Nginx 反向代理对外提供。

## 结构

```text
浏览器 ──> nginx :8080 ──┬─> /            dist 静态文件（frontend/dist）
                          └─> /api/       ──> uvicorn :8000 (server/main.py)
                                                  └─> dsh Agent（MiniMax 模型）
                                             ──> engine :8100 (MCP 工具，由 API 调用)
```

- 仅 8080 对外监听（`0.0.0.0`），8000 / 8100 只绑定 `127.0.0.1`。
- 运行时目录：`D:\develop\soil-web`（dist 副本、日志、pid）。

## 前置条件

| 项目 | 要求 |
| --- | --- |
| Python | 3.11+，已安装 `requirements.txt` 依赖 |
| Node.js | 20+，仅构建前端时需要 |
| Nginx | `D:\develop\nginx-1.28.3\nginx.exe`（路径见 `deploy/start-local.ps1` 顶部变量） |
| dsh 运行时 | `D:\develop\dsh-runtime\node_modules\@deepseek-ai\dsh\lib\bin.js` |
| 模型密钥 | 环境变量 `MINIMAX_API_KEY`，不得写入仓库 |

## 启动

```powershell
# 构建前端（首次或前端改动后）
cd frontend
npm install
npm run build

# 启动（必须带密钥）
cd ..
$env:MINIMAX_API_KEY = "<你的密钥>"
powershell -ExecutionPolicy Bypass -File deploy\start-local.ps1
```

脚本会依次：停掉占用 8000/8100 的旧进程与旧 Nginx → 复制 `frontend/dist` 到运行时目录 → 启动 MCP 引擎（8100）→ 启动 API（8000）→ 等待健康检查 → 启动 Nginx（8080）→ 打印本机与局域网地址。

## 停止

```powershell
powershell -ExecutionPolicy Bypass -File deploy\stop-local.ps1
```

## 局域网放行

Windows 防火墙默认拒绝入站连接。首次部署需以管理员身份执行一次：

```powershell
powershell -ExecutionPolicy Bypass -File deploy\open-firewall.ps1
```

放行 TCP 8080 后，组员在同一局域网访问 `http://<本机内网IP>:8080/`。

## 验证

```powershell
curl http://127.0.0.1:8080/                # 200，返回前端页面
curl http://127.0.0.1:8080/api/health      # {"ok":true,...}
```

## 日志与排查

| 文件 | 内容 |
| --- | --- |
| `D:\develop\soil-web\api.err.log` | FastAPI 启动与异常 |
| `D:\develop\soil-web\mcp.err.log` | 领域引擎异常 |
| `D:\develop\soil-web\nginx.logs\error.log` | Nginx 错误 |
| `D:\develop\soil-web\nginx.out.log` | Nginx 启动输出 |

常见问题：

- 启动脚本停在“API 未启动”：看 `api.err.log`，通常是依赖缺失或 `MINIMAX_API_KEY` 未设置。
- 页面能打开但局域网其他机器打不开：先确认防火墙已放行 8080；再看 `netstat -ano | findstr :8080` 是否监听在 `0.0.0.0`。
- Agent 一直“执行中”无输出：看 `api.err.log` 中 dsh 子进程的退出信息；单次任务上限 240 秒。

## 说明

- 该方式用于课程验收演示，不是生产部署；Docker 版本待整体功能稳定后再补。
- 前端 `frontend/dist` 未纳入版本库，克隆后需自行 `npm run build`。
- 会话记录保存在 `server/data/agent_sessions.json`，产出文件保存在 `agent-workspace/outputs/`，两者均不纳入版本库。
