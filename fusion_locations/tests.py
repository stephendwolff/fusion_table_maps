import random

import requests
from django.core import urlresolvers

from django.test import TestCase

from .fusion_tables import add_fusion_table_row
from .models import GoogleFusionTable, GoogleMapLocation
from .utils import get_google_api_key


class FusionLocationsTestCase(TestCase):

    def setUp(self):
        self.fusion_table = GoogleFusionTable.objects.get_fusion_table()
        self.google_api_key = get_google_api_key()

    def get_table_rows(self):
        """
        var table_get_url = 'https://www.googleapis.com/fusiontables/v2/query?sql=SELECT%20Location,%20Address%20from%20' +
            google_fusion_table_id + '&key=' + google_api_key + '&cacheBust=' + (Math.random() * 99999999).toString();

        $.get(table_get_url, function( data ){

            var table_html = "<table class='table'><thead><th>Location</th><th>Address</th></thead>";
            $.each(data["rows"], function( index, value) {
                table_html += "<tr><td>" + value[0] + "</td><td>" + value[1] + "</td></tr>";
            });
            table_html += "</table>";
            $("#map-table").html(table_html);
        });
        """
        google_fusion_table = GoogleFusionTable.objects.get_fusion_table()
        table_get_url = 'https://www.googleapis.com/fusiontables/v2/query?sql=SELECT Location, Address from ' \
                        '%s&key=%s&cacheBust=%s' % (
                            google_fusion_table.table_id,
                            self.google_api_key,
                            (random.random() * 99999999))

        r = requests.get(table_get_url, headers={'referer': "http://localhost:8000/"})
        r_object = r.json()
        rows = []
        object_rows = r_object.get('rows', None)
        if object_rows:
            rows += r_object.get('rows', None)
        return rows

    def test_single_table_in_use(self):
        """
        For each database, there will only be one fusion table entry

        in theory that means one will be created each time the test suite is run,
        but lets check there is only one
        """
        google_fusion_table = GoogleFusionTable.objects.get_fusion_table()
        self.assertEqual(self.fusion_table.table_id, google_fusion_table.table_id)

    def test_add_row_to_fusion_table(self):
        start_fusion_table_rows = self.get_table_rows()
        start_rows = len(start_fusion_table_rows)
        # make location google map location object
        google_map_location = GoogleMapLocation(
            lat=90.0,
            lng=0.0,
            address="Somewhere near the north pole"
        )
        add_fusion_table_row(google_map_location)
        fusion_table_rows = self.get_table_rows()
        end_rows = len(fusion_table_rows)
        self.assertEqual(start_rows + 1, end_rows)

    def test_creating_google_location_adds_fusion_row(self):
        start_fusion_table_rows = self.get_table_rows()
        start_rows = len(start_fusion_table_rows)
        # creating a location adds a row to the fusion table on 'save'
        GoogleMapLocation.objects.create(
            lat=90.0,
            lng=0.0,
            address="Somewhere near the north pole"
        )

        fusion_table_rows = self.get_table_rows()
        end_rows = len(fusion_table_rows)
        self.assertEqual(start_rows + 1, end_rows)

    def test_clear_fusion_table_view(self):

        GoogleMapLocation.objects.create(
            lat=90.0,
            lng=0.0,
            address="Somewhere near the north pole"
        )
        GoogleMapLocation.objects.create(
            lat=90.0,
            lng=0.0,
            address="Somewhere near the north pole"
        )
        start_fusion_table_rows = self.get_table_rows()
        start_rows = len(start_fusion_table_rows)
        self.assertGreater(start_rows, 0)

        self.client.get(urlresolvers.reverse('clear-fusion-table'))
        fusion_table_rows = self.get_table_rows()
        end_rows = len(fusion_table_rows)
        self.assertEqual(end_rows, 0)

