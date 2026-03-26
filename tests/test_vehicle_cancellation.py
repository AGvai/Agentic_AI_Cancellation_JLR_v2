"""Unit tests for VehicleCancellationAgent."""

import unittest
from datetime import date

from agents.vehicle_cancellation import VehicleCancellationAgent
from models.cancellation_request import CancellationRequest, CancellationType
from models.cancellation_response import CancellationStatus


def _make_request(**kwargs) -> CancellationRequest:
    defaults = dict(
        cancellation_type=CancellationType.VEHICLE_ORDER,
        order_reference="JLR-V-001",
        customer_name="Alice Smith",
        contact_email="alice@example.com",
        request_date=date(2025, 6, 1),
    )
    defaults.update(kwargs)
    return CancellationRequest(**defaults)


class TestVehicleCancellationAgent(unittest.TestCase):

    def setUp(self):
        self.agent = VehicleCancellationAgent()

    # ------------------------------------------------------------------
    # Pre-contract (reservation stage)
    # ------------------------------------------------------------------

    def test_pre_contract_status_is_pending_retailer(self):
        request = _make_request(contract_signed=False)
        response = self.agent.process(request)
        self.assertEqual(response.status, CancellationStatus.PENDING_RETAILER)

    def test_pre_contract_refund_days_is_five(self):
        request = _make_request(contract_signed=False)
        response = self.agent.process(request)
        self.assertEqual(response.estimated_refund_days, 5)

    def test_pre_contract_message_contains_order_reference(self):
        request = _make_request(contract_signed=False)
        response = self.agent.process(request)
        self.assertIn("JLR-V-001", response.message)

    def test_pre_contract_next_steps_non_empty(self):
        request = _make_request(contract_signed=False)
        response = self.agent.process(request)
        self.assertTrue(len(response.next_steps) > 0)

    def test_pre_contract_contact_details_present(self):
        request = _make_request(contract_signed=False)
        response = self.agent.process(request)
        self.assertTrue(len(response.contact_details) > 0)

    def test_pre_contract_agent_name_set(self):
        request = _make_request(contract_signed=False)
        response = self.agent.process(request)
        self.assertIn("Vehicle", response.agent_name)

    # ------------------------------------------------------------------
    # Post-contract (contract already signed)
    # ------------------------------------------------------------------

    def test_post_contract_status_is_manual_review(self):
        request = _make_request(contract_signed=True)
        response = self.agent.process(request)
        self.assertEqual(response.status, CancellationStatus.REQUIRES_MANUAL_REVIEW)

    def test_post_contract_no_refund_days(self):
        request = _make_request(contract_signed=True)
        response = self.agent.process(request)
        self.assertIsNone(response.estimated_refund_days)

    def test_post_contract_message_mentions_contract(self):
        request = _make_request(contract_signed=True)
        response = self.agent.process(request)
        self.assertIn("contract", response.message.lower())

    def test_post_contract_next_steps_non_empty(self):
        request = _make_request(contract_signed=True)
        response = self.agent.process(request)
        self.assertTrue(len(response.next_steps) > 0)


if __name__ == "__main__":
    unittest.main()
