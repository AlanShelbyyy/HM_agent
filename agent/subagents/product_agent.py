from __future__ import annotations

import json
import re
from typing import Any, Dict, Optional

from rag.rag_service import RagSummarizeService
from agent.shared_context import SharedContext
from agent.tools.domain_mock_tools import mock_query_product_system


class ProductAgent:
    def __init__(self, rag: Optional[RagSummarizeService] = None):
        self.rag = rag or RagSummarizeService()

    def _extract_keyword_or_sku(self, query: str) -> str:
        m = re.search(r"\bSKU-\d{4,}\b", query, re.IGNORECASE)
        if m:
            return m.group(0).upper()
        m2 = re.search(r"(商品|product|sku|库存|价格|多少钱)\s*[:：]?\s*([^\s，。,]{2,20})", query, re.IGNORECASE)
        if m2:
            return m2.group(2)
        return query.strip()[:20] or "扫地机器人"

    def run(self, query: str, ctx: SharedContext) -> Dict[str, Any]:
        keyword = self._extract_keyword_or_sku(query)
        data = mock_query_product_system(keyword_or_sku=keyword)

        kb = ""
        try:
            kb = self.rag.rag_summarize(f"与商品查询/库存/价格相关的规则与说明。用户问题：{query}")
        except Exception:
            kb = ""

        return {
            "agent": "product",
            "query": keyword,
            "result": data,
            "kb_summary": kb,
            "result_json": json.dumps(data, ensure_ascii=False),
        }
