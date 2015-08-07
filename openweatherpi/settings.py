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

# Getting enviornment variables
import os
CWB_USERNAME = os.environ['CWB_USERNAME']
CWB_PASSWORD = os.environ['CWB_PASSWORD']
