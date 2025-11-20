"""
Tests for Hardy validation service

Verifies three-state validation (LATENT → HYPOTHETICAL → PRESTIGE)
Based on TEAOS Hardy framework (agents/hardy_standalone.py)
"""
import pytest
from datetime import date, timedelta
from api.services.hardy_validator import HardyValidator, ConceptState


class TestHardyValidator:
    """Test Hardy validation for ParentPath items"""

    def test_prestige_item_approved(self):
        """
        Test PRESTIGE validation (0.90+ confidence, auto-approve)

        Success criteria:
        - State = PRESTIGE
        - Confidence ≥ 0.90
        - Approved = True
        - No validation issues
        """
        # Perfect item: all fields valid, high Gemini confidence
        item = {
            "type": "Event",
            "title": "Spring Concert",
            "description": "Annual music performance",
            "date": date.today() + timedelta(days=14),  # 2 weeks from now
            "time": "18:00:00",
            "location": "School Gym",
            "audience_tags": ["grade_5", "all"],
            "source_snippet": "Join us for the annual Spring Concert on March 15th at 6pm in the school gym.",
            "confidence_score": 0.95,  # High Gemini confidence
            "gemini_reasoning": "Clear event with all details"
        }

        result = HardyValidator.validate_item(item)

        # Assertions
        assert result["state"] == ConceptState.PRESTIGE.name, \
            f"Expected PRESTIGE, got {result['state']}"
        assert result["confidence"] == 0.90, \
            f"Expected confidence 0.90, got {result['confidence']}"
        assert result["approved"] is True, \
            "PRESTIGE items should be auto-approved"
        assert len(result["issues"]) == 0, \
            f"PRESTIGE item should have no issues, found: {result['issues']}"
        assert "All validation checks passed" in result["reasoning"]

        print(f"✓ PRESTIGE validation passed: {result}")

    def test_hypothetical_needs_review(self):
        """
        Test HYPOTHETICAL validation (0.65-0.89 confidence, needs review)

        Success criteria:
        - State = HYPOTHETICAL
        - Confidence ≥ 0.65
        - Approved = False (needs human review)
        - Some minor issues allowed
        """
        # Good item but with minor issues (low-ish confidence)
        item = {
            "type": "Event",
            "title": "Pizza Day",
            "description": "Hot lunch pizza",
            "date": date.today() + timedelta(days=7),
            "audience_tags": ["grade_5"],
            "source_snippet": "Pizza day next week",  # Short but valid
            "confidence_score": 0.65,  # Moderate Gemini confidence
            "gemini_reasoning": "Likely event but missing some details"
        }

        result = HardyValidator.validate_item(item)

        # Assertions
        assert result["state"] == ConceptState.HYPOTHETICAL.name, \
            f"Expected HYPOTHETICAL, got {result['state']}"
        assert 0.65 <= result["confidence"] < 0.90, \
            f"HYPOTHETICAL confidence should be 0.65-0.89, got {result['confidence']}"
        assert result["approved"] is False, \
            "HYPOTHETICAL items should NOT be auto-approved"
        # Some issues allowed for HYPOTHETICAL
        assert len(result["issues"]) <= 2, \
            f"HYPOTHETICAL can have 1-2 minor issues, found {len(result['issues'])}: {result['issues']}"

        print(f"✓ HYPOTHETICAL validation passed: {result}")

    def test_latent_item_rejected(self):
        """
        Test LATENT validation (<0.65 confidence, reject)

        Success criteria:
        - State = LATENT
        - Confidence < 0.65
        - Approved = False
        - Has critical validation issues
        """
        # Bad item: missing required fields, low confidence
        item = {
            "type": "UnknownType",  # Invalid type
            "title": "",  # Missing title (critical)
            "date": date.today() + timedelta(days=3),
            "audience_tags": [],  # Empty audience (critical)
            "source_snippet": "Bad",  # Too short
            "confidence_score": 0.30,  # Low Gemini confidence
            "gemini_reasoning": "Uncertain extraction"
        }

        result = HardyValidator.validate_item(item)

        # Assertions
        assert result["state"] == ConceptState.LATENT.name, \
            f"Expected LATENT, got {result['state']}"
        assert result["confidence"] < 0.65, \
            f"LATENT confidence should be <0.65, got {result['confidence']}"
        assert result["approved"] is False, \
            "LATENT items should be rejected"
        assert len(result["issues"]) >= 3, \
            f"LATENT item should have multiple issues, found {len(result['issues'])}: {result['issues']}"

        # Check for critical issues
        has_critical = any("missing_required_field" in issue or "invalid_item_type" in issue
                          for issue in result["issues"])
        assert has_critical, "LATENT item should have critical validation issues"

        print(f"✓ LATENT validation passed: {result}")

    def test_batch_validation_stats(self):
        """
        Test batch validation with aggregated statistics

        Success criteria:
        - Correct counts for PRESTIGE/HYPOTHETICAL/LATENT
        - Auto-approval count matches PRESTIGE count
        - Needs-review count matches HYPOTHETICAL count
        - Approval rate calculated correctly
        """
        items = [
            # PRESTIGE item 1
            {
                "type": "Event",
                "title": "Field Trip",
                "date": date.today() + timedelta(days=10),
                "audience_tags": ["grade_5"],
                "source_snippet": "Annual field trip to science center on April 10th",
                "confidence_score": 0.90
            },
            # PRESTIGE item 2
            {
                "type": "Fundraiser",
                "title": "Bake Sale",
                "date": date.today() + timedelta(days=5),
                "audience_tags": ["all"],
                "source_snippet": "Support our school with a bake sale this Friday",
                "confidence_score": 0.85
            },
            # HYPOTHETICAL item
            {
                "type": "Announcement",
                "title": "Library Update",
                "audience_tags": ["all"],
                "source_snippet": "Library hours",
                "confidence_score": 0.65
            },
            # LATENT item
            {
                "type": "Event",
                "title": "",  # Missing title
                "date": date.today() - timedelta(days=30),  # Old date
                "audience_tags": [],  # No audience
                "source_snippet": "X",
                "confidence_score": 0.20
            }
        ]

        result = HardyValidator.validate_batch(items)

        # Assertions
        assert result["total"] == 4, f"Expected 4 items, got {result['total']}"
        assert result["prestige_count"] == 2, \
            f"Expected 2 PRESTIGE, got {result['prestige_count']}"
        assert result["hypothetical_count"] == 1, \
            f"Expected 1 HYPOTHETICAL, got {result['hypothetical_count']}"
        assert result["latent_count"] == 1, \
            f"Expected 1 LATENT, got {result['latent_count']}"
        assert result["auto_approved"] == 2, \
            f"Expected 2 auto-approved (PRESTIGE), got {result['auto_approved']}"
        assert result["needs_review"] == 1, \
            f"Expected 1 needs review (HYPOTHETICAL), got {result['needs_review']}"

        # Approval rate = auto_approved / total = 2/4 = 0.5
        expected_rate = 2 / 4
        assert abs(result["approval_rate"] - expected_rate) < 0.01, \
            f"Expected approval rate {expected_rate}, got {result['approval_rate']}"

        assert len(result["results"]) == 4, \
            "Should return individual results for all items"

        print(f"✓ Batch validation passed: {result}")

    def test_event_date_validation(self):
        """
        Test date validation for events (future dates required)

        Edge cases:
        - Event in past (>7 days) → issue
        - Event in near past (<7 days) → allowed (for newsletters)
        - Event in future → no issue
        """
        # Event >7 days in past (should flag)
        old_event = {
            "type": "Event",
            "title": "Old Event",
            "date": date.today() - timedelta(days=10),
            "audience_tags": ["all"],
            "source_snippet": "This event already happened",
            "confidence_score": 0.80
        }

        result_old = HardyValidator.validate_item(old_event)
        assert any("date_in_past" in issue for issue in result_old["issues"]), \
            "Should flag event >7 days in past"

        # Event within 7 days (should allow for newsletters)
        recent_event = {
            "type": "Event",
            "title": "Recent Event",
            "date": date.today() - timedelta(days=3),
            "audience_tags": ["all"],
            "source_snippet": "This event was very recent, might be in this week's newsletter",
            "confidence_score": 0.85
        }

        result_recent = HardyValidator.validate_item(recent_event)
        assert not any("date_in_past" in issue for issue in result_recent["issues"]), \
            "Should allow event within 7 days (newsletter window)"

        print("✓ Event date validation passed")

    def test_missing_confidence_score(self):
        """
        Test handling when Gemini confidence_score is missing

        Should flag as LOW_CONFIDENCE:missing
        """
        item = {
            "type": "Event",
            "title": "Event Without Confidence",
            "date": date.today() + timedelta(days=5),
            "audience_tags": ["all"],
            "source_snippet": "Some event description",
            # confidence_score: missing
        }

        result = HardyValidator.validate_item(item)

        # Should flag missing confidence
        assert any("low_gemini_confidence:missing" in issue for issue in result["issues"]), \
            "Should flag missing Gemini confidence score"

        print("✓ Missing confidence handling passed")


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
