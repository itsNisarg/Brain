from collections.abc import Sequence
from typing import Any

from agent_framework import BaseHistoryProvider, Message


# class GoalContextProvider(BaseHistoryProvider):
#     def __init__(self, session_name: str) -> None:
#         super().__init__("goal-history", load_messages=True)
#         self._file = f"interactions/{session_name}/goal_details.json"

#     async def get_messages(
#         self,
#         session_id: str | None,
#         *,
#         state: dict[str, Any] | None = None,
#         **kwargs: Any,
#     ) -> list[Message]:
#         key = (state or {}).get(self.source_id, {}).get("history_key", session_id or "default")
#         rows = await self._db.load_messages(key)
#         return [Message.from_dict(row) for row in rows]

#     async def save_messages(
#         self,
#         session_id: str | None,
#         messages: Sequence[Message],
#         *,
#         state: dict[str, Any] | None = None,
#         **kwargs: Any,
#     ) -> None:
#         if not messages:
#             return
#         if state is not None:
#             key = state.setdefault(self.source_id, {}).setdefault("history_key", session_id or "default")
#         else:
#             key = session_id or "default"
#         await self._db.save_messages(key, [m.to_dict() for m in messages])