openweatherpi
=============

openweatherpi is a open-source open weather data web scraper project.

Source Code release on Github: https://github.com/sammyfung/openweatherpi

Author
------

Sammy Fung < sammy@sammy.hk >


Requirement
-----------

You must installed a django web framework project with openweather app.

openweather app (for django) is available at https://github.com/sammyfung/openweather

Installation
------------

**Installing openweatherpi and required:**

$ git clone https://github.com/sammyfung/openweatherpi.git

$ virtualenv env

$ source env/bin/activate

$ pip install -r openweatherpi/requirement.txt

**Initialize database for Django web framework in default sqlite and create first Django admin user:**

$ cd openweatherpi/openweatherdata

$ ./manage.py makemigration

$ ./manage.py syncdb

**Setting CWB Username and Password**

$ export CWB_USERNAME='your@email.address'

$ export CWB_PASSWORD='yourpassword'

**Web Scraping CWB Tropical Cyclone Data**

$ cd openweatherpi

$ scrapy crawl cwb_tc

**Web Scraping JTWC Tropical Cyclone Data**

$ scrapy crawl jtwc

**Web Scraping HKO Tropical Cyclone Data**

$ scrapy crawl hko_tc

**Web Scraping JMA Tropical Cyclone Data**

$ scrapy crawl jma_tc
