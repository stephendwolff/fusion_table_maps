from django.conf.urls import url

from .views import GoogleFusionTableMapView, GoogleMapLocationCreate, clear_fusion_table_view

urlpatterns = [
    url(r'^$', GoogleFusionTableMapView.as_view(), name='single-page-app'),
    url(r'^clear_fusion_table', clear_fusion_table_view, name='clear-fusion-table'),
    url(r'^save_map_location/$', GoogleMapLocationCreate.as_view(), name='save-map-location'),
]
