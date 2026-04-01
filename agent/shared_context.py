from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class SharedContext:
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    memory: Dict[str, Any] = field(default_factory=dict)

    def get(self, key: str, default: Any = None) -> Any:
        return self.memory.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self.memory[key] = value
