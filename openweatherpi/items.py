# -*- coding: utf-8 -*-
# openweatherpi
# Sammy Fung <sammy@sammy.hk>
from scrapy_djangoitem import DjangoItem
from weatherdata.models import TropicalCyclone

class TropicalCycloneItem(DjangoItem):
  django_model = TropicalCyclone