# -*- coding: utf-8 -*-
import datetime
import urllib
import urllib.request
from urllib.error import URLError, HTTPError
import json
import time
import csv
import telepot


from django.http import HttpResponse
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist

from coins.models import *


def get_model_fields(model):
    print(model._meta.fields)
    return model._meta.fields


def write_csv(request):

    for c in Curr.objects.all().order_by('source_rate'):
        print(c)
        curr = c
        queryset = Asat.objects.filter(curr=curr).order_by('-date')
        # opts = queryset.model._meta
        # model = queryset.model
        # field_names = [field.name for field in opts.fields]
        filename = c.symbol + '_file.csv'
        with open(filename, 'w') as csvfile:
            fieldnames = ['date','ts','open','high','low','close','volumefrom','volumeto']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for obj in queryset:
                # print([getattr(obj, field) for field in field_names])
                writer.writerow(obj.get_dict())

    return HttpResponse('try')



from cryptomonitor.information import TelegramBotKey, TelegramChannel

def telegram_bot(message):
    bot = telepot.Bot(TelegramBotKey)
    bot.sendMessage(TelegramChannel, message)


def my_scheduled_job():
    bot = telepot.Bot(TelegramBotKey)
    bot.sendMessage(TelegramChannel, 'People equal shit test')


def fetch_coinmarketcap():
    url = 'https://api.coinmarketcap.com/v1/ticker/'
    try:
        response = urllib.request.urlopen(url)
        responce_read = response.read().decode('utf-8')
        responce_loaded = json.loads(responce_read)
        response_dict = {item['symbol']: item for item in responce_loaded} #to iterate by Curr, not by response list
        return response_dict
    except HTTPError as e:
        telegram_bot('HTTPError: fetch_coinmarketcap. Error code: ' + str(e.code))
        return {}
    except URLError as e:
        telegram_bot('URLError: fetch_coinmarketcap. Reason: ' + str(e.reason))
        return {}


def check_equations(last_date):
    for curr in Curr.objects.all():
        # print(curr, ' CURRENCY')
        if Point.objects.filter(curr=curr).count() > 5:
            try:
                parameters = Parameters.objects.get(curr=curr)
            except ObjectDoesNotExist:
                parameters = Parameters.objects.filter(isdefault=True).first()
            # print(parameters, parameters.price_period)
            price_period = parameters.price_period
            price_percentage = parameters.price_percentage
            turnover24_period = parameters.turnover24_period
            turnover24_percentage = parameters.turnover24_percentage
            try:
                last_point = Point.objects.get(date=last_date, curr=curr)
            except:
                last_point = Point.objects.filter(curr=curr).order_by('-date').first()
            # PRICE CHECK:
            desired_price_past_date = last_date - datetime.timedelta(0, price_period)
            # print('desired_price_past_date : ', desired_price_past_date)
            # print(Point.objects.filter(curr=curr).filter(date__gt=desired_price_past_date).order_by("date").first())
            closest_price = \
            Point.objects.filter(curr=curr, date__lt=desired_price_past_date).order_by("-date").first()
            if not closest_price:
                closest_price = \
                Point.objects.filter(curr=curr, date__gt=desired_price_past_date).order_by("date").first()
            actual_price_period = last_date - closest_price.date
            correction_price = actual_price_period.seconds / price_period #поправка на разницу между желаемым периодом и реальным
            #print('correction_price:  ', correction_price)
            price_change = (last_point.price_usd - closest_price.price_usd) / closest_price.price_usd
            #print('last_point.price_usd: ', last_point.price_usd, ', closest_price.price_usd: ', closest_price.price_usd)
            #print('price change persentage before correction:  ', price_change)
            #print('for the period:  ', actual_price_period)
            if abs(price_change) > (price_percentage / correction_price):
                #print('price_change ', price_change, '> ', (price_percentage/correction_price), ' (/)')
                reason = 'Price ALARM: curr-' + curr.symbol +\
                    ', price_change: '+ str(round(price_change*100, 2)) + '% for ' + str(actual_price_period.seconds) + 'sec'
                telegram_bot(reason)

            # TURNOVER24 CHECK:
            desired_turnover_past_date = last_date - datetime.timedelta(0, turnover24_period)
            closest_turnover = \
            Point.objects.filter(curr=curr, date__lt=desired_turnover_past_date).order_by("-date").first()
            if not closest_turnover:
                closest_turnover = \
                Point.objects.filter(curr=curr, date__gt=desired_turnover_past_date).order_by("date").first()

            actual_turnover_period = last_date - closest_turnover.date
            correction_turnover = actual_turnover_period.seconds / turnover24_period #поправка на разницу между желаемым периодом и реальным
            turnover_change = (last_point.volume24_usd - closest_turnover.volume24_usd) / closest_turnover.volume24_usd
            #print('turnover_change: ', turnover_change, ' = ', last_point.volume24_usd, '-', closest_turnover.volume24_usd, ' /...')
            if abs(turnover_change) > (turnover24_percentage / correction_turnover):
                reason = 'Turnover ALARM: ' + 'Turnover ALARM: curr-' + curr.symbol + \
                ', turnover_change: ' + str(round(turnover_change*100, 2)) + '%, for ' + str(actual_turnover_period.seconds) + 'sec'
                #print(reason)
                telegram_bot(reason)
        else:
            reason = 'No information for : ' + curr.symbol
            #telegram_bot(reason)

    return ('')


def check_other(response_dict):
    try:
        entry_params = EntryParametrs.objects.all().first()
        try:
            percent_change_1h = entry_params.percent_change_1h
        except:
            percent_change_1h = None
        try:
            percent_change_24h = entry_params.percent_change_24h
        except:
            percent_change_24h = None
        try:
            percent_change_7d = entry_params.percent_change_7d
        except:
            percent_change_7d = None

        for i in response_dict:
            if not Curr.objects.get(symbol=i):
                reason = None
                if percent_change_1h and i['percent_change_1h'] > percent_change_1h:
                    reason = 'Currency ' + i + ' has been added - percent_change_1h: ' + str(i['percent_change_1h'])
                elif percent_change_24h and i['percent_change_24h'] > percent_change_24h:
                    reason = 'Currency ' + i + ' has been - percent_change_24h:' + str(i['percent_change_24h'])
                elif percent_change_7d and i['percent_change_7d'] > percent_change_7d:
                    reason = 'Currency ' + i + ' has been - percent_change_7d:' + str(i['percent_change_7d'])
                if reason:
                    new = Curr(symbol=i['symbol'])
                    new.name = i['name']
                    new.source_rate = i['rank']
                    new.save()
                    telegram_bot(reason)
    except:
        pass

    return ('')


def fetch_n_save():
    point_time = datetime.datetime.utcnow()
    response_dict = fetch_coinmarketcap()
    if response_dict: #if it void - error message has already sent
        for curr in Curr.objects.all().order_by('source_rate'): #[:3]: TODO change to all
            try:
                point = Point(curr=curr, date=point_time)
                point.price_usd = float(response_dict[curr.symbol]['price_usd'])
                point.volume24_usd = float(response_dict[curr.symbol]['24h_volume_usd'])
                point.save()
            except:
                # print('error with fetching currency: ', curr.symbol)
                telegram_bot('error with fetching currency: ' + curr.symbol)#TODO send to telegram

        check_equations(point_time)
        check_other(response_dict)

    else:
        pass

    # return HttpResponse('nothing')


def initial_curr(request, initial_rank):
    response_dict = fetch_coinmarketcap()
    added = []
    for i in response_dict:

        if int(response_dict[i]['rank']) <= int(initial_rank):
            try:
                curr = Curr.objects.get(symbol=i)
            except ObjectDoesNotExist:
                new = Curr(symbol=response_dict[i]['symbol'])
                new.name = response_dict[i]['name']
                new.source_rate = int(response_dict[i]['rank'])
                new.save()
                added.append(new.symbol)
    return HttpResponse(added)


def test_separately(request):
    fetch_n_save()
    return HttpResponse('test_separately')