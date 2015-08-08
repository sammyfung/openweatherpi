openweatherpi
=============

openweatherpi is a open-source open weather data web scraper project.

Source Code release on Github: https://github.com/sammyfung/openweatherpi

Author
------

Sammy Fung <sammy@sammy.hk>

Installation
------------

Installing openweatherpi and required:

$ git clone https://github.com/sammyfung/openweatherpi.git
$ virtualenv env
$ source env/bin/activate
$ pip install -r openweatherpi/requirement.txt

Initialize database for Django web framework in default sqlite and create first Django admin user:

$ cd openweatherpi/openweatherdata
$ ./manage.py makemigration
$ ./manage.py syncdb

Setting CWB Username and Password
$ export CWB_USERNAME='your@email.address'
$ export CWB_PASSWORD='yourpassword'

Web Scraping CWB Tropical Cyclone Data
$ cd openweatherpi
$ scrapy crawl cwb_tc

