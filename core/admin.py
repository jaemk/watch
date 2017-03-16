from django.contrib import admin

from core import models


admin.site.register(models.Cam)
admin.site.register(models.Snap)
admin.site.register(models.Archive)
admin.site.register(models.Token)

