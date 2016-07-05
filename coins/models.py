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


class Point(models.Model):
    curr = models.ForeignKey(Curr)
    date = models.DateTimeField(null=True, blank=True)
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
    alarm_hold_period = models.IntegerField()
    isdefault = models.BooleanField(default=False)
    # TODO only one can be without curr - default. add a check to the save method

    def __str__(self):
        try:
            string = self.curr.symbol
        except:
            string = 'default'
        return string


class EntryParametrs(models.Model):
    percent_change_1h = models.FloatField(null=True, blank=True)
    percent_change_24h = models.FloatField(null=True, blank=True)
    percent_change_7d = models.FloatField(null=True, blank=True)
    turnover_materiality = models.FloatField()
    turnover_to_add = models.FloatField()


class AlarmLog(models.Model):
    date = models.DateTimeField(null=True, blank=True)
    curr = models.ForeignKey(Curr)
    ALARM_TYPE = (
        ('1', u'Price'),
        ('2', u'Turnover'),
    )
    alarm_type = models.IntegerField(choices=ALARM_TYPE)

    def __str__(self):
        return "%s %s" % (self.curr.symbol,
                          self.alarm_type)