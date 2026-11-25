from datetime import timedelta
from unittest import mock

from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied
from django.test import RequestFactory, TestCase
from django.utils import timezone

from core import models as core_models
from metrics import models as metrics_models
from plugins.downloads_by_country import logic, views
from submission import models as submission_models
from utils.testing import helpers


class ScaleTests(TestCase):
    def test_empty_scale(self):
        self.assertEqual(logic.build_scale(0), [])

    def test_small_counts_get_one_bin_each_ending_darkest(self):
        scale = logic.build_scale(3)
        self.assertEqual([b["high"] for b in scale], [1, 2, 3])
        self.assertEqual(scale[-1]["colour"], logic.RAMP[-1])
        self.assertEqual(scale[0]["colour"], logic.RAMP[0])

    def test_large_counts_are_log_spaced_and_cover_range(self):
        scale = logic.build_scale(1234)
        self.assertEqual(len(scale), 5)
        self.assertEqual(scale[0]["low"], 1)
        self.assertEqual(scale[-1]["high"], 1234)
        highs = [b["high"] for b in scale]
        self.assertEqual(highs, sorted(set(highs)))
        for previous, current in zip(scale, scale[1:]):
            self.assertEqual(current["low"], previous["high"] + 1)

    def test_colour_for(self):
        scale = logic.build_scale(100)
        self.assertEqual(logic.colour_for(0, scale), logic.NO_DATA_COLOUR)
        self.assertEqual(logic.colour_for(1, scale), logic.RAMP[0])
        self.assertEqual(logic.colour_for(100, scale), logic.RAMP[-1])

    def test_map_data_loads(self):
        world = logic.load_map()
        codes = {shape["code"] for shape in world["shapes"]}
        self.assertIn("US", codes)
        self.assertNotIn("AQ", codes)
        self.assertIn("SG", {dot["code"] for dot in world["dots"]})


class CountsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.press = helpers.create_press()
        cls.journal, cls.other_journal = helpers.create_journals()
        cls.article = helpers.create_article(
            cls.journal, stage=submission_models.STAGE_PUBLISHED
        )
        cls.unpublished = helpers.create_article(
            cls.journal, stage=submission_models.STAGE_UNASSIGNED
        )
        cls.other = helpers.create_article(
            cls.other_journal, stage=submission_models.STAGE_PUBLISHED
        )
        cls.us, _ = core_models.Country.objects.get_or_create(
            code="US", defaults={"name": "United States"}
        )
        cls.gb, _ = core_models.Country.objects.get_or_create(
            code="GB", defaults={"name": "United Kingdom"}
        )
        now = timezone.now()

        def access(article, country, kind="download", when=now):
            metrics_models.ArticleAccess.objects.create(
                article=article,
                type=kind,
                identifier="x",
                country=country,
                accessed=when,
            )

        for _ in range(3):
            access(cls.article, cls.us)
        access(cls.article, cls.gb)
        access(cls.article, None)
        access(cls.article, cls.us, kind="view")
        access(cls.article, cls.us, when=now - timedelta(days=500))
        access(cls.unpublished, cls.us)
        access(cls.other, cls.gb)
        cls.today = now.date()
        cls.start = cls.today - timedelta(days=30)

    def test_counts_downloads_for_journal(self):
        events = logic.access_events(self.journal, self.start, self.today, "download")
        rows, unknown, total = logic.counts_by_country(events)
        self.assertEqual(
            [(r["code"], r["count"], r["rank"]) for r in rows],
            [("US", 3, 1), ("GB", 1, 2)],
        )
        self.assertEqual(unknown, 1)
        self.assertEqual(total, 5)
        self.assertEqual(rows[0]["share"], 60.0)

    def test_views_are_counted_separately(self):
        events = logic.access_events(self.journal, self.start, self.today, "view")
        _rows, _unknown, total = logic.counts_by_country(events)
        self.assertEqual(total, 1)

    def test_article_filter_and_press_level(self):
        events = logic.access_events(None, self.start, self.today, "download")
        _rows, _unknown, total = logic.counts_by_country(events)
        self.assertEqual(total, 6)  # both journals, published only, in range
        events = logic.access_events(
            None, self.start, self.today, "download", article=self.other
        )
        self.assertEqual(logic.counts_by_country(events)[2], 1)

    def test_csv_export(self):
        events = logic.access_events(self.journal, self.start, self.today, "download")
        rows, unknown, total = logic.counts_by_country(events)
        response = logic.export_csv(rows, unknown, total, "Downloads", "x.csv")
        lines = response.content.decode().strip().splitlines()
        self.assertEqual(lines[0], "Rank,Country,ISO code,Downloads,Share (%)")
        self.assertEqual(lines[1], "1,United States,US,3,60.0")
        self.assertEqual(lines[-1], ",Total,,5,100")


class ViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.press = helpers.create_press()
        cls.journal, cls.other_journal = helpers.create_journals()
        cls.editor = helpers.create_editor(cls.journal)
        cls.author = helpers.create_author(cls.journal)
        cls.staff = helpers.create_user("staff@example.org", is_staff=True)
        cls.factory = RequestFactory()

    def _request(self, user, journal, params=None):
        request = self.factory.get("/plugins/downloads-by-country/", params or {})
        request.user = user
        request.journal = journal
        request.press = self.press
        request.repository = None
        return request

    def test_permissions(self):
        self.assertTrue(logic.user_can_view(self._request(self.editor, self.journal)))
        self.assertTrue(logic.user_can_view(self._request(self.staff, None)))
        self.assertFalse(logic.user_can_view(self._request(self.author, self.journal)))
        self.assertFalse(logic.user_can_view(self._request(self.editor, None)))
        self.assertFalse(
            logic.user_can_view(self._request(AnonymousUser(), self.journal))
        )

    def test_author_is_denied(self):
        request = self._request(self.author, self.journal)
        with self.assertRaises(PermissionDenied):
            views.index.__wrapped__(request)

    @mock.patch("plugins.downloads_by_country.views.render")
    def test_editor_sees_page_with_defaults(self, render):
        render.return_value = "ok"
        views.index.__wrapped__(self._request(self.editor, self.journal))
        context = render.call_args[0][2]
        self.assertEqual(context["measure_label"], "Downloads")
        self.assertEqual(context["total"], 0)
        self.assertEqual(context["journal"], self.journal)
        self.assertIn("export=csv", context["export_query"])

    def test_csv_export_view(self):
        response = views.index.__wrapped__(
            self._request(
                self.editor,
                self.journal,
                {
                    "start_date": "2026-01-01",
                    "end_date": "2026-11-25",
                    "measure": "view",
                    "export": "csv",
                },
            )
        )
        self.assertEqual(response["Content-Type"], "text/csv")
        self.assertIn(
            'filename="views-by-country-tst-2026-01-01-2026-11-25.csv"',
            response["Content-Disposition"],
        )
