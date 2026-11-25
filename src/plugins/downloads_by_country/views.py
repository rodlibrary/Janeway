from django.core.exceptions import PermissionDenied
from django.http import QueryDict
from django.shortcuts import render
from django.utils.text import slugify

from plugins.downloads_by_country import forms, logic
from security.decorators import base_check_required


@base_check_required
def index(request):
    """
    Downloads (or views) of published articles by country, as a shaded
    world map and a table, with a CSV export.

    Inside a journal: editors and journal managers of that journal.
    At press level: staff, across all journals or one chosen journal.
    """
    if not logic.user_can_view(request):
        raise PermissionDenied

    start, end = forms.default_dates()
    defaults = {"start_date": start, "end_date": end, "measure": "download"}
    data = request.GET if "start_date" in request.GET else defaults
    form = forms.FilterForm(data, journal=request.journal)

    if form.is_valid():
        filters = form.cleaned_data
    else:
        filters = {**defaults, "journal": None, "article": None}

    journal = request.journal or filters.get("journal")
    article = filters.get("article")
    measure = filters["measure"]
    measure_label, measure_noun = logic.MEASURES[measure]

    events = logic.access_events(
        journal, filters["start_date"], filters["end_date"], measure, article=article
    )
    rows, unknown, total = logic.counts_by_country(events)

    if request.GET.get("export") == "csv":
        scope = article.pk if article else (journal.code if journal else "press")
        filename = "{}-by-country-{}-{}-{}.csv".format(
            measure_noun,
            slugify(str(scope)),
            filters["start_date"].isoformat(),
            filters["end_date"].isoformat(),
        )
        return logic.export_csv(rows, unknown, total, measure_label, filename)

    if "start_date" in request.GET:
        export_query = request.GET.copy()
    else:
        export_query = QueryDict(mutable=True)
        export_query.update({k: str(v) for k, v in defaults.items()})
    export_query["export"] = "csv"

    context = {
        "form": form,
        "journal": journal,
        "article": article,
        "start_date": filters["start_date"],
        "end_date": filters["end_date"],
        "measure_label": measure_label,
        "measure_noun": measure_noun,
        "rows": rows,
        "unknown": unknown,
        "unknown_share": round(100 * unknown / total, 1) if total else 0,
        "total": total,
        "top": rows[0] if rows else None,
        "map": logic.map_context(rows, measure_noun),
        "export_query": export_query.urlencode(),
    }
    return render(request, "downloads_by_country/index.html", context)
