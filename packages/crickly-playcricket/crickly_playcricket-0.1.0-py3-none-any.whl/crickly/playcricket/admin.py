# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from crickly.playcricket import models

admin.site.register(models.Club)
admin.site.register(models.Competition)
admin.site.register(models.Ground)
admin.site.register(models.League)
admin.site.register(models.Match)
admin.site.register(models.Player)
admin.site.register(models.Scorer)
admin.site.register(models.Team)
admin.site.register(models.Umpire)
