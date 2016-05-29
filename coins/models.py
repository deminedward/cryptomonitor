# -*- coding: utf-8 -*-
from django.db import models


class Curr(models.Model):
    name = models.CharField(max_length=100)
    symbol = models.CharField(max_length=10, unique=True)
    source_rate = models.IntegerField(null=True, blank=True)
    my_rate = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.name


def date_formatted(obj):
    return "%s %s" % (obj.strftime("%d/%m/%Y"),
                         obj.strftime("%H:%M:%S"))


#data fro the currency as at (timestamp)
class Asat(models.Model):

    curr = models.ForeignKey(Curr)
    date = models.DateTimeField(null=True, blank=True)
    ts = models.IntegerField() #time
    open = models.FloatField()
    high = models.FloatField()
    low = models.FloatField()
    close = models.FloatField()
    volumefrom = models.FloatField()
    volumeto = models.FloatField()
    when = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return date_formatted(self.date)

    def get_dict(self):
        d = {}
        # d['id'] = self.pk
        # d['curr'] = self.curr.symbol
        d['date'] = date_formatted(self.date)
        d['ts'] = str(self.ts)
        d['open'] = str(self.open)
        d['high'] = str(self.high)
        d['low'] = str(self.low)
        d['close'] = str(self.close)
        d['volumefrom'] = str(self.volumefrom)
        d['volumeto'] = str(self.volumeto)
        return d


class Point(models.Model):
    curr = models.ForeignKey(Curr)
    date = models.DateTimeField(null=True, blank=True)
    ts = models.IntegerField() #timestamp
    price_usd = models.FloatField()
    volume24_usd = models.FloatField()

    def __str__(self):
        return date_formatted(self.date)


class Parameters(models.Model):
    price_period = models.IntegerField()
    price_percentage = models.FloatField()
    turnover24_period = models.IntegerField()
    turnover24_percentage = models.FloatField()
    curr = models.OneToOneField(Curr, null=True, blank=True)
    # TODO only one can be without curr - default. add a check to the save method

    def __str__(self):
        return str(self.price_period)
        # TODO if curr - return symbol, if not - 'current'

