# -*- coding: utf-8 -*-
# openweatherpi - JTWC Tropical Cyclone Web Scraper
# Sammy Fung <sammy@sammy.hk>
import scrapy, StringIO, re
from openweatherpi.items import TropicalCycloneItem
from datetime import datetime, timedelta

class JtwcSpider(scrapy.Spider):
    name = "jtwc"
    allowed_domains = ["usno.navy.mil", "anonymouse.org"]
    proxy = 'http://anonymouse.org/cgi-bin/anon-www.cgi/'
    start_urls = (
        # ### Direct Access ###
        #'http://www.usno.navy.mil/NOOC/nmfc-ph/RSS/jtwc/ab/abpwweb.txt',
        # Thru Proxy:
        #'%s%s'%(proxy, 'http://www.usno.navy.mil/NOOC/nmfc-ph/RSS/jtwc/ab/abpwweb.txt'),
        # JTWC
        '%s%s'%(proxy, 'http://www.usno.navy.mil/JTWC/'),
    )
    agency = u'JTWC'
    ktstokmh = 1.852
    wind_unit = u'KMH'

    def conv_reporttime(self, report_time):
        # Convert Report Time Line to Time
        now = datetime.now()
        if len(report_time) != 6:
            report_time = re.split('\W+',report_time)[2]
        report_time = u"%s%s%s%s"%(now.year,now.month,report_time,'UTC')
        report_time = datetime.strptime(report_time, '%Y%m%d%H%M%Z')+timedelta(hours=8)
        return report_time.isoformat()

    def parse(self,response):
        items = []
        # Checking overview report
        items += [ scrapy.Request(url='%s%s'%(self.proxy, 'http://www.usno.navy.mil/NOOC/nmfc-ph/RSS/jtwc/ab/abpwweb.txt'),
                                  callback=self.parse_overview) ]
        # Checking for any TC reports for NW Pacfic Area
        url = response.xpath('//table/tr/td[2]/ul/li/a/@href').extract()
        for i in url:
            if re.search('wp\d{4}web.txt', i):
                items += [ scrapy.Request(url='%s%s'%(self.proxy, i), callback=self.parse_tc) ]
        return items

    def parse_tc(self, response):
        tc_items = []
        code = ''
        name = ''
        report_time = ''
        forecast = False
        report = StringIO.StringIO(response.body)
        lines = report.readlines()
        for line in lines:
            if re.search(u'^WTPN\d{2}',line):
                report_time = self.conv_reporttime(line)
            # ### Analyse TC Report ###
            # Tropical Cyclone Basic Information
            if re.search(u'^1\. ', line):
                if re.search(u'\(', line):
                    name = re.split('\(',line)[1]
                    name = re.split('\)',name)[0]
                    name = u"%s"%name.upper()
                for i in re.split(' ', line):
                    if re.search('\d{2}W', i):
                        code = u"%s"%i
            # Getting current warning position
            elif re.search(u'^\s*FORECASTS:',line):
                forecast = True
            elif re.search(u'Z --- ', line):
                tc = TropicalCycloneItem()
                tc['agency'] = self.agency
                tc['code'] = code
                tc['name'] = name
                tc['report_time'] = report_time
                if forecast:
                    tc['position_type'] = u"F"
                else:
                    tc['position_type'] = u"C"
                for i in re.split(' ', line):
                    if re.search(u'\d{6}Z', i):
                        # Getting position time
                        tc['position_time'] = self.conv_reporttime(i[:6])
                    if re.search(u'\dN', i):
                        tc['latitude'] = round(float(re.sub('N','',i)), 2)
                    if re.search(u'\dE', i):
                        tc['longitude'] = round(float(re.sub('E','',i)), 2)
            elif re.search(u'^\s*MAX SUSTAINED WINDS - ', line):
                line = re.sub(u'.*WINDS - ','',line)
                line = re.split(' ', line)
                wind_speed = int(round(int(line[0])*self.ktstokmh, 0))
                tc['wind_speed'] = wind_speed
                tc['gust_speed'] = int(round(int(line[3])*self.ktstokmh, 0))
                if tc['wind_speed'] < 62:
                    tc['cyclone_type'] = u"TD"
                elif tc['wind_speed'] < 118:
                    tc['cyclone_type'] = u"TS"
                elif tc['wind_speed'] < 240:
                    tc['cyclone_type'] = u"TY"
                else:
                    tc['cyclone_type'] = u"STY"
                tc['wind_unit'] = self.wind_unit
                tc_items.append(tc)
        return tc_items

    def parse_overview(self, response):
        nwarea = False
        tdarea = False
        m = '' # Message Paragraph
        tc = [] # List of Tropical Cyclones
        td = [] # List of Tropical Disturbances
        report_time = ''
        item_list = []
        report = StringIO.StringIO(response.body)
        lines = report.readlines()
        for line in lines:
            if re.search(u'^ABPW10',line):
                report_time = self.conv_reporttime(line)
            # Looking into NW Pacific Area Information
            if re.search(u'^1. WESTERN NORTH PACIFIC AREA',line):
                nwarea = True
            elif re.search(u'^2. SOUTH PACIFIC AREA', line):
                nwarea = False
            elif nwarea == True:
                # In NW Pacific information
                if re.search(u'B. TROPICAL DISTURBANCE SUMMARY:',line):
                    if len(tc) > 0:
                        if not(re.search(u'NO OTHER SUSPECT AREA',m) or re.search(u'NO OTHER TROPICAL CYCLONE',m)):
                            tc = tc + [m]
                    m = ""
                    tdarea = True
                elif re.search(u'^\s*\([0-9]*\)',line) and len(m) > 0:
                    if tdarea == False:
                        # add to Tropical Cyclone line
                        tc = tc + [m]
                    elif not(re.search(u'IS NOW THE SUBJECT OF A TROPICAL CYCLONE WARNING',m)):
                        # add to Tropical Disturbance list
                        td = td + [m]
                    m = ""
                if not(re.search(u'A. TROPICAL CYCLONE SUMMARY:',line) or \
                        re.search(u'B. TROPICAL DISTURBANCE SUMMARY:',line)):
                    m = m + line

        # Analyse Tropical Disturbance Information
        num = 0
        for d in td:
            d = re.sub("\r\n"," ",d)
            d = re.sub("\n"," ",d)
            d = re.sub("  *"," ",d)
            if re.search(u'HAS PERSISTED NEAR', d):
                item = TropicalCycloneItem()
                item['report_time'] = report_time
                item['position_time'] = report_time
                item['position_type'] = u'C'
                item['cyclone_type'] = u'LPA'
                item['agency'] = self.agency
                item['name'] = u''
                item['code'] = u'%sW'%(99-num)
                d = re.sub(".*HAS PERSISTED NEAR ","",d)
                item['latitude'] = round(float(re.sub("N.*","",d)), 2)
                item['longitude'] = round(float(re.sub("E.*","",re.sub(".*[0-9]N ","",d))), 2)
                item_list.append(item)
                num += 1
        return item_list
