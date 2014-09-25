from django.contrib import admin

from boto1.models import Image, Hit, Result

admin.site.register(Image)
admin.site.register(Hit)
admin.site.register(Result)

