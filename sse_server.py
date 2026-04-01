from __future__ import annotations

from fastapi import FastAPI
from fastapi.responses import StreamingResponse

from agent.main_agent import MainAgent
from agent.shared_context import SharedContext


app = FastAPI()
agent = MainAgent()


@app.get("/chat/stream")
def chat_stream(q: str, user_id: str | None = None, session_id: str | None = None):
    ctx = SharedContext(user_id=user_id, session_id=session_id)

    return StreamingResponse(
        agent.execute_sse(q, ctx=ctx),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )


@app.get("/healthz")
def healthz():
    return {"ok": True}
