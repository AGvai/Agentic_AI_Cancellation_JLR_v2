"""Data models for JLR cancellation requests."""

from dataclasses import dataclass, field
from datetime import date
from enum import Enum, auto
from typing import Optional


class CancellationType(Enum):
    """Supported JLR UK cancellation journeys."""

    VEHICLE_ORDER = auto()
    MERCHANDISE = auto()
    WARRANTY = auto()
    SUBSCRIPTION = auto()
    UNKNOWN = auto()


@dataclass
class CancellationRequest:
    """Represents a customer cancellation request.

    Attributes:
        cancellation_type: The category of the cancellation journey.
        order_reference: Customer-provided order or reservation reference.
        customer_name: Full name of the requesting customer.
        contact_email: Customer email address for follow-up correspondence.
        request_date: Date the cancellation request is being submitted.
        notes: Any additional free-text context supplied by the customer.
        contract_signed: For vehicle orders – whether a purchase/finance
            contract has already been signed with the retailer.
        days_since_purchase: Used by warranty and subscription agents to
            determine whether the cooling-off period is still active.
        goods_returned: For merchandise – whether the goods have already
            been dispatched back to the store.
        is_personalised_item: For merchandise – whether the item is
            personalised/custom-made (excluded from standard return rights).
        subscription_active: For subscriptions – whether the subscription is
            currently active or has already expired.
        vehicle_sold: For subscriptions – whether the vehicle has been sold or
            the lease has ended.
        claim_made: For warranties – whether a warranty claim has already been
            paid or is in progress.
    """

    cancellation_type: CancellationType
    order_reference: str
    customer_name: str
    contact_email: str
    request_date: date = field(default_factory=date.today)
    notes: str = ""
    # Vehicle-order specific
    contract_signed: bool = False
    # Warranty / subscription specific
    days_since_purchase: Optional[int] = None
    # Merchandise specific
    goods_returned: bool = False
    is_personalised_item: bool = False
    # Subscription specific
    subscription_active: bool = True
    vehicle_sold: bool = False
    # Warranty specific
    claim_made: bool = False
