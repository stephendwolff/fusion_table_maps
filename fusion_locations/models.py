from __future__ import unicode_literals

from django.db import models

from .managers import GoogleFusionTableManager


class GoogleMapLocation(models.Model):
    """
    Model for storing lat, lng and address of a point on a Google Map, which has been clicked on,
    only if the Google Map geocoder returns an address with a type of street_address
    """
    lat = models.CharField(max_length=30)
    lng = models.CharField(max_length=30)
    address = models.CharField(max_length=255, unique=True)

    def save(self, *args, **kwargs):
        """ Override save to add map location to fusion tables, only on new location"""
        from .fusion_tables import add_fusion_table_row

        if not self.pk:
            add_fusion_table_row(self)

        super(GoogleMapLocation, self).save(*args, **kwargs)


class GoogleFusionTable(models.Model):
    """
    Store the table id once created, for reuse
    """
    table_id = models.CharField(max_length=255)

    # only ever need a single table for this test, so use a custom manager for access
    objects = GoogleFusionTableManager()
