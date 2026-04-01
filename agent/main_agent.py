from __future__ import annotations

import json
import uuid
from typing import Any, Dict, Generator, Optional

from langchain_core.messages import HumanMessage, SystemMessage

from agent.shared_context import SharedContext
from agent.subagents.order_agent import OrderAgent
from agent.subagents.product_agent import ProductAgent
from agent.subagents.logistics_agent import LogisticsAgent
from model.factory import chat_model
from rag.rag_service import RagSummarizeService


class MainAgent:
    """
    主 Agent：意图识别 -> 任务分发 -> 汇总 -> 结合RAG生成最终回复（流式输出）
    """

    def __init__(self):
        self.rag = RagSummarizeService()
        self.order_agent = OrderAgent(rag=self.rag)
        self.product_agent = ProductAgent(rag=self.rag)
        self.logistics_agent = LogisticsAgent(rag=self.rag)

    def _intent_by_rule(self, query: str) -> str:
        q = query.lower()
        if any(k in q for k in ["物流", "快递", "运单", "tracking", "配送", "派送"]):
            return "logistics"
        if any(k in q for k in ["订单", "下单", "支付", "退款", "order"]):
            return "order"
        if any(k in q for k in ["商品", "sku", "库存", "价格", "多少钱", "参数", "规格", "product"]):
            return "product"
        return "general"

    def _intent_by_llm(self, query: str) -> Optional[str]:
        try:
            sys = SystemMessage(
                content=(
                    "你是一个意图识别器。只输出JSON，不要解释。\n"
                    '可选intent: "order", "product", "logistics", "general"\n'
                    '输出格式: {"intent":"...","confidence":0-1}\n'
                )
            )
            msg = HumanMessage(content=f"用户输入：{query}")
            text = chat_model.invoke([sys, msg]).content.strip()
            obj = json.loads(text)
            intent = str(obj.get("intent", "")).strip()
            conf = float(obj.get("confidence", 0))
            if intent in {"order", "product", "logistics", "general"} and conf >= 0.45:
                return intent
            return None
        except Exception:
            return None

    def _choose_intent(self, query: str) -> str:
        intent = self._intent_by_llm(query)
        if intent:
            return intent
        return self._intent_by_rule(query)

    def execute_stream(self, query: str, ctx: Optional[SharedContext] = None) -> Generator[str, None, None]:
        ctx = ctx or SharedContext()
        if not ctx.session_id:
            ctx.session_id = uuid.uuid4().hex

        intent = self._choose_intent(query)
        yield f"[路由] intent={intent}\n"

        sub_result: Dict[str, Any] = {}
        if intent == "order":
            yield "[子Agent] 正在查询订单系统...\n"
            sub_result = self.order_agent.run(query, ctx)
        elif intent == "product":
            yield "[子Agent] 正在查询商品系统...\n"
            sub_result = self.product_agent.run(query, ctx)
        elif intent == "logistics":
            yield "[子Agent] 正在查询物流系统...\n"
            sub_result = self.logistics_agent.run(query, ctx)
        else:
            sub_result = {"agent": "general"}

        yield "[RAG] 正在检索知识库...\n"
        rag_summary = ""
        try:
            rag_summary = self.rag.rag_summarize(query)
        except Exception:
            rag_summary = ""

        system_prompt = (
            "你是一个智能客服主助手。你会收到：用户问题、子Agent返回的JSON结果、以及RAG检索摘要。\n"
            "要求：\n"
            "- 先给出直接结论/答案，再给必要的依据。\n"
            "- 如果子Agent结果为空或不完整，要说明缺失信息并给出用户需要补充什么。\n"
            "- 输出使用简体中文。\n"
        )

        user_payload = {
            "user_query": query,
            "intent": intent,
            "sub_agent_result": sub_result,
            "rag_summary": rag_summary,
            "shared_context": {"user_id": ctx.user_id, "session_id": ctx.session_id},
        }

        yield "[主Agent] 正在生成回复...\n"
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=json.dumps(user_payload, ensure_ascii=False)),
        ]

        for chunk in chat_model.stream(messages):
            content = getattr(chunk, "content", None)
            if content:
                yield content

    def execute_sse(self, query: str, ctx: Optional[SharedContext] = None) -> Generator[str, None, None]:
        """
        以SSE帧格式输出，适用于FastAPI/HTTP流式传输。
        """
        for piece in self.execute_stream(query, ctx=ctx):
            data = piece.replace("\r", "").replace("\n", "\\n")
            yield f"data: {data}\n\n"
