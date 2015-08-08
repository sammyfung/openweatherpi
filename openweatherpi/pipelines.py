# -*- coding: utf-8 -*-
# openweatherpi - Scrapy Item Pipelines to Django web framework
# Sammy Fung <sammy@sammy.hk>

from scrapy.exceptions import DropItem
from weatherdata.models import TropicalCyclone

class OpenweatherpiPipeline(object):
    def process_item(self, item, spider):
        if spider.name == 'cwb_tc' or spider.name == 'cwb_tc_hourly' or spider.name == 'jtwc':
            if not TropicalCyclone.objects.filter(report_time = item['report_time'], agency=item['agency'],
                                                  position_time = item['position_time'], code=item['code'],
                                                  position_type = item['position_type']):
                item.save()
            else:
                raise DropItem("Duplicated %s data from %s report"%(item['agency'],item['report_time']))
        return item
