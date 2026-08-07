"""
Lab 11 — Part 4: Human-in-the-Loop Design
  TODO 11: Confidence Router
  TODO 12: Design 3 HITL decision points
"""
from dataclasses import dataclass


# ============================================================
# TODO 11: Implement ConfidenceRouter
#
# Route agent responses based on confidence scores:
#   - HIGH (>= 0.9): Auto-send to user
#   - MEDIUM (0.7 - 0.9): Queue for human review
#   - LOW (< 0.7): Escalate to human immediately
#
# Special case: if the action is HIGH_RISK (e.g., money transfer,
# account deletion), ALWAYS escalate regardless of confidence.
#
# Implement the route() method.
# ============================================================

HIGH_RISK_ACTIONS = [
    "transfer_money",
    "close_account",
    "change_password",
    "delete_data",
    "update_personal_info",
]


@dataclass
class RoutingDecision:
    """Result of the confidence router."""
    action: str          # "auto_send", "queue_review", "escalate"
    confidence: float
    reason: str
    priority: str        # "low", "normal", "high"
    requires_human: bool


class ConfidenceRouter:
    """Route agent responses based on confidence and risk level.

    Thresholds:
        HIGH:   confidence >= 0.9 -> auto-send
        MEDIUM: 0.7 <= confidence < 0.9 -> queue for review
        LOW:    confidence < 0.7 -> escalate to human

    High-risk actions always escalate regardless of confidence.
    """

    HIGH_THRESHOLD = 0.9
    MEDIUM_THRESHOLD = 0.7

    def route(self, response: str, confidence: float,
              action_type: str = "general") -> RoutingDecision:
        """Route a response based on confidence score and action type.

        Args:
            response: The agent's response text
            confidence: Confidence score between 0.0 and 1.0
            action_type: Type of action (e.g., "general", "transfer_money")

        Returns:
            RoutingDecision with routing action and metadata
        """
        if action_type in HIGH_RISK_ACTIONS:
            return RoutingDecision(
                action="escalate",
                confidence=confidence,
                reason=f"High-risk action: {action_type}",
                priority="high",
                requires_human=True,
            )

        if confidence >= self.HIGH_THRESHOLD:
            return RoutingDecision(
                action="auto_send",
                confidence=confidence,
                reason="High confidence",
                priority="low",
                requires_human=False,
            )
        elif confidence >= self.MEDIUM_THRESHOLD:
            return RoutingDecision(
                action="queue_review",
                confidence=confidence,
                reason="Medium confidence — needs review",
                priority="normal",
                requires_human=True,
            )
        else:
            return RoutingDecision(
                action="escalate",
                confidence=confidence,
                reason="Low confidence — escalating",
                priority="high",
                requires_human=True,
            )


# ============================================================
# TODO 12: Design 3 HITL decision points + a review lifecycle
# ============================================================

hitl_decision_points = [
    {
        "id": 1,
        "name": "High-Value Money Transfer Approval",
        "trigger": "Action is transfer_money and amount >= 50,000,000 VND or transfer_money requested via untrusted channel",
        "hitl_model": "human-in-the-loop",
        "context_needed": "Sender account, Beneficiary account & bank, exact amount, user IP/device ID, intent diff, and fraud risk score",
        "example": "User requests transferring 100,000,000 VND to a newly added external beneficiary account",
        "approval_path": "Approve: Transaction executed & logged; Reject: Transaction cancelled with user alert; Timeout: Auto-hold after 10 mins and notify supervisor",
        "audit_fields": "correlation_id, intent_type, amount, sender_id, recipient_id, reviewer_id, review_decision, timestamp",
    },
    {
        "id": 2,
        "name": "Account Closure & Sensitive Data Deletion",
        "trigger": "Action is close_account or delete_data",
        "hitl_model": "human-in-the-loop",
        "context_needed": "Account status, outstanding loan/credit balance, verification status, and reason for termination",
        "example": "User asks the chatbot to immediately close savings account and delete transaction history",
        "approval_path": "Approve: Flag account for 2-step verification & queue closure; Reject: Cancel request & notify customer; Timeout: Decline automatically after 15 mins",
        "audit_fields": "correlation_id, user_id, action_type, account_status, remaining_balance, reviewer_id, decision, timestamp",
    },
    {
        "id": 3,
        "name": "Credential & Contact Info Modification",
        "trigger": "Action is change_password or update_personal_info",
        "hitl_model": "human-on-the-loop",
        "context_needed": "Old vs proposed new phone/email/address, multi-factor auth (MFA) log, device fingerprint, and recent password reset history",
        "example": "User requests updating registered OTP phone number to a new number from an unrecognized location",
        "approval_path": "Approve: Update credentials & trigger SMS alert to old number; Reject: Block update & lock account for 1 hour; Timeout: Hold update until secondary OTP verification",
        "audit_fields": "correlation_id, user_id, field_changed, old_value_masked, new_value_masked, mfa_status, reviewer_id, timestamp",
    },
]


# ============================================================
# Quick tests
# ============================================================

def test_confidence_router():
    """Test ConfidenceRouter with sample scenarios."""
    router = ConfidenceRouter()

    test_cases = [
        ("Balance inquiry", 0.95, "general"),
        ("Interest rate question", 0.82, "general"),
        ("Ambiguous request", 0.55, "general"),
        ("Transfer $50,000", 0.98, "transfer_money"),
        ("Close my account", 0.91, "close_account"),
    ]

    print("Testing ConfidenceRouter:")
    print("=" * 80)
    print(f"{'Scenario':<25} {'Conf':<6} {'Action Type':<18} {'Decision':<15} {'Priority':<10} {'Human?'}")
    print("-" * 80)

    for scenario, conf, action_type in test_cases:
        decision = router.route(scenario, conf, action_type)
        print(
            f"{scenario:<25} {conf:<6.2f} {action_type:<18} "
            f"{decision.action:<15} {decision.priority:<10} "
            f"{'Yes' if decision.requires_human else 'No'}"
        )

    print("=" * 80)


def test_hitl_points():
    """Display HITL decision points."""
    print("\nHITL Decision Points:")
    print("=" * 60)
    for point in hitl_decision_points:
        print(f"\n  Decision Point #{point['id']}: {point['name']}")
        print(f"    Trigger:  {point['trigger']}")
        print(f"    Model:    {point['hitl_model']}")
        print(f"    Context:  {point['context_needed']}")
        print(f"    Example:  {point['example']}")
    print("\n" + "=" * 60)


if __name__ == "__main__":
    test_confidence_router()
    test_hitl_points()
