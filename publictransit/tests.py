from django.http import JsonResponse
from django.test import Client, TestCase
from django.urls import reverse


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
        self.assertEqual(response_data["error"], "Invalid lat or lng value.")
