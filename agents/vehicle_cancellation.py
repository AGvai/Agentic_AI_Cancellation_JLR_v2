"""Vehicle order / reservation cancellation agent.

Journey summary (JLR UK public terms)
--------------------------------------
* Customer reserves / orders online and pays a reservation fee.
* The retailer owns the next steps; no self-serve cancel flow exists once the
  reservation is live.
* Cancellation is cleanest *before* a purchase or finance contract is signed
  with the retailer.
* Reservation-fee refund: up to 5 working days after the request.
* Contact: 01926 691736 | UKwebsales@jaguarlandrover.com | Mon–Fri 09:00–17:00
"""

from models.cancellation_request import CancellationRequest
from models.cancellation_response import CancellationResponse, CancellationStatus

_AGENT_NAME = "VehicleCancellationAgent"

_CONTACT_DETAILS = [
    "Phone : 01926 691736",
    "Email : UKwebsales@jaguarlandrover.com",
    "Hours : Monday–Friday, 09:00–17:00",
]


class VehicleCancellationAgent:
    """Handles JLR UK vehicle order and reservation cancellations.

    The agent applies the publicly stated business rules from the Jaguar and
    Land Rover UK FAQ / online reservation terms to decide whether a
    cancellation can be processed, and what the customer must do next.
    """

    def process(self, request: CancellationRequest) -> CancellationResponse:
        """Evaluate a vehicle cancellation request and return a response.

        Args:
            request: A fully populated
                :class:`~models.cancellation_request.CancellationRequest`.

        Returns:
            A :class:`~models.cancellation_response.CancellationResponse`
            describing the outcome and recommended next steps.
        """
        if request.contract_signed:
            return self._post_contract_response(request)
        return self._pre_contract_response(request)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _pre_contract_response(
        self, request: CancellationRequest
    ) -> CancellationResponse:
        """Cancellation at the reservation stage (no contract signed yet)."""
        return CancellationResponse(
            status=CancellationStatus.PENDING_RETAILER,
            message=(
                "Your reservation can be cancelled before a purchase or finance "
                "contract is signed. Please contact your chosen retailer or JLR "
                "Concierge as soon as possible, quoting your order reference "
                f"'{request.order_reference}'."
            ),
            next_steps=[
                f"Quote your order reference: {request.order_reference}.",
                "Contact your chosen JLR retailer directly to request cancellation.",
                "Alternatively, contact JLR Concierge by phone or email (see below).",
                "Your reservation fee will be refunded to the original payment method "
                "within up to 5 working days of the cancellation request being accepted.",
                "If the refund is delayed, follow up with the retailer or JLR Concierge.",
            ],
            contact_details=_CONTACT_DETAILS,
            estimated_refund_days=5,
            agent_name=_AGENT_NAME,
        )

    def _post_contract_response(
        self, request: CancellationRequest
    ) -> CancellationResponse:
        """Cancellation where a purchase/finance contract has already been signed."""
        return CancellationResponse(
            status=CancellationStatus.REQUIRES_MANUAL_REVIEW,
            message=(
                "A purchase or finance contract has already been signed with the "
                "retailer. At this stage, cancellation depends on the specific terms "
                "of your contract and how far the order has progressed. You must "
                "contact your retailer directly as soon as possible."
            ),
            next_steps=[
                f"Quote your order reference: {request.order_reference}.",
                "Contact your chosen JLR retailer immediately to discuss options.",
                "Review the specific terms in your signed purchase or finance contract.",
                "If your retailer cannot resolve the issue, contact JLR Concierge.",
            ],
            contact_details=_CONTACT_DETAILS,
            estimated_refund_days=None,
            agent_name=_AGENT_NAME,
        )
