"""Get data from OpenStreetMap about railway station locations."""

import pandas as pd

from publictransit.overpass_api import OverpassClient

from . import models


class GetStationData:
    """Python wrapper for the OpenStreetMap Overpass API."""

    def __init__(self):
        self.client = OverpassClient()

    def _generate_query(self, map_region: str):
        query = (
            '[out:csv(::id, ::lat, ::lon, name; true; "|")][timeout:25];'
            + map_region
            + 'node(area.region)["railway"="station"]'
            + '["wikipedia"]["usage"!~"tourism"];'
            + "out body;"
        )
        return query

    def _csv_response_to_df(self, data: list[tuple[str]]) -> pd.DataFrame:
        """Convert a CSV response to a Pandas DataFrame.

        Parameters
        ----------
        data : list[tuple[str]]
            Convert a CSV response to a Pandas DataFrame.

        Returns
        -------
        pd.DataFrame
            A Pandas DataFrame with the columns 'osm_id', 'latitude',
            'longitude', and 'name'.
        """
        df = pd.DataFrame([d[0].split("|") for d in data])
        df.columns = ["osm_id", "latitude", "longitude", "name"]
        df = df.drop(df.index[0])
        df[["osm_id", "latitude", "longitude"]] = df[
            ["osm_id", "latitude", "longitude"]
        ].apply(pd.to_numeric)
        df["name"] = df["name"].str.replace('"', "")
        df = df.reset_index(drop=True)
        return df

    def get_railway_station_data(self, map_region: str):
        """Get railway station names and locations for a given map region.

        Parameters
        ----------
        map_region : str
            Region string, for example the City of London:
                'area["ref:gss"="E09000001"][admin_level=6]->.region;'
            For more details see: https://www.openstreetmap.org/relation/51800

        Returns
        -------
        pd.DataFrame
            A Pandas DataFrame with the columns 'osm_id', 'latitude',
            'longitude', and 'name'.
        """
        query = self._generate_query(map_region)
        response = self.client.get(query)
        df = self._csv_response_to_df(response)
        return df

    def get_and_save_railway_station_data(self, map_region: str):
        df = self.get_railway_station_data(map_region)
        for index, row in df.iterrows():
            if models.Station.objects.filter(osm_id=row["osm_id"]).exists():
                continue
            station = models.Station(
                osm_id=row["osm_id"],
                name=row["name"],
                latitude=row["latitude"],
                longitude=row["longitude"],
            )
            station.save()
            print(index, station)
