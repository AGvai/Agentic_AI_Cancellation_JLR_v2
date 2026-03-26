"""Unit tests for OrchestratorAgent routing and helpers."""

import unittest
from datetime import date

from agents.orchestrator import OrchestratorAgent
from models.cancellation_request import CancellationRequest, CancellationType
from models.cancellation_response import CancellationStatus
from utils.helpers import parse_intent, format_response


def _make_request(cancellation_type: CancellationType, **kwargs) -> CancellationRequest:
    defaults = dict(
        cancellation_type=cancellation_type,
        order_reference="JLR-TEST-001",
        customer_name="Test User",
        contact_email="test@example.com",
        request_date=date(2025, 6, 1),
    )
    defaults.update(kwargs)
    return CancellationRequest(**defaults)


class TestOrchestratorRouting(unittest.TestCase):

    def setUp(self):
        self.orchestrator = OrchestratorAgent()

    def test_routes_vehicle_order(self):
        request = _make_request(CancellationType.VEHICLE_ORDER, contract_signed=False)
        response = self.orchestrator.process(request)
        self.assertIn("Vehicle", response.agent_name)

    def test_routes_merchandise(self):
        request = _make_request(CancellationType.MERCHANDISE, days_since_purchase=5)
        response = self.orchestrator.process(request)
        self.assertIn("Merchandise", response.agent_name)

    def test_routes_warranty(self):
        request = _make_request(
            CancellationType.WARRANTY, days_since_purchase=5, claim_made=False
        )
        response = self.orchestrator.process(request)
        self.assertIn("Warranty", response.agent_name)

    def test_routes_subscription(self):
        request = _make_request(
            CancellationType.SUBSCRIPTION,
            days_since_purchase=5,
            subscription_active=True,
        )
        response = self.orchestrator.process(request)
        self.assertIn("Subscription", response.agent_name)

    def test_unknown_type_returns_manual_review(self):
        request = _make_request(CancellationType.UNKNOWN)
        response = self.orchestrator.process(request)
        self.assertEqual(response.status, CancellationStatus.REQUIRES_MANUAL_REVIEW)

    def test_unknown_type_agent_name_is_orchestrator(self):
        request = _make_request(CancellationType.UNKNOWN)
        response = self.orchestrator.process(request)
        self.assertIn("Orchestrator", response.agent_name)


class TestParseIntent(unittest.TestCase):

    def test_vehicle_keywords(self):
        for text in [
            "I want to cancel my car reservation",
            "cancel my jaguar order",
            "I'd like to return my vehicle deposit",
        ]:
            with self.subTest(text=text):
                result = parse_intent(text)
                self.assertEqual(result, CancellationType.VEHICLE_ORDER)

    def test_merchandise_keywords(self):
        for text in [
            "I want to return some accessories I bought",
            "cancel my lifestyle store order",
            "return the goods I received",
        ]:
            with self.subTest(text=text):
                result = parse_intent(text)
                self.assertEqual(result, CancellationType.MERCHANDISE)

    def test_warranty_keywords(self):
        for text in [
            "I want to cancel my approved warranty",
            "cancel my extended warranty cover",
        ]:
            with self.subTest(text=text):
                result = parse_intent(text)
                self.assertEqual(result, CancellationType.WARRANTY)

    def test_subscription_keywords(self):
        for text in [
            "cancel my incontrol subscription",
            "I no longer want the connected services",
            "cancel my in-control renewal",
        ]:
            with self.subTest(text=text):
                result = parse_intent(text)
                self.assertEqual(result, CancellationType.SUBSCRIPTION)

    def test_unknown_returns_unknown(self):
        result = parse_intent("aaaaa bbbbb ccccc")
        self.assertEqual(result, CancellationType.UNKNOWN)


class TestFormatResponse(unittest.TestCase):

    def test_format_contains_status(self):
        request = _make_request(CancellationType.VEHICLE_ORDER, contract_signed=False)
        orchestrator = OrchestratorAgent()
        response = orchestrator.process(request)
        formatted = format_response(response)
        self.assertIn("PENDING_RETAILER", formatted)

    def test_format_contains_next_steps(self):
        request = _make_request(CancellationType.VEHICLE_ORDER, contract_signed=False)
        orchestrator = OrchestratorAgent()
        response = orchestrator.process(request)
        formatted = format_response(response)
        self.assertIn("Next Steps", formatted)

    def test_format_contains_contact_details(self):
        request = _make_request(CancellationType.VEHICLE_ORDER, contract_signed=False)
        orchestrator = OrchestratorAgent()
        response = orchestrator.process(request)
        formatted = format_response(response)
        self.assertIn("Contact Details", formatted)

    def test_format_contains_refund_days_when_present(self):
        request = _make_request(CancellationType.VEHICLE_ORDER, contract_signed=False)
        orchestrator = OrchestratorAgent()
        response = orchestrator.process(request)
        formatted = format_response(response)
        self.assertIn("5", formatted)


if __name__ == "__main__":
    unittest.main()
