# -*- coding: utf-8 -*-
from django.contrib import admin
from coins.models import *


class CurrAdmin(admin.ModelAdmin):
    list_display = ('name', 'symbol', 'source_rate', 'pk',)


def date_formatted(obj):
    return "%s %s" % (obj.date.strftime("%d/%m/%Y"),
                         obj.date.strftime("%H:%M"))

date_formatted.short_description = u'Когда'
date_formatted.admin_order_field = 'date'  # to sort by start_date, using that column




class PointAdmin(admin.ModelAdmin):
    list_display = ('curr', 'date', 'price_usd', 'volume24_usd')
    list_filter = ('curr',)
    pass


class ParametersAdmin(admin.ModelAdmin):
    pass


class EntryParametrsAdmin(admin.ModelAdmin):
    pass



admin.site.register(Curr, CurrAdmin)
admin.site.register(Point, PointAdmin)
admin.site.register(Parameters, ParametersAdmin)
admin.site.register(EntryParametrs, EntryParametrsAdmin)