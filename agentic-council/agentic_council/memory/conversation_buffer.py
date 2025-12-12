"""Conversation buffer for maintaining context."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from collections import deque


@dataclass
class Message:
    """A single message in the conversation."""
    role: str  # "user", "assistant", "system", "agent"
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }


class ConversationBuffer:
    """Manages conversation history with size limits."""

    def __init__(
        self,
        max_messages: int = 100,
        max_tokens: int = 50000,
    ):
        """Initialize conversation buffer.

        Args:
            max_messages: Maximum number of messages to keep
            max_tokens: Approximate maximum tokens to keep
        """
        self.max_messages = max_messages
        self.max_tokens = max_tokens
        self._messages: deque[Message] = deque(maxlen=max_messages)
        self._estimated_tokens = 0

    def add(
        self,
        role: str,
        content: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Add a message to the buffer.

        Args:
            role: Message role
            content: Message content
            metadata: Optional metadata
        """
        message = Message(
            role=role,
            content=content,
            metadata=metadata or {},
        )

        # Estimate tokens (rough approximation)
        tokens = len(content.split()) * 1.3

        # Remove old messages if needed
        while (
            self._estimated_tokens + tokens > self.max_tokens
            and len(self._messages) > 0
        ):
            old_message = self._messages.popleft()
            self._estimated_tokens -= len(old_message.content.split()) * 1.3

        self._messages.append(message)
        self._estimated_tokens += tokens

    def get_messages(
        self,
        limit: int | None = None,
        roles: list[str] | None = None,
    ) -> list[Message]:
        """Get messages from the buffer.

        Args:
            limit: Maximum number of messages to return
            roles: Filter by specific roles

        Returns:
            List of messages
        """
        messages = list(self._messages)

        if roles:
            messages = [m for m in messages if m.role in roles]

        if limit:
            messages = messages[-limit:]

        return messages

    def get_formatted(
        self,
        limit: int | None = None,
        include_timestamps: bool = False,
    ) -> str:
        """Get formatted conversation history.

        Args:
            limit: Maximum number of messages
            include_timestamps: Include timestamps in output

        Returns:
            Formatted string
        """
        messages = self.get_messages(limit=limit)
        lines = []

        for msg in messages:
            if include_timestamps:
                ts = msg.timestamp.strftime("%H:%M:%S")
                lines.append(f"[{ts}] {msg.role.upper()}: {msg.content}")
            else:
                lines.append(f"{msg.role.upper()}: {msg.content}")

        return "\n".join(lines)

    def get_for_llm(
        self,
        limit: int | None = None,
    ) -> list[dict[str, str]]:
        """Get messages formatted for LLM API.

        Args:
            limit: Maximum number of messages

        Returns:
            List of role/content dicts
        """
        messages = self.get_messages(limit=limit)

        # Map agent roles to assistant
        role_mapping = {
            "user": "user",
            "assistant": "assistant",
            "agent": "assistant",
            "system": "system",
        }

        return [
            {
                "role": role_mapping.get(m.role, "assistant"),
                "content": m.content,
            }
            for m in messages
        ]

    def clear(self) -> None:
        """Clear all messages."""
        self._messages.clear()
        self._estimated_tokens = 0

    def __len__(self) -> int:
        return len(self._messages)

    @property
    def estimated_tokens(self) -> int:
        return int(self._estimated_tokens)

    def to_dict(self) -> dict[str, Any]:
        """Convert buffer to dictionary."""
        return {
            "messages": [m.to_dict() for m in self._messages],
            "estimated_tokens": self.estimated_tokens,
        }
