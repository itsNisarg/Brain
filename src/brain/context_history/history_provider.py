from datetime import datetime
from collections.abc import Sequence
from typing import Any
import logging

from agent_framework import BaseHistoryProvider, InMemoryHistoryProvider, Message
from tinydb import Query, TinyDB


# Create a logger instance for this module
logger = logging.getLogger(__name__)


class GlobalAuditProvider(BaseHistoryProvider):
    def __init__(self, db: TinyDB) -> None:
        # load_messages=False ensures this doesn't accidentally load into the agent's context.
        # store_context_messages=True ensures it captures the full prompt + response.
        super().__init__(
            "global_audit", load_messages=False, store_context_messages=True
        )
        if db is None:
            db = TinyDB(".interactions/auto_history.json")
        self._db = db
        self.audit_table = self._db.table("global_audit")

    async def get_messages(
        self,
        session_id: str | None,
        *,
        state: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> list[Message]:
        # Always return empty to the Agent so we don't contaminate the LLM's context.
        return []

    async def save_messages(
        self,
        session_id: str | None,
        messages: Sequence[Message],
        *,
        state: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> None:
        if not messages:
            return

        # Save every interaction globally, tagged with a timestamp and session_id
        logger.info(f"Saving {len(messages)} messages to GlobalAuditProvider for session_id: {session_id}")
        self.audit_table.insert(
            {
                "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S"),
                "session_id": session_id or "default",
                "messages": [m.to_dict() for m in messages],
            }
        )


class GoalContextProvider(BaseHistoryProvider):

    def __init__(self, db: TinyDB) -> None:
        super().__init__("goal_history", load_messages=True)
        if db is None:
            db = TinyDB(".interactions/auto_history.json")
        self._db = db
        self.goal_history = self._db.table("goal_history")

    async def get_messages(
        self,
        session_id: str | None,
        *,
        state: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> list[Message]:
        key = (
            (state or {})
            .get(self.source_id, {})
            .get("history_key", session_id or "default")
        )
        logger.info(f"Retrieving messages from GoalContextProvider with key: {key}")
        if not key:
            rows = []
        else:
            query = Query()
            condition = query[key].exists()
            docs = self.goal_history.search(cond=condition)
            rows = [row for doc in docs if key in doc for row in doc[key]]
        logger.info(f"Found {len(rows)} messages")
        return [Message.from_dict(row) for row in rows]

    async def save_messages(
        self,
        session_id: str | None,
        messages: Sequence[Message],
        *,
        state: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> None:
        if not messages:
            return
        if state is not None:
            key = state.setdefault(self.source_id, {}).setdefault(
                "history_key", session_id or "default"
            )
        else:
            key = session_id or "default"
        logger.info(f"Saving {len(messages)} messages to GoalContextProvider under key: {key}")
        self.goal_history.insert({key: [m.to_dict() for m in messages]})


class ScreenAnalysisContextProvider(BaseHistoryProvider):
    
    def __init__(self, db: TinyDB) -> None:
        super().__init__("screen_analysis_history", load_messages=True)
        if db is None:
            db = TinyDB(".interactions/auto_history.json")
        self._db = db
        self.screen_analysis_history = self._db.table("screen_analysis_history")

    async def get_messages(
        self,
        session_id: str | None,
        *,
        state: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> list[Message]:
        key = (
            (state or {})
            .get(self.source_id, {})
            .get("history_key", session_id or "default")
        )
        logger.info(f"Retrieving messages from ScreenAnalysisContextProvider with key: {key}")
        if not key:
            rows = []
        else:
            query = Query()
            condition = query[key].exists()
            docs = self.screen_analysis_history.search(cond=condition)
            rows = [row for doc in docs if key in doc for row in doc[key]]
            rows = rows[-1] if rows else []  # Only return the most recent screen analysis result for context
        logger.info(f"Retrieved {len(rows)} messages")
        return [Message.from_dict(row) for row in rows]

    async def save_messages(
        self,
        session_id: str | None,
        messages: Sequence[Message],
        *,
        state: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> None:
        if not messages:
            return
        if state is not None:
            key = state.setdefault(self.source_id, {}).setdefault(
                "history_key", session_id or "default"
            )
        else:
            key = session_id or "default"
        logger.info(f"Saving {len(messages)} messages to ScreenAnalysisContextProvider under key: {key}")
        self.screen_analysis_history.insert({key: [m.to_dict() for m in messages]})
