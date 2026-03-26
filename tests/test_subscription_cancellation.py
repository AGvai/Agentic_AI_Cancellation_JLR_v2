"""Unit tests for SubscriptionCancellationAgent."""

import unittest
from datetime import date

from agents.subscription_cancellation import SubscriptionCancellationAgent
from models.cancellation_request import CancellationRequest, CancellationType
from models.cancellation_response import CancellationStatus


def _make_request(**kwargs) -> CancellationRequest:
    defaults = dict(
        cancellation_type=CancellationType.SUBSCRIPTION,
        order_reference="JLR-S-201",
        customer_name="David Lee",
        contact_email="david@example.com",
        request_date=date(2025, 6, 1),
        subscription_active=True,
        vehicle_sold=False,
    )
    defaults.update(kwargs)
    return CancellationRequest(**defaults)


class TestSubscriptionCancellationAgent(unittest.TestCase):

    def setUp(self):
        self.agent = SubscriptionCancellationAgent()

    # ------------------------------------------------------------------
    # Within 14-day cooling-off
    # ------------------------------------------------------------------

    def test_within_cooling_off_approved(self):
        request = _make_request(days_since_purchase=7)
        response = self.agent.process(request)
        self.assertEqual(response.status, CancellationStatus.APPROVED)

    def test_within_cooling_off_refund_days(self):
        request = _make_request(days_since_purchase=7)
        response = self.agent.process(request)
        self.assertEqual(response.estimated_refund_days, 14)

    def test_on_boundary_day_14_approved(self):
        request = _make_request(days_since_purchase=14)
        response = self.agent.process(request)
        self.assertEqual(response.status, CancellationStatus.APPROVED)

    def test_within_cooling_off_message_mentions_cooling_off(self):
        request = _make_request(days_since_purchase=3)
        response = self.agent.process(request)
        self.assertIn("cooling", response.message.lower())

    # ------------------------------------------------------------------
    # Vehicle sold / lease ended
    # ------------------------------------------------------------------

    def test_vehicle_sold_approved(self):
        request = _make_request(days_since_purchase=100, vehicle_sold=True)
        response = self.agent.process(request)
        self.assertEqual(response.status, CancellationStatus.APPROVED)

    def test_vehicle_sold_message_mentions_remove(self):
        request = _make_request(days_since_purchase=100, vehicle_sold=True)
        response = self.agent.process(request)
        self.assertIn("remove", response.message.lower())

    def test_vehicle_sold_next_steps_mention_incontrol(self):
        request = _make_request(days_since_purchase=100, vehicle_sold=True)
        response = self.agent.process(request)
        combined = " ".join(response.next_steps).lower()
        self.assertIn("incontrol", combined)

    # ------------------------------------------------------------------
    # Subscription already expired
    # ------------------------------------------------------------------

    def test_already_expired_approved(self):
        request = _make_request(
            days_since_purchase=400, subscription_active=False, vehicle_sold=False
        )
        response = self.agent.process(request)
        self.assertEqual(response.status, CancellationStatus.APPROVED)

    def test_already_expired_message_mentions_expired(self):
        request = _make_request(
            days_since_purchase=400, subscription_active=False, vehicle_sold=False
        )
        response = self.agent.process(request)
        self.assertIn("expired", response.message.lower())

    # ------------------------------------------------------------------
    # Active subscription outside cooling-off (non-renewal advice)
    # ------------------------------------------------------------------

    def test_active_outside_window_ineligible(self):
        request = _make_request(
            days_since_purchase=90, subscription_active=True, vehicle_sold=False
        )
        response = self.agent.process(request)
        self.assertEqual(response.status, CancellationStatus.INELIGIBLE)

    def test_active_outside_window_message_mentions_non_renewal(self):
        request = _make_request(
            days_since_purchase=90, subscription_active=True, vehicle_sold=False
        )
        response = self.agent.process(request)
        self.assertIn("renew", response.message.lower())

    def test_active_outside_window_no_days_is_ineligible(self):
        """No days provided and active subscription → non-renewal advice."""
        request = _make_request(
            days_since_purchase=None, subscription_active=True, vehicle_sold=False
        )
        response = self.agent.process(request)
        self.assertEqual(response.status, CancellationStatus.INELIGIBLE)

    def test_agent_name_set(self):
        request = _make_request(days_since_purchase=7)
        response = self.agent.process(request)
        self.assertIn("Subscription", response.agent_name)


if __name__ == "__main__":
    unittest.main()
