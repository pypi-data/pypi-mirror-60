from django.db import models

from .stock import StockData, StockProfile, StockUniverse


class TreemapCoordinate(models.Model):
    data = models.ForeignKey(StockData, on_delete=models.CASCADE)
    profile = models.ForeignKey(StockProfile, on_delete=models.CASCADE)
    universe = models.ForeignKey(StockUniverse, on_delete=models.CASCADE)
    x0 = models.PositiveIntegerField(default=0, help_text="up-left x")
    y0 = models.PositiveIntegerField(default=0, help_text="up-left y")
    x1 = models.PositiveIntegerField(default=0, help_text="bottom-right x")
    y1 = models.PositiveIntegerField(default=0, help_text="bottom-right y")

    class Meta:
        ordering = ['universe', 'data']

    def __str__(self):
        return self.universe.name + ':' + self.data.symbol + '[(' + format(self.x0) + ',' + \
               format(self.y1) + '); (' + format(self.x1) + ',' + format(self.y1) + ')]'
