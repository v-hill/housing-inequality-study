from django.db import models


class Location(models.Model):
    latitude = models.DecimalField(max_digits=7, decimal_places=5)
    longitude = models.DecimalField(max_digits=7, decimal_places=5)


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

        unique_together = ("osm_id",)

    @property
    def url(self):
        url = f"https://www.openstreetmap.org/relation/{self.osm_id}"
        return url


class Station(models.Model):
    boundary = models.ForeignKey(MapBoundary, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    name = models.CharField(max_length=128)
    osm_id = models.IntegerField()

    def __str__(self) -> str:
        return self.name

    class Meta:
        """Metadata options."""

        unique_together = ("osm_id", "boundary")
