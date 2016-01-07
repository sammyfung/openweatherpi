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

**Setting enviornment variables for Django and CWB Account**

$ export PYTHONPATH=/full/path/to/your/django/project   

$ export DJANGO_SETTINGS_MODULE=just_filename_of_your_django_settings_file    

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
