from django.contrib import admin
from django.urls import path
from app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('user/create/', views.create_user, name="create_user"),
    path('post/create/', views.create_post, name="create_post"),
    # Add remaining endpoints here
    path('users/top', views.get_top_users, name="get_top_users"),
    path('users/follow', views.follow_user, name="follow_user"),
    path('users/feed/<int:user_id>', views.user_feed, name="user_feed")

]
