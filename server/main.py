from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

BASE = Path(__file__).resolve().parents[1]
WORKSPACE = BASE / "agent-workspace"
DSH_HOME = BASE / "dsh-home"
PATCH = BASE / "agent" / "dsh" / "minimax.patch.yml"
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
    cmd = [
        NODE,
        str(DSH_BIN),
        "--profile",
        "headless",
        "--patch",
        str(PATCH),
        "--json",
        req.message,
    ]
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
        detail = (stderr or stdout)[-2000:]
        raise HTTPException(502, f"agent failed ({proc.returncode}): {detail}")
    return ChatResponse(
        answer=answer,
        thinking=thinking or None,
        session_id=session_id,
        events=count,
    )
