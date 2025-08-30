from django.urls import path
from . import views

app_name = 'posts'

urlpatterns = [
    path('', views.feed_view, name='feed'),
    path('create/', views.create_post_view, name='create'),
    path('<int:pk>/', views.post_detail_view, name='detail'),
    path('<int:pk>/edit/', views.edit_post_view, name='edit'),
    path('<int:pk>/delete/', views.delete_post_view, name='delete'),
    path('<int:pk>/like/', views.like_post_view, name='like'),
    path('<int:pk>/comment/', views.add_comment_view, name='add_comment'),
    path('comment/<int:pk>/delete/', views.delete_comment_view, name='delete_comment'),
    path('explore/', views.explore_view, name='explore'),
    path('reels/', views.reels_view, name='reels'),
    path('search/', views.search_posts_view, name='search'),
]
