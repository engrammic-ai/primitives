"""Base protocol definitions for EAG agents.

Agents in EAG operate in phases (fast, plan, deep, stitch), each with
distinct output types and budget constraints. This module defines the
abstract interfaces; implementations are private.
"""

from __future__ import annotations

from abc import abstractmethod
from dataclasses import dataclass, field
from enum import StrEnum
from typing import TYPE_CHECKING, Any, Protocol, TypeVar, runtime_checkable

from pydantic import BaseModel, ConfigDict

if TYPE_CHECKING:
    from primitives.eag.agents.tools import ToolProtocol


class AgentPhase(StrEnum):
    """Visit phases for EAG agents."""

    FAST = "fast"
    PLAN = "plan"
    DEEP = "deep"
    STITCH = "stitch"


class BudgetStatus(BaseModel):
    """Budget state exposed to agents in tool responses."""

    model_config = ConfigDict(extra="forbid")

    tokens_remaining: int
    tool_calls_remaining: int
    wrap_up_signal: bool


@dataclass
class BudgetConfig:
    """Per-phase budget configuration."""

    nominal_tokens: int
    hard_tokens: int
    tool_calls_limit: int
    request_limit: int
    soft_signal_ratio: float = 0.69


@dataclass
class AgentConfig:
    """Configuration for an agent instance."""

    phase: AgentPhase
    model: str
    budget: BudgetConfig
    retries: int = 8


DepsT = TypeVar("DepsT", bound="DepsProtocol")
OutputT = TypeVar("OutputT")


@runtime_checkable
class DepsProtocol(Protocol):
    """Minimal interface for per-visit dependencies.

    Implementations carry org/silo/cluster context, buffer for committed
    artifacts, and infrastructure handles. The protocol defines only the
    fields that tools and result types depend on.
    """

    org_id: str
    silo_id: str
    cluster_id: str
    pass_id: str
    seen_node_ids: set[str]
    budget: BudgetStatus
    finalized: bool

    def record_commit(self, event: dict[str, Any]) -> None:
        """Append an event to the commit log."""
        ...


@dataclass
class AgentResult[T]:
    """Result from an agent run."""

    output: T
    finalized: bool
    claims_committed: int
    edges_committed: int
    rejections: int
    tokens_used: int
    tool_calls_used: int
    commit_log: list[dict[str, Any]] = field(default_factory=list)


@runtime_checkable
class AgentProtocol(Protocol[DepsT, OutputT]):
    """Protocol for EAG agents.

    An agent encapsulates a model, system prompt, output type, and budget
    constraints. Tools are registered separately via the ToolProtocol.
    """

    @property
    def phase(self) -> AgentPhase:
        """The phase this agent operates in."""
        ...

    @property
    def config(self) -> AgentConfig:
        """Agent configuration."""
        ...

    @abstractmethod
    async def run(
        self,
        deps: DepsT,
        user_prompt: str,
    ) -> AgentResult[OutputT]:
        """Execute the agent with the given dependencies and prompt.

        The agent runs until it produces an output, calls finalize, or
        exhausts its budget. Tools mutate deps in place.
        """
        ...

    def register_tool(self, tool: ToolProtocol[DepsT]) -> None:
        """Register a tool on this agent."""
        ...
