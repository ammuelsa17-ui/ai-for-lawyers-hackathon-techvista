from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class CMSAdapter(ABC):
    """Abstract interface for Case Management System (CMS) interactions.
    
    Non-negotiable contract:
    Every write action requires a non-empty `approved_by` string.
    Every task created must include source citation identifiers (`source_doc_id`, `source_chunk_id`).
    """

    @staticmethod
    def validate_approval(approved_by: str) -> str:
        if not approved_by or not approved_by.strip():
            raise ValueError("approved_by is required for all CMS operations and cannot be empty.")
        return approved_by.strip()

    @staticmethod
    def validate_citations(source_doc_id: str, source_chunk_id: str) -> tuple[str, str]:
        if not source_doc_id or not source_doc_id.strip():
            raise ValueError("source_doc_id is required for task creation.")
        if not source_chunk_id or not source_chunk_id.strip():
            raise ValueError("source_chunk_id is required for task creation.")
        return source_doc_id.strip(), source_chunk_id.strip()

    @abstractmethod
    def create_matter(
        self,
        title: str,
        client_name: str,
        practice_area: str,
        approved_by: str,
    ) -> Dict[str, Any]:
        """Create a new case matter in CMS. Requires attorney approval."""
        pass

    @abstractmethod
    def create_task(
        self,
        matter_id: str,
        title: str,
        due_date: str,
        rule_reference: Optional[str],
        source_doc_id: str,
        source_chunk_id: str,
        approved_by: str,
    ) -> Dict[str, Any]:
        """Create or approve an actionable task/deadline in CMS with citations. Requires attorney approval."""
        pass

    @abstractmethod
    def add_note(
        self,
        matter_id: str,
        content: str,
        approved_by: str,
    ) -> Dict[str, Any]:
        """Append a note to an existing matter in CMS. Requires attorney approval."""
        pass

    @abstractmethod
    def tag_document(
        self,
        document_id: str,
        matter_id: str,
        tag: str,
        approved_by: str,
    ) -> Dict[str, Any]:
        """Tag/categorize a matter document in CMS. Requires attorney approval."""
        pass
