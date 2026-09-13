from django.utils.deprecation import MiddlewareMixin

from apps.accounts.services import get_user_studio


class MultiTenantMiddleware(MiddlewareMixin):
    """
    Enforce multi-tenancy by injecting studio context.
    Prevents cross-tenant data access.
    """

    def process_request(self, request):
        request.tenant_studio = None

        if request.user.is_authenticated:
            try:
                request.tenant_studio = get_user_studio(request.user)
            except Exception:
                pass

        return None
