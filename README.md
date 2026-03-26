# JLR Agentic AI Cancellation System

A vibe-coded Python application that models the four JLR UK order-cancellation
customer journeys as an agentic AI system.

## Overview

The system implements an **OrchestratorAgent** that routes incoming cancellation
requests to one of four specialised sub-agents:

| Sub-Agent | Journey | Key Rule |
|---|---|---|
| `VehicleCancellationAgent` | Vehicle order / reservation | Retailer-led; refund ≤ 5 working days if pre-contract |
| `MerchandiseCancellationAgent` | Lifestyle store | Cancel before dispatch or within 30 days; return within 14 days |
| `WarrantyCancellationAgent` | Approved Warranty | 14-day cooling-off; no refund after / if claim made |
| `SubscriptionCancellationAgent` | InControl connected services | 14-day cooling-off; otherwise non-renewal or account removal |

## Project Structure

```
.
├── main.py                          # Interactive CLI entry point
├── requirements.txt
├── agents/
│   ├── orchestrator.py              # Routes requests to sub-agents
│   ├── vehicle_cancellation.py
│   ├── merchandise_cancellation.py
│   ├── warranty_cancellation.py
│   └── subscription_cancellation.py
├── models/
│   ├── cancellation_request.py      # CancellationRequest dataclass + CancellationType enum
│   └── cancellation_response.py     # CancellationResponse dataclass + CancellationStatus enum
├── utils/
│   └── helpers.py                   # parse_intent() and format_response()
└── tests/
    ├── test_vehicle_cancellation.py
    ├── test_merchandise_cancellation.py
    ├── test_warranty_cancellation.py
    ├── test_subscription_cancellation.py
    └── test_orchestrator.py
```

## Quick Start

```bash
# Install dependencies (only pytest is needed for tests)
pip install -r requirements.txt

# Run the interactive CLI
python main.py

# Run all tests
python -m pytest tests/ -v
```

## CLI Usage

The CLI presents a menu where the customer selects their cancellation type (or
describes their issue in plain English).  The orchestrator agent evaluates the
request against the published JLR UK business rules and returns:

- **Status** – `APPROVED`, `PENDING_RETAILER`, `PENDING_STORE`, `INELIGIBLE`, or `REQUIRES_MANUAL_REVIEW`
- **Message** – plain-English explanation of the outcome
- **Next Steps** – ordered list of actions for the customer
- **Contact Details** – relevant JLR contact information
- **Refund Timeline** – estimated working days for refund (where applicable)

## Business Rules Summary

### 1. Vehicle Order / Reservation
- Pre-contract reservation → `PENDING_RETAILER`; refund up to **5 working days**.
- Post-contract → `REQUIRES_MANUAL_REVIEW`; retailer must be contacted immediately.

### 2. Merchandise
- Personalised / custom items → `INELIGIBLE`.
- Within **30 days** of delivery → `APPROVED`; return goods within **14 days**; refund within **14 days** of receipt.
- Beyond 30 days → `INELIGIBLE` (defective goods handled separately).

### 3. Approved Warranty
- Claim already made → `INELIGIBLE` (no refund).
- Within **14-day** cooling-off → `PENDING_RETAILER`; full refund via supplying retailer.
- After 14 days → `INELIGIBLE`; normally no refund.

### 4. InControl Subscription
- Within **14-day** cooling-off → `APPROVED`; refund within **14 days**.
- Vehicle sold / lease ended → `APPROVED`; remove vehicle from InControl account.
- Subscription already expired → `APPROVED`; no further action needed.
- Active, outside cooling-off → `INELIGIBLE`; standard path is non-renewal.

## Architecture Notes

This project uses the **Agent pattern**:

1. The `OrchestratorAgent` acts as a *router* that selects the appropriate sub-agent.
2. Each sub-agent is a self-contained *decision engine* that applies domain-specific business rules.
3. `parse_intent()` in `utils/helpers.py` provides keyword-based intent detection for plain-English input.
4. All data is modelled with Python `dataclasses` and `enum` – no external AI API keys required.

## Contact (JLR Concierge)

| Channel | Details |
|---|---|
| Phone | 01926 691736 |
| Email | UKwebsales@jaguarlandrover.com |
| Hours | Monday–Friday, 09:00–17:00 |
