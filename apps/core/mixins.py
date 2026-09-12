from django.db.models import Q


class SearchMixin:
    """Add search functionality to list views."""
    search_fields = []
    search_param = "q"

    def get_search_query(self):
        return self.request.GET.get(self.search_param, "").strip()

    def apply_search(self, queryset):
        query = self.get_search_query()
        if not query or not self.search_fields:
            return queryset

        q = Q()
        for field in self.search_fields:
            q |= Q(**{f"{field}__icontains": query})
        return queryset.filter(q)


class DateFilterMixin:
    """Add date range filtering to list views."""
    date_field = "created_at"
    date_from_param = "date_from"
    date_to_param = "date_to"

    def apply_date_filter(self, queryset):
        from datetime import date

        date_from = self.request.GET.get(self.date_from_param)
        date_to = self.request.GET.get(self.date_to_param)

        if date_from:
            try:
                date_from = date.fromisoformat(date_from)
                queryset = queryset.filter(**{f"{self.date_field}__gte": date_from})
            except (ValueError, TypeError):
                pass

        if date_to:
            try:
                date_to = date.fromisoformat(date_to)
                queryset = queryset.filter(**{f"{self.date_field}__lte": date_to})
            except (ValueError, TypeError):
                pass

        return queryset
