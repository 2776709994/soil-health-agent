from __future__ import annotations

import asyncio
import json
import os
import uuid
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

BASE = Path(__file__).resolve().parents[1]
WORKSPACE = BASE / "agent-workspace"
DSH_HOME = BASE / "dsh-home"
PATCH = BASE / "agent" / "dsh" / "minimax.patch.yml"
OUTPUTS = WORKSPACE / "outputs"
NODE = os.environ.get("NODE_BIN", "node")
DSH_BIN = Path(
    os.environ.get(
        "DSH_BIN",
        r"D:/develop/dsh-runtime/node_modules/@deepseek-ai/dsh/lib/bin.js",
    )
)

app = FastAPI(title="Soil Health Agent Bridge", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:8899",
        "http://localhost:8899",
        "http://127.0.0.1:5173",
        "http://localhost:5173",
        "http://127.0.0.1:4173",
        "http://localhost:4173",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=8000)


class ChatResponse(BaseModel):
    answer: str
    thinking: str | None = None
    session_id: str | None = None
    events: int = 0


class AgentRequest(BaseModel):
    message: str = Field(min_length=1, max_length=8000)
    session_id: str | None = None
    task_id: str | None = None


ACTIVE_TASKS: dict[str, asyncio.subprocess.Process] = {}


def _parse_events(stdout: str) -> tuple[str, str, str | None, int]:
    thinking: list[str] = []
    texts: list[str] = []
    final = ""
    session_id: str | None = None
    count = 0
    for line in stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            event: dict[str, Any] = json.loads(line)
        except json.JSONDecodeError:
            continue
        count += 1
        kind = event.get("type")
        if kind == "thinking" and event.get("text"):
            thinking.append(str(event["text"]))
        elif kind == "text" and event.get("text"):
            texts.append(str(event["text"]))
        elif kind == "final":
            final = str(event.get("text") or "")
            session_id = event.get("sessionId") or session_id
        elif kind == "session":
            session_id = event.get("sessionId") or session_id
    answer = final.strip() or "\n".join(t.strip() for t in texts if t.strip()).strip()
    return answer, "\n\n".join(thinking).strip(), session_id, count


def _agent_command(message: str, session_id: str | None = None) -> list[str]:
    cmd = [
        NODE,
        str(DSH_BIN),
        "--profile",
        "headless",
        "--patch",
        str(PATCH),
    ]
    if session_id:
        cmd += ["--session-id", session_id]
    cmd += ["--json", message]
    return cmd


@app.get("/api/health")
def health() -> dict[str, Any]:
    return {
        "ok": True,
        "workspace": str(WORKSPACE),
        "dsh_bin": str(DSH_BIN),
        "dsh_exists": DSH_BIN.exists(),
        "patch_exists": PATCH.exists(),
        "key_configured": bool(os.environ.get("MINIMAX_API_KEY")),
    }


@app.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest) -> ChatResponse:
    if not DSH_BIN.exists():
        raise HTTPException(500, f"dsh runtime not found: {DSH_BIN}")
    if not PATCH.exists():
        raise HTTPException(500, f"patch not found: {PATCH}")
    if not os.environ.get("MINIMAX_API_KEY"):
        raise HTTPException(500, "MINIMAX_API_KEY is not set on the server")

    env = os.environ.copy()
    env["DSH_HOME"] = str(DSH_HOME)
    concise = (
        "请用不超过 800 字回答，先给结论和关键依据，"
        "不要展开与问题无关的逐地块资源分配；需要详细计算时先说明下一步。\n\n"
        "用户问题：" + req.message
    )
    cmd = _agent_command(concise)
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=str(WORKSPACE),
            env=env,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout_b, stderr_b = await asyncio.wait_for(proc.communicate(), timeout=240)
    except asyncio.TimeoutError:
        raise HTTPException(504, "agent timed out after 240s")
    except OSError as exc:
        raise HTTPException(500, f"failed to start agent: {exc}") from exc

    stdout = stdout_b.decode("utf-8", errors="replace")
    stderr = stderr_b.decode("utf-8", errors="replace")
    answer, thinking, session_id, count = _parse_events(stdout)
    if proc.returncode != 0 or not answer:
        if "max-tokens" in stdout or "max_tokens" in stdout:
            raise HTTPException(
                502,
                "模型输出达到 max_tokens，未产出最终答案。请缩短问题或重试。",
            )
        raise HTTPException(502, f"agent failed ({proc.returncode})")
    return ChatResponse(
        answer=answer,
        thinking=thinking or None,
        session_id=session_id,
        events=count,
    )


@app.post("/api/agent/stream")
async def agent_stream(req: AgentRequest):
    if not DSH_BIN.exists():
        raise HTTPException(500, f"dsh runtime not found: {DSH_BIN}")
    if not PATCH.exists():
        raise HTTPException(500, f"patch not found: {PATCH}")
    if not os.environ.get("MINIMAX_API_KEY"):
        raise HTTPException(500, "MINIMAX_API_KEY is not set on the server")

    task_id = req.task_id or f"task-{uuid.uuid4().hex[:10]}"
    env = os.environ.copy()
    env["DSH_HOME"] = str(DSH_HOME)
    task = (
        "请按步骤执行；先给结论，再给必要计算。单次最终回答控制在 1200 字内；"
        "详细台账、清单或方案写入 outputs/。\n\n任务：" + req.message
    )
    cmd = _agent_command(task, req.session_id)
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=str(WORKSPACE),
            env=env,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
    except OSError as exc:
        raise HTTPException(500, f"failed to start agent: {exc}") from exc

    ACTIVE_TASKS[task_id] = proc

    async def gen():
        final_text = ""
        max_tokens_hit = False
        saw_final = False
        try:
            yield "data: " + json.dumps({"type": "task", "taskId": task_id}, ensure_ascii=False) + "\n\n"
            while True:
                line = await proc.stdout.readline()
                if not line:
                    break
                text = line.decode("utf-8", errors="replace").strip()
                if not text:
                    continue
                yield "data: " + text + "\n\n"
                try:
                    event = json.loads(text)
                except json.JSONDecodeError:
                    continue
                kind = event.get("type")
                if kind == "final":
                    final_text = str(event.get("text") or "")
                    saw_final = True
                if kind == "turn_end" and (event.get("reason") or {}).get("kind") == "max-tokens":
                    max_tokens_hit = True
            stderr_b = await proc.stderr.read()
            returncode = await proc.wait()
            if not final_text:
                message = (
                    "模型输出达到 max_tokens，未产出最终答案。请缩短问题或重试。"
                    if max_tokens_hit
                    else f"Agent 未产出最终答案（exit {returncode}）。"
                )
                yield "data: " + json.dumps(
                    {"type": "agent_error", "message": message},
                    ensure_ascii=False,
                ) + "\n\n"
            elif returncode != 0 and not saw_final:
                yield "data: " + json.dumps(
                    {"type": "agent_error", "message": f"Agent 异常退出（exit {returncode}）。"},
                    ensure_ascii=False,
                ) + "\n\n"
        finally:
            ACTIVE_TASKS.pop(task_id, None)
            if proc.returncode is None:
                try:
                    proc.kill()
                except ProcessLookupError:
                    pass

    return StreamingResponse(
        gen(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.post("/api/agent/{task_id}/cancel")
async def cancel_agent(task_id: str):
    proc = ACTIVE_TASKS.get(task_id)
    if not proc:
        return {"ok": False, "message": "task not running"}
    try:
        proc.kill()
    except ProcessLookupError:
        pass
    return {"ok": True}


@app.get("/api/agent/artifacts")
def list_artifacts():
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    rows = []
    for path in sorted(OUTPUTS.rglob("*")):
        if path.is_file():
            stat = path.stat()
            rows.append({
                "name": path.name,
                "path": str(path.relative_to(OUTPUTS)).replace("\\", "/"),
                "size": stat.st_size,
                "mtime": int(stat.st_mtime),
            })
    return {"files": rows[-100:]}


@app.get("/api/agent/artifact")
def read_artifact(path: str):
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    target = (OUTPUTS / path).resolve()
    if not str(target).startswith(str(OUTPUTS.resolve())) or not target.is_file():
        raise HTTPException(404, "artifact not found")
    try:
        content = target.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        raise HTTPException(500, f"read failed: {exc}") from exc
    return {"name": target.name, "path": path, "content": content[:200_000]}
