"""Merchandise / lifestyle-store cancellation and returns agent.

Journey summary (JLR UK public store terms)
--------------------------------------------
* Standard direct e-commerce flow.
* Customer may cancel before dispatch.
* Customer may cancel within 30 days of delivery.
* Goods must be returned within 14 days of cancellation.
* Refund issued within 14 days of store receiving goods back (or evidence of
  return).
* Personalised, made-to-measure, custom-made, and perishable goods are
  excluded from the standard cancellation right.
* Damaged / defective goods follow a separate support path.
"""

from models.cancellation_request import CancellationRequest
from models.cancellation_response import CancellationResponse, CancellationStatus

_AGENT_NAME = "MerchandiseCancellationAgent"

_CONTACT_DETAILS = [
    "Jaguar Lifestyle Store : shop.jaguar.com/contact",
    "Land Rover Lifestyle Store : shop.landrover.com/contact",
]

# Merchandise cancellation windows (days)
_RETURN_WINDOW_DAYS = 30
_RETURN_DISPATCH_DAYS = 14
_REFUND_PROCESSING_DAYS = 14


class MerchandiseCancellationAgent:
    """Handles JLR UK lifestyle/merchandise store cancellations and returns.

    Business rules applied:

    1. Personalised items → ineligible for standard cancellation right.
    2. Request raised within the 30-day return window → approved,
       customer must return goods within 14 days.
    3. Request raised beyond 30 days → ineligible unless goods are defective.
    4. Goods already returned → confirm refund timeline.
    """

    _RETURN_WINDOW_DAYS = _RETURN_WINDOW_DAYS
    _RETURN_DISPATCH_DAYS = _RETURN_DISPATCH_DAYS
    _REFUND_PROCESSING_DAYS = _REFUND_PROCESSING_DAYS

    def process(self, request: CancellationRequest) -> CancellationResponse:
        """Evaluate a merchandise cancellation / return request.

        Args:
            request: A fully populated
                :class:`~models.cancellation_request.CancellationRequest`.

        Returns:
            A :class:`~models.cancellation_response.CancellationResponse`.
        """
        if request.is_personalised_item:
            return self._personalised_item_response(request)

        days = request.days_since_purchase
        if days is None or days <= self._RETURN_WINDOW_DAYS:
            return self._eligible_return_response(request)

        return self._outside_window_response(request)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _personalised_item_response(
        self, request: CancellationRequest
    ) -> CancellationResponse:
        return CancellationResponse(
            status=CancellationStatus.INELIGIBLE,
            message=(
                "Personalised, made-to-measure, custom-made, and perishable goods "
                "are excluded from the standard cancellation right. Your order "
                f"'{request.order_reference}' cannot be cancelled under the standard "
                "returns policy. Please contact the store for further assistance."
            ),
            next_steps=[
                f"Quote your order reference: {request.order_reference}.",
                "Contact the store directly to discuss your specific situation.",
                "If the goods are damaged or defective, contact the store as soon "
                "as possible so repair, exchange, or refund can be considered under "
                "your legal rights.",
            ],
            contact_details=_CONTACT_DETAILS,
            agent_name=_AGENT_NAME,
        )

    def _eligible_return_response(
        self, request: CancellationRequest
    ) -> CancellationResponse:
        if request.goods_returned:
            message = (
                f"Your return for order '{request.order_reference}' has been noted. "
                "A refund will be issued within 14 working days of the store "
                "receiving the goods or evidence of return."
            )
            next_steps = [
                f"Quote your order reference: {request.order_reference}.",
                "Ensure proof of postage / return is retained.",
                "Expect your refund within 14 days of the store confirming receipt.",
            ]
        else:
            message = (
                f"Your cancellation request for order '{request.order_reference}' "
                "is within the 30-day return window. Contact the store to confirm "
                "the return, then dispatch the goods within 14 days."
            )
            next_steps = [
                f"Quote your order reference: {request.order_reference}.",
                "Contact the store to confirm your cancellation/return.",
                f"Return the goods within {self._RETURN_DISPATCH_DAYS} days of "
                "confirming the cancellation.",
                "Take reasonable care of the goods during return transit.",
                f"Expect your refund within {self._REFUND_PROCESSING_DAYS} days "
                "after the store receives the goods or evidence of return.",
            ]
        return CancellationResponse(
            status=CancellationStatus.APPROVED,
            message=message,
            next_steps=next_steps,
            contact_details=_CONTACT_DETAILS,
            estimated_refund_days=self._REFUND_PROCESSING_DAYS,
            agent_name=_AGENT_NAME,
        )

    def _outside_window_response(
        self, request: CancellationRequest
    ) -> CancellationResponse:
        return CancellationResponse(
            status=CancellationStatus.INELIGIBLE,
            message=(
                f"Your order '{request.order_reference}' is outside the "
                f"{self._RETURN_WINDOW_DAYS}-day return window. Standard cancellation "
                "rights no longer apply. If the goods are damaged or defective, "
                "contact the store as soon as possible."
            ),
            next_steps=[
                f"Quote your order reference: {request.order_reference}.",
                "Contact the store to discuss your options.",
                "If goods are damaged or defective, your statutory legal rights "
                "still apply — contact the store immediately.",
            ],
            contact_details=_CONTACT_DETAILS,
            agent_name=_AGENT_NAME,
        )
