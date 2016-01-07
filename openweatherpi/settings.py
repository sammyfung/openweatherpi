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

# Initialize Django web framework for data store
# Use environment variable PYTHONPATH for abspath to Django project
# and DJANGO_SETTINGS_MODULE for Settings filename of Django project
try:
    import django
    django.setup()
except ImportError:
    # Allow to work without Django
    pass
