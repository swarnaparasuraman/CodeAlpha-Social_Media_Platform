from django.urls import path
from . import views

app_name = 'social'

urlpatterns = [
    path('notifications/', views.notifications_view, name='notifications'),
    path('notifications/mark-read/', views.mark_notifications_read_view, name='mark_notifications_read'),
    path('messages/', views.messages_view, name='messages'),
    path('messages/<int:conversation_id>/', views.conversation_detail_view, name='conversation_detail'),
]
