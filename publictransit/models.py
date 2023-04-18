from decimal import Decimal

import pyproj
from django.core.validators import MinValueValidator
from django.db import models


class LocationManager(models.Manager):
    def get_or_create(self, *args, **kwargs):
        # Round the latitude and longitude to 5 digits
        if "latitude" in kwargs:
            kwargs["latitude"] = round(Decimal(kwargs["latitude"]), 5)
        if "longitude" in kwargs:
            kwargs["longitude"] = round(Decimal(kwargs["longitude"]), 5)

        # Call the parent class's get_or_create method
        return super().get_or_create(*args, **kwargs)


class Location(models.Model):
    latitude = models.DecimalField(max_digits=7, decimal_places=5)
    longitude = models.DecimalField(max_digits=7, decimal_places=5)

    objects = LocationManager()

    class Meta:
        """Metadata options."""

        unique_together = ("latitude", "longitude")

    def __str__(self) -> str:
        return f"{self.latitude:0.3f}, {self.longitude:0.3f}"

    def save(self, *args, **kwargs):
        # Round the latitude and longitude to 5 digits
        self.latitude = round(Decimal(self.latitude), 5)
        self.longitude = round(Decimal(self.longitude), 5)

        # Call the parent class's save method
        super().save(*args, **kwargs)


class MapBoundary(models.Model):
    admin_level = models.IntegerField()
    iso31662 = models.CharField(max_length=128)
    name = models.CharField(max_length=128)
    osm_id = models.IntegerField()  # Openstreetmap ID
    ref_gss = models.CharField(max_length=128)

    def __str__(self) -> str:
        return self.name

    class Meta:
        """Metadata options."""

        verbose_name_plural = "MapBoundaries"
        unique_together = ("osm_id",)

    @property
    def url(self):
        url = f"https://www.openstreetmap.org/relation/{self.osm_id}"
        return url

    @property
    def polygon_query(self):
        query = f"""[out:json][timeout:25];
                    relation["ref:gss"="{self.ref_gss}"];
                    out body;
                    >;
                    out skel qt;"""
        return query

    @property
    def stations_list_query(self):
        query = f"""[out:csv(name, ::id, ::lat, ::lon)][timeout:25];
                    area["ref:gss"="{self.ref_gss}"]->.map_region;
                    (node["railway"="station"]
                    ["usage"!="tourism"]["name"](area.map_region););
                    (._;>;);
                    out;"""
        return query

    @property
    def stations_list_query_outside_boundary(self, radius=2000):
        query = f"""[out:csv(name, ::id, ::lat, ::lon)][timeout:25];
                    rel["ref:gss"="{self.ref_gss}"]->.boundary;
                    node(around.boundary:{radius})[railway]["railway"="station"]
                    ["usage"!="tourism"]["name"]->.stations;
                    (.stations;);
                    out;"""
        return query


class Station(models.Model):
    boundary = models.ForeignKey(MapBoundary, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    name = models.CharField(max_length=128)
    osm_id = models.IntegerField()
    isin_boundary = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.name

    class Meta:
        """Metadata options."""

        unique_together = ("osm_id", "boundary")


class BoundaryPoint(models.Model):
    boundary = models.ForeignKey(MapBoundary, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    order = models.IntegerField(validators=[MinValueValidator(0)])

    def __str__(self) -> str:
        return self.name

    class Meta:
        """Metadata options."""

        unique_together = ("boundary", "order")
