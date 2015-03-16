from django.conf.urls import patterns, url

dummy_view = lambda: True

urlpatterns = patterns('',
    url(r'^(?P<pk>\w+)/', dummy_view, name="viewname"),
)