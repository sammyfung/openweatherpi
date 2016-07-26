# -*- coding: utf-8 -*-
# openweatherpi - HKO Tropical Cyclone Web Scraper
# Sammy Fung <sammy@sammy.hk>
import scrapy, re
from openweatherpi.items import TropicalCycloneItem
from datetime import datetime

class HkoTcSpider(scrapy.Spider):
    name = "hko_tc"
    allowed_domains = ["weather.gov.hk"]
    start_urls = (
        'http://www.weather.gov.hk/additionalMenu_EN.js',
    )
    agency = u'HKO'
    wind_unit = u'KMH'
    code = ''
    tc_name = ''
    report_time = ''

    def parse(self, response):
        items = []
        a = re.split(' ', str(response.body))
        num = 0
        for i in a:
            if re.search('^href="/wxinfo/currwx/tc_pos_', i):
                self.code = re.sub('.*pos_', '', i)
                self.code = re.sub('\..*', '', self.code)
                self.code = re.sub('"', '', self.code)
                self.tc_name = re.sub('\<.*', '', a[num+3])
                items += [ scrapy.Request(url='http://www.weather.gov.hk/wxinfo/currwx/tc_posc_%s.htm'%self.code,
                                          callback=self.parse_forecast) ]
                items += [ scrapy.Request(url='http://www.weather.gov.hk/wxinfo/currwx/tc_pastposc_%s.htm'%self.code,
                                          callback=self.parse_current) ]
            num += 1
        return items

    def get_items(self, t, pos_type):
        items = []
        for i in t:
            if len(i.xpath('td')):
                item = TropicalCycloneItem()
                row = i.xpath('td/text()').extract()
                item['agency'] = self.agency
                item['code'] = u'%sW'%self.code[2:4]
                item['name'] = self.tc_name
                item['wind_unit'] = self.wind_unit
                item['report_time'] = self.report_time
                item['position_time'] = re.sub(u' [年月日時]', '', row[0])
                item['position_time'] = re.sub(u'\s*$', '', item['position_time'])
                item['position_time'] = re.sub(u'\s\s*', ' ', item['position_time'])
                item['position_time'] = datetime.strptime(item['position_time'], '%Y %m %d %H')
                item['position_time'] = item['position_time'].isoformat()
                item['latitude'] = row[1]
                item['latitude'] = re.sub('^北\s*緯\s*', '', item['latitude'])
                item['latitude'] = round(float(re.sub(' 度$', '', item['latitude'])), 2)
                item['longitude'] = row[2]
                item['longitude'] = re.sub('^東\s*經\s*', '', item['longitude'])
                item['longitude'] = round(float(re.sub(' 度$', '', item['longitude'])), 2)
                item['wind_speed'] = int(re.split(u' ', row[4])[2])
                item['position_type'] = pos_type
                if re.search(u'低壓區', row[3]):
                    item['cyclone_type'] = 'LPA'
                elif re.search(u'熱帶低氣壓', row[3]):
                    item['cyclone_type'] = 'TD'
                elif re.search(u'.*熱帶風暴.*', row[3]):
                    item['cyclone_type'] = 'TS'
                elif re.search(u'超強颱風', row[3]):
                    item['cyclone_type'] = 'STY'
                elif re.search(u'.*颱風', row[3]):
                    item['cyclone_type'] = 'TY'
                items.append(item)
        return items

    def parse_forecast(self, response):
        items = []
        self.report_time = response.xpath('//table/tr/td/table/tr/td/div/span/text()').extract()[0]
        self.report_time = re.sub(u'(.*在香港時間 |年 |月 |日 | 時.*|\r|\n)', '', self.report_time)
        self.report_time = datetime.strptime(self.report_time, '%Y %m %d %H')
        self.report_time = self.report_time.isoformat()
        t = response.xpath('//table/tr/td/table/tr/td/div/span/table/tr')
        items = self.get_items(t, u'F')
        return items

    def parse_current(self, response):
        items = []
        self.report_time = response.xpath('//table/tr/td/table/tr/td/h1/text()').extract()[1]
        self.report_time = re.sub(u'(.*在香港時間 |年 |月 |日 | 時.*|\r|\n)', '', self.report_time)
        self.report_time = datetime.strptime(self.report_time, '%Y %m %d %H')
        self.report_time = self.report_time.isoformat()
        t = response.xpath('//table/tr/td/table/tr/td/div/table/tr')
        items = self.get_items(t, u'C')
        return items

