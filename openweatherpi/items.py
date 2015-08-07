# -*- coding: utf-8 -*-
# openweatherpi
# Sammy Fung <sammy@sammy.hk>
import scrapy

class TropicalCycloneItem(scrapy.Item):
  position_time = scrapy.Field()
  agency = scrapy.Field()
  report_time = scrapy.Field()
  code = scrapy.Field()
  name = scrapy.Field()
  position_type = scrapy.Field()
  cyclone_type = scrapy.Field()
  latitude = scrapy.Field() #N
  longitude = scrapy.Field() #E
  pressure = scrapy.Field()
  wind_speed = scrapy.Field()
  wind_unit = scrapy.Field()

