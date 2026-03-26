"""JLR Agentic AI Cancellation System — CLI entry point.

Run with:
    python main.py

The CLI presents an interactive menu that lets a customer describe their
cancellation need.  The orchestrator agent routes the request to the
appropriate sub-agent and displays a structured response.

Example (non-interactive / piped input):
    echo "I want to cancel my vehicle reservation" | python main.py
"""

import sys
from datetime import date

from agents.orchestrator import OrchestratorAgent
from models.cancellation_request import CancellationRequest, CancellationType
from utils.helpers import format_response, parse_intent

# ---------------------------------------------------------------------------
# Menu helpers
# ---------------------------------------------------------------------------

_MENU = """
╔══════════════════════════════════════════════════════════════╗
║       JLR UK Order Cancellation — Agentic AI Assistant       ║
╚══════════════════════════════════════════════════════════════╝

Please select the type of cancellation:

  1. Vehicle order / reservation
  2. Merchandise (lifestyle store)
  3. Approved Warranty
  4. InControl subscription / connected services
  5. I'm not sure — describe my issue

  0. Exit

Enter choice [0-5]: """

_TYPE_MAP = {
    "1": CancellationType.VEHICLE_ORDER,
    "2": CancellationType.MERCHANDISE,
    "3": CancellationType.WARRANTY,
    "4": CancellationType.SUBSCRIPTION,
}


def _prompt(label: str, default: str = "") -> str:
    """Prompt the user for a value, returning ``default`` if blank."""
    value = input(f"  {label}: ").strip()
    return value if value else default


def _prompt_bool(label: str) -> bool:
    """Prompt the user for a yes/no answer."""
    answer = input(f"  {label} [y/N]: ").strip().lower()
    return answer in ("y", "yes")


def _prompt_int(label: str) -> int | None:
    """Prompt the user for an integer; returns ``None`` if blank or invalid."""
    raw = input(f"  {label} (press Enter to skip): ").strip()
    if not raw:
        return None
    try:
        return int(raw)
    except ValueError:
        return None


# ---------------------------------------------------------------------------
# Request builders per cancellation type
# ---------------------------------------------------------------------------

def _build_vehicle_request(ref: str, name: str, email: str) -> CancellationRequest:
    contract_signed = _prompt_bool(
        "Have you already signed a purchase or finance contract with the retailer?"
    )
    return CancellationRequest(
        cancellation_type=CancellationType.VEHICLE_ORDER,
        order_reference=ref,
        customer_name=name,
        contact_email=email,
        request_date=date.today(),
        contract_signed=contract_signed,
    )


def _build_merchandise_request(
    ref: str, name: str, email: str
) -> CancellationRequest:
    days = _prompt_int("How many days ago did you receive the order?")
    personalised = _prompt_bool("Is the item personalised / custom-made?")
    goods_returned = _prompt_bool("Have you already returned / dispatched the goods?")
    return CancellationRequest(
        cancellation_type=CancellationType.MERCHANDISE,
        order_reference=ref,
        customer_name=name,
        contact_email=email,
        request_date=date.today(),
        days_since_purchase=days,
        is_personalised_item=personalised,
        goods_returned=goods_returned,
    )


def _build_warranty_request(ref: str, name: str, email: str) -> CancellationRequest:
    days = _prompt_int(
        "How many days ago did you receive the warranty booklet / confirmation?"
    )
    claim_made = _prompt_bool("Has a warranty claim already been made or paid?")
    return CancellationRequest(
        cancellation_type=CancellationType.WARRANTY,
        order_reference=ref,
        customer_name=name,
        contact_email=email,
        request_date=date.today(),
        days_since_purchase=days,
        claim_made=claim_made,
    )


def _build_subscription_request(
    ref: str, name: str, email: str
) -> CancellationRequest:
    days = _prompt_int("How many days ago did you purchase the subscription?")
    vehicle_sold = _prompt_bool("Has the vehicle been sold or has the lease ended?")
    subscription_active = not _prompt_bool(
        "Has the subscription already expired / ended?"
    )
    return CancellationRequest(
        cancellation_type=CancellationType.SUBSCRIPTION,
        order_reference=ref,
        customer_name=name,
        contact_email=email,
        request_date=date.today(),
        days_since_purchase=days,
        vehicle_sold=vehicle_sold,
        subscription_active=subscription_active,
    )


# ---------------------------------------------------------------------------
# Main flow
# ---------------------------------------------------------------------------

_BUILDERS = {
    CancellationType.VEHICLE_ORDER: _build_vehicle_request,
    CancellationType.MERCHANDISE: _build_merchandise_request,
    CancellationType.WARRANTY: _build_warranty_request,
    CancellationType.SUBSCRIPTION: _build_subscription_request,
}


def _gather_common_fields() -> tuple[str, str, str]:
    """Collect the fields common to all cancellation types."""
    print()
    ref = _prompt("Order / reference number", default="UNKNOWN")
    name = _prompt("Your full name", default="Customer")
    email = _prompt("Your email address", default="")
    return ref, name, email


def run_cli() -> None:
    """Main CLI loop."""
    orchestrator = OrchestratorAgent()
    print("\nWelcome to the JLR Agentic AI Cancellation Assistant.")

    while True:
        choice = input(_MENU).strip()

        if choice == "0":
            print("\nThank you for using the JLR Cancellation Assistant. Goodbye!\n")
            sys.exit(0)

        if choice in _TYPE_MAP:
            cancellation_type = _TYPE_MAP[choice]
        elif choice == "5":
            description = input(
                "\n  Please describe your cancellation issue:\n  > "
            ).strip()
            cancellation_type = parse_intent(description)
            if cancellation_type == CancellationType.UNKNOWN:
                print(
                    "\n  Unable to determine cancellation type from your description.\n"
                    "  Please contact JLR Concierge directly:\n"
                    "    Phone : 01926 691736\n"
                    "    Email : UKwebsales@jaguarlandrover.com\n"
                    "    Hours : Monday–Friday, 09:00–17:00\n"
                )
                continue
            print(
                f"\n  Detected cancellation type: "
                f"{cancellation_type.name.replace('_', ' ').title()}"
            )
        else:
            print("\n  Invalid choice. Please enter a number between 0 and 5.\n")
            continue

        ref, name, email = _gather_common_fields()
        builder = _BUILDERS[cancellation_type]
        request = builder(ref, name, email)

        response = orchestrator.process(request)
        print(format_response(response))


if __name__ == "__main__":
    run_cli()
