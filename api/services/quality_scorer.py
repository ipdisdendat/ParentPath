"""
ParentPath Quality Scorer - Multi-signal confidence scoring for parsed items

Pattern: Adapted from CHAI quality_scorer.py (compliance scoring)
Purpose: Validate item extraction quality before delivery

Architecture:
    QualityScorer
      ├─ Multi-signal confidence (Gemini + field completeness + snippet quality)
      ├─ Audience tag specificity scoring
      └─ Overall quality assessment

Integration:
- api/models/item.py (Item model with confidence_score, source_snippet)
- Gemini confidence (0.0-1.0)
- Field completeness check
- Source snippet quality

Evidence:
- chai/quality_scorer.py:8-94 (multi-component scoring pattern)
- chai/quality_scorer.py:156-218 (quality breakdown pattern)
"""

from typing import Dict, Any, Optional
from decimal import Decimal


class QualityScorer:
    """
    Scores item extraction quality based on multiple signals

    Signals:
    - Gemini confidence (40%)
    - Field completeness (30%)
    - Source snippet quality (20%)
    - Audience tag specificity (10%)
    """

    def __init__(self):
        """Initialize quality scorer with scoring weights"""
        self.gemini_weight = 0.40  # AI confidence
        self.completeness_weight = 0.30  # Required fields present
        self.snippet_weight = 0.20  # Source snippet quality
        self.tag_weight = 0.10  # Audience tag specificity

    def score_item(self, item_data: Dict[str, Any]) -> float:
        """
        Calculate overall quality score for extracted item

        Pattern: Adapted from chai/quality_scorer.py:19-54

        Args:
            item_data: Dictionary with item fields

        Returns:
            Overall quality score 0.0-1.0
        """
        # Component scores
        gemini_score = self._score_gemini_confidence(item_data)
        completeness_score = self._score_field_completeness(item_data)
        snippet_score = self._score_snippet_quality(item_data)
        tag_score = self._score_tag_specificity(item_data)

        # Weighted average
        overall_score = (
            gemini_score * self.gemini_weight +
            completeness_score * self.completeness_weight +
            snippet_score * self.snippet_weight +
            tag_score * self.tag_weight
        )

        return round(overall_score, 3)

    def _score_gemini_confidence(self, item_data: Dict[str, Any]) -> float:
        """
        Extract Gemini's confidence score

        Args:
            item_data: Item dictionary

        Returns:
            Gemini confidence 0.0-1.0
        """
        confidence = item_data.get('confidence_score')

        if confidence is None:
            # No Gemini confidence available
            return 0.5  # Neutral score

        # Convert Decimal to float if needed
        if isinstance(confidence, Decimal):
            confidence = float(confidence)

        # Ensure 0.0-1.0 range
        return max(0.0, min(1.0, confidence))

    def _score_field_completeness(self, item_data: Dict[str, Any]) -> float:
        """
        Score based on required field completeness

        Pattern: Adapted from chai/quality_scorer.py:56-94

        Args:
            item_data: Item dictionary

        Returns:
            Completeness score 0.0-1.0
        """
        # Required fields by type
        type_requirements = {
            'Event': ['title', 'date', 'description'],
            'PermissionSlip': ['title', 'deadline', 'action_link'],
            'Fundraiser': ['title', 'description', 'cost'],
            'HotLunch': ['title', 'date', 'cost', 'deadline'],
            'Announcement': ['title', 'description']
        }

        item_type = item_data.get('type', 'Announcement')
        required_fields = type_requirements.get(item_type, ['title', 'description'])

        # Count present fields
        present_count = sum(
            1 for field in required_fields
            if item_data.get(field) is not None
        )

        completeness = present_count / len(required_fields) if required_fields else 0.0

        # Bonus for optional enrichments (location, time, etc.)
        optional_fields = ['location', 'time', 'end_date', 'cost']
        optional_count = sum(
            1 for field in optional_fields
            if item_data.get(field) is not None
        )

        # Add up to 20% bonus for optional fields
        optional_bonus = min(optional_count / len(optional_fields), 1.0) * 0.2

        return min(completeness + optional_bonus, 1.0)

    def _score_snippet_quality(self, item_data: Dict[str, Any]) -> float:
        """
        Score source snippet quality

        Args:
            item_data: Item dictionary

        Returns:
            Snippet quality score 0.0-1.0
        """
        snippet = item_data.get('source_snippet', '')

        if not snippet:
            return 0.3  # Missing snippet is low quality

        # Length quality (prefer 50-300 chars)
        length = len(snippet)

        if length < 20:
            length_score = 0.3  # Too short
        elif 50 <= length <= 300:
            length_score = 1.0  # Ideal length
        elif length < 50:
            length_score = 0.7  # Slightly short
        elif length <= 500:
            length_score = 0.8  # Slightly long
        else:
            length_score = 0.5  # Too long

        # Content quality checks
        content_score = 1.0

        # Check for noise indicators
        noise_indicators = [
            '...', '???', 'N/A', 'TBD', 'MISSING',
            'error', 'failed', 'unable to extract'
        ]

        for indicator in noise_indicators:
            if indicator.lower() in snippet.lower():
                content_score -= 0.2

        content_score = max(0.0, content_score)

        # Combined score
        return (length_score * 0.5 + content_score * 0.5)

    def _score_tag_specificity(self, item_data: Dict[str, Any]) -> float:
        """
        Score audience tag specificity

        Pattern: More specific tags = higher quality
        Examples:
        - 'all' = 0.3 (too broad)
        - 'grade_5' = 0.7 (good specificity)
        - 'grade_5,Basketball' = 1.0 (very specific)

        Args:
            item_data: Item dictionary

        Returns:
            Tag specificity score 0.0-1.0
        """
        audience_tags = item_data.get('audience_tags', [])

        if not audience_tags:
            return 0.0  # No tags

        # Check for 'all' tag only
        if audience_tags == ['all']:
            return 0.3  # Too broad

        # Count specific tags (grade_X, activity names)
        specific_tag_count = sum(
            1 for tag in audience_tags
            if tag != 'all'
        )

        # Score based on specificity
        if specific_tag_count == 0:
            return 0.3  # Only 'all' tag
        elif specific_tag_count == 1:
            return 0.7  # One specific tag
        elif specific_tag_count >= 2:
            return 1.0  # Multiple specific tags

        return 0.5  # Default

    def calculate_quality_breakdown(
        self,
        item_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate detailed quality breakdown

        Pattern: Adapted from chai/quality_scorer.py:156-218

        Args:
            item_data: Item dictionary

        Returns:
            Dictionary with detailed scores and recommendations
        """
        # Component scores
        gemini_score = self._score_gemini_confidence(item_data)
        completeness_score = self._score_field_completeness(item_data)
        snippet_score = self._score_snippet_quality(item_data)
        tag_score = self._score_tag_specificity(item_data)

        # Overall score
        overall_score = self.score_item(item_data)

        # Determine quality level
        quality_level = self._score_to_quality_level(overall_score)

        # Identify strengths and weaknesses
        strengths = []
        weaknesses = []

        if gemini_score >= 0.7:
            strengths.append("High AI confidence")
        elif gemini_score < 0.5:
            weaknesses.append("Low AI confidence - needs review")

        if completeness_score >= 0.8:
            strengths.append("All required fields present")
        elif completeness_score < 0.6:
            weaknesses.append("Missing required fields")

        if snippet_score >= 0.7:
            strengths.append("Good source snippet quality")
        elif snippet_score < 0.5:
            weaknesses.append("Poor source snippet - may need re-extraction")

        if tag_score >= 0.7:
            strengths.append("Specific audience targeting")
        elif tag_score < 0.5:
            weaknesses.append("Broad audience tags - consider refinement")

        # Recommendation
        recommendation = self._get_quality_recommendation(quality_level)

        return {
            'overall_score': overall_score,
            'overall_percentage': round(overall_score * 100, 1),
            'quality_level': quality_level,
            'component_scores': {
                'gemini_confidence': round(gemini_score, 3),
                'field_completeness': round(completeness_score, 3),
                'snippet_quality': round(snippet_score, 3),
                'tag_specificity': round(tag_score, 3)
            },
            'weights': {
                'gemini_weight': self.gemini_weight,
                'completeness_weight': self.completeness_weight,
                'snippet_weight': self.snippet_weight,
                'tag_weight': self.tag_weight
            },
            'strengths': strengths,
            'weaknesses': weaknesses,
            'recommendation': recommendation
        }

    def _score_to_quality_level(self, score: float) -> str:
        """
        Convert score to quality level label

        Args:
            score: Quality score 0.0-1.0

        Returns:
            Quality level (Excellent, Good, Fair, Poor)
        """
        if score >= 0.85:
            return 'Excellent'
        elif score >= 0.70:
            return 'Good'
        elif score >= 0.55:
            return 'Fair'
        else:
            return 'Poor'

    def _get_quality_recommendation(self, quality_level: str) -> str:
        """
        Get recommendation based on quality level

        Args:
            quality_level: Quality level string

        Returns:
            Recommendation text
        """
        recommendations = {
            'Excellent': 'Ready for delivery to parents. High confidence.',
            'Good': 'Approved for delivery. Minor refinements may improve quality.',
            'Fair': 'Review recommended. May need field enrichment or tag refinement.',
            'Poor': 'Manual review required before delivery. Check extraction accuracy.'
        }

        return recommendations.get(quality_level, 'Review quality metrics before delivery.')

    def batch_score_items(
        self,
        items_data: list[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Score multiple items in batch

        Args:
            items_data: List of item dictionaries

        Returns:
            Batch scoring summary
        """
        scores = [self.score_item(item) for item in items_data]

        if not scores:
            return {
                'total_items': 0,
                'average_score': 0.0,
                'quality_distribution': {}
            }

        # Calculate statistics
        average_score = sum(scores) / len(scores)

        # Quality distribution
        distribution = {
            'Excellent': sum(1 for s in scores if s >= 0.85),
            'Good': sum(1 for s in scores if 0.70 <= s < 0.85),
            'Fair': sum(1 for s in scores if 0.55 <= s < 0.70),
            'Poor': sum(1 for s in scores if s < 0.55)
        }

        return {
            'total_items': len(items_data),
            'average_score': round(average_score, 3),
            'average_percentage': round(average_score * 100, 1),
            'quality_distribution': distribution,
            'items_needing_review': distribution['Fair'] + distribution['Poor']
        }
