import pandas as pd
from django.http import JsonResponse
from django.test import Client, TestCase
from django.urls import reverse

from publictransit.overpass_api import OverpassClient
from publictransit.station_data import GetStationData


class MainViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("publictransit:main")

    def test_main_view(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "main.html")


class SearchViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_search_view_ajax_request(self):
        url = reverse("publictransit:search")
        data = {"lat": "51.50129", "lng": "-0.14182"}

        response = self.client.get(
            url, data, HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response, JsonResponse)

        response_data = response.json()
        self.assertIn("lat", response_data)
        self.assertIn("lng", response_data)
        self.assertEqual(response_data["lat"], 51.50129)
        self.assertEqual(response_data["lng"], -0.14182)

    def test_search_view_invalid_input(self):
        url = reverse("publictransit:search")
        data = {"lat": "invalid", "lng": "-0.14182"}

        response = self.client.get(
            url, data, HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )
        self.assertEqual(response.status_code, 400)
        self.assertIsInstance(response, JsonResponse)

        response_data = response.json()
        self.assertIn("error", response_data)
        self.assertEqual(
            response_data["error"], "Invalid latitude or longitude value."
        )


class TestMyOverpassClient(TestCase):
    def setUp(self):
        self.client: OverpassClient = OverpassClient()

    def test_get_json_response(self):
        query = """[out:json][timeout:25];
                    way(374945234);
                    out body;
                    >;
                    out skel qt;"""
        response = self.client.get(query)
        self.assertIsNotNone(response)
        self.assertEqual(
            response["elements"][0]["tags"]["name"], "Victoria Memorial"
        )

    def test_get_csv_response(self):
        query = """[out:csv(name)][timeout:25];
                    way(374945234);
                    out;"""
        response = self.client.get(query)
        self.assertIsNotNone(response)
        self.assertEqual(response[1][0], "Victoria Memorial")

    def test_get_xml_response(self):
        query = """[out:xml][timeout:25];
                    way(374945234);
                    out;"""
        response = self.client.get(query)
        self.assertIsNotNone(response)
        self.assertIn("Victoria Memorial", response)


class TestGetStationData(TestCase):
    def setUp(self):
        self.get_station_data = GetStationData()
        # City of London (17 stations in total)
        # see: https://www.openstreetmap.org/relation/51800
        self.map_region = (
            'area["ref:gss"="E09000001"][admin_level=6]->.region;'
        )
        self.expected_df = pd.DataFrame(
            [
                {
                    "osm_id": 18395696,
                    "latitude": 51.5118924,
                    "longitude": -0.0952228,
                    "name": "Mansion House",
                },
                {
                    "osm_id": 1637578440,
                    "latitude": 51.5131048,
                    "longitude": -0.0893749,
                    "name": "Bank",
                },
            ]
        )

    def test_generate_query(self):
        self.assertIsInstance(
            self.get_station_data._generate_query(self.map_region), str
        )

    def test_get_railway_station_data(self):
        actual_df = self.get_station_data.get_railway_station_data(
            self.map_region
        )
        actual_df = actual_df.iloc[:2]
        pd.testing.assert_frame_equal(self.expected_df, actual_df)

    def test_csv_response_to_df(self):
        input_list = [
            ["@id|@lat|@lon|name"],
            ["18395696|51.5118924|-0.0952228|Mansion House"],
            ["1637578440|51.5131048|-0.0893749|Bank"],
        ]
        actual_df = self.get_station_data._csv_response_to_df(input_list)
        pd.testing.assert_frame_equal(self.expected_df, actual_df)
