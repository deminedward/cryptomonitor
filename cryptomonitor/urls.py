"""cryptomonitor URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin

from coins import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),

    # url(r'^api/influxdb_test/$', views.influxdb_test, name='influxdb_test'),
    # url(r'^api/utc_test/$', views.utc_test, name='utc_test'),
    # url(r'^api/query_test/$', views.query_test, name='query_test'),

    # url(r'^api/histo_m/$', views.histo_m, name='histo_m'),

    # url(r'^api/fetcher_hourly/$', views.fetcher_hourly, name='fetcher_hourly'),
    # url(r'^api/write_csv/$', views.write_csv, name='write_csv'),
    # url(r'^api/fetch_online/(?P<sec>[0-9]+)/$', views.fetch_online, name='fetch_online'),
    # url(r'^api/fetch_coinmarketcap/$', views.fetch_coinmarketcap, name='fetch_coinmarketcap'),

    # url(r'^api/compare/$', views.compare, name='compare'),

    # url(r'^api/telegram/$', views.telegram, name='telegram'),

    # url(r'^api/fetch_n_save/$', views.fetch_n_save, name='fetch_n_save'),
    url(r'^api/initial_curr/(?P<initial_rank>[0-9]+)/$', views.initial_curr, name='initial_curr'),

    url(r'^api/test_separately/$', views.test_separately, name='test_separately'),
]
