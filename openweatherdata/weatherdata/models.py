# openweatherpi - Open Weather Data Model for Django Web Framework
# Sammy Fung <sammy@sammy.hk>
from django.db import models

class TropicalCyclone(models.Model):
    AGENCY_CHOICES = (
        ('CWB', 'Central Weather Bureau'),
    )
    POS_TYPE_CHOICES = (
        ('C', 'Current'),
        ('F', 'Forecast'),
    )
    TC_TYPE_CHOICES = (
        ('DIS', 'Tropical Disturbance'),
        ('TD', 'Tropical Depression'),
        ('TS', 'Tropical Storm'),
        ('TY', 'Typhoon'),
        ('STY', 'Super Typhoon'),
    )
    WIND_UNIT_CHOICES = (
        ('KMH', 'km/h'),
    )
    position_time = models.DateTimeField(verbose_name='Position Time')
    agency = models.CharField(verbose_name='Agency',max_length=4, choices=AGENCY_CHOICES)
    report_time = models.DateTimeField(verbose_name='Report Time')
    code = models.CharField(verbose_name='Code',max_length=3)
    name = models.CharField(verbose_name='Name',max_length=20)
    position_type = models.CharField(verbose_name='Position Type', max_length=1, choices=POS_TYPE_CHOICES)
    cyclone_type = models.CharField(verbose_name='Cyclone Type', max_length=3, choices=TC_TYPE_CHOICES)
    latitude = models.FloatField(verbose_name='Latitude') # N - positive, S - negative
    longitude = models.FloatField(verbose_name='Longitude') # E - positive, W - positive
    pressure = models.IntegerField(verbose_name='Surface Pressure', blank=True, null=True)
    wind_speed = models.IntegerField(verbose_name='Max Sustained Wind', blank=True, null=True)
    wind_unit = models.CharField(verbose_name='Wind Unit',max_length=3, blank=True, null=True, choices=WIND_UNIT_CHOICES)

