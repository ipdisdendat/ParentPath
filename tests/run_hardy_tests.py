"""Simple test runner for Hardy validation"""
import sys
sys.path.insert(0, '.')

from datetime import date, timedelta
from api.services.hardy_validator import HardyValidator, ConceptState


def test_prestige_item_approved():
    """Test PRESTIGE validation (0.90+ confidence, auto-approve)"""
    item = {
        "type": "Event",
        "title": "Spring Concert",
        "description": "Annual music performance",
        "date": date.today() + timedelta(days=14),
        "time": "18:00:00",
        "location": "School Gym",
        "audience_tags": ["grade_5", "all"],
        "source_snippet": "Join us for the annual Spring Concert on March 15th at 6pm in the school gym.",
        "confidence_score": 0.95,
        "gemini_reasoning": "Clear event with all details"
    }

    result = HardyValidator.validate_item(item)

    assert result["state"] == ConceptState.PRESTIGE.name
    assert result["confidence"] == 0.90
    assert result["approved"] is True
    assert len(result["issues"]) == 0

    print("PASS: test_prestige_item_approved")
    return True


def test_hypothetical_needs_review():
    """Test HYPOTHETICAL validation (0.65-0.89 confidence, needs review)"""
    item = {
        "type": "Event",
        "title": "Pizza Day",
        "description": "Hot lunch pizza",
        "date": date.today() + timedelta(days=7),
        "audience_tags": ["grade_5"],
        "source_snippet": "Pizza day next week",
        "confidence_score": 0.65,
        "gemini_reasoning": "Likely event but missing some details"
    }

    result = HardyValidator.validate_item(item)

    assert result["state"] == ConceptState.HYPOTHETICAL.name
    assert 0.65 <= result["confidence"] < 0.90
    assert result["approved"] is False

    print("PASS: test_hypothetical_needs_review")
    return True


def test_latent_item_rejected():
    """Test LATENT validation (<0.65 confidence, reject)"""
    item = {
        "type": "UnknownType",
        "title": "",
        "date": date.today() + timedelta(days=3),
        "audience_tags": [],
        "source_snippet": "Bad",
        "confidence_score": 0.30,
        "gemini_reasoning": "Uncertain extraction"
    }

    result = HardyValidator.validate_item(item)

    assert result["state"] == ConceptState.LATENT.name
    assert result["confidence"] < 0.65
    assert result["approved"] is False
    assert len(result["issues"]) >= 3

    print("PASS: test_latent_item_rejected")
    return True


def test_batch_validation_stats():
    """Test batch validation with aggregated statistics"""
    items = [
        # PRESTIGE 1
        {
            "type": "Event",
            "title": "Field Trip",
            "date": date.today() + timedelta(days=10),
            "audience_tags": ["grade_5"],
            "source_snippet": "Annual field trip to science center on April 10th",
            "confidence_score": 0.90
        },
        # PRESTIGE 2
        {
            "type": "Fundraiser",
            "title": "Bake Sale",
            "date": date.today() + timedelta(days=5),
            "audience_tags": ["all"],
            "source_snippet": "Support our school with a bake sale this Friday",
            "confidence_score": 0.85
        },
        # HYPOTHETICAL
        {
            "type": "Announcement",
            "title": "Library Update",
            "audience_tags": ["all"],
            "source_snippet": "Library hours",
            "confidence_score": 0.65
        },
        # LATENT
        {
            "type": "Event",
            "title": "",
            "date": date.today() - timedelta(days=30),
            "audience_tags": [],
            "source_snippet": "X",
            "confidence_score": 0.20
        }
    ]

    result = HardyValidator.validate_batch(items)

    assert result["total"] == 4
    assert result["prestige_count"] == 2
    assert result["hypothetical_count"] == 1
    assert result["latent_count"] == 1
    assert result["auto_approved"] == 2
    assert result["needs_review"] == 1
    assert abs(result["approval_rate"] - 0.5) < 0.01

    print("PASS: test_batch_validation_stats")
    return True


if __name__ == "__main__":
    tests = [
        test_prestige_item_approved,
        test_hypothetical_needs_review,
        test_latent_item_rejected,
        test_batch_validation_stats
    ]

    passed = 0
    failed = 0

    print("Running Hardy validation tests...\n")

    for test in tests:
        try:
            if test():
                passed += 1
        except AssertionError as e:
            print(f"FAIL: {test.__name__} - {e}")
            failed += 1
        except Exception as e:
            print(f"ERROR: {test.__name__} - {e}")
            failed += 1

    print(f"\n{'='*60}")
    print(f"Results: {passed}/{len(tests)} tests passed")
    print(f"{'='*60}")

    if failed == 0:
        print("\n[OK] All Hardy validation tests passed!")
        sys.exit(0)
    else:
        print(f"\n[FAIL] {failed} test(s) failed")
        sys.exit(1)
