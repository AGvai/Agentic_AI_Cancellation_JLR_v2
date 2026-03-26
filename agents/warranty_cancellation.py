"""Warranty cancellation agent.

Journey summary (JLR UK Approved Warranty public terms)
---------------------------------------------------------
* Customer has a 14-day cooling-off period from receiving the warranty booklet
  and Registration Confirmation Letter.
* Cancellation during the cooling-off period: contact the supplying retailer;
  retailer arranges cancellation and full refund.
* Outside the cooling-off period: normally no refund.
* No refund if a warranty claim has already been paid or made.
"""

from models.cancellation_request import CancellationRequest
from models.cancellation_response import CancellationResponse, CancellationStatus

_AGENT_NAME = "WarrantyCancellationAgent"

_CONTACT_DETAILS = [
    "Contact your supplying JLR retailer directly.",
    "JLR Concierge Phone : 01926 691736",
    "JLR Concierge Email : UKwebsales@jaguarlandrover.com",
    "Hours : Monday–Friday, 09:00–17:00",
]

_COOLING_OFF_DAYS = 14


class WarrantyCancellationAgent:
    """Handles JLR UK Approved Warranty cancellations.

    Business rules applied:

    1. Claim already made or paid → ineligible for refund.
    2. Within 14-day cooling-off period → approved via supplying retailer,
       full refund.
    3. Outside 14-day cooling-off period → normally no refund (ineligible).
    """

    _COOLING_OFF_DAYS = _COOLING_OFF_DAYS

    def process(self, request: CancellationRequest) -> CancellationResponse:
        """Evaluate a warranty cancellation request.

        Args:
            request: A fully populated
                :class:`~models.cancellation_request.CancellationRequest`.

        Returns:
            A :class:`~models.cancellation_response.CancellationResponse`.
        """
        if request.claim_made:
            return self._claim_already_made_response(request)

        days = request.days_since_purchase
        if days is None or days <= self._COOLING_OFF_DAYS:
            return self._within_cooling_off_response(request)

        return self._outside_cooling_off_response(request)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _claim_already_made_response(
        self, request: CancellationRequest
    ) -> CancellationResponse:
        return CancellationResponse(
            status=CancellationStatus.INELIGIBLE,
            message=(
                "A warranty claim has already been made or paid on this policy "
                f"(reference: '{request.order_reference}'). Under JLR's published "
                "Approved Warranty terms, no refund is available once a claim has "
                "been made."
            ),
            next_steps=[
                f"Quote your warranty reference: {request.order_reference}.",
                "Contact your supplying retailer if you believe this decision "
                "is incorrect.",
            ],
            contact_details=_CONTACT_DETAILS,
            agent_name=_AGENT_NAME,
        )

    def _within_cooling_off_response(
        self, request: CancellationRequest
    ) -> CancellationResponse:
        return CancellationResponse(
            status=CancellationStatus.PENDING_RETAILER,
            message=(
                f"Your warranty (reference: '{request.order_reference}') is within "
                f"the {self._COOLING_OFF_DAYS}-day cooling-off period. You are "
                "entitled to a full refund. Contact your supplying retailer to "
                "arrange cancellation."
            ),
            next_steps=[
                f"Quote your warranty reference: {request.order_reference}.",
                "Contact the supplying JLR retailer to request cancellation.",
                "The retailer will arrange the cancellation and process your full refund.",
                "Retain your warranty booklet and Registration Confirmation Letter "
                "until the refund is confirmed.",
            ],
            contact_details=_CONTACT_DETAILS,
            estimated_refund_days=None,
            agent_name=_AGENT_NAME,
        )

    def _outside_cooling_off_response(
        self, request: CancellationRequest
    ) -> CancellationResponse:
        return CancellationResponse(
            status=CancellationStatus.INELIGIBLE,
            message=(
                f"Your warranty (reference: '{request.order_reference}') is outside "
                f"the {self._COOLING_OFF_DAYS}-day cooling-off period. Under JLR's "
                "published Approved Warranty terms, no refund is normally available "
                "after this window. Please contact your supplying retailer if you "
                "have exceptional circumstances."
            ),
            next_steps=[
                f"Quote your warranty reference: {request.order_reference}.",
                "Contact the supplying JLR retailer to discuss your options.",
                "Be aware that the standard published position is no refund outside "
                "the cooling-off period.",
            ],
            contact_details=_CONTACT_DETAILS,
            agent_name=_AGENT_NAME,
        )
