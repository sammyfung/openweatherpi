# -*- coding: utf-8 -*-
# openweatherpi - CWB Tropical Cyclone (Hourly Data on Web Site) Web Scraper
# Sammy Fung <sammy@sammy.hk>
import scrapy, re
from openweatherpi.items import TropicalCycloneItem
from datetime import datetime

class CwbTcHourlySpider(scrapy.Spider):
    name = "cwb_tc_hourly"
    allowed_domains = ["cwb.gov.tw"]
    start_urls = (
        'http://www.cwb.gov.tw/V7/index.htm',
    )
    agency = u'CWB'
    mps2kmh = 3.6
    wind_unit = u'KMH'

    def parse(self, response):
        bar = response.xpath(u'//div[@id="NavPath"]/a[contains(@href, "/V7/prevent/warning")]/@href').extract()
        if len(bar) > 0:
            report_url = re.sub('\.htm','_content.htm', bar[0])
            return scrapy.Request(url='http://www.cwb.gov.tw%s'%report_url, callback=self.parse_report)
        else:
            pass

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

