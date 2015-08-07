# openweatherpi - Open Weather Data Model Admin for Django Web Framework
# Sammy Fung <sammy@sammy.hk>
from django.contrib import admin
from weatherdata.models import TropicalCyclone

class TropicalCycloneAdmin(admin.ModelAdmin):
  list_display = ('report_time', 'agency', 'code', 'name', 'position_type', 'position_time', 'latitude', 'longitude',
                  'cyclone_type', 'wind_speed', 'wind_unit', 'pressure')

admin.site.register(TropicalCyclone, TropicalCycloneAdmin)