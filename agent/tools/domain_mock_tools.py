from __future__ import annotations

import random
import time
from typing import Any, Dict, Optional


def _sleep_ms(min_ms: int = 150, max_ms: int = 450) -> None:
    time.sleep(random.uniform(min_ms, max_ms) / 1000.0)


def mock_query_order_system(order_id: str, user_id: Optional[str] = None) -> Dict[str, Any]:
    _sleep_ms()
    status_pool = ["已下单", "已支付", "已发货", "已完成", "已取消", "退款中", "已退款"]
    status = random.choice(status_pool)
    return {
        "source": "mock_order_system",
        "order_id": order_id,
        "user_id": user_id,
        "status": status,
        "items": [
            {"sku": f"SKU-{random.randint(1000, 9999)}", "name": "扫地机器人耗材套装", "qty": 1},
        ],
        "created_at": "2026-03-31 20:15:00",
        "updated_at": "2026-04-01 09:20:00",
    }


def mock_query_product_system(keyword_or_sku: str) -> Dict[str, Any]:
    _sleep_ms()
    price = round(random.uniform(199.0, 3999.0), 2)
    stock = random.randint(0, 200)
    return {
        "source": "mock_product_system",
        "query": keyword_or_sku,
        "sku": f"SKU-{random.randint(1000, 9999)}",
        "name": f"{keyword_or_sku}（示例商品）",
        "price": price,
        "currency": "CNY",
        "stock": stock,
        "sale_status": "有货" if stock > 0 else "缺货",
    }


def mock_query_logistics_system(tracking_no: str) -> Dict[str, Any]:
    _sleep_ms()
    steps = [
        {"time": "2026-03-31 21:10:00", "status": "已揽收", "location": "深圳转运中心"},
        {"time": "2026-04-01 02:30:00", "status": "运输中", "location": "华南干线"},
        {"time": "2026-04-01 09:10:00", "status": "派送中", "location": "合肥配送站"},
    ]
    return {
        "source": "mock_logistics_system",
        "tracking_no": tracking_no,
        "carrier": random.choice(["顺丰", "中通", "圆通", "京东物流"]),
        "latest_status": steps[-1]["status"],
        "trace": steps,
    }
