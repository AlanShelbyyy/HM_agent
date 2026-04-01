from __future__ import annotations

import json
import re
from typing import Any, Dict, Optional

from rag.rag_service import RagSummarizeService
from agent.shared_context import SharedContext
from agent.tools.domain_mock_tools import mock_query_logistics_system


class LogisticsAgent:
    def __init__(self, rag: Optional[RagSummarizeService] = None):
        self.rag = rag or RagSummarizeService()

    def _extract_tracking_no(self, query: str) -> Optional[str]:
        m = re.search(r"(运单|快递|物流|tracking)[^\w]{0,5}([A-Za-z0-9]{8,})", query, re.IGNORECASE)
        if m:
            return m.group(2)
        m2 = re.search(r"\b[A-Za-z0-9]{10,}\b", query)
        return m2.group(0) if m2 else None

    def run(self, query: str, ctx: SharedContext) -> Dict[str, Any]:
        tracking_no = self._extract_tracking_no(query) or "YT202604010001"
        data = mock_query_logistics_system(tracking_no=tracking_no)

        kb = ""
        try:
            kb = self.rag.rag_summarize(f"与物流/快递查询相关的规则与说明。用户问题：{query}")
        except Exception:
            kb = ""

        return {
            "agent": "logistics",
            "tracking_no": tracking_no,
            "result": data,
            "kb_summary": kb,
            "result_json": json.dumps(data, ensure_ascii=False),
        }
