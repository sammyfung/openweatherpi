# -*- coding: utf-8 -*-
# openweatherpi - JMA Tropical Cyclone Web Scraper
# Sammy Fung <sammy@sammy.hk>
import scrapy, re
from openweatherpi.items import TropicalCycloneItem
from datetime import datetime, timedelta

class JmaTcSpider(scrapy.Spider):
    name = "jma_tc"
    allowed_domains = ["jma.go.jp"]
    start_urls = (
        'http://www.jma.go.jp/en/typh/',
    )
    agency = u'JMA'
    ktstokmh = 1.852
    wind_unit = u'KMH'

    def parse(self, response):
        items = []
        tc_list = response.xpath('//div[@class="infotable"]/div[@class="typhoonInfo"]')
        for tc in tc_list:
            item = TropicalCycloneItem()
            code = u"%sW"%tc.xpath('@id').extract()[0][2:]
            report_time = re.sub('.*at ', '', tc.xpath('text()').extract()[1])
            report_time = re.sub(' UTC', '', report_time)
            if re.search(u'\, \d ', report_time):
                report_time = "%s0%s"%(report_time[:7], report_time[7:])
            report_time = datetime.strptime(report_time, '%H:%M, %d %B %Y')+timedelta(hours=8)
            if re.search("^(TD|TS|TY|STY)", re.split(' ', tc.xpath("text()").extract()[0])[0]):
                cyclone_type = re.split(' ', tc.xpath("text()").extract()[0])[0]
            else:
                cyclone_type = u''
            if re.search("([A-Z]*)", tc.xpath("text()").extract()[0]):
                tc_name = u"%s"%re.sub('.*\(', '', re.sub('\).*', '', tc.xpath("text()").extract()[0]))
            else:
                tc_name = u''
            for i in tc.xpath('div/table/tr'):
                if re.search(u'(Analysis at|Forecast for)', i.xpath('td').extract()[0]):
                    item['agency'] = self.agency
                    item['wind_unit'] = self.wind_unit
                    item['report_time'] = report_time.isoformat()
                    item['code'] = code
                    item['cyclone_type'] = cyclone_type
                    item['name'] = tc_name
                    if re.search(u'Analysis at', i.xpath('td').extract()[0]):
                        item['position_type'] = u'C'
                    else:
                        item['position_type'] = u'F'
                    pos_time = re.sub('\<(Analysis at|Forecast for) ', '', i.xpath('td/text()').extract()[0])
                    pos_time = re.split(' ', re.sub(' UTC,', '', pos_time))
                    next_month = 0
                    if int(pos_time[1]) < report_time.day:
                        next_month = 1
                    if report_time.month < 10:
                        pos_time = u"%s 0%s %s %s"%(report_time.year, report_time.month+next_month, pos_time[1],
                                                    pos_time[0])
                    else:
                        pos_time = u"%s %s %s %s"%(report_time.year, report_time.month+next_month, pos_time[1],
                                                   pos_time[0])
                    item['position_time'] = datetime.strptime(pos_time, '%Y %m %d %H')+timedelta(hours=8)
                    item['position_time'] = item['position_time'].isoformat()
                if len(i.xpath('td')) > 1:
                    if re.search('^Center position.*$', i.xpath('td/text()').extract()[0]):
                        item['latitude'] = i.xpath('td/text()').extract()[1]
                        item['latitude'] = round(float(re.sub(u'.*\(', '', re.sub(u'°\).*', '',
                                                                                  item['latitude']))), 2)
                    if re.search('<td></td>', i.xpath('td').extract()[0]):
                        if re.search('E\d.*', i.xpath('td/text()').extract()[0]):
                            item['longitude'] = i.xpath('td/text()').extract()[0]
                            item['longitude'] = round(float(re.sub(u'.*\(', '', re.sub(u'°\).*', '',
                                                                                       item['longitude']))), 2)
                if re.search(u'Central pressure', i.xpath('td').extract()[0]):
                    item['pressure'] = int(re.sub('hPa.*', '', i.xpath('td/text()').extract()[1]))
                if re.search(u'(Maximum wind speed near the center|Maximum wind gust speed)', i.xpath('td').extract()[0]):
                    speed = i.xpath('td/text()').extract()[1]
                    speed = int(round(int(re.sub('kt.*', '', re.sub('.*\(', '', speed)))*self.ktstokmh, 0))
                    if re.search(u'Maximum wind speed near the center', i.xpath('td').extract()[0]):
                        item['wind_speed'] = speed
                        if speed < 61:
                            item['cyclone_type'] = u'TD'
                        elif speed < 118:
                            item['cyclone_type'] = u'TS'
                        elif speed < 194:
                            item['cyclone_type'] = u'TY'
                        else:
                            item['cyclone_type'] = u'STY'
                    else:
                        item['gust_speed'] = speed
                        items.append(item)
                        item = TropicalCycloneItem()
            if 'position_type' in item:
                if item['position_type'] == u'C':
                    items.append(item)
        return items


