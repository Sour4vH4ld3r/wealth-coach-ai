"""
Chat History Storage Service

Saves conversation history to markdown files organized by user and session.
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class ChatHistoryService:
    """Service for managing chat history in markdown files."""

    def __init__(self, base_dir: str = "./data/chat_history"):
        """
        Initialize chat history service.

        Args:
            base_dir: Base directory for storing chat history
        """
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _get_user_dir(self, user_id: str) -> Path:
        """Get or create user-specific directory."""
        user_dir = self.base_dir / user_id
        user_dir.mkdir(parents=True, exist_ok=True)
        return user_dir

    def _get_session_file(self, user_id: str, session_id: Optional[str] = None) -> Path:
        """
        Get session file path.

        If session_id is None, creates a new session file with timestamp.
        """
        user_dir = self._get_user_dir(user_id)

        if session_id:
            return user_dir / f"{session_id}.md"
        else:
            # Create new session with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            return user_dir / f"session_{timestamp}.md"

    def create_session(
        self,
        user_id: str,
        user_email: str,
        session_id: Optional[str] = None
    ) -> str:
        """
        Create a new chat session file.

        Args:
            user_id: User ID
            user_email: User email for header
            session_id: Optional session ID (generates one if not provided)

        Returns:
            Session file path
        """
        if not session_id:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            session_id = f"session_{timestamp}"

        file_path = self._get_session_file(user_id, session_id)

        # Create initial markdown file with header
        header = f"""# Wealth Coach AI - Chat History

**User**: {user_email}
**Session ID**: {session_id}
**Started**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---

"""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(header)

        logger.info(f"Created chat session: {file_path}")
        return session_id

    def append_message(
        self,
        user_id: str,
        session_id: str,
        role: str,
        content: str,
        metadata: Optional[dict] = None
    ) -> None:
        """
        Append a message to the session file.

        Args:
            user_id: User ID
            session_id: Session ID
            role: Message role ('user' or 'assistant')
            content: Message content
            metadata: Optional metadata (tokens, cost, sources, etc.)
        """
        file_path = self._get_session_file(user_id, session_id)

        # Check if file exists, if not create session first
        if not file_path.exists():
            logger.warning(f"Session file not found, creating: {file_path}")
            self.create_session(user_id, "unknown@user.com", session_id)

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Format message based on role
        if role == "user":
            message_block = f"\n## 👤 User ({timestamp})\n\n{content}\n\n"
        else:  # assistant
            message_block = f"\n## 🤖 Assistant ({timestamp})\n\n{content}\n\n"

            # Add metadata if provided
            if metadata:
                meta_lines = []
                if metadata.get('tokens_used'):
                    meta_lines.append(f"- **Tokens**: {metadata['tokens_used']}")
                if metadata.get('cost'):
                    meta_lines.append(f"- **Cost**: ${metadata['cost']:.4f}")
                if metadata.get('sources_count'):
                    meta_lines.append(f"- **Sources**: {metadata['sources_count']}")
                if metadata.get('cached'):
                    meta_lines.append(f"- **Cached**: ⚡ Yes")

                if meta_lines:
                    message_block += "*Metadata:*\n" + "\n".join(meta_lines) + "\n\n"

        # Append to file
        with open(file_path, 'a', encoding='utf-8') as f:
            f.write(message_block)

        logger.debug(f"Appended {role} message to {file_path}")

    def get_session_history(self, user_id: str, session_id: str) -> Optional[str]:
        """
        Get the full content of a session file.

        Args:
            user_id: User ID
            session_id: Session ID

        Returns:
            Session markdown content or None if not found
        """
        file_path = self._get_session_file(user_id, session_id)

        if not file_path.exists():
            return None

        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()

    def list_user_sessions(self, user_id: str) -> list[dict]:
        """
        List all sessions for a user.

        Args:
            user_id: User ID

        Returns:
            List of session info dicts with id, filename, created, size
        """
        user_dir = self._get_user_dir(user_id)
        sessions = []

        for file_path in user_dir.glob("*.md"):
            stat = file_path.stat()
            sessions.append({
                "session_id": file_path.stem,
                "filename": file_path.name,
                "created": datetime.fromtimestamp(stat.st_ctime),
                "modified": datetime.fromtimestamp(stat.st_mtime),
                "size_bytes": stat.st_size,
            })

        # Sort by creation time, newest first
        sessions.sort(key=lambda x: x['created'], reverse=True)
        return sessions

    def export_session(
        self,
        user_id: str,
        session_id: str,
        output_path: Optional[str] = None
    ) -> str:
        """
        Export a session to a specified location.

        Args:
            user_id: User ID
            session_id: Session ID
            output_path: Optional output path (defaults to downloads)

        Returns:
            Path to exported file
        """
        source_path = self._get_session_file(user_id, session_id)

        if not source_path.exists():
            raise FileNotFoundError(f"Session not found: {session_id}")

        if not output_path:
            output_path = f"./{session_id}_export.md"

        # Copy file
        import shutil
        shutil.copy2(source_path, output_path)

        logger.info(f"Exported session {session_id} to {output_path}")
        return output_path

    def delete_session(self, user_id: str, session_id: str) -> bool:
        """
        Delete a session file.

        Args:
            user_id: User ID
            session_id: Session ID

        Returns:
            True if deleted, False if not found
        """
        file_path = self._get_session_file(user_id, session_id)

        if not file_path.exists():
            return False

        file_path.unlink()
        logger.info(f"Deleted session: {file_path}")
        return True


# Global instance
chat_history_service = ChatHistoryService()
