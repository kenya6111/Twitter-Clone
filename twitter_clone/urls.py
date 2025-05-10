from django.urls import path
from . import views

urlpatterns = [
    path('', views.top_view, name='top'),
    path("users/signup", views.signup_view, name="signup"),
    path('users/email_verify/', views.email_verify_view, name='email_verify'),
    path('users/password_input/', views.password_input_view, name='password_input'),
    path('main/', views.main_view, name='main'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit', views.profile_edit_view, name='profile_edit'),
    path('tweet', views.tweet_view, name='tweet'),
    path('tweet_detail', views.tweet_detail_view, name='tweet_detail'),
    path('like', views.like_view, name='like'),
    path('retweet', views.retweet_view, name='retweet'),
    path('follow', views.follow_unfollow, name='follow'),
    path('bookmark', views.bookmark, name='bookmark'),
    path('message', views.message, name='message'),
    path('make_message_room', views.make_message_room_view, name='make_message_room'),
]