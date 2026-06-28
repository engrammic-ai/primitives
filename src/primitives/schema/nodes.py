"""Ephemeral node models for source content verification.

These are transient artifacts used during SAGE verification and are not
part of the permanent CITE graph. They exist only between learn() ingestion
and Claim promotion to Fact.
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class Source(BaseModel):
    """Ephemeral node holding source content for verification.

    Created when an agent provides source_content with learn().
    Deleted after the linked Claim is promoted to Fact by SAGE.
    The evidence_uri is preserved on the Claim/Fact for audit.
    """

    id: UUID
    silo_id: str
    content: str  # Full source text (max 4096 chars)
    evidence_uri: str  # Original URI for audit trail
    content_hash: str  # SHA256 for dedup
    created_at: datetime
    # No embedding - not searchable, exists only for SAGE verification
