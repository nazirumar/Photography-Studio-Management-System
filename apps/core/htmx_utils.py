from django.http import HttpResponse
from django.template.loader import render_to_string


def htmx_response(request, template, context=None, partial=None):
    """Return HTMX partial or full page response."""
    if request.headers.get("HX-Request"):
        if partial:
            template = f"partials/{partial}.html"
        html = render_to_string(template, context or {}, request=request)
        return HttpResponse(html)
    from django.shortcuts import render
    return render(request, template, context or {})


def htmx_redirect(url):
    """Return HTMX redirect response."""
    response = HttpResponse()
    response["HX-Redirect"] = url
    return response


def htmx_trigger(event, url=None):
    """Return HTMX trigger response."""
    import json
    response = HttpResponse()
    response["HX-Trigger"] = json.dumps({event: True})
    if url:
        response["HX-Redirect"] = url
    return response


def htmx_swap_oob(template, context, target_id):
    """Return OOB swap for updating multiple elements."""
    html = render_to_string(template, context)
    return f'<div id="{target_id}" hx-swap-oob="true">{html}</div>'
