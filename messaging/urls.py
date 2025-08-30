from django.urls import path
from . import views

app_name = 'messaging'

urlpatterns = [
    path('', views.messages_list_view, name='list'),
    path('<int:conversation_id>/', views.conversation_detail_view, name='conversation_detail'),
    path('<int:conversation_id>/send/', views.send_message_view, name='send_message'),
    path('start/<str:username>/', views.start_conversation_view, name='start_conversation'),
]
