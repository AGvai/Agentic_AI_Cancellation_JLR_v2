"""Connected-service / InControl subscription cancellation agent.

Journey summary (JLR UK InControl public terms & FAQs)
--------------------------------------------------------
* Subscriptions are managed via the Services Store, My InControl, or in-vehicle
  settings.
* Renewals are typically for 12 months.
* Cooling-off refund window: 14 days from purchase.
* Once activated, early termination is allowed only in limited circumstances
  (JLR breach, materially disadvantageous changes, certain external-control
  events).
* The standard paths are: non-renewal (services stop at expiry) or vehicle
  removal from account when ownership changes.
* Subscriptions cannot be transferred to another vehicle.
* When selling the vehicle, the customer must remove it from the InControl
  account to protect personal data and avoid continued charges.
"""

from models.cancellation_request import CancellationRequest
from models.cancellation_response import CancellationResponse, CancellationStatus

_AGENT_NAME = "SubscriptionCancellationAgent"

_CONTACT_DETAILS = [
    "Services Store / My InControl : incontrol.jaguar.com or incontrol.landrover.com",
    "JLR Concierge Phone : 01926 691736",
    "JLR Concierge Email : UKwebsales@jaguarlandrover.com",
    "Hours : Monday–Friday, 09:00–17:00",
]

_COOLING_OFF_DAYS = 14


class SubscriptionCancellationAgent:
    """Handles JLR UK InControl / connected-service subscription cancellations.

    Business rules applied:

    1. Within 14-day cooling-off period → refund available via JLR Concierge.
    2. Vehicle sold / lease ended → advise customer to remove vehicle from
       account; remaining term may continue for new owner on that vehicle.
    3. Subscription already expired → no action needed, services have stopped.
    4. Active subscription outside cooling-off period → standard path is
       non-renewal; mid-term cancellation is restricted.
    """

    _COOLING_OFF_DAYS = _COOLING_OFF_DAYS

    def process(self, request: CancellationRequest) -> CancellationResponse:
        """Evaluate a subscription cancellation request.

        Args:
            request: A fully populated
                :class:`~models.cancellation_request.CancellationRequest`.

        Returns:
            A :class:`~models.cancellation_response.CancellationResponse`.
        """
        days = request.days_since_purchase

        if days is not None and days <= self._COOLING_OFF_DAYS:
            return self._cooling_off_response(request)

        if request.vehicle_sold:
            return self._vehicle_sold_response(request)

        if not request.subscription_active:
            return self._already_expired_response(request)

        return self._non_renewal_advice_response(request)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _cooling_off_response(
        self, request: CancellationRequest
    ) -> CancellationResponse:
        return CancellationResponse(
            status=CancellationStatus.APPROVED,
            message=(
                f"Your subscription (reference: '{request.order_reference}') is "
                f"within the {self._COOLING_OFF_DAYS}-day cooling-off period. You "
                "are eligible for a refund. Contact JLR Concierge to arrange "
                "cancellation and refund."
            ),
            next_steps=[
                f"Quote your subscription reference: {request.order_reference}.",
                "Contact JLR Concierge by phone or email (see below).",
                "Request cancellation and confirm the refund to your original payment method.",
                "Services will be disabled on your vehicle following cancellation.",
            ],
            contact_details=_CONTACT_DETAILS,
            estimated_refund_days=14,
            agent_name=_AGENT_NAME,
        )

    def _vehicle_sold_response(
        self, request: CancellationRequest
    ) -> CancellationResponse:
        return CancellationResponse(
            status=CancellationStatus.APPROVED,
            message=(
                "As the vehicle has been sold or the lease has ended, you should "
                "remove the vehicle from your InControl account immediately to "
                "protect your personal data and avoid ongoing charges or "
                f"responsibility. Reference: '{request.order_reference}'."
            ),
            next_steps=[
                "Log in to the Services Store or My InControl.",
                f"Locate your vehicle (reference: {request.order_reference}) and "
                "select 'Remove vehicle from account'.",
                "Clear any personal data and settings in the vehicle where possible "
                "before handover.",
                "Note: any remaining subscription term on that vehicle may continue "
                "for the new owner, but the subscription cannot be transferred to "
                "your next vehicle.",
                "Contact JLR Concierge if you need further assistance.",
            ],
            contact_details=_CONTACT_DETAILS,
            agent_name=_AGENT_NAME,
        )

    def _already_expired_response(
        self, request: CancellationRequest
    ) -> CancellationResponse:
        return CancellationResponse(
            status=CancellationStatus.APPROVED,
            message=(
                f"Your subscription (reference: '{request.order_reference}') has "
                "already expired. The associated connected services were disabled at "
                "the expiry date. No further action is required unless you wish to "
                "renew."
            ),
            next_steps=[
                "No cancellation action is needed — services stopped at expiry.",
                "If you believe services are still active or you are being charged, "
                "contact JLR Concierge immediately.",
                "To renew, visit the Services Store or My InControl.",
            ],
            contact_details=_CONTACT_DETAILS,
            agent_name=_AGENT_NAME,
        )

    def _non_renewal_advice_response(
        self, request: CancellationRequest
    ) -> CancellationResponse:
        return CancellationResponse(
            status=CancellationStatus.INELIGIBLE,
            message=(
                f"Your subscription (reference: '{request.order_reference}') is "
                "active and outside the 14-day cooling-off period. Under the "
                "published InControl terms, voluntary mid-term cancellation is "
                "not the standard path. The recommended route is to simply not "
                "renew when the current term expires."
            ),
            next_steps=[
                f"Quote your subscription reference: {request.order_reference}.",
                "Allow the current subscription term to expire without renewing — "
                "services will stop automatically at the expiry date.",
                "To check your expiry date, log in to the Services Store or "
                "My InControl.",
                "If your circumstances fall under a JLR breach, materially "
                "disadvantageous change, or specific external-control event, "
                "contact JLR Concierge to discuss early termination.",
            ],
            contact_details=_CONTACT_DETAILS,
            agent_name=_AGENT_NAME,
        )
