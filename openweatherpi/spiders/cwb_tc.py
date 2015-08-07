# -*- coding: utf-8 -*-
# openweatherpi - CWB Tropical Cyclone Web Scraper
# Sammy Fung <sammy@sammy.hk>
import scrapy, re, StringIO, zipfile
from openweatherpi.items import TropicalCycloneItem
from datetime import datetime

class CwbTcSpider(scrapy.Spider):
    name = "cwb_tc"
    allowed_domains = ["cwb.gov.tw"]
    start_urls = (
        'http://opendata.cwb.gov.tw/doLogin',
    )
    agency = u'CWB'
    mps2kmh = 3.6
    wind_unit = u'KMH'

    def parse(self, response):
        s = scrapy.conf.settings
        form_data = { 'userid': s['CWB_USERNAME'], 'password': s['CWB_PASSWORD'] }
        return [scrapy.http.FormRequest.from_response(response, formdata = form_data, callback=self.after_login)]

    def after_login(self, response):
        if 'redirect_times' in response.meta:
            print 'not logon'
        else:
            return scrapy.Request(url='http://opendata.cwb.gov.tw/datadownload?dataid=W-C0034-002', callback=self.parse_kml)

    def parse_kml(self, response):
        tc_items = []
        kmz = StringIO.StringIO()
        kmz.write(response.body)
        kmunzip = zipfile.ZipFile(kmz)
        kml = kmunzip.open('fifows_typhoon.kml')
        lines = kml.read()
        #num = scrapy.Selector(text=lines).xpath('//kml/document/folder/folder').extract()
        report_time = scrapy.Selector(text=lines).xpath('//kml/document/folder/description/text()').extract()[0]
        # ### Current ###
        current = scrapy.Selector(text=lines).xpath('//kml/document/folder/folder/placemark')
        desc = re.sub('[\r\n]','', current.xpath('description/text()').extract()[0])
        code = re.sub(u".*編號第 ",'',desc)
        code = "%sW"%re.sub(' .*','', code)
        name = re.sub(u".*國際命名 ",'',desc)
        name = re.sub(u"\).*",'',name)
        current_location = re.split(',',current.xpath('point/coordinates/text()').extract()[0])
        tc = TropicalCycloneItem()
        tc['agency'] = self.agency
        tc['report_time'] = report_time
        tc['code'] = code
        tc['latitude'] = round(float(current_location[1]), 2)
        tc['longitude'] = round(float(current_location[0]), 2)
        tc['position_time'] = report_time
        tc['name'] = name
        tc['position_type'] = u'C'
        cyclone_type = re.sub(u' .*', '', desc)
        if re.search(u'.*熱帶性低氣壓.*',cyclone_type):
            tc['cyclone_type'] = u"TD"
        elif re.search(u'.*輕度颱風.*',cyclone_type):
            tc['cyclone_type'] = u"TS"
        elif re.search(u'.*中度颱風.*',cyclone_type):
            tc['cyclone_type'] = u"TY"
        elif re.search(u'.*強烈颱風.*',cyclone_type):
            tc['cyclone_type'] = u"STY"
        else:
            tc['cyclone_type'] = u""
        tc['pressure'] = re.sub(u'.*中心氣壓 ', '', desc)
        tc['pressure'] = int(re.sub(u' .*', '', tc['pressure']))
        tc['wind_speed'] = re.sub(u'.*近中心最大風速每秒 ', '', desc)
        tc['wind_speed'] = int(round(int(re.sub(u' .*', '', tc['wind_speed'])) * self.mps2kmh, 0))
        tc['wind_unit'] = self.wind_unit
        tc_items.append(tc)
        # ### Forecasts ###
        for i in scrapy.Selector(text=lines).xpath('//kml/document/folder/folder/folder/placemark'):
            forecast_time = i.xpath(u'name/text()').extract()[0].encode('ascii',"ignore")
            forecast_location = re.split(',',i.xpath('point/coordinates/text()').extract()[0])
            tc = TropicalCycloneItem()
            tc['agency'] = self.agency
            tc['report_time'] = report_time
            tc['code'] = code
            tc['latitude'] = round(float(forecast_location[1]), 2)
            tc['longitude'] = round(float(forecast_location[0]), 2)
            now = datetime.now()
            tc['position_time'] = datetime.strptime(u"%s"%now.year+forecast_time,'%Y%m%d%H').isoformat()
            tc['name'] = name
            tc['position_type'] = u'F'
            tc_items.append(tc)
        return tc_items
