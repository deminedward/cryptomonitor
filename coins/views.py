# -*- coding: utf-8 -*-
import datetime
import pytz
import urllib
import json
import time
import csv

from django.shortcuts import render
from django.http import HttpResponse
from django.utils import timezone

from influxdb import InfluxDBClient

from coins.models import *


def influxdb_test(request):
    # date = datetime.datetime.now()
    x = datetime.datetime.now(tz=pytz.utc)
    #ok timestamp:
    #2015-01-29T21:55:43.702900257Z
    #2016-05-11 06:16:45.545327
    #


    print(x)
    json_body = [
        {
            "measurement": "my_mesurment",
            "tags": {"region":"EMEA",},
            "time": "2016-04-21T19:28:07.580664347Z",
            "fields":
                {
                    "turnover": "value=38000000",
                    "price": "value=100.4",
                },

        }
    ]
    ts = 1483617600
    utc_ts = datetime.datetime.fromtimestamp(ts)
    tz = datetime.datetime.now(tz=pytz.utc)
    conv = datetime.datetime.fromtimestamp(ts)

    json_body2 = [
        {
            "measurement": "currency_state",
            "tags": {
                "currency": "TTT",
                "market": "mid"
            },
            "time": str(utc_ts),
            # "time": "1459198938163208459
            "fields": {
                "value": 460.12
            }
        }
    ]

    client = InfluxDBClient('localhost', 8086, 'root', 'root', 'example')

    # client.create_database('example')

    client.write_points(json_body2)
    result2 = client.query('SHOW MEASUREMENTS;')
    print(result2)
    result = client.query('select value from currency_state;')
    print(result)
    #print("Result: {0}".format(result))

    print(client.query('''select value from currency_state WHERE currency='TTT';'''))

    return HttpResponse('11111')


import pandas
def utc_test(request):
    now = datetime.datetime.now()
    x = datetime.datetime.now(tz=pytz.utc)
    utc_dt = datetime.datetime.utcnow()
    print(utc_dt, utc_dt.isoformat())
    tz = datetime.datetime.now(tz=pytz.utc)
    print(tz)
    ts = 1483617600#1460463185#'1460463185' #'1460463279'
    conv = datetime.datetime.fromtimestamp(ts)
    print('conv ', conv)

    print('pandas - ', pandas.to_datetime(ts))
    return HttpResponse(str(utc_dt)+"| _______ |"+str(tz))


def query_test(request):

    client = InfluxDBClient('localhost', 8086, 'root', 'root', 'example')
    result = client.query('select value from currency_state;')
    print(result)
    print(client.query('''select value from currency_state WHERE currency='TTT';'''))
    print(client.query('''select value from currency_state WHERE TIME ='2016-04-12T12:13:05Z';'''))
    print(client.query('''select value from currency_state WHERE time > now() - 100d;'''))


    return HttpResponse('3333')


def fetch_cryptocompare(e_, fsym, tsym, limit, toTs):
    url = 'https://www.cryptocompare.com/api/data/histohour/?'+ \
        'e=' + e_ + \
        '&fsym=' + fsym + \
        '&tsym=' + tsym + \
        '&limit=' + str(limit) + \
        '&toTs=' + str(toTs)

    response = urllib.request.urlopen(url)
    responce_read = response.read().decode('utf-8')
    responce_loaded = json.loads(responce_read)['Data']

    return (responce_loaded)


def histo_m(request):
    response = urllib.request.urlopen('https://www.cryptocompare.com/api/data/histohour/'
                                      '?e=CCCAGG&'
                                      'fsym=BTC&'
                                      'limit=3&'
                                      'tsym=USD&'
                                      'toTs=1456833600')

    #https://www.cryptocompare.com/api/data/histominute/?e=CCCAGG&fsym=BTC&limit=10&tsym=USD&aggregate=2
    # response2 = + 5 * 60 * 60

    fetch_cryptocompare(e_='CCCAGG', fsym='BTC', tsym='USD', limit=3, toTs='1456833600')



    clist = response.read().decode('utf-8')
    clist = json.loads(clist)['Data']
    for i in clist:
        print(i)

    print(clist)
    return HttpResponse(clist)


def fetcher_hourly(request):
    start_ts = 1463540400
    step_source = 1000
    curr_symb = 'CRAIG'
    iter = 0
    stop_iter = 0
    count_hours = 0
    curr = Curr.objects.get(symbol=curr_symb)

    while (iter < 25) & (stop_iter < 6):
        print('iter before: ', iter, ' stop iter: ', stop_iter, ' hours: ', count_hours, datetime.datetime.now())
        bunch = fetch_cryptocompare(e_='CCCAGG', fsym=curr_symb, tsym='USD', limit=step_source, toTs=start_ts)
        dt = datetime.datetime.fromtimestamp(start_ts)
        start_ts -= (step_source + 1) * 60 * 60
        if bunch:
            for i in bunch:
                if not Asat.objects.filter(ts=i['time'], curr=curr):
                    asat = Asat()
                    asat.curr = curr
                    asat.date = datetime.datetime.fromtimestamp(i['time'])
                    asat.ts = i['time']
                    asat.open = i['open']
                    asat.high = i['high']
                    asat.low = i['low']
                    asat.close = i['close']
                    asat.volumefrom = i['volumefrom']
                    asat.volumeto = i['volumeto']
                    asat.when = timezone.now()
                    asat.save()
                    count_hours += 1

            iter += 1
            time.sleep(5)
        else:
            stop_iter += 1

    return HttpResponse('bunch')



# def export_leads(request):
#     return excel.make_response_from_a_table(Student, 'xlsx')


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


from django.db.models import Func, F

def fetch_online(request, sec):
    price_period = int(sec)
    price_percentage = 0.0006
    print('period: ', price_period, 'percentage: ', price_percentage)

    curr = Curr.objects.filter(symbol='BTC')
    try:
        parameters = Parameters.objects.get(curr=curr)
    except:
        parameters = Parameters.objects.filter(curr__isnull=True)[0]

    print('parameters obj: ', parameters, parameters.curr)

    last_= Asat.objects.filter(curr=curr).order_by('date').last()
    #it will be a date of real-time data
    last_date = last_.date

    real_priceperiod = last_date-datetime.timedelta(0, price_period)
    print(last_date-datetime.timedelta(0, price_period))

    closest_lt = Asat.objects.filter(curr=curr).filter(date__lt=real_priceperiod).order_by("-date")[0]
    print(closest_lt)

    fair_diff = (last_date - closest_lt.date)
    print('fair_diff.seconds  ', fair_diff.seconds)
    coeff = fair_diff.seconds/price_period
    print(coeff)
    change = (last_.high - closest_lt.high)/closest_lt.high

    if change > price_percentage/coeff:
        print('ALARM!  ', 'change ', change, 'dynamic/coeff: ', price_percentage*coeff)

    print(change)

    # closest = Asat.objects.annotate(abs_diff=Func(F('date') - depth, function='ABS')).order_by('abs_diff').first()
    # closest = Asat.objects.filter(date__lt=last_date)#[0]
    # print(closest)

    return HttpResponse('fetch_online')


def fetch_coinmarketcap(request):
    url = 'https://api.coinmarketcap.com/v1/ticker/'
    response = urllib.request.urlopen(url)
    responce_read = response.read().decode('utf-8')
    responce_loaded = json.loads(responce_read)

    for i in responce_loaded:
        if i['rank'] <= 40:
            try:
                i_curr = Curr.objects.get(symbol=i['symbol'])
                if i_curr.source_rate != int(i['rank']):
                    i_curr.source_rate = int(i['rank'])
                    i_curr.save()
                    print('source_rate was changed') #TODO send to user
            except Curr.DoesNotExist:
                # new_curr = Curr(symbol=i['symbol'], name=i['name'], source_rate=i['rank'])
                # new_curr.save()
                print('DoesNotExist')


    return HttpResponse('fetch_Сoinmarketcap')


def compare(request):
    url = 'https://www.cryptocompare.com/api/data/coinlist/'
    response = urllib.request.urlopen(url)
    responce_read = response.read().decode('utf-8')
    responce_loaded = json.loads(responce_read)['Data']
    # print(responce_loaded)
    filename = 'cryptocompare_coinlist.csv'
    # for i in responce_loaded:
    #     print(i, responce_loaded[i])

    with open(filename, 'w') as csvfile:
        fieldnames = ['symbol', 'rate',]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for i in responce_loaded:
            # print([getattr(obj, field) for field in field_names])
            writer.writerow({'symbol': i, 'rate': responce_loaded[i]['SortOrder']})

    return HttpResponse('compare')