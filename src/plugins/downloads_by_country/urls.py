from django.urls import re_path

from plugins.downloads_by_country import views

urlpatterns = [
    re_path(r"^$", views.index, name="downloads_by_country_index"),
]
