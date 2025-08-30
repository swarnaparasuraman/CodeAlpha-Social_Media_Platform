from django.urls import path
from . import views

app_name = 'media_manager'

urlpatterns = [
    path('', views.media_library, name='library'),
    path('upload/', views.upload_media, name='upload'),
    path('media/<uuid:media_id>/', views.media_detail, name='detail'),
    path('media/<uuid:media_id>/delete/', views.delete_media, name='delete'),
    path('collections/', views.collections, name='collections'),
    path('collections/<uuid:collection_id>/', views.collection_detail, name='collection_detail'),
    path('stats/', views.media_stats, name='stats'),
]
