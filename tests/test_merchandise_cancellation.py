"""Unit tests for MerchandiseCancellationAgent."""

import unittest
from datetime import date

from agents.merchandise_cancellation import MerchandiseCancellationAgent
from models.cancellation_request import CancellationRequest, CancellationType
from models.cancellation_response import CancellationStatus


def _make_request(**kwargs) -> CancellationRequest:
    defaults = dict(
        cancellation_type=CancellationType.MERCHANDISE,
        order_reference="JLR-M-042",
        customer_name="Bob Jones",
        contact_email="bob@example.com",
        request_date=date(2025, 6, 1),
    )
    defaults.update(kwargs)
    return CancellationRequest(**defaults)


class TestMerchandiseCancellationAgent(unittest.TestCase):

    def setUp(self):
        self.agent = MerchandiseCancellationAgent()

    # ------------------------------------------------------------------
    # Personalised items
    # ------------------------------------------------------------------

    def test_personalised_item_is_ineligible(self):
        request = _make_request(is_personalised_item=True, days_since_purchase=5)
        response = self.agent.process(request)
        self.assertEqual(response.status, CancellationStatus.INELIGIBLE)

    def test_personalised_item_message_mentions_personalised(self):
        request = _make_request(is_personalised_item=True)
        response = self.agent.process(request)
        self.assertIn("personalised", response.message.lower())

    # ------------------------------------------------------------------
    # Within 30-day return window — goods not yet returned
    # ------------------------------------------------------------------

    def test_within_window_approved(self):
        request = _make_request(days_since_purchase=10)
        response = self.agent.process(request)
        self.assertEqual(response.status, CancellationStatus.APPROVED)

    def test_within_window_refund_days(self):
        request = _make_request(days_since_purchase=10)
        response = self.agent.process(request)
        self.assertEqual(response.estimated_refund_days, 14)

    def test_within_window_next_steps_non_empty(self):
        request = _make_request(days_since_purchase=10)
        response = self.agent.process(request)
        self.assertTrue(len(response.next_steps) > 0)

    def test_on_boundary_day_30_approved(self):
        request = _make_request(days_since_purchase=30)
        response = self.agent.process(request)
        self.assertEqual(response.status, CancellationStatus.APPROVED)

    def test_no_days_provided_defaults_to_approved(self):
        """When days_since_purchase is None, agent should approve (benefit of doubt)."""
        request = _make_request(days_since_purchase=None)
        response = self.agent.process(request)
        self.assertEqual(response.status, CancellationStatus.APPROVED)

    # ------------------------------------------------------------------
    # Within window — goods already returned
    # ------------------------------------------------------------------

    def test_goods_returned_approved(self):
        request = _make_request(days_since_purchase=7, goods_returned=True)
        response = self.agent.process(request)
        self.assertEqual(response.status, CancellationStatus.APPROVED)

    def test_goods_returned_message_mentions_refund(self):
        request = _make_request(days_since_purchase=7, goods_returned=True)
        response = self.agent.process(request)
        self.assertIn("refund", response.message.lower())

    # ------------------------------------------------------------------
    # Outside 30-day window
    # ------------------------------------------------------------------

    def test_outside_window_ineligible(self):
        request = _make_request(days_since_purchase=31)
        response = self.agent.process(request)
        self.assertEqual(response.status, CancellationStatus.INELIGIBLE)

    def test_outside_window_message_mentions_window(self):
        request = _make_request(days_since_purchase=31)
        response = self.agent.process(request)
        self.assertIn("30", response.message)

    def test_outside_window_agent_name_set(self):
        request = _make_request(days_since_purchase=45)
        response = self.agent.process(request)
        self.assertIn("Merchandise", response.agent_name)


if __name__ == "__main__":
    unittest.main()
