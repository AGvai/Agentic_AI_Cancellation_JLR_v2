"""Unit tests for WarrantyCancellationAgent."""

import unittest
from datetime import date

from agents.warranty_cancellation import WarrantyCancellationAgent
from models.cancellation_request import CancellationRequest, CancellationType
from models.cancellation_response import CancellationStatus


def _make_request(**kwargs) -> CancellationRequest:
    defaults = dict(
        cancellation_type=CancellationType.WARRANTY,
        order_reference="JLR-W-099",
        customer_name="Carol Green",
        contact_email="carol@example.com",
        request_date=date(2025, 6, 1),
    )
    defaults.update(kwargs)
    return CancellationRequest(**defaults)


class TestWarrantyCancellationAgent(unittest.TestCase):

    def setUp(self):
        self.agent = WarrantyCancellationAgent()

    # ------------------------------------------------------------------
    # Claim already made
    # ------------------------------------------------------------------

    def test_claim_made_is_ineligible(self):
        request = _make_request(claim_made=True, days_since_purchase=5)
        response = self.agent.process(request)
        self.assertEqual(response.status, CancellationStatus.INELIGIBLE)

    def test_claim_made_message_mentions_claim(self):
        request = _make_request(claim_made=True, days_since_purchase=5)
        response = self.agent.process(request)
        self.assertIn("claim", response.message.lower())

    def test_claim_made_even_within_cooling_off_is_ineligible(self):
        """A claim overrides the cooling-off period."""
        request = _make_request(claim_made=True, days_since_purchase=3)
        response = self.agent.process(request)
        self.assertEqual(response.status, CancellationStatus.INELIGIBLE)

    # ------------------------------------------------------------------
    # Within 14-day cooling-off period
    # ------------------------------------------------------------------

    def test_within_cooling_off_pending_retailer(self):
        request = _make_request(days_since_purchase=7, claim_made=False)
        response = self.agent.process(request)
        self.assertEqual(response.status, CancellationStatus.PENDING_RETAILER)

    def test_within_cooling_off_message_mentions_cooling_off(self):
        request = _make_request(days_since_purchase=7, claim_made=False)
        response = self.agent.process(request)
        self.assertIn("cooling", response.message.lower())

    def test_on_boundary_day_14_pending_retailer(self):
        request = _make_request(days_since_purchase=14, claim_made=False)
        response = self.agent.process(request)
        self.assertEqual(response.status, CancellationStatus.PENDING_RETAILER)

    def test_no_days_provided_defaults_to_pending_retailer(self):
        """When days_since_purchase is None, give benefit of the doubt."""
        request = _make_request(days_since_purchase=None, claim_made=False)
        response = self.agent.process(request)
        self.assertEqual(response.status, CancellationStatus.PENDING_RETAILER)

    def test_within_cooling_off_next_steps_mention_retailer(self):
        request = _make_request(days_since_purchase=5, claim_made=False)
        response = self.agent.process(request)
        combined = " ".join(response.next_steps).lower()
        self.assertIn("retailer", combined)

    # ------------------------------------------------------------------
    # Outside 14-day cooling-off period
    # ------------------------------------------------------------------

    def test_outside_cooling_off_ineligible(self):
        request = _make_request(days_since_purchase=15, claim_made=False)
        response = self.agent.process(request)
        self.assertEqual(response.status, CancellationStatus.INELIGIBLE)

    def test_outside_cooling_off_message_mentions_no_refund(self):
        request = _make_request(days_since_purchase=30, claim_made=False)
        response = self.agent.process(request)
        self.assertIn("no refund", response.message.lower())

    def test_outside_cooling_off_agent_name_set(self):
        request = _make_request(days_since_purchase=60, claim_made=False)
        response = self.agent.process(request)
        self.assertIn("Warranty", response.agent_name)


if __name__ == "__main__":
    unittest.main()
