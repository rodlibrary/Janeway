from django.template.loader import render_to_string

from plugins.downloads_by_country.logic import user_can_view


def nav_hook(context):
    """Adds a 'Downloads by Country' link to the back-office menu."""
    request = context.get("request")
    if not request or not user_can_view(request):
        return ""
    return render_to_string("downloads_by_country/elements/nav.html", request=request)
