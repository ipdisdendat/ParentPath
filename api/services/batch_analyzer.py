"""
ParentPath Batch Analyzer - Generate personalized weekly digests for parents

Pattern: Adapted from CHAI batch_analyzer.py (parallel facility compliance)
Purpose: Weekly digest generation with grade/activity filtering

Architecture:
    BatchAnalyzer
      ├─ Generate personalized digests per parent
      ├─ Filter items by child grades + activity subscriptions
      ├─ Group by type (Events, PermissionSlips, etc.)
      └─ Format with emojis for WhatsApp + translate

Integration:
- api/models/parent.py (Parent, Child, Subscription models)
- api/models/item.py (Item model with audience_tags)
- api/services/gemini_service.py (translation)

Evidence:
- chai/batch_analyzer.py:162-211 (parallel analysis pattern)
- chai/batch_analyzer.py:302-353 (aggregation pattern)
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from api.models.parent import Parent, Child, Subscription
from api.models.item import Item


class BatchAnalyzer:
    """
    Generate personalized weekly digests for parents

    Filters items by:
    - Child grades
    - Activity subscriptions
    - Date range

    Formats output for WhatsApp delivery
    """

    # Type emojis for WhatsApp formatting
    TYPE_EMOJIS = {
        'Event': '📅',
        'PermissionSlip': '📝',
        'Fundraiser': '💰',
        'HotLunch': '🍕',
        'Announcement': '📢',
        'default': '📌'
    }

    def __init__(self, db: Session):
        """
        Initialize batch analyzer

        Args:
            db: SQLAlchemy session
        """
        self.db = db

    async def generate_digest(
        self,
        parent: Parent,
        date_range_days: int = 7
    ) -> str:
        """
        Generate personalized weekly digest for parent

        Pattern: Adapted from chai/batch_analyzer.py:213-280

        Args:
            parent: Parent record
            date_range_days: Number of days to include (default 7)

        Returns:
            Formatted digest text for WhatsApp
        """
        # Get children and their grades/activities
        children = parent.children

        if not children:
            return self._format_no_children_message(parent)

        # Build filter criteria
        grade_list = [child.grade for child in children]
        activity_list = [sub.activity for sub in parent.subscriptions]

        # Query relevant items
        items = self._query_relevant_items(
            grade_list=grade_list,
            activity_list=activity_list,
            date_range_days=date_range_days
        )

        if not items:
            return self._format_no_items_message(parent, date_range_days)

        # Group items by type
        grouped_items = self._group_items_by_type(items)

        # Format digest
        digest = self._format_digest(
            parent=parent,
            grouped_items=grouped_items,
            date_range_days=date_range_days
        )

        # Translate if needed
        if parent.language != 'en':
            digest = await self._translate_digest(digest, parent.language)

        return digest

    def _query_relevant_items(
        self,
        grade_list: List[int],
        activity_list: List[str],
        date_range_days: int
    ) -> List[Item]:
        """
        Query items matching parent's children/subscriptions

        Pattern: Adapted from chai/batch_analyzer.py:234-239

        Args:
            grade_list: List of child grades
            activity_list: List of subscribed activities
            date_range_days: Date range in days

        Returns:
            List of matching items
        """
        # Calculate date range
        now = datetime.utcnow()
        cutoff_date = now - timedelta(days=date_range_days)

        # Build audience tag filters
        audience_filters = []

        # Grade tags (e.g., 'grade_5')
        for grade in grade_list:
            audience_filters.append(f'grade_{grade}')

        # Activity tags
        audience_filters.extend(activity_list)

        # Add 'all' tag (applies to everyone)
        audience_filters.append('all')

        # Query items
        # Note: PostgreSQL array overlap operator
        # audience_tags && ARRAY['grade_5', 'Basketball', 'all']
        items = self.db.query(Item).filter(
            and_(
                Item.status == 'approved',
                Item.created_at >= cutoff_date,
                or_(*[
                    Item.audience_tags.contains([tag])
                    for tag in audience_filters
                ])
            )
        ).order_by(Item.date.asc()).all()

        return items

    def _group_items_by_type(
        self,
        items: List[Item]
    ) -> Dict[str, List[Item]]:
        """
        Group items by type for digest formatting

        Pattern: Adapted from chai/batch_analyzer.py:460-507

        Args:
            items: List of items

        Returns:
            Dictionary mapping type -> items
        """
        grouped = {}

        for item in items:
            item_type = item.type

            if item_type not in grouped:
                grouped[item_type] = []

            grouped[item_type].append(item)

        return grouped

    def _format_digest(
        self,
        parent: Parent,
        grouped_items: Dict[str, List[Item]],
        date_range_days: int
    ) -> str:
        """
        Format digest with emojis for WhatsApp

        Pattern: Adapted from chai/batch_analyzer.py:355-458

        Args:
            parent: Parent record
            grouped_items: Items grouped by type
            date_range_days: Date range in days

        Returns:
            Formatted digest text
        """
        lines = []

        # Header
        lines.append(f"📬 *Weekly Digest*")
        lines.append(f"_{datetime.now().strftime('%B %d, %Y')}_")
        lines.append("")

        # Greeting
        child_names = [child.name or f"Grade {child.grade}" for child in parent.children]
        if len(child_names) == 1:
            greeting = f"Updates for {child_names[0]}:"
        else:
            greeting = f"Updates for {', '.join(child_names)}:"

        lines.append(greeting)
        lines.append("")

        # Items by type
        type_order = ['Event', 'PermissionSlip', 'Fundraiser', 'HotLunch', 'Announcement']

        for item_type in type_order:
            if item_type not in grouped_items:
                continue

            items = grouped_items[item_type]
            emoji = self.TYPE_EMOJIS.get(item_type, self.TYPE_EMOJIS['default'])

            lines.append(f"*{emoji} {item_type}s ({len(items)})*")
            lines.append("")

            for item in items:
                lines.append(self._format_item(item))
                lines.append("")

        # Footer
        lines.append("---")
        lines.append(f"📊 Total: {sum(len(items) for items in grouped_items.values())} items")

        return "\n".join(lines)

    def _format_item(self, item: Item) -> str:
        """
        Format single item for digest

        Args:
            item: Item to format

        Returns:
            Formatted item text
        """
        parts = []

        # Title
        parts.append(f"• *{item.title}*")

        # Date/Time
        if item.date:
            date_str = item.date.strftime('%b %d')
            if item.time:
                time_str = item.time.strftime('%I:%M %p')
                parts.append(f"  📆 {date_str} at {time_str}")
            else:
                parts.append(f"  📆 {date_str}")

        # Location
        if item.location:
            parts.append(f"  📍 {item.location}")

        # Cost
        if item.cost:
            parts.append(f"  💵 ${item.cost:.2f}")

        # Deadline
        if item.deadline:
            deadline_str = item.deadline.strftime('%b %d')
            parts.append(f"  ⏰ Due: {deadline_str}")

        # Description (truncated)
        if item.description:
            desc = item.description[:100]
            if len(item.description) > 100:
                desc += "..."
            parts.append(f"  {desc}")

        # Action link
        if item.action_link:
            parts.append(f"  🔗 {item.action_link}")

        return "\n".join(parts)

    def _format_no_children_message(self, parent: Parent) -> str:
        """
        Format message when parent has no children registered

        Args:
            parent: Parent record

        Returns:
            Formatted message
        """
        return (
            "👋 Welcome to ParentPath!\n\n"
            "It looks like you haven't added any children yet. "
            "Reply with your child's grade to get started.\n\n"
            "Example: 'Grade 5'"
        )

    def _format_no_items_message(
        self,
        parent: Parent,
        date_range_days: int
    ) -> str:
        """
        Format message when no items match parent's criteria

        Args:
            parent: Parent record
            date_range_days: Date range used

        Returns:
            Formatted message
        """
        return (
            f"📭 *No New Updates*\n\n"
            f"No items in the past {date_range_days} days matching your "
            f"children's grades or activities.\n\n"
            f"Check back soon!"
        )

    async def _translate_digest(
        self,
        digest: str,
        target_language: str
    ) -> str:
        """
        Translate digest to parent's language

        Pattern: Placeholder for future Gemini integration

        Args:
            digest: English digest text
            target_language: ISO 639-1 language code

        Returns:
            Translated digest (or original if translation unavailable)
        """
        # TODO: Integrate with gemini_service.py for translation
        # For now, return original
        return digest

    async def generate_batch_digests(
        self,
        parent_ids: Optional[List[str]] = None,
        date_range_days: int = 7
    ) -> Dict[str, str]:
        """
        Generate digests for multiple parents (batch processing)

        Pattern: Adapted from chai/batch_analyzer.py:162-211

        Args:
            parent_ids: Optional list of parent IDs (None = all active)
            date_range_days: Date range in days

        Returns:
            Dictionary mapping parent_id -> digest_text
        """
        # Query parents
        query = self.db.query(Parent).filter(Parent.status == 'active')

        if parent_ids:
            query = query.filter(Parent.id.in_(parent_ids))

        parents = query.all()

        # Generate digests
        digests = {}

        for parent in parents:
            try:
                digest = await self.generate_digest(parent, date_range_days)
                digests[str(parent.id)] = digest
            except Exception as e:
                # Log error, continue with other parents
                print(f"Error generating digest for parent {parent.id}: {e}")
                digests[str(parent.id)] = self._format_error_message()

        return digests

    def _format_error_message(self) -> str:
        """
        Format error message when digest generation fails

        Returns:
            Error message text
        """
        return (
            "⚠️ *Digest Unavailable*\n\n"
            "We encountered an error generating your digest. "
            "Please contact support if this persists."
        )
