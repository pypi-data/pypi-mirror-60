from django.test import TestCase
from edc_sites import get_site_id, InvalidSiteError

from ..sites import inte_sites


class SiteTests(TestCase):
    def test_all(self):
        self.assertEqual(get_site_id("reviewer", sites=inte_sites), 1)
        self.assertEqual(get_site_id("kinoni", sites=inte_sites), 100)
        self.assertEqual(get_site_id("bugamba", sites=inte_sites), 110)
        self.assertEqual(get_site_id("bwizibwera", sites=inte_sites), 120)
        self.assertEqual(get_site_id("ruhoko", sites=inte_sites), 140)
        self.assertEqual(get_site_id("kyazanga", sites=inte_sites), 150)
        self.assertEqual(get_site_id("bukulula", sites=inte_sites), 160)
        self.assertEqual(get_site_id("kojja", sites=inte_sites), 170)
        self.assertEqual(get_site_id("mpigi", sites=inte_sites), 180)
        self.assertEqual(get_site_id("namayumba", sites=inte_sites), 190)
        self.assertEqual(get_site_id("buwambo", sites=inte_sites), 200)
        self.assertEqual(get_site_id("kajjansi", sites=inte_sites), 210)
        self.assertEqual(get_site_id("tikalu", sites=inte_sites), 220)
        self.assertEqual(get_site_id("namulonge", sites=inte_sites), 230)
        self.assertEqual(get_site_id("kasanje", sites=inte_sites), 240)
        self.assertEqual(get_site_id("kasangati", sites=inte_sites), 250)

    def test_bad(self):
        self.assertRaises(InvalidSiteError, get_site_id,
                          "erik", sites=inte_sites)
