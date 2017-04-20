from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^', views.add_crawl_point, name="add_crawl_point"),
]
