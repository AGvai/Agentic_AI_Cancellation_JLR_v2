"""Data models for JLR cancellation responses."""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List


class CancellationStatus(Enum):
    """Overall outcome status returned by a cancellation agent."""

    APPROVED = auto()
    PENDING_RETAILER = auto()
    PENDING_STORE = auto()
    INELIGIBLE = auto()
    REQUIRES_MANUAL_REVIEW = auto()


@dataclass
class CancellationResponse:
    """Structured response produced by a cancellation agent.

    Attributes:
        status: The outcome of the agent's evaluation.
        message: A human-readable summary of the outcome.
        next_steps: Ordered list of actions the customer should take.
        contact_details: Relevant contact information (phone, email, hours).
        estimated_refund_days: Expected refund timeline in working days where
            applicable; ``None`` when no refund is due.
        agent_name: Identifier of the sub-agent that produced this response.
    """

    status: CancellationStatus
    message: str
    next_steps: List[str] = field(default_factory=list)
    contact_details: List[str] = field(default_factory=list)
    estimated_refund_days: int | None = None
    agent_name: str = ""
