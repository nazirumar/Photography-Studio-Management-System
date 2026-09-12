from __future__ import annotations

BRIEFING_PROMPT = """\
Generate a morning briefing for {studio_name} on {date}.

Data summary:
- Active bookings today: {active_bookings}
- Pending invoices: {pending_invoices} (total ₦{pending_amount})
- Overdue invoices: {overdue_invoices} (total ₦{overdue_amount})
- Low stock items: {low_stock_items}
- Equipment needing maintenance: {equipment_maintenance}
- New leads this week: {new_leads}

Provide a concise briefing covering:
1. Today's schedule and priorities
2. Financial highlights (outstanding payments, recent transactions)
3. Inventory or equipment alerts
4. Upcoming deadlines or follow-ups
"""

ALERT_PROMPT = """\
Explain the following alert to the studio staff in plain language.

Alert type: {alert_type}
Entity: {entity_name} ({entity_type})
Details: {alert_details}
Severity: {severity}

Provide:
1. A one-sentence summary of the issue
2. Why it matters for daily operations
3. Suggested action to resolve it
"""

ANALYTICS_PROMPT = """\
Explain the following business analytics for {studio_name}.

Period: {period}
Metric: {metric_name}
Value: {metric_value}
Change vs previous period: {change_percentage}%
Context: {context}

Provide:
1. What this metric means for the business
2. Whether the trend is positive, negative, or neutral
3. Practical recommendations based on the data
"""
