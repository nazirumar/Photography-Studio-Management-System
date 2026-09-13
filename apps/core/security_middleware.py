import logging
import time
from collections import defaultdict
from django.conf import settings
from django.http import JsonResponse, HttpResponseForbidden
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger("security")

# Simple in-memory rate limiter (production should use Redis)
_rate_limits = defaultdict(list)


class RateLimitMiddleware(MiddlewareMixin):
    """Rate limit API and form submissions."""
    
    def process_request(self, request):
        # Skip rate limiting in testing
        if getattr(settings, "TESTING", False):
            return None
            
        ip = self._get_client_ip(request)
        now = time.time()
        
        # Rate limits: per IP per path prefix
        limits = {
            "/api/": (100, 60),      # 100 requests per minute
            "/accounts/login/": (10, 60),  # 10 login attempts per minute
            "/portal/": (60, 60),    # 60 portal requests per minute
            "/bookings/request/": (5, 60),  # 5 booking requests per minute
        }
        
        for prefix, (max_requests, window) in limits.items():
            if request.path.startswith(prefix):
                key = f"{ip}:{prefix}"
                _rate_limits[key] = [t for t in _rate_limits[key] if t > now - window]
                if len(_rate_limits[key]) >= max_requests:
                    logger.warning(f"Rate limit exceeded: {ip} on {prefix}")
                    if request.path.startswith("/api/"):
                        return JsonResponse({"error": "Rate limit exceeded"}, status=429)
                    return HttpResponseForbidden("Too many requests. Please try again later.")
                _rate_limits[key].append(now)
                break
        
        return None
    
    def _get_client_ip(self, request):
        x_forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded:
            return x_forwarded.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR", "")


class SecurityHeadersMiddleware(MiddlewareMixin):
    """Add security headers to responses."""
    
    def process_response(self, request, response):
        response["X-Content-Type-Options"] = "nosniff"
        response["X-Frame-Options"] = "DENY"
        response["X-XSS-Protection"] = "1; mode=block"
        response["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        if not settings.DEBUG:
            response["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
            response["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.tailwindcss.com https://unpkg.com; style-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com; img-src 'self' data: https:; font-src 'self' https://fonts.gstatic.com;"
        
        return response


class InputSanitizationMiddleware(MiddlewareMixin):
    """Log and sanitize suspicious input patterns."""
    
    SUSPICIOUS_PATTERNS = [
        "<script", "javascript:", "onerror=", "onload=",
        "UNION SELECT", "DROP TABLE", "INSERT INTO",
        "../../", "..\\",
    ]
    
    def process_request(self, request):
        if request.method in ("POST", "PUT", "PATCH"):
            body = request.body.decode("utf-8", errors="ignore")[:5000]
            for pattern in self.SUSPICIOUS_PATTERNS:
                if pattern.lower() in body.lower():
                    logger.warning(
                        f"Suspicious input from {request.META.get('REMOTE_ADDR')}: "
                        f"pattern={pattern} path={request.path}"
                    )
                    break
        return None
