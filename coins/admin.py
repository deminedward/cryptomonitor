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


class AsatAdmin(admin.ModelAdmin):
    list_display = ('curr', date_formatted, 'open', 'close', 'volumefrom', 'volumeto')
    list_filter = ('curr',)


class PointAdmin(admin.ModelAdmin):
    pass


class ParametersAdmin(admin.ModelAdmin):
    pass


admin.site.register(Curr, CurrAdmin)
admin.site.register(Asat, AsatAdmin)
admin.site.register(Point, PointAdmin)
admin.site.register(Parameters, ParametersAdmin)
