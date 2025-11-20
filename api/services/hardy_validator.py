"""
Hardy Validation Service for ParentPath

Adapted from TEAOS Hardy framework (agents/hardy_standalone.py:43-47)
Three-state validation: LATENT → HYPOTHETICAL → PRESTIGE
"""
from enum import Enum
from typing import Dict, List, Any, Optional
from datetime import datetime, date
from decimal import Decimal


class ConceptState(Enum):
    """Three-state validation progression (TEAOS Hardy framework)"""
    LATENT = 0.45       # Observed, unvalidated - needs review or rejection
    HYPOTHETICAL = 0.65  # Working validation - needs human review
    PRESTIGE = 0.90     # Validated, deployable - auto-approve


class ValidationIssue:
    """Structured validation issue"""
    MISSING_FIELD = "missing_required_field"
    INVALID_DATE = "invalid_date_range"
    INVALID_AUDIENCE = "invalid_audience_tags"
    LOW_CONFIDENCE = "low_gemini_confidence"
    MISSING_SOURCE = "missing_source_snippet"
    INVALID_TYPE = "invalid_item_type"
    FUTURE_DATE = "date_in_past"


class HardyValidator:
    """
    Hardy validation service adapted for ParentPath items

    Confidence thresholds (TEAOS standard):
    - PRESTIGE (0.90+): Auto-approve, high confidence
    - HYPOTHETICAL (0.65-0.89): Human review queue
    - LATENT (<0.65): Reject, too uncertain

    Evidence requirements:
    - Required fields present
    - Dates valid for events
    - Audience tags present and valid
    - Source snippet quality check
    - Gemini confidence threshold
    """

    # Valid item types
    VALID_TYPES = {'Event', 'PermissionSlip', 'Fundraiser', 'HotLunch', 'Announcement'}

    # Confidence thresholds (from TEAOS Hardy framework)
    PRESTIGE_THRESHOLD = 0.90
    HYPOTHETICAL_THRESHOLD = 0.65
    LATENT_THRESHOLD = 0.45

    @staticmethod
    def validate_item(item: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate a single item using Hardy framework

        Args:
            item: Dict with item fields (matches Item model schema)

        Returns:
            {
                "state": "PRESTIGE" | "HYPOTHETICAL" | "LATENT",
                "confidence": float,
                "issues": List[str],
                "approved": bool,
                "reasoning": str
            }
        """
        issues = []
        reasoning_parts = []

        # 1. Check required fields
        if not item.get('type'):
            issues.append(ValidationIssue.MISSING_FIELD + ":type")
        if not item.get('title'):
            issues.append(ValidationIssue.MISSING_FIELD + ":title")
        if not item.get('audience_tags') or len(item.get('audience_tags', [])) == 0:
            issues.append(ValidationIssue.INVALID_AUDIENCE)

        # 2. Validate item type
        if item.get('type') and item['type'] not in HardyValidator.VALID_TYPES:
            issues.append(ValidationIssue.INVALID_TYPE + f":{item['type']}")

        # 3. Validate dates for events
        if item.get('type') == 'Event':
            if not item.get('date'):
                issues.append(ValidationIssue.MISSING_FIELD + ":date")
            else:
                # Check if event date is in the future (or very recent)
                event_date = item['date']
                if isinstance(event_date, str):
                    try:
                        event_date = datetime.fromisoformat(event_date).date()
                    except:
                        issues.append(ValidationIssue.INVALID_DATE + ":date_parse_failed")
                        event_date = None

                if event_date:
                    today = date.today()
                    # Allow events up to 7 days in the past (for newsletters)
                    from datetime import timedelta
                    if event_date < (today - timedelta(days=7)):
                        issues.append(ValidationIssue.FUTURE_DATE)
                        reasoning_parts.append(f"Event date {event_date} is >7 days past")

            # Check date ordering if end_date exists
            if item.get('end_date') and item.get('date'):
                start = item['date']
                end = item['end_date']
                if isinstance(start, str):
                    start = datetime.fromisoformat(start).date()
                if isinstance(end, str):
                    end = datetime.fromisoformat(end).date()
                if end < start:
                    issues.append(ValidationIssue.INVALID_DATE + ":end_before_start")

        # 4. Check source snippet quality
        source_snippet = item.get('source_snippet', '')
        if not source_snippet or len(source_snippet.strip()) < 10:
            issues.append(ValidationIssue.MISSING_SOURCE)
            reasoning_parts.append("Source snippet missing or too short")

        # 5. Check Gemini confidence
        gemini_confidence = item.get('confidence_score')
        if gemini_confidence is None:
            issues.append(ValidationIssue.LOW_CONFIDENCE + ":missing")
            reasoning_parts.append("No Gemini confidence score")
        else:
            # Convert to float if Decimal
            if isinstance(gemini_confidence, Decimal):
                gemini_confidence = float(gemini_confidence)
            if gemini_confidence < 0.5:
                issues.append(ValidationIssue.LOW_CONFIDENCE + f":{gemini_confidence}")
                reasoning_parts.append(f"Gemini confidence {gemini_confidence} < 0.5")

        # Determine Hardy state based on issues and confidence
        state, confidence = HardyValidator._determine_state(
            issues=issues,
            gemini_confidence=gemini_confidence if gemini_confidence is not None else 0.0
        )

        # Auto-approve if PRESTIGE
        approved = (state == ConceptState.PRESTIGE)

        # Build reasoning
        if not reasoning_parts:
            reasoning_parts.append("All validation checks passed")
        reasoning = "; ".join(reasoning_parts)

        return {
            "state": state.name,
            "confidence": confidence,
            "issues": issues,
            "approved": approved,
            "reasoning": reasoning
        }

    @staticmethod
    def _determine_state(issues: List[str], gemini_confidence: float) -> tuple:
        """
        Determine Hardy state based on validation issues and Gemini confidence

        Logic:
        - 0 critical issues + Gemini ≥0.80 → PRESTIGE (0.90)
        - 0 critical issues + Gemini ≥0.60 → HYPOTHETICAL (0.70)
        - 1-2 minor issues + Gemini ≥0.70 → HYPOTHETICAL (0.65)
        - 3+ issues OR critical issues → LATENT (0.40)

        Critical issues: missing_required_field, invalid_item_type
        """
        # Count critical vs minor issues
        critical_issues = [i for i in issues if
                          ValidationIssue.MISSING_FIELD in i or
                          ValidationIssue.INVALID_TYPE in i]
        minor_issues = [i for i in issues if i not in critical_issues]

        has_critical = len(critical_issues) > 0
        issue_count = len(issues)

        # PRESTIGE: No issues, high Gemini confidence
        if issue_count == 0 and gemini_confidence >= 0.80:
            return ConceptState.PRESTIGE, 0.90

        # HYPOTHETICAL: No critical issues, decent confidence
        if not has_critical:
            if gemini_confidence >= 0.60 and issue_count <= 2:
                return ConceptState.HYPOTHETICAL, 0.70
            elif gemini_confidence >= 0.50 and issue_count <= 1:
                return ConceptState.HYPOTHETICAL, 0.65

        # LATENT: Critical issues or too many problems
        return ConceptState.LATENT, 0.40

    @staticmethod
    def validate_batch(items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate batch of items with aggregated statistics

        Args:
            items: List of item dicts

        Returns:
            {
                "total": int,
                "prestige_count": int,
                "hypothetical_count": int,
                "latent_count": int,
                "auto_approved": int,
                "needs_review": int,
                "approval_rate": float,
                "results": List[Dict]  # Individual validation results
            }
        """
        results = []
        prestige_count = 0
        hypothetical_count = 0
        latent_count = 0
        auto_approved = 0

        for item in items:
            result = HardyValidator.validate_item(item)
            results.append(result)

            # Count states
            if result['state'] == ConceptState.PRESTIGE.name:
                prestige_count += 1
                auto_approved += 1
            elif result['state'] == ConceptState.HYPOTHETICAL.name:
                hypothetical_count += 1
            else:  # LATENT
                latent_count += 1

        total = len(items)
        needs_review = hypothetical_count
        approval_rate = (auto_approved / total) if total > 0 else 0.0

        return {
            "total": total,
            "prestige_count": prestige_count,
            "hypothetical_count": hypothetical_count,
            "latent_count": latent_count,
            "auto_approved": auto_approved,
            "needs_review": needs_review,
            "approval_rate": approval_rate,
            "results": results
        }
