# -*- coding: utf-8 -*-
# openweatherpi - CWB Tropical Cyclone Web Scraper
# Sammy Fung <sammy@sammy.hk>
import scrapy, re, StringIO, zipfile, os
from openweatherpi.items import TropicalCycloneItem
from datetime import datetime

class CwbTcSpider(scrapy.Spider):
    name = "cwb_tc"
    allowed_domains = ["cwb.gov.tw"]
    start_urls = (
        'http://www.cwb.gov.tw/V7/index.htm',
    )
    agency = u'CWB'
    mps2kmh = 3.6
    wind_unit = u'KMH'

    def parse(self, response):
        items = []
        bar = response.xpath(u'//div[@id="NavPath"]/a[contains(@href, "/V7/prevent/warning")]/@href').extract()
        if len(bar) > 0:
            report_url = re.sub('\.htm','_content.htm', bar[0])
            items += [ scrapy.Request(url='http://www.cwb.gov.tw%s'%report_url, callback=self.parse_report) ]
        items += [ scrapy.Request(url='http://opendata.cwb.gov.tw/doLogin', callback=self.login) ]
        return items

    def parse_report(self, response):
        content = scrapy.Selector(response).xpath(u'//div/pre/text()').extract()[0].encode('utf-8')
        content = unicode(content, 'utf-8')
        content = re.split(u'\r\n',content)
        tc_report = False
        tc = TropicalCycloneItem()
        report_time = u''
        for i in content:
            if re.search(u'中央氣象局  颱風警報單', i):
                tc_report = True
            elif re.search(u'^發    布    時    間：', i):
                rt = re.sub(u'.*民國','',i)
                rt = re.sub(u'[年月日時分]',' ',rt)
                rt = re.sub(u'。.*','',rt)
                rt = re.split(' ',rt)
                report_time = u'%s'%(1911+int(rt[0]))
                for j in range(1,5):
                    report_time += u"%02d"%int(rt[j])
                tc['report_time'] = datetime.strptime(report_time, "%Y%m%d%H%M")
            elif re.search(u'^颱 風 強 度 及 編 號：', i):
                if re.search(u'.*熱帶性低氣壓.*',i):
                    tc['cyclone_type'] = u"TD"
                elif re.search(u'.*輕度颱風.*',i):
                    tc['cyclone_type'] = u"TS"
                elif re.search(u'.*中度颱風.*',i):
                    tc['cyclone_type'] = u"TY"
                elif re.search(u'.*強烈颱風.*',i):
                    tc['cyclone_type'] = u"STY"
                else:
                    tc['cyclone_type'] = u""
                tc['code'] = u"%sW"%re.sub(u'號.*','',re.sub(u'.*編號第','',i))
                tc['name'] = re.sub(u'，.*','',re.sub(u'.*國際命名：','',i))
            elif re.search(u'^中    心    氣    壓：',i):
                tc['pressure'] = int(re.sub(u'.*中    心    氣    壓：','',re.sub(u'百帕.*','',i)))
            elif re.search(u'^目    前    時    間：',i):
                position_time = re.sub(u'.*間：','',i)
                position_time = re.sub(u'[日時]',' ',position_time)
                position_time = re.split(u' ',position_time)
                tc['position_time'] = report_time[:6]+u'%02d%02d'%(int(position_time[0]),int(position_time[1]))
                tc['position_time'] = datetime.strptime(tc['position_time'], "%Y%m%d%H")
            elif re.search(u'^中    心    位    置：',i):
                tc['latitude'] = round(float(re.sub(u' .*','',re.sub(u'.*北緯 ','',i))), 2)
                tc['longitude'] = round(float(re.sub(u' .*','',re.sub(u'.*東經 ','',i))), 2)
            elif re.search(u'^近 中 心 最 大 風 速：',i):
                tc['wind_speed'] = int(re.sub(u' .*','',re.sub(u'.*約每小時 ','',i)))
                tc['wind_unit'] = u'KMH'
            elif re.search(u'^瞬 間 之 最 大 陣 風：',i):
                gust_speed = int(re.sub(u' .*','',re.sub(u'.*約每小時 ','',i)))
        if tc_report:
            tc['agency'] = self.agency
            tc['position_type'] = u'C'
            return [ tc ]

    def login(self, response):
        # Getting enviornment variables CWB_USERNAME and CWB_PASSWORD
        form_data = { 'userid': os.environ['CWB_USERNAME'], 'password': os.environ['CWB_PASSWORD'] }
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
        current = scrapy.Selector(text=lines).xpath('//kml/document/folder/folder')
        for cyclone in current:
            desc = re.sub('[\r\n]','', cyclone.xpath('placemark/description/text()').extract()[0])
            code = re.sub(u".*編號第 ",'',desc)
            code = "%sW"%re.sub(' .*','', code)
            name = re.sub(u".*國際命名 ",'',desc)
            name = re.sub(u"\).*",'',name)
            current_location = re.split(',',cyclone.xpath('placemark/point/coordinates/text()').extract()[0])
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
            #for i in scrapy.Selector(text=lines).xpath('//kml/document/folder/folder/folder/placemark'):
            for i in cyclone.xpath('folder/placemark'):
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
