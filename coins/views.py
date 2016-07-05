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


def check_onhold(curr, alarm_type, parameters, point_time):
    last_alarm = AlarmLog.objects.filter(curr=curr, alarm_type=alarm_type).last()
    if last_alarm:
        if (point_time - last_alarm.date).seconds > parameters.alarm_hold_period:
            is_active = True
        else:
            is_active = False
    else:
        is_active = True

    return (is_active)


def check_equations(last_date):
    for curr in Curr.objects.all():
        # print(curr, ' CURRENCY')
        if Point.objects.filter(curr=curr).count() > 5:
            try:
                parameters = Parameters.objects.get(curr=curr)
            except ObjectDoesNotExist:
                parameters = Parameters.objects.filter(isdefault=True).first()

            price_period = parameters.price_period
            price_percentage = parameters.price_percentage
            turnover24_period = parameters.turnover24_period
            turnover24_percentage = parameters.turnover24_percentage
            try:
                last_point = Point.objects.get(date=last_date, curr=curr)
            except:
                last_point = Point.objects.filter(curr=curr).order_by('-date').first()
            # PRICE CHECK:
            if check_onhold(curr=curr, alarm_type=1, parameters=parameters, point_time=last_date):
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
                price_change = (last_point.price_usd - closest_price.price_usd) / closest_price.price_usd
                if abs(price_change) > (price_percentage / correction_price):
                    reason = 'Price ALARM: curr-' + curr.symbol +\
                        ', price_change: ' + str(round(price_change*100, 2)) + '% for ' + str(actual_price_period.seconds) + 'sec'
                    telegram_bot(reason)
                    alarm_log = AlarmLog(date=last_date, curr=curr, alarm_type=1)
                    alarm_log.save()

            # TURNOVER24 CHECK:
            if check_onhold(curr=curr, alarm_type=2, parameters=parameters, point_time=last_date):
                desired_turnover_past_date = last_date - datetime.timedelta(0, turnover24_period)
                closest_turnover = \
                Point.objects.filter(curr=curr, date__lt=desired_turnover_past_date).order_by("-date").first()
                if not closest_turnover:
                    closest_turnover = \
                    Point.objects.filter(curr=curr, date__gt=desired_turnover_past_date).order_by("date").first()

                actual_turnover_period = last_date - closest_turnover.date
                correction_turnover = actual_turnover_period.seconds / turnover24_period #поправка на разницу между желаемым периодом и реальным
                turnover_change = (last_point.volume24_usd - closest_turnover.volume24_usd) / closest_turnover.volume24_usd
                if abs(turnover_change) > (turnover24_percentage / correction_turnover):
                    reason = 'Turnover ALARM: ' + 'Turnover ALARM: curr-' + curr.symbol + \
                    ', turnover_change: ' + str(round(turnover_change*100, 2)) + '%, for ' + str(actual_turnover_period.seconds) + 'sec'
                    telegram_bot(reason)
                    alarm_log = AlarmLog(date=last_date, curr=curr, alarm_type=2)
                    alarm_log.save()
        else:
            pass
            #reason = 'No information for : ' + curr.symbol
            #telegram_bot(reason)

    return ('')


def check_other(response_dict):
    try:
        entry_params = EntryParametrs.objects.all().first()
        for i in response_dict:
            i_data = response_dict[i]
            if not Curr.objects.filter(symbol=i):
                reason = None

                if i_data['24h_volume_usd'] and i_data['24h_volume_usd'] != 'None':
                    turnover24 = float(i_data['24h_volume_usd'])
                else:
                    turnover24 = 0.0
                if i_data['percent_change_1h'] and i_data['percent_change_1h'] != 'None':
                    percent_change_1h = float(i_data['percent_change_1h'])
                else:
                    percent_change_1h = 0.0
                if i_data['percent_change_24h'] and i_data['percent_change_24h'] != 'None':
                    percent_change_24h = float(i_data['percent_change_24h'])
                else:
                    percent_change_24h = 0.0
                if i_data['percent_change_7d'] and i_data['percent_change_7d'] != 'None':
                    percent_change_7d = float(i_data['percent_change_7d'])
                else:
                    percent_change_7d = 0

                if turnover24 >= entry_params.turnover_to_add:
                    reason = 'Currency ' + i + ' has been added - 24h_volume_usd:' + str(turnover24)
                    # print(i, 'IF111--24h_volume_usd >turnover_to_add', i_data['24h_volume_usd'])
                elif turnover24 >= entry_params.turnover_materiality:
                    # print(i, 'IF222--24h_volume_usd >turnover_materiality', i_data['24h_volume_usd'])
                    if entry_params.percent_change_1h and percent_change_1h >= entry_params.percent_change_1h:
                        reason = 'Currency ' + i + ' has been added - percent_change_1h: ' + str(percent_change_1h)
                    elif entry_params.percent_change_24h and percent_change_24h >= entry_params.percent_change_24h:
                        reason = 'Currency ' + i + ' has been added - percent_change_24h: ' + str(percent_change_24h)
                    elif entry_params.percent_change_7d and percent_change_7d >= entry_params.percent_change_7d:
                        reason = 'Currency ' + i + ' has been added - percent_change_7d: ' + str(percent_change_7d)
                    else:
                        pass

                else:
                    pass

                if reason:
                    new = Curr(symbol=i_data['symbol'])
                    new.name = i_data['name']
                    new.source_rate = i_data['rank']
                    new.save()
                    telegram_bot(reason)
                else:
                    pass
            else:
                pass

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