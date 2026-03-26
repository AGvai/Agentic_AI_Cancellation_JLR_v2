"""Orchestrator agent — routes cancellation requests to the correct sub-agent.

The orchestrator is the top-level entry point for the agentic AI system.
It inspects the ``cancellation_type`` field of the incoming request and
dispatches to the appropriate specialised sub-agent.  When the type cannot
be determined, it returns a helpful fallback response directing the customer
to JLR Concierge.
"""

from models.cancellation_request import CancellationRequest, CancellationType
from models.cancellation_response import CancellationResponse, CancellationStatus
from agents.vehicle_cancellation import VehicleCancellationAgent
from agents.merchandise_cancellation import MerchandiseCancellationAgent
from agents.warranty_cancellation import WarrantyCancellationAgent
from agents.subscription_cancellation import SubscriptionCancellationAgent

_AGENT_NAME = "OrchestratorAgent"

_FALLBACK_CONTACT = [
    "JLR Concierge Phone : 01926 691736",
    "JLR Concierge Email : UKwebsales@jaguarlandrover.com",
    "Hours : Monday–Friday, 09:00–17:00",
]


class OrchestratorAgent:
    """Top-level orchestrator that routes requests to specialised sub-agents.

    The orchestrator maintains one instance of each sub-agent and dispatches
    to the correct one based on the ``cancellation_type`` of the request.

    Sub-agents:
    * :class:`~agents.vehicle_cancellation.VehicleCancellationAgent`
    * :class:`~agents.merchandise_cancellation.MerchandiseCancellationAgent`
    * :class:`~agents.warranty_cancellation.WarrantyCancellationAgent`
    * :class:`~agents.subscription_cancellation.SubscriptionCancellationAgent`
    """

    def __init__(self) -> None:
        self._vehicle_agent = VehicleCancellationAgent()
        self._merchandise_agent = MerchandiseCancellationAgent()
        self._warranty_agent = WarrantyCancellationAgent()
        self._subscription_agent = SubscriptionCancellationAgent()

        self._routing_table = {
            CancellationType.VEHICLE_ORDER: self._vehicle_agent.process,
            CancellationType.MERCHANDISE: self._merchandise_agent.process,
            CancellationType.WARRANTY: self._warranty_agent.process,
            CancellationType.SUBSCRIPTION: self._subscription_agent.process,
        }

    def process(self, request: CancellationRequest) -> CancellationResponse:
        """Route the request to the appropriate sub-agent.

        Args:
            request: A populated
                :class:`~models.cancellation_request.CancellationRequest`.

        Returns:
            The :class:`~models.cancellation_response.CancellationResponse`
            produced by the matching sub-agent, or a fallback response when
            the cancellation type is ``UNKNOWN``.
        """
        handler = self._routing_table.get(request.cancellation_type)
        if handler is None:
            return self._unknown_type_response(request)
        return handler(request)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _unknown_type_response(request: CancellationRequest) -> CancellationResponse:
        return CancellationResponse(
            status=CancellationStatus.REQUIRES_MANUAL_REVIEW,
            message=(
                "The cancellation type could not be determined from your request "
                f"(reference: '{request.order_reference}'). Please contact JLR "
                "Concierge directly so the correct team can assist you."
            ),
            next_steps=[
                f"Quote your reference: {request.order_reference}.",
                "Contact JLR Concierge by phone or email (see below).",
                "Specify whether your query relates to a vehicle order, merchandise "
                "purchase, approved warranty, or InControl subscription.",
            ],
            contact_details=_FALLBACK_CONTACT,
            agent_name=_AGENT_NAME,
        )
