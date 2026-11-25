from datetime import date

from dateutil.relativedelta import relativedelta
from django import forms

from journal import models as journal_models
from plugins.downloads_by_country.logic import MEASURES
from submission import models as submission_models


class DateInput(forms.DateInput):
    input_type = "date"


def default_dates():
    """The last 12 months, ending today."""
    today = date.today()
    return today - relativedelta(years=1) + relativedelta(days=1), today


class FilterForm(forms.Form):
    start_date = forms.DateField(label="From", widget=DateInput)
    end_date = forms.DateField(label="To", widget=DateInput)
    measure = forms.ChoiceField(
        label="Show",
        choices=[(key, label) for key, (label, _noun) in MEASURES.items()],
        initial="download",
    )
    journal = forms.ModelChoiceField(
        label="Journal",
        queryset=journal_models.Journal.objects.none(),
        required=False,
        empty_label="All journals",
    )
    article = forms.ModelChoiceField(
        label="Article",
        queryset=submission_models.Article.objects.none(),
        required=False,
        empty_label="All articles",
    )

    def __init__(self, *args, journal=None, **kwargs):
        super().__init__(*args, **kwargs)
        if journal:
            # Inside a journal: no journal picker, articles from this journal.
            del self.fields["journal"]
            self.fields["article"].queryset = submission_models.Article.objects.filter(
                journal=journal,
                stage=submission_models.STAGE_PUBLISHED,
            ).order_by("title")
        else:
            # Press level (staff only): pick a journal; filter by article
            # within a journal from the journal's own page.
            del self.fields["article"]
            self.fields[
                "journal"
            ].queryset = journal_models.Journal.objects.all().order_by("code")

    def clean(self):
        cleaned = super().clean()
        start, end = cleaned.get("start_date"), cleaned.get("end_date")
        if start and end and start > end:
            raise forms.ValidationError("The start date must be before the end date.")
        return cleaned
