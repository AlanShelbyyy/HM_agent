from __future__ import annotations

import json
import re
from typing import Any, Dict, Optional

from rag.rag_service import RagSummarizeService
from agent.shared_context import SharedContext
from agent.tools.domain_mock_tools import mock_query_order_system


class OrderAgent:
    def __init__(self, rag: Optional[RagSummarizeService] = None):
        self.rag = rag or RagSummarizeService()

    def _extract_order_id(self, query: str) -> Optional[str]:
        m = re.search(r"(订单|order)[^\d]{0,5}(\d{6,})", query, re.IGNORECASE)
        if m:
            return m.group(2)
        m2 = re.search(r"\b\d{8,}\b", query)
        return m2.group(0) if m2 else None

    def run(self, query: str, ctx: SharedContext) -> Dict[str, Any]:
        order_id = self._extract_order_id(query) or "10000001"
        data = mock_query_order_system(order_id=order_id, user_id=ctx.user_id)

        kb = ""
        try:
            kb = self.rag.rag_summarize(f"与订单查询相关的规则与说明。用户问题：{query}")
        except Exception:
            kb = ""

        return {
            "agent": "order",
            "order_id": order_id,
            "result": data,
            "kb_summary": kb,
            "result_json": json.dumps(data, ensure_ascii=False),
        }
