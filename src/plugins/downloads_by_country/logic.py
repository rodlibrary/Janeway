"""Data and map logic for the Downloads by Country page."""

import csv
import json
import math
import os
from functools import lru_cache

from django.db.models import Count
from django.http import HttpResponse

from metrics import models as metrics_models
from submission import models as submission_models

MAP_FILE = os.path.join(os.path.dirname(__file__), "data", "world_map.json")

# Sequential purple ramp (light = fewer, dark = more), ending at UNI Panther
# Purple. OKLab lightness steps evenly: 0.87, 0.74, 0.60, 0.46, 0.34.
RAMP = ["#ddcdea", "#bd99da", "#9466c2", "#6c36a0", "#500778"]
NO_DATA_COLOUR = "#ebebeb"

MEASURES = {
    "download": ("Downloads", "downloads"),
    "view": ("Views", "views"),
}


def user_can_view(request):
    """Staff, editors and journal managers of the current journal."""
    user = getattr(request, "user", None)
    if not user or not user.is_authenticated:
        return False
    if user.is_staff:
        return True
    journal = getattr(request, "journal", None)
    return bool(
        journal and (user.is_editor(request) or user.is_journal_manager(journal))
    )


def access_events(journal, start_date, end_date, measure, article=None):
    """ArticleAccess rows for published articles, filtered by the page's controls."""
    events = metrics_models.ArticleAccess.objects.filter(
        article__stage=submission_models.STAGE_PUBLISHED,
        accessed__date__gte=start_date,
        accessed__date__lte=end_date,
        type=measure,
    )
    if journal:
        events = events.filter(article__journal=journal)
    if article:
        events = events.filter(article=article)
    return events


def counts_by_country(events):
    """
    Returns (rows, unknown, total).

    rows: one dict per country with code, name, count and share (percent),
    largest first. unknown: events with no country (local or unrecognised
    addresses, or recorded before country lookups existed).
    """
    grouped = (
        events.values("country__code", "country__name")
        .annotate(count=Count("id"))
        .order_by("-count", "country__name")
    )
    rows, unknown = [], 0
    for row in grouped:
        if row["country__code"]:
            rows.append(
                {
                    "code": row["country__code"],
                    "name": row["country__name"],
                    "count": row["count"],
                }
            )
        else:
            unknown += row["count"]
    total = sum(r["count"] for r in rows) + unknown
    for position, row in enumerate(rows, start=1):
        row["rank"] = position
        row["share"] = round(100 * row["count"] / total, 1) if total else 0
    return rows, unknown, total


def _nice(value):
    """Round up to 1, 2 or 5 x 10^n so legend breaks read cleanly."""
    if value <= 1:
        return 1
    exponent = math.floor(math.log10(value))
    for step in (1, 2, 5, 10):
        candidate = step * 10**exponent
        if candidate >= value:
            return int(candidate)
    return int(10 ** (exponent + 1))


def build_scale(max_count):
    """
    Splits 1..max_count into up to five bins. Breaks are log-spaced because
    download counts are usually dominated by one or two countries; a linear
    scale would leave every other country in the lightest shade.

    Returns a list of {"low", "high", "colour", "label"} from lightest to darkest.
    """
    if max_count <= 0:
        return []
    if max_count <= len(RAMP):
        uppers = list(range(1, max_count + 1))
    else:
        uppers = []
        steps = len(RAMP)
        for k in range(1, steps):
            edge = _nice(max_count ** (k / steps))
            if edge < max_count and (not uppers or edge > uppers[-1]):
                uppers.append(edge)
        uppers.append(max_count)
    # Spread fewer bins across the whole ramp, always ending at the darkest.
    n = len(uppers)
    last = len(RAMP) - 1
    colours = (
        [RAMP[last]] if n == 1 else [RAMP[round(i * last / (n - 1))] for i in range(n)]
    )
    bins, low = [], 1
    for high, colour in zip(uppers, colours):
        label = f"{low:,}" if low == high else f"{low:,}–{high:,}"
        bins.append({"low": low, "high": high, "colour": colour, "label": label})
        low = high + 1
    return bins


def colour_for(count, scale):
    if not count:
        return NO_DATA_COLOUR
    for band in scale:
        if count <= band["high"]:
            return band["colour"]
    return scale[-1]["colour"]


@lru_cache(maxsize=1)
def load_map():
    with open(MAP_FILE, encoding="utf-8") as handle:
        return json.load(handle)


def map_context(rows, measure_noun):
    """Country shapes and dots with fill colours and hover text."""
    world = load_map()
    counts = {row["code"]: row for row in rows}
    scale = build_scale(max((r["count"] for r in rows), default=0))

    def decorate(item):
        row = counts.get(item["code"])
        count = row["count"] if row else 0
        name = row["name"] if row else item["name"]
        noun = measure_noun if count != 1 else measure_noun.rstrip("s")
        return {
            **item,
            "name": name,
            "count": count,
            "colour": colour_for(count, scale),
            "label": f"{name}: {count:,} {noun}",
        }

    return {
        "width": world["width"],
        "height": world["height"],
        "shapes": [decorate(s) for s in world["shapes"]],
        "dots": [decorate(d) for d in world["dots"]],
        "scale": scale,
        "no_data_colour": NO_DATA_COLOUR,
    }


def export_csv(rows, unknown, total, measure_label, filename):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    writer = csv.writer(response)
    writer.writerow(["Rank", "Country", "ISO code", measure_label, "Share (%)"])
    for row in rows:
        writer.writerow(
            [row["rank"], row["name"], row["code"], row["count"], row["share"]]
        )
    if unknown:
        writer.writerow(
            ["", "Unknown location", "", unknown, round(100 * unknown / total, 1)]
        )
    writer.writerow(["", "Total", "", total, 100 if total else 0])
    return response
