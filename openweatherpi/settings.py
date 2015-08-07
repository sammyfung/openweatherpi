# -*- coding: utf-8 -*-

# Scrapy settings for openweatherpi project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'openweatherpi'

SPIDER_MODULES = ['openweatherpi.spiders']
NEWSPIDER_MODULE = 'openweatherpi.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'openweatherpi (+http://www.yourdomain.com)'

# Scrapy Item Pipelines in Active
ITEM_PIPELINES = {
  'openweatherpi.pipelines.OpenweatherpiPipeline': 300,
}

# Configuration for DjangoItems
import sys, os
django_path = os.path.join(os.path.dirname(__file__),'../openweatherdata')
sys.path.append(os.path.abspath(django_path))
os.environ['DJANGO_SETTINGS_MODULE'] = 'openweatherdata.settings'

# Getting enviornment variables
import os
CWB_USERNAME = os.environ['CWB_USERNAME']
CWB_PASSWORD = os.environ['CWB_PASSWORD']
