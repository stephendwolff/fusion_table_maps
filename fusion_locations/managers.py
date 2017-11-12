from django.db import models

from .fusion_tables import create_fusion_table


class GoogleFusionTableManager(models.Manager):

    def get_fusion_table(self):
        """ Only ever create one table for this test application """
        try:
            fusion_table = self.all()[0]
        except IndexError:
            fusion_table = create_fusion_table()

        return fusion_table
