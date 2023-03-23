"""Get data from the Overpass API."""

import csv
import json
from io import StringIO

import requests


class OverpassClient:
    """Python wrapper for the OpenStreetMap Overpass API."""

    _timeout = 25  # second
    _endpoint = "https://overpass-api.de/api/interpreter"
    _headers = {"Accept-Charset": "utf-8;q=0.7,*;q=0.7"}
    _text_content_types = [
        "text/xml",
        "application/xml",
        "application/osm3s+xml",
    ]

    def __init__(self, *args, **kwargs):
        self.endpoint = kwargs.get("endpoint", self._endpoint)
        self.headers = kwargs.get("headers", self._headers)
        self.timeout = kwargs.get("timeout", self._timeout)

    def _make_request(self, query: str) -> requests.Response:
        """Send a POST request to the Overpass API with the given query.

        Parameters
        ----------
        query : str
            A string containing the Overpass query to send to the API.

        Returns
        -------
        requests.Response
            A 'requests.Response' object representing the response to the POST
            request. If the request was successful (i.e., the status code is
            less than 400), the response object will contain the data returned
            by the Overpass API. Otherwise, None will be returned.

        Raises
        ------
        requests.exceptions.Timeout
            If a timeout occurs while trying to make the request.
        requests.exceptions.RequestException
            If any other exception occurs while making the request.
        """
        payload = {"data": query}
        try:
            response = requests.post(
                self.endpoint,
                data=payload,
                timeout=self.timeout,
                headers=self.headers,
            )
            # raise error if response is not successful (status code >= 400)
            response.raise_for_status()
            response.encoding = "utf-8"
            return response
        except requests.exceptions.Timeout:
            # Timeout occurred while trying to make the request
            print("Timeout error occurred while making the request.")
            return None
        except requests.exceptions.RequestException as e:
            # Other exceptions occurred
            print("An error occurred while making the request:", e)
            return None

    def get(self, query):
        """Send an Overpass QL query to the API endpoint and return a response.

        Parameters
        ----------
        query : str
            The Overpass QL query to send to the endpoint.

        Returns
        -------
        response : str or list
            The response from the Overpass API.
            If the content type is "text/csv", the response is returned as a
            list of lists (using the csv.reader function). Otherwise, the
            response is returned as a string.

        Notes
        -----
        The '_make_request' method is used to make the request to the Overpass
        API endpoint. If an error occurs while making the request, the method
        returns 'None'.
        """
        # Get the response from Overpass
        response = self._make_request(query)
        if response:
            content_type = response.headers.get("content-type")
            if content_type == "text/csv":
                return list(
                    csv.reader(StringIO(response.text), delimiter="\t")
                )
            elif content_type in self._text_content_types:
                return response.text
            elif content_type == "application/json":
                response = json.loads(response.text)
        return response
