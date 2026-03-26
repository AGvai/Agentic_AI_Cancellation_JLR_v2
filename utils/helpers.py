"""Shared helper utilities for the JLR Agentic AI Cancellation system."""

from models.cancellation_request import CancellationType
from models.cancellation_response import CancellationResponse


# ---------------------------------------------------------------------------
# Intent parsing
# ---------------------------------------------------------------------------

_VEHICLE_KEYWORDS = {
    "vehicle",
    "car",
    "order",
    "reservation",
    "reserve",
    "deposit",
    "jaguar",
    "land rover",
    "discovery",
    "defender",
    "range rover",
    "evoque",
    "freelander",
}

_MERCHANDISE_KEYWORDS = {
    "merchandise",
    "shop",
    "store",
    "clothing",
    "accessory",
    "accessories",
    "lifestyle",
    "product",
    "item",
    "goods",
    "return",
    "refund item",
}

_WARRANTY_KEYWORDS = {
    "warranty",
    "approved warranty",
    "extended warranty",
    "cover",
    "protection plan",
    "service plan",
}

_SUBSCRIPTION_KEYWORDS = {
    "subscription",
    "incontrol",
    "in-control",
    "connected",
    "services",
    "wifi",
    "wi-fi",
    "remote",
    "pro services",
    "data plan",
    "renewal",
    "my incontrol",
}


def parse_intent(user_input: str) -> CancellationType:
    """Infer the cancellation type from a free-text user input.

    The function uses keyword matching against the four JLR cancellation
    journey categories.  The category with the most keyword hits wins; ties
    default to ``UNKNOWN``.

    Args:
        user_input: Raw natural-language text supplied by the customer.

    Returns:
        The most likely :class:`~models.cancellation_request.CancellationType`.
    """
    lowered = user_input.lower()
    scores: dict[CancellationType, int] = {
        CancellationType.VEHICLE_ORDER: 0,
        CancellationType.MERCHANDISE: 0,
        CancellationType.WARRANTY: 0,
        CancellationType.SUBSCRIPTION: 0,
    }

    for keyword in _VEHICLE_KEYWORDS:
        if keyword in lowered:
            scores[CancellationType.VEHICLE_ORDER] += 1

    for keyword in _MERCHANDISE_KEYWORDS:
        if keyword in lowered:
            scores[CancellationType.MERCHANDISE] += 1

    for keyword in _WARRANTY_KEYWORDS:
        if keyword in lowered:
            scores[CancellationType.WARRANTY] += 1

    for keyword in _SUBSCRIPTION_KEYWORDS:
        if keyword in lowered:
            scores[CancellationType.SUBSCRIPTION] += 1

    best_type = max(scores, key=lambda k: scores[k])
    return best_type if scores[best_type] > 0 else CancellationType.UNKNOWN


# ---------------------------------------------------------------------------
# Response formatting
# ---------------------------------------------------------------------------

def format_response(response: CancellationResponse) -> str:
    """Render a :class:`~models.cancellation_response.CancellationResponse`
    as a human-readable string suitable for CLI output.

    Args:
        response: The response object returned by a cancellation agent.

    Returns:
        A formatted multi-line string.
    """
    lines: list[str] = [
        "",
        "=" * 60,
        f"  JLR Cancellation Agent: {response.agent_name}",
        "=" * 60,
        f"  Status  : {response.status.name}",
        f"  Message : {response.message}",
    ]

    if response.estimated_refund_days is not None:
        lines.append(
            f"  Refund  : up to {response.estimated_refund_days} working day(s)"
        )

    if response.next_steps:
        lines.append("")
        lines.append("  Next Steps:")
        for i, step in enumerate(response.next_steps, start=1):
            lines.append(f"    {i}. {step}")

    if response.contact_details:
        lines.append("")
        lines.append("  Contact Details:")
        for detail in response.contact_details:
            lines.append(f"    • {detail}")

    lines.append("=" * 60)
    lines.append("")
    return "\n".join(lines)
