from django.db import models


# Create your models here.


class StockProfile(models.Model):
    symbol = models.CharField(max_length=20, primary_key=True, help_text='stock symbol / ticker')
    company_name = models.CharField(max_length=200, blank=True, help_text='company name')
    exchange = models.CharField(max_length=20, blank=True, help_text='exchange name')
    country = models.CharField(max_length=200, blank=True)
    address1 = models.CharField(max_length=200, blank=True)
    address2 = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=200, blank=True)
    state = models.CharField(max_length=200, blank=True)
    zipcode = models.CharField(max_length=200, blank=True)
    weburl = models.URLField(blank=True, help_text='company website URL')
    ipo_date = models.DateField(blank=True, help_text='date of IPO')
    business_desc = models.TextField(max_length=2000, blank=True, help_text='business description')
    sector = models.CharField(max_length=200, blank=True)
    industry = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ['symbol', 'exchange', 'sector', 'industry']

    def __str__(self):
        return self.exchange + ':' + self.symbol + ' (' + self.company_name + ')'


class StockUniverse(models.Model):
    name = models.CharField(max_length=20, primary_key=True, help_text='short name of stock universe')
    desc = models.TextField(max_length=2000, blank=True, help_text='detailed description')

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class StockData(models.Model):
    symbol = models.CharField(max_length=20, primary_key=True, help_text='stock symbol / ticker')
    histdata_market = models.FileField(upload_to='histdata_market/', null=True)
    histdata_fund = models.FileField(upload_to='histdata_fundamental/', null=True)
    recent_date = models.DateField(blank=True, help_text='recent market date')
    recent_price = models.FloatField(blank=True, null=True, default=0.0, help_text="recent close price")
    recent_mktcap = models.FloatField(blank=True, null=True, default=0.0, help_text="recent market capitalization")
    recent_return_1d = models.FloatField(blank=True, null=True, default=0.0, help_text="recent 1-day return")
    recent_return_1w = models.FloatField(blank=True, null=True, default=0.0, help_text="recent 1-week return")
    recent_return_1m = models.FloatField(blank=True, null=True, default=0.0, help_text="recent 1-month return")
    recent_return_1y = models.FloatField(blank=True, null=True, default=0.0, help_text="recent 1-year return")
    pred_short = models.FloatField(blank=True, null=True, default=0.0, help_text="short-term prediction")
    pred_medium = models.FloatField(blank=True, null=True, default=0.0, help_text="medium-term prediction")
    pred_long = models.FloatField(blank=True, null=True, default=0.0, help_text="long-term prediction")
    pred_short_star = models.IntegerField(choices=[(i, i) for i in list(range(-5, 0)) + list(range(1, 6))],
                                          blank=True, null=True, help_text="stars of short-term prediction [-5, 5]")
    pred_medium_star = models.IntegerField(choices=[(i, i) for i in list(range(-5, 0)) + list(range(1, 6))],
                                           blank=True, null=True, help_text="stars of medium-term prediction [-5, 5]")
    pred_long_star = models.IntegerField(choices=[(i, i) for i in list(range(-5, 0)) + list(range(1, 6))],
                                         blank=True, null=True, help_text="stars of long-term prediction [-5, 5]")
    profile = models.ForeignKey('StockProfile', on_delete=models.SET_NULL, null=True)
    universe = models.ManyToManyField('StockUniverse', verbose_name='stock universe', blank=True,
                                      through='TreemapCoordinate')

    class Meta:
        ordering = ['symbol', 'recent_mktcap', 'recent_return_1d']

    def __str__(self):
        return str(self.symbol) + ' [' + str(round(self.recent_price, 2)) + ']'
