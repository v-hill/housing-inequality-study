import json
from unittest.mock import patch

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase

from publictransit import views
from publictransit.overpass_api import OverpassClient


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


class CheckBoundaryViewTestCase(APITestCase):
    def setUp(self):
        self.url = "/publictransit/check_boundary/"

    # Mock the process_check_boundary_request method to avoid making an
    # actual API call
    @patch.object(views.CheckBoundaryView, "process_check_boundary_request")
    def test_check_boundary_view_get(
        self, mock_process_check_boundary_request
    ):
        test_data = {
            "success": (
                "Found relation: <a"
                " href='https://www.openstreetmap.org/relation/51800'"
                " target='_blank'>City of London</a>"
            ),
            "osm_id": 51800,
        }
        mock_process_check_boundary_request.return_value = test_data

        response = self.client.get(
            self.url, {"area_standard": "ISO 3166-2", "area_value": "GB-LND"}
        )

        # Check if the response status is HTTP 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Deserialize the response content from bytes to a dictionary object
        response_data = json.loads(response.content)

        # Compare the response_data dictionary with the expected test_data
        # dictionary
        self.assertEqual(response_data, test_data)
