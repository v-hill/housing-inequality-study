from rest_framework import serializers

from publictransit import models


class MapBoundarySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.MapBoundary
        fields = "__all__"


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Location
        fields = ["latitude", "longitude"]


class StationSerializer(serializers.ModelSerializer):
    # Use the LocationSerializer to return that latitude and longitude values
    location = LocationSerializer()

    class Meta:
        model = models.Station
        fields = [
            "id",
            "boundary",
            "location",
            "name",
            "osm_id",
            "isin_boundary",
        ]


class CheckBoundarySerializer(serializers.Serializer):
    area_standard = serializers.ChoiceField(
        choices=[("Ref GSS", "Ref GSS"), ("ISO 3166-2", "ISO 3166-2")]
    )
    area_value = serializers.CharField()
