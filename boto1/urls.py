

from django.conf.urls import patterns, url
from django.contrib.auth.views import login, logout

from boto1 import views
from django.views.decorators.csrf import csrf_exempt

urlpatterns = patterns('',
  url(r'^$', views.index, name='index'),

  # this one will be addressed by the form
  url(r'^im/(?P<pk>\d+)/$', views.ImageAnnotation.as_view(), name = 'image_annotation_form'),
)


